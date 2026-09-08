"""
* Plugin and Template Loader
"""

from collections.abc import Callable
from contextlib import suppress
from functools import cached_property
from json import load
from logging import getLogger
from pathlib import Path
from shutil import rmtree
from threading import Lock
from types import ModuleType
from typing import Annotated, Any, Literal, NotRequired, Protocol, TypedDict

import yarl
from omnitils.api.gdrive import gdrive_download_file, gdrive_get_metadata
from omnitils.modules import get_local_module, import_module_from_path, import_package
from omnitils.strings import normalize_ver
from py7zr import SevenZipFile
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationError,
    model_validator,
)
from pydantic_core import Url

from src import DEFAULT_HEADERS
from src._config import ConfigHandler
from src._state import PATH, AppConstants, AppEnvironment
from src.enums.mtg import (
    LayoutCategory,
    LayoutType,
    layout_map_display_condition,
    layout_map_display_condition_dual,
    layout_map_types,
    layout_map_types_display,
)
from src.utils.data_structures import dump_model, parse_model
from src.utils.download import download_cloudfront
from src.utils.event import SubscribableEvent

_logger = getLogger(__name__)

# region Types


class TemplateUpdate(TypedDict):
    """Details about the latest update for a given AppTemplate."""

    name: NotRequired[str]
    version: NotRequired[str]
    size: NotRequired[int]


class TemplateDetails(TypedDict):
    """Details about a specific template within the TemplateCategoryMap."""

    name: str
    class_name: str
    config: ConfigHandler


ManifestTemplateMap = dict[str, dict[str, list[LayoutType]]]
"""Dictionary which maps a template's displayed names to classes, and classes to template types."""


SymbolRarity = Literal["80", "B", "C", "H", "M", "R", "S", "T", "U", "WM"]


class SymbolsMeta(BaseModel):
    date: str
    version: str
    uri: str


class SymbolsSet(BaseModel):
    aliases: dict[str, str]
    routes: dict[str, str]
    rarities: dict[SymbolRarity, str]
    symbols: dict[str, list[SymbolRarity]]


class SymbolsWatermark(BaseModel):
    routes: dict[str, str] | None = None
    symbols: list[str]


class SymbolsManifest(BaseModel):
    meta: SymbolsMeta
    set: SymbolsSet
    watermark: SymbolsWatermark


class PluginInfo(BaseModel):
    name: str | None = None
    author: str | None = None
    desc: str | None = None
    source: str | None = None
    docs: str | None = None
    license: str | None = None
    version: str | None = None


class TemplateFileInfo(BaseModel):
    name: str | None = None
    id: str | None = None
    desc: str | None = None
    version: str | None = None
    templates: ManifestTemplateMap


TemplateFileInfoRoot = RootModel[dict[str, TemplateFileInfo]]


class PluginManifest(BaseModel):
    plugin: Annotated[PluginInfo, Field(alias="PLUGIN")]
    files: Annotated[dict[str, TemplateFileInfo], Field(exclude=True)] = {}

    @model_validator(mode="before")
    @classmethod
    def extra_validator(cls, data: Any) -> Any:
        if isinstance(data, dict):
            exclude_keys = [*cls.model_fields.keys(), "PLUGIN"]
            for key, value in data.items():  # pyright: ignore[reportUnknownVariableType]
                if not isinstance(key, str) or key in exclude_keys:
                    continue
                data[key] = TemplateFileInfo.model_validate(value)
        return data  # pyright: ignore[reportUnknownVariableType]

    @model_validator(mode="after")
    def post_validate(self) -> PluginManifest:
        if self.model_extra:
            self.files = self.model_extra
        return self

    model_config = ConfigDict(extra="allow")


# endregion Types

# region Plugins


class RemotePluginDefinitionBase(BaseModel):
    name: str
    author: str


class RemoteGithubPluginDefinition(RemotePluginDefinitionBase):
    github_author: str
    github_repo: str


class RemoteGitPluginDefinition(RemotePluginDefinitionBase):
    git_repo: Url


class RemotePluginDefinitions(
    RootModel[dict[str, RemoteGithubPluginDefinition | RemoteGitPluginDefinition]]
):
    pass


_template_import_lock = Lock()


class AppPlugin:
    """Represents a Proxyshop plugin found in `src/plugins/`.

    Args:
        con: Global application constants object.
        path: Path to the plugin directory.

    Attributes:
        _root (Path): Root path where the plugin's files are located.
        _manifest (Path): Path to the plugin's manifest file.
        _templates (dict[str, TemplateFileInfo]): Data loaded from manifest file.
        _info (PluginInfo): Top level table from the manifest file containing the plugin's metadata.
        _module (ModuleType): This plugin's loaded Python module.

    Raises:
        FileNotFoundError: If the plugin path or manifest file couldn't be found.
        ModuleNotFoundError: If the plugin's python module couldn't be found.
    """

    def __init__(
        self,
        con: AppConstants,
        env: AppEnvironment,
        path: Path,
        template_file_versions: dict[str, str],
    ):
        self._module: ModuleType | None = None

        # Save a reference to the global application constants
        self.con: AppConstants = con
        self.env: AppEnvironment = env
        self.versions = template_file_versions

        # Ensure path exists
        if not path.is_dir():
            raise FileNotFoundError(f"Couldn't locate plugin path: {path}")
        self._root = path

        # Find a valid manifest
        plugin_manifest_path = Path(path, "manifest.yml")
        if not plugin_manifest_path.is_file():
            plugin_manifest_path = plugin_manifest_path.with_suffix(".yaml")
        if not plugin_manifest_path.is_file():
            plugin_manifest_path = plugin_manifest_path.with_suffix(".json")
        if not plugin_manifest_path.is_file():
            plugin_manifest_path = plugin_manifest_path.with_suffix(".toml")
        if not plugin_manifest_path.is_file():
            raise FileNotFoundError(
                f"Couldn't locate manifest file for plugin at path: {path}"
            )

        # Load the manifest data
        if plugin_manifest_path.suffix == ".json":
            # Backwards compatibility
            plugin_manifest = self.load_manifest_json_legacy(plugin_manifest_path)
        else:
            plugin_manifest: PluginManifest = parse_model(
                plugin_manifest_path, PluginManifest
            )

        self._info: PluginInfo = plugin_manifest.plugin
        self._templates: dict[str, TemplateFileInfo] = plugin_manifest.files

        # Load templates
        self.load_templates()

    @cached_property
    def id(self) -> str:
        return self._root.name

    @cached_property
    def template_map(self) -> dict[str, AppTemplate]:
        """dict[str, AppTemplate]: A dictionary mapping of AppTemplate's by file name pulled from this plugin."""
        return {}

    """
    * Pathing
    """

    @property
    def root(self) -> Path:
        return self._root

    @cached_property
    def path_config(self) -> Path:
        """Path: Path to this plugin's config directory."""
        return Path(self._root, "config")

    @cached_property
    def path_ini(self) -> Path:
        """Path: Path to this plugin's INI config directory."""
        return Path(self._root, "config_ini")

    @cached_property
    def path_img(self) -> Path:
        """Path: Path to this plugin's preview image directory."""
        return Path(self._root, "img")

    @cached_property
    def path_templates(self) -> Path:
        """Path: Path to this plugin's templates directory."""
        return self._root / "templates"

    """
    * Plugin Metadata
    """

    @cached_property
    def name(self) -> str:
        """str: Displayed name of the plugin. Fallback on root directory name."""
        return self._info.name if self._info.name is not None else self._root.stem

    @cached_property
    def author(self) -> str | None:
        """str: Displayed name of the plugin's author. Fallback on name."""
        return self._info.author if self._info.author is not None else None

    @cached_property
    def description(self) -> str | None:
        """Optional[str]: Displayed description of the plugin. Fallback on None."""
        return self._info.desc

    @cached_property
    def source(self) -> str | None:
        """Link to the hosted files of this plugin."""
        return self._info.source

    @cached_property
    def docs(self) -> str | None:
        """Link to the hosted documentation for this plugin."""
        return self._info.docs

    @cached_property
    def license(self) -> str | None:
        """Name of the open source license carried by this plugin. Fallback on MPL-2.0."""
        return self._info.license

    @cached_property
    def version(self) -> str:
        """Current version of the plugin."""
        return self._info.version or "0.0.0"

    """
    * Module Details
    """

    @property
    def module(self) -> ModuleType | None:
        if not self._module:
            self.load_module()
        return self._module

    @cached_property
    def module_path(self) -> Path:
        """Path: The path to this plugin's Python module."""
        return Path(self._root, "py")

    @cached_property
    def module_name(self) -> str:
        """str: The name of this plugin's Python module, e.g. 'plugins.MyPlugin.py'."""
        return f"{self._root.name}.py"

    """
    * Plugin Methods
    """

    def load_manifest_json_legacy(self, path: Path) -> PluginManifest:
        """Load the legacy `manifest.json` data for this plugin.

        Raises:
            ValueError: If the manifest file contains invalid data.
        """

        try:
            with open(path, "r", encoding="UTF-8") as f:
                # Load Plugin metadata
                templates: dict[str, Any] | None = load(f)
                if not isinstance(templates, dict):
                    raise TypeError("Plugin manifest isn't a dictionary")
                manifest = PluginManifest(plugin=templates.pop("PLUGIN", {}), files={})
        except Exception as e:
            raise ValueError(f"Manifest file contains invalid data: {path}") from e

        # Re-format templates dict for TemplateDetails
        manifest.files = {}
        for t, temps in templates.items():
            if t not in layout_map_types:
                continue
            for name, details in temps.items():
                # Add new file
                file_name = details.get("file", "")
                class_name = details.get("class", "")
                manifest.files.setdefault(file_name, TemplateFileInfo(templates={}))
                # Add Google Drive ID
                if details.get("id"):
                    manifest.files[file_name].id = details["id"]

                template_type = LayoutType(t)

                # Existing name
                if name in manifest.files[file_name].templates:
                    # Existing class name
                    if class_name in manifest.files[file_name].templates[name]:
                        manifest.files[file_name].templates[name][class_name].append(
                            template_type
                        )
                        continue
                    # Add new class
                    manifest.files[file_name].templates[name][class_name] = [
                        template_type
                    ]
                # Add new template
                manifest.files[file_name].templates[name] = {
                    class_name: [template_type]
                }

        return manifest

    def load_templates(self) -> None:
        """Load the dictionary of AppTemplate's pulled from this plugin's manifest file.

        Returns:
            A dictionary where keys are PSD/PSB filenames and values are AppTemplate objects.
        """
        # Use one config manager per python class
        config_managers: dict[str, ConfigHandler] = {}
        for file_name, data in self._templates.items():
            self.template_map[file_name] = AppTemplate(
                con=self.con,
                env=self.env,
                data=data,
                file_name=file_name,
                config_managers=config_managers,
                versions=self.versions,
                plugin=self,
            )

    def load_module(self, hotswap: bool = False) -> None:
        """Load the plugin's Python module."""
        # Generate a 'py' module if it doesn't exist
        if not self.module_path.is_dir():
            self.module_path.mkdir(mode=777, parents=True, exist_ok=True)

        # Check if root has init
        root_init = self._root / "__init__.py"
        has_root_init = root_init.is_file()
        if not has_root_init:
            with open(root_init, "w", encoding="utf-8") as f:
                f.write("")
        import_module_from_path(name=self._root.stem, path=root_init, hotswap=hotswap)
        # if not has_root_init:
        #     try:
        #         os.remove(root_init)
        #     except OSError:
        #         print("Failed to remove temporary plugin init file:", str(root_init))
        #         print_exc()

        # Ensure init file in py module
        if not Path(self.module_path, "__init__.py").is_file():
            with open(
                Path(self.module_path, "__init__.py"), "w", encoding="utf-8"
            ) as f:
                f.write("from .templates import *")

        # Attempt to load this module
        self._module = import_package(
            name=self.module_name, path=self.module_path, hotswap=hotswap
        )

    def get_template_list(self) -> list[AppTemplate]:
        """list[AppTemplate]: Returns a list of AppTemplate's pulled from this plugin."""
        return list(self.template_map.values())

    def remove(self) -> None:
        rmtree(self._root)


def get_all_plugins(
    con: AppConstants, env: AppEnvironment, template_file_versions: dict[str, str]
) -> dict[str, AppPlugin]:
    """Gets a dict of 'AppPlugin' objects mapped by their name attribute.

    Args:
        con: Global constants object.
        env: Global environment object.

    Returns:
        A mapping of plugin ids to their respective 'AppPlugin' object.
    """
    plugins: dict[str, AppPlugin] = {}

    # Load all plugins and plugin templates
    for folder in [p for p in PATH.PLUGINS.iterdir() if p.is_dir()]:
        if folder.stem.startswith("__") or folder.stem.startswith("!"):
            continue
        try:
            plugin = AppPlugin(
                con=con,
                env=env,
                path=folder,
                template_file_versions=template_file_versions,
            )
            plugins[plugin.id] = plugin
        except Exception:
            _logger.exception(f"Failed to load plugin at path: {folder}")
    return dict(sorted(plugins.items()))


# endregion Plugins

# region Templates

TemplateFileVersionsModel = RootModel[dict[str, str]]


def get_template_file_versions() -> TemplateFileVersionsModel:
    if PATH.SRC_DATA_VERSIONS.exists():
        try:
            return parse_model(PATH.SRC_DATA_VERSIONS, TemplateFileVersionsModel)
        except ValidationError:
            pass
    return TemplateFileVersionsModel({})


def get_template_class(
    class_name: str, plugin: AppPlugin | None = None, force_reload: bool = False
) -> type[object]:
    """
    Loads the template class for a template of a given class name.

    Raises:
        Exception: if module loading fails.
    """
    with _template_import_lock:
        if plugin:
            # Load plugin module
            if force_reload:
                plugin.load_module(hotswap=True)
            module = plugin.module
        else:
            # Load local module
            module = get_local_module(module_path="src.templates", hotswap=force_reload)
        return getattr(module, class_name)


def sort_layout_categories(
    items: set[LayoutCategory], place_first: LayoutCategory | None = None
) -> list[LayoutCategory]:
    first_item: LayoutCategory | None = None
    out = list(items)
    if place_first and (place_first in items):
        out.remove(place_first)
        first_item = place_first
    out.sort()
    if first_item:
        out.insert(0, first_item)
    return out


class RenderableTemplate(Protocol):
    name: str
    plugin: AppPlugin | None

    def get_config(self, class_name: str) -> ConfigHandler | None: ...

    def get_class_name_and_file_for_layout(
        self, layout_type: LayoutType
    ) -> tuple[str, Path] | None: ...


class TemplateClassDetails(TypedDict):
    config: ConfigHandler
    layouts: list[LayoutType]


class NamedTemplate(RenderableTemplate):
    def __init__(
        self,
        name: str,
        template_classes: dict[str, TemplateClassDetails],
        parent: AppTemplate,
    ) -> None:
        self.name = name
        self.template_classes = template_classes
        self.parent = parent
        self.plugin = parent.plugin

    @cached_property
    def layout_categories(self) -> set[LayoutCategory]:
        categories: set[LayoutCategory] = set()
        for template_class_details in self.template_classes.values():
            for layout in template_class_details["layouts"]:
                categories.add(layout_map_types[layout])
        return categories

    def get_config(self, class_name: str) -> ConfigHandler | None:
        if class_name in self.template_classes:
            return self.template_classes[class_name]["config"]

    def has_config(self, layout_category: LayoutCategory | None = None) -> bool:
        for template_class_details in self.template_classes.values():
            if layout_category:
                contains_layout: bool = False
                for layout in template_class_details["layouts"]:
                    if layout_category.matches_layout_type(layout_category, layout):
                        contains_layout = True
                        break
                if not contains_layout:
                    continue

            return template_class_details["config"].has_config
        return False

    def get_preview_image_path(self, layout: LayoutCategory) -> Path | None:
        for class_name, template_class_details in self.template_classes.items():
            for layout_type in template_class_details["layouts"]:
                if LayoutCategory.matches_layout_type(layout, layout_type):
                    return self.parent.get_path_preview(class_name, layout_type)

    def get_class_name_for_layout(self, layout_type: LayoutType) -> str | None:
        for class_name, template_class_details in self.template_classes.items():
            if layout_type in template_class_details["layouts"]:
                return class_name
        return None

    def get_class_name_and_file_for_layout(
        self, layout_type: LayoutType
    ) -> tuple[str, Path] | None:
        if class_name := self.get_class_name_for_layout(layout_type):
            return (class_name, self.parent.path_psd)


class AppTemplate:
    """Represents a template definition from a `manifest.yml` file."""

    def __init__(
        self,
        con: AppConstants,
        env: AppEnvironment,
        data: TemplateFileInfo,
        file_name: str,
        config_managers: dict[str, ConfigHandler],
        versions: dict[str, str],
        plugin: AppPlugin | None = None,
    ):
        self.con: AppConstants = con
        self.env: AppEnvironment = env
        self._info: TemplateFileInfo = data
        self.file_name = file_name
        self.versions = versions
        self.plugin: AppPlugin | None = plugin

        self.template_installed: SubscribableEvent[None] = SubscribableEvent()

        # Initialize per template class config managers
        self.config_managers: dict[str, ConfigHandler] = {}
        for classes in data.templates.values():
            for class_name in classes:
                if class_name not in self.config_managers:
                    if not (conf_mgr := config_managers.get(class_name, None)):
                        conf_mgr = ConfigHandler(
                            base_schema_path=PATH.SRC_DATA_CONFIG_BASE,
                            schema_path=conf_path
                            if (conf_path := self.get_path_config(class_name)).is_file()
                            else None,
                            ini_path=self.get_path_ini(class_name),
                        )
                        config_managers[class_name] = conf_mgr
                    self.config_managers[class_name] = conf_mgr

        self.named_templates: dict[str, NamedTemplate] = {
            name: NamedTemplate(
                name,
                {
                    class_name: {
                        "config": self.config_managers[class_name],
                        "layouts": layouts,
                    }
                    for class_name, layouts in classes.items()
                },
                self,
            )
            for name, classes in data.templates.items()
        }
        self.manifest_map: ManifestTemplateMap = data.templates

    """
    * Template Metadata
    """

    @cached_property
    def id(self) -> str:
        """A unique identifier for the template."""
        return str(self.path_psd)

    @cached_property
    def name(self) -> str:
        """str: Name of the template displayed in download manager menus."""
        return (
            self._info.name
            if self._info.name is not None
            else self.generate_template_name()
        )

    @cached_property
    def google_drive_id(self) -> str | None:
        """The template's Google Drive file ID, fallback to None."""
        return self._info.id

    @cached_property
    def description(self) -> str | None:
        """The template's displayed description, fallback to None."""
        return self._info.desc

    @property
    def version(self) -> str | None:
        """The version of the template's installed PSD file."""
        if self.google_drive_id:
            return self.versions.get(self.google_drive_id, None)

    """
    * Template Update Data
    """

    @cached_property
    def _update(self) -> TemplateUpdate:
        """TemplateUpdate: Returns the current dictionary of update details for this template. Value is set
        dynamically when checking for updates."""
        return {}

    @property
    def update_file(self) -> str | None:
        """Optional[str]: Returns the filename of the fetched updated version of this template."""
        return self._update.get("name")

    @property
    def update_size(self) -> int | None:
        """Optional[int]: Returns the size in bytes of the fetched updated version of this template."""
        return self._update.get("size")

    @property
    def update_version(self) -> str | None:
        """Optional[str]: Returns the version number of the fetched updated version of this template."""
        return self._update.get("version")

    """
    * Boolean Properties
    """

    @property
    def is_installed(self) -> bool:
        """Whether PSD/PSB file for this template is installed."""
        return self.path_psd.is_file()

    """
    * Template Paths
    """

    @cached_property
    def path_templates(self) -> Path:
        return self.plugin.path_templates if self.plugin else PATH.TEMPLATES

    @cached_property
    def path_psd(self) -> Path:
        """Path: Path to the PSD/PSB file."""
        return self.path_templates / self.file_name

    @cached_property
    def path_7z(self) -> Path:
        """Path: Path to the 7z archive downloaded for this plugin."""
        return self.path_psd.with_suffix(".7z")

    @property
    def path_download(self) -> Path | None:
        """Optional[Path]: Path the file should be saved to when downloaded, if update ready."""
        if self.update_file:
            return self.path_templates / self.update_file
        return

    """
    * Template URLs
    """

    @property
    def url_amazon(self) -> yarl.URL | None:
        """yarl.URL: Amazon download URL for this template."""
        if self.env.API_AMAZON and self.update_file:
            with suppress(Exception):
                base = yarl.URL(self.env.API_AMAZON)
                # Add plugin name to URL
                if self.plugin:
                    base = base / self.plugin.root.name
                return base / self.update_file
        return

    @property
    def url_google_drive(self) -> yarl.URL | None:
        """yarl.URL: Google Drive download URL for this template."""
        if self.env.API_GOOGLE and self.update_file and self.google_drive_id:
            with suppress(Exception):
                # Return Google Drive URL with file ID
                return yarl.URL("https://drive.google.com/uc").with_query(
                    {"id": self.google_drive_id}
                )
        return

    """
    * Collections
    """

    @cached_property
    def supported_layout_types(self) -> list[LayoutType]:
        """All the types supported by this template."""
        types = {
            t
            for class_map in self.manifest_map.values()
            for types in class_map.values()
            for t in types
        }

        # Start the list with "normal" if it is supported
        supports_normal = LayoutType.Normal in types
        if supports_normal:
            types.remove(LayoutType.Normal)

        sorted_types = list(types)
        sorted_types.sort()

        if supports_normal:
            sorted_types.insert(0, LayoutType.Normal)

        return sorted_types

    @cached_property
    def supported_layout_categories(self) -> list[LayoutCategory]:
        return sort_layout_categories(
            {
                layout_map_types[layout_type]
                for layout_type in self.supported_layout_types
            },
            place_first=LayoutCategory.Normal,
        )

    @cached_property
    def all_names(self) -> list[str]:
        """All display names used by this template."""
        return list({name for name in self.manifest_map})

    @cached_property
    def all_classes(self) -> list[str]:
        """All python classes used by this template."""
        return list(
            {
                cls_name
                for class_map in self.manifest_map.values()
                for cls_name in class_map
            }
        )

    @cached_property
    def all_classes_and_layouts(self) -> dict[str, list[LayoutType]]:
        classes_and_layouts: dict[str, list[LayoutType]] = {}
        for class_map in self.manifest_map.values():
            for cls_name, layouts in class_map.items():
                classes_and_layouts.setdefault(cls_name, [])
                classes_and_layouts[cls_name].extend(layouts)
        return classes_and_layouts

    """
    * Template Utils
    """

    def generate_template_name(self) -> str:
        """Generate an automatic name when name isn't manually defined."""

        # Use first name on the list and look for types supported for that name
        name = self.all_names[0]
        supported = (
            self.supported_layout_types.copy()
            if len(self.all_names) == 1
            else {t for types in self.manifest_map[name].values() for t in types}
        )
        if LayoutType.Normal in supported:
            supported.remove(LayoutType.Normal)

        # When 'normal' type is present, just use the name
        if not supported:
            return self.all_names[0]

        # Format types into display names
        cats: set[str] = set()
        for cat, types in layout_map_display_condition_dual.items():
            # Add both face types
            if all(n in supported for n in types):
                [supported.remove(n) for n in types]
                cats.add(cat)
        for cat, t in layout_map_display_condition.items():
            # Add single face type
            if t in supported:
                supported.remove(t)
                cats.add(cat)
        # Add remaining display names
        [cats.add(layout_map_types_display[t]) for t in supported]

        # Build the name with categories supported
        return f"{self.all_names[0]} ({', '.join(cats)})"

    """
    * Update Utils
    """

    def check_for_update(self) -> bool:
        """Check if a template is up-to-date based on the live file metadata.

        Returns:
            True if Template needs to be updated, otherwise False.
        """
        if not self.google_drive_id:
            print(f"{self.name} ({self.file_name}) does not have a Google Drive ID")
            return False

        # Get our metadata
        if not (data := gdrive_get_metadata(self.google_drive_id, self.env.API_GOOGLE)):
            print(f"{self.name} ({self.file_name}) not found on Google Drive")
            return False

        # Cache update data
        self._update = {
            "version": data.get("description", "v1.0.0"),
            "name": data.get("name", self.file_name),
            "size": data["size"],
        }

        # Compare the versions
        self._validate_version()
        if not self.version:
            return True
        return not (
            self.update_version
            and normalize_ver(self.version) == normalize_ver(self.update_version)
        )

    def _validate_version(self) -> None:
        """Checks the current on-file version of this template and if the template is installed,
        updates the version tracker accordingly."""
        if self.google_drive_id:
            # If installed but version is not logged, log default version
            if self.is_installed and not self.version:
                self.versions[self.google_drive_id] = "1.0.0"
                return

            # If installed but version mistakenly logged, reset
            if not self.is_installed and self.version:
                del self.versions[self.google_drive_id]

    def update_template(
        self, callback: Callable[[int, int], None] | None = None
    ) -> bool:
        """Update a given template to the latest version.

        Args:
            callback: Callback method to update progress bar.

        Returns:
            True if succeeded, False if failed.
        """

        def get_fail_message() -> str:
            return f"Failed to update template: {self.name}"

        if self.path_download:
            try:
                result: bool = False
                will_install = not self.is_installed

                if self.google_drive_id and self.url_google_drive:
                    # Download using Google Drive
                    result = bool(
                        gdrive_download_file(
                            url=self.url_google_drive,
                            path=self.path_download,
                            path_cookies=PATH.LOGS_COOKIES,
                            callback=callback,
                            headers={**DEFAULT_HEADERS},
                        )
                    )

                    # If downloaded file is a 7z archive, extract the template from it
                    if result and self.path_download.suffix == ".7z":
                        with SevenZipFile(self.path_7z, "r") as archive:
                            archive.extractall(self.path_templates)
                        self.path_7z.unlink(missing_ok=True)

                if self.url_amazon and not result:
                    # Google Drive failed or isn't an option, download from Amazon S3
                    result = download_cloudfront(
                        url=self.url_amazon,
                        path=self.path_download,
                        callback=callback,
                    )

                if self.google_drive_id and self.update_version:
                    self.versions[self.google_drive_id] = self.update_version

                if will_install:
                    self.template_installed.trigger(None)

                if not result:
                    _logger.error(get_fail_message())

                return result

            # Exception caught while downloading / unpacking
            except Exception:
                _logger.exception(get_fail_message())
        else:
            _logger.error("Template update failed. Download path isn't specified.")
        return False

    """
    * Pathing Utils
    """

    def get_path_preview(self, class_name: str, class_type: LayoutType) -> Path:
        """Gets the path to a preview image for a given template name and type.

        Args:
            class_name: Name of the template's class.
            class_type: Type of the template.

        Returns:
            Path: Path to the image preview file, fallback to standard 'not found' image if missing.
        """
        # Plugin or app template?
        root = self.plugin.path_img if self.plugin else PATH.SRC_IMG_PREVIEWS

        # Try with type provided, then with just the class name, fallback to "Not Found" image
        path = (root / f"{class_name}[{class_type}]").with_suffix(".jpg")
        path = path if path.is_file() else (root / f"{class_name}").with_suffix(".jpg")
        return path if path.is_file() else PATH.SRC_IMG_NOTFOUND

    def get_path_config(self, class_name: str) -> Path:
        """Gets the path to a config definition file for a given template class.

        Args:
            class_name: Name of the template class.

        Returns:
            Path: Path to the 'json' or 'toml' config file for this template.
        """
        # Get plugin template config
        if self.plugin:
            json_path = (self.plugin.path_config / class_name).with_suffix(".json")
            if json_path.is_file():
                return json_path
            return json_path.with_suffix(".toml")

        # Get app template config
        return (PATH.SRC_DATA_CONFIG / class_name).with_suffix(".toml")

    def get_path_ini(self, class_name: str) -> Path:
        """Gets the path to an INI config file for a given template class.

        Args:
            class_name: Name of the template class.

        Returns:
            Path: Path to the 'ini' config file for this template.
        """
        # Is this a plugin template?
        if self.plugin:
            return (self.plugin.path_ini / class_name).with_suffix(".ini")
        return (PATH.SRC_DATA_CONFIG_INI / class_name).with_suffix(".ini")


class AssembledTemplateInstalledArgs(TypedDict):
    sender: AssembledTemplate
    origin: AppTemplate


class AssembledTemplateConfigChangedArgs(TypedDict):
    sender: AssembledTemplate
    class_name: str
    config: ConfigHandler
    has_config: bool


class AssembledTemplate(RenderableTemplate):
    def __init__(
        self, name: str, templates: list[NamedTemplate], plugin: AppPlugin | None = None
    ) -> None:
        self.name = name
        self.templates = templates
        self.plugin = plugin

        self.template_installed: SubscribableEvent[AssembledTemplateInstalledArgs] = (
            SubscribableEvent()
        )
        for parent_template in {templ.parent for templ in templates}:
            parent_template.template_installed.add_listener(
                lambda _, parent=parent_template: self._on_child_template_installed(
                    parent
                )
            )

        self.config_state_changed: SubscribableEvent[
            AssembledTemplateConfigChangedArgs
        ] = SubscribableEvent()
        confs_for_classes: dict[ConfigHandler, str] = {}
        for template in self.templates:
            for class_name, template_details in template.template_classes.items():
                confs_for_classes.setdefault(template_details["config"], class_name)
        for config, class_name in confs_for_classes.items():
            config.config_added.add_listener(
                lambda _, c_name=class_name, conf=config: self._on_config_state_changed(
                    class_name=c_name, config=conf, has_config=True
                )
            )
            config.config_deleted.add_listener(
                lambda _, c_name=class_name, conf=config: self._on_config_state_changed(
                    class_name=c_name, config=conf, has_config=False
                )
            )

    @cached_property
    def layout_categories(self) -> set[LayoutCategory]:
        categories: set[LayoutCategory] = set()
        return categories.union(
            *[template.layout_categories for template in self.templates]
        )

    @property
    def installed_template_files(self) -> list[str]:
        return [
            parent_template.file_name
            for parent_template in {templ.parent for templ in self.templates}
            if parent_template.is_installed
        ]

    @property
    def missing_template_files(self) -> list[str]:
        return [
            parent_template.file_name
            for parent_template in {templ.parent for templ in self.templates}
            if not parent_template.is_installed
        ]

    def is_installed(self, layout_category: LayoutCategory | None = None) -> bool:
        for template in self.templates:
            if layout_category and layout_category not in template.layout_categories:
                continue

            if template.parent.is_installed:
                return True
        return False

    def has_config(self, layout_category: LayoutCategory | None = None) -> bool:
        for template in self.templates:
            if layout_category and layout_category not in template.layout_categories:
                continue

            if template.has_config(layout_category):
                return True
        return False

    def get_config(self, class_name: str) -> ConfigHandler | None:
        for template in self.templates:
            if conf_mgr := template.get_config(class_name):
                return conf_mgr

    def get_preview_image_path(self, layout: LayoutCategory) -> Path | None:
        for template in self.templates:
            if preview_path := template.get_preview_image_path(layout):
                return preview_path

    def get_class_name_and_file_for_layout(
        self, layout_type: LayoutType
    ) -> tuple[str, Path] | None:
        for template in self.templates:
            if class_name := template.get_class_name_for_layout(layout_type):
                return (class_name, template.parent.path_psd)
        return None

    def _on_child_template_installed(self, template: AppTemplate) -> None:
        self.template_installed.trigger(
            AssembledTemplateInstalledArgs(sender=self, origin=template)
        )

    def _on_config_state_changed(
        self, class_name: str, config: ConfigHandler, has_config: bool
    ) -> None:
        self.config_state_changed.trigger(
            AssembledTemplateConfigChangedArgs(
                sender=self, class_name=class_name, config=config, has_config=has_config
            )
        )


class TemplateLibrary:
    def __init__(
        self,
        con: AppConstants,
        env: AppEnvironment,
        initial_template_file_versions: TemplateFileVersionsModel,
        template_file_versions: TemplateFileVersionsModel,
        plugins: dict[str, AppPlugin],
    ) -> None:
        self.initial_versions = initial_template_file_versions
        self.versions = template_file_versions
        self.templates: list[AppTemplate] = get_all_templates(
            con, env, plugins, template_file_versions.root
        )

        built_in, grouped_by_plugin = self._group_templates_by_plugin(self.templates)

        self.built_in_templates_by_name = self._group_templates_by_name(built_in)
        self.plugin_templates_by_name: dict[str, dict[str, AssembledTemplate]] = {}

        for plugin, templates in grouped_by_plugin.items():
            self.plugin_templates_by_name[plugin.id] = self._group_templates_by_name(
                templates, plugin
            )

    def save_template_versions(self) -> None:
        if self.initial_versions != self.versions:
            dump_model(PATH.SRC_DATA_VERSIONS, self.versions)

    def get_templates_for_layout_category(
        self, layout_category: LayoutCategory
    ) -> list[AssembledTemplate]:
        templates: list[AssembledTemplate] = []
        for template in self.built_in_templates_by_name.values():
            if template.is_installed(layout_category):
                templates.append(template)
        for plugin_templates in self.plugin_templates_by_name.values():
            for template in plugin_templates.values():
                if template.is_installed(layout_category):
                    templates.append(template)
        return templates

    def _group_templates_by_plugin(
        self, templates: list[AppTemplate]
    ) -> tuple[list[AppTemplate], dict[AppPlugin, list[AppTemplate]]]:
        built_in: list[AppTemplate] = []
        grouped_by_plugin: dict[AppPlugin, list[AppTemplate]] = {}
        for template in templates:
            if template.plugin:
                grouped_by_plugin.setdefault(template.plugin, [])
                grouped_by_plugin[template.plugin].append(template)
            else:
                built_in.append(template)
        return (built_in, grouped_by_plugin)

    def _group_templates_by_name(
        self, templates: list[AppTemplate], plugin: AppPlugin | None = None
    ) -> dict[str, AssembledTemplate]:
        grouped: dict[str, list[NamedTemplate]] = {}
        for root_template in templates:
            for named_template in root_template.named_templates.values():
                grouped.setdefault(named_template.name, [])
                grouped[named_template.name].append(named_template)
        return {
            name: AssembledTemplate(name, templates, plugin)
            for name, templates in grouped.items()
        }


class PluginLibrary:
    def __init__(
        self,
        con: AppConstants,
        env: AppEnvironment,
        initial_template_file_versions: TemplateFileVersionsModel,
    ) -> None:
        self._con = con
        self._env = env
        self._initial_template_file_versions = initial_template_file_versions
        self.plugins: dict[str, AppPlugin] = get_all_plugins(
            con, env, initial_template_file_versions.root
        )
        self.plugins_changed: SubscribableEvent[dict[str, AppPlugin]] = (
            SubscribableEvent()
        )
        self._template_library: TemplateLibrary | None = None
        self.template_library_changed: SubscribableEvent[TemplateLibrary] = (
            SubscribableEvent()
        )

    @property
    def template_library(self) -> TemplateLibrary:
        if self._template_library:
            return self._template_library
        return self.construct_template_library()

    def construct_template_library(self) -> TemplateLibrary:
        self._template_library = TemplateLibrary(
            self._con,
            self._env,
            initial_template_file_versions=self._initial_template_file_versions,
            template_file_versions=self._template_library.versions
            if self._template_library
            else self._initial_template_file_versions,
            plugins=self.plugins,
        )
        self.template_library_changed.trigger(self._template_library)
        return self._template_library

    def add_plugin(self, path: Path) -> AppPlugin:
        plugin = AppPlugin(
            self._con,
            self._env,
            path,
            self._template_library.versions.root
            if self._template_library
            else self._initial_template_file_versions.root,
        )
        self.plugins[plugin.id] = plugin
        self.plugins_changed.trigger(self.plugins)
        self.construct_template_library()
        return plugin

    def remove_plugin(self, plugin_id: str) -> AppPlugin | None:
        try:
            if plugin := self.plugins.get(plugin_id, None):
                plugin.remove()
                self.plugins.pop(plugin_id, None)
                self.plugins_changed.trigger(self.plugins)
                self.construct_template_library()
                return plugin
        except Exception:
            _logger.exception(f"Failed to remove plugin '{plugin_id}'")


def get_all_templates(
    con: AppConstants,
    env: AppEnvironment,
    plugins: dict[str, AppPlugin],
    template_file_versions: dict[str, str],
) -> list[AppTemplate]:
    """Gets a list of all 'AppTemplate' objects.

    Args:
        con: Global constants object.
        env: Global environment object.
        plugins: A dictionary of 'AppPlugin' objects mapped by name.

    Returns:
        A list of all 'AppTemplate' objects in the app and plugins.
    """
    # Track all plugins and templates for sorting
    templates: list[AppTemplate] = []

    # Load the built-in templates
    manifest: TemplateFileInfoRoot = parse_model(
        PATH.SRC_DATA_MANIFEST, TemplateFileInfoRoot
    )

    # Use one config manager per python template class
    conifg_managers: dict[str, ConfigHandler] = {}

    # Build a TemplateDetails for each template
    for file_name, data in manifest.root.items():
        templates.append(
            AppTemplate(
                con=con,
                env=env,
                data=data,
                file_name=file_name,
                config_managers=conifg_managers,
                versions=template_file_versions,
            )
        )

    # Load all plugins and plugin templates
    for p in plugins.values():
        templates.extend(p.get_template_list())
    return templates


# endregion Templates

# region Symbols


def get_symbols_manifest() -> SymbolsManifest | None:
    if PATH.SRC_IMG_SYMBOLS_MANIFEST.exists():
        return SymbolsManifest.model_validate_json(
            PATH.SRC_IMG_SYMBOLS_MANIFEST.read_bytes()
        )
    return None


# endregion Symbols
