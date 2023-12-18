"""
* Plugin and Template Loader
* Only import enums and utils
"""
# Standard Library Imports
from concurrent.futures import ThreadPoolExecutor, Future
from configparser import ConfigParser
from contextlib import suppress
import os
from pathlib import Path
from typing import Optional, TypedDict, NotRequired, Any, Callable

# Third Party Imports
import yarl

# Local Imports
from src._state import AppConstants, AppEnvironment, PATH
from src.api.amazon import download_cloudfront
from src.api.google import get_google_drive_metadata, download_google_drive
from src.enums.mtg import layout_map_types_display, layout_map_category, layout_map_types
from src.utils.files import (
    load_data_file,
    get_kivy_config_from_schema,
    get_config_object,
    verify_config_fields,
    ensure_path_exists,
    copy_config_or_verify)
from src.utils.modules import get_loaded_module
from src.utils.properties import auto_prop_cached
from src.utils.strings import normalize_ver

"""
* Types
"""


class TemplateUpdate(TypedDict):
    """Details about the latest update for a given AppTemplate."""
    name: NotRequired[str]
    version: NotRequired[str]
    size: NotRequired[int]


class TemplateDetails(TypedDict):
    """Details about a specific template within the TemplateCategoryMap."""
    name: str
    class_name: str
    object: 'AppTemplate'
    config: 'ConfigManager'


"""Dictionary which maps a template's displayed names to classes, and classes to template types."""
ManifestTemplateMap = dict[str, dict[str, list[str]]]

"""Reversed dictionary which maps a template type, to a template name, to a template class."""
TemplateTypeMap = dict[str, dict[str, TemplateDetails]]

"""Map of templates selected for each template type."""
TemplateSelectedMap = dict[str, TemplateDetails]


class ManifestTemplateDetails(TypedDict):
    """Template details pulled from a plugin's `manifest.yml` file or Proxyshop's `templates.yml` file."""
    file: str
    name: NotRequired[str]
    id: NotRequired[str]
    desc: NotRequired[str]
    version: NotRequired[str]
    templates: ManifestTemplateMap


class TemplateMetadata(TypedDict):
    """TemplateDetails, minus the template class map."""
    file: str
    name: NotRequired[str]
    id: NotRequired[str]
    desc: NotRequired[str]


class PluginMetadata(TypedDict):
    """Metadata contained in the `PLUGIN` table of a plugin's `manifest.yml` file."""
    name: NotRequired[str]
    author: NotRequired[str]
    desc: NotRequired[str]
    source: NotRequired[str]
    docs: NotRequired[str]
    license: NotRequired[str]
    requires: NotRequired[str]
    version: NotRequired[str]


class TemplateCategoryMap(TypedDict):
    """Data mapped to a displayed template category, e.g. 'Normal'."""
    names: list[str]
    map: TemplateTypeMap


"""
* Classes
"""


class ConfigManager:
    """Represents the combined loaded configuration data for the app and template/plugin if provided.

    Args:
        template_class: Name of the template class, if provided.
        template: AppTemplate object corresponding to the template class, if provided.
    """

    def __init__(
        self, template_class: Optional[str] = None,
        template: Optional['AppTemplate'] = None
    ) -> None:

        # Establish template and plugin details
        self._template_class: Optional[str] = template_class.replace(
            'Back', 'Front') if template_class else None
        self._template: Optional[AppTemplate] = template or None
        self._plugin: Optional[AppPlugin] = template.plugin if template else None

        # Core path where config folders exist
        self._path_schema = self._plugin.path_config if self._plugin else PATH.SRC_DATA_CONFIG
        self._path_ini = self._plugin.path_ini if self._plugin else PATH.SRC_DATA_CONFIG_INI

    """
    * Path: App settings only modified in Global
    """

    @property
    def app_path_schema(self) -> Path:
        """System config schema, in JSON or TOML."""
        return PATH.SRC_DATA_CONFIG_APP

    @property
    def app_path_ini(self) -> Path:
        """System config INI."""
        return PATH.SRC_DATA_CONFIG_INI_APP

    @property
    def app_json(self) -> str:
        """System config as Kivy readable JSON string dump."""
        return get_kivy_config_from_schema(self.app_path_schema)

    @property
    def app_cfg(self) -> ConfigParser:
        """System ConfigParser instance."""
        return get_config_object(self.app_path_ini)

    """
    * Path: Settings modifiable by Template
    """

    @property
    def base_path_schema(self) -> Path:
        """Main template config schema, in JSON or TOML."""
        return PATH.SRC_DATA_CONFIG_BASE

    @property
    def base_path_ini(self) -> Path:
        """Main template config INI."""
        return PATH.SRC_DATA_CONFIG_INI_BASE

    @property
    def base_json(self) -> str:
        """Main template config as Kivy readable JSON string dump."""
        return get_kivy_config_from_schema(self.base_path_schema)

    @property
    def base_cfg(self) -> ConfigParser:
        """Main template ConfigParser instance."""
        return get_config_object(self.base_path_ini)

    """
    * Path: Template specific settings
    """

    @property
    def template_path_schema(self) -> Optional[Path]:
        """Template specific config schema, in JSON or TOML."""
        if self._template:
            path = self._template.get_path_config(self._template_class)
            return path if path.is_file() else None
        return

    @property
    def template_path_ini(self) -> Optional[Path]:
        """Template specific config INI."""
        if self._template:
            path = self._template.get_path_ini(self._template_class)
            return path if path.is_file() else None
        return

    @property
    def template_json(self) -> Optional[str]:
        """Template specific config as Kivy readable JSON string dump."""
        if self.template_path_schema:
            return get_kivy_config_from_schema(self.template_path_schema)
        return

    @property
    def template_cfg(self) -> Optional[ConfigParser]:
        """Template specific ConfigParser instance."""
        if self.template_path_ini:
            return get_config_object(self.template_path_ini)
        return

    """
    * Bool Checks
    """

    @property
    def has_template_ini(self) -> bool:
        """Returns True if a template has a separate INI file."""
        return bool(self.template_path_ini and self.template_path_ini.is_file())

    """
    * Utility Methods
    """

    def get_config(self) -> ConfigParser:
        """Return a ConfigParser instance with all relevant config data loaded."""
        self.validate_configs()
        if self.has_template_ini:
            # Load template INI file instead of base
            self.validate_template_configs()
            return get_config_object([
                self.app_path_ini,
                self.template_path_ini])
        # Load app and base only
        return get_config_object([
            self.app_path_ini,
            self.base_path_ini])

    """
    * Validate Methods
    """

    def validate_configs(self) -> None:
        """Validate app and base configs against data schemas."""
        verify_config_fields(
            ini_file=self.app_path_ini,
            data_file=self.app_path_schema)
        verify_config_fields(
            ini_file=self.base_path_ini,
            data_file=self.base_path_schema)

    def validate_template_configs(self) -> None:
        """Validate template configs against data schemas."""
        if not self.template_path_ini:
            return

        # Validate base template configs
        ensure_path_exists(self.template_path_ini)
        copy_config_or_verify(
            path_from=self.base_path_ini,
            path_to=self.template_path_ini,
            data_file=self.base_path_schema)

        # Validate template specific configs
        if self.template_path_schema:
            verify_config_fields(
                ini_file=self.template_path_ini,
                data_file=self.template_path_schema)


class AppPlugin:
    """Represents a Proxyshop plugin found in `src/plugins/`.

    Args:
        con: Global application constants object.
        path: Path to the plugin directory.

    Attributes:
        _root (Path): Root path where the plugin's files are located.
        _manifest (Path): Path to the plugin's manifest file.
        _templates (dict[str, TemplateDetails]): Data loaded from manifest file.
        _info (PluginMetadata): Top level table from the manifest file containing the plugin's metadata.

    Raises:
        FileNotFoundError: If the plugin path or manifest file couldn't be found.
        ModuleNotFoundError: If the plugin's python module couldn't be found.
    """
    def __init__(self, con: AppConstants, env: AppEnvironment, path: Path):

        # Save a reference to the global application constants
        self.con: AppConstants = con
        self.env: AppEnvironment = env

        # Ensure path exists
        if not path.is_dir():
            raise FileNotFoundError(f"Couldn't locate plugin path: {str(path)}")
        self._root = path

        # Find a valid manifest
        self._manifest = Path(path, 'manifest.yml')
        if not self._manifest.is_file():
            self._manifest = Path(path, 'manifest.json')
        if not self._manifest.is_file():
            raise FileNotFoundError(f"Couldn't locate manifest file for plugin at path: {str(path)}")

        # Load the manifest data
        self.load_manifest() if self._manifest.suffix.lower() == '.yml' else self.load_manifest_json()

        # Ensure plugin has a valid module path
        _ = self.py_module

        # Load templates
        self.load_templates()

    """
    * Tracked Properties
    """

    @auto_prop_cached
    def template_map(self) -> dict[str, 'AppTemplate']:
        """dict[str, AppTemplate]: A dictionary mapping of AppTemplate's by file name pulled from this plugin."""
        return {}

    """
    * Pathing
    """

    @auto_prop_cached
    def py_module(self) -> str:
        """str: Path to the recognized python module for this plugin."""
        if (self._root / '__init__.py').is_file():
            # Init file in root of the plugin
            return f'plugins.{self._root.stem}'
        if (self._root / 'src' / '__init__.py').is_file():
            # Init file in 'src' directory
            return f'plugins.{self._root.stem}.src'
        if (self._root / 'src' / 'templates.py').is_file():
            # 'templates.py' file in root of the plugin
            return f'plugins.{self._root.stem}.templates'
        raise ModuleNotFoundError(f"Couldn't find a module path for Plugin: '{self.name}'")

    @auto_prop_cached
    def path_config(self) -> Path:
        """Path: Path to this plugin's config directory."""
        return Path(self._root, 'config')

    @auto_prop_cached
    def path_ini(self) -> Path:
        """Path: Path to this plugin's INI config directory."""
        return Path(self._root, 'config_ini')

    @auto_prop_cached
    def path_img(self) -> Path:
        """Path: Path to this plugin's preview image directory."""
        return Path(self._root, 'config_ini')

    @auto_prop_cached
    def path_templates(self) -> Path:
        """Path: Path to this plugin's templates directory."""
        return self._root / 'templates'

    """
    * Plugin Metadata
    """

    @auto_prop_cached
    def name(self) -> str:
        """str: Displayed name of the plugin. Fallback on root directory name."""
        return self._info.get('name', self._root.stem)

    @auto_prop_cached
    def author(self) -> str:
        """str: Displayed name of the plugin's author. Fallback on name."""
        return self._info.get('author', self.name)

    @auto_prop_cached
    def description(self) -> Optional[str]:
        """Optional[str]: Displayed description of the plugin. Fallback on None."""
        return self._info.get('desc', None)

    @auto_prop_cached
    def source(self) -> Optional[yarl.URL]:
        """Optional[URL]: Link to the hosted files of this plugin."""
        if url := self._info.get('source'):
            with suppress(Exception):
                url = yarl.URL(url)
                return url
        return

    @auto_prop_cached
    def docs(self) -> Optional[yarl.URL]:
        """Optional[URL]: Link to the hosted documentation for this plugin."""
        if url := self._info.get('docs'):
            with suppress(Exception):
                url = yarl.URL(url)
                return url
        return

    @auto_prop_cached
    def license(self) -> str:
        """str: Name of the open source license carried by this plugin. Fallback on MPL-2.0."""
        return self._info.get('license', 'MPL-2.0')

    @auto_prop_cached
    def required_version(self) -> Optional[str]:
        """Optional[str]: Proxyshop version this plugin requires to function as intended."""
        return self._info.get('requires', None)

    @auto_prop_cached
    def version(self) -> str:
        """str: Current version of the plugin."""
        return self._info.get('version', '0.1.0')

    """
    * Plugin Methods
    """

    def load_manifest(self) -> None:
        """Load the `manifest.yml` data for this plugin.

        Raises:
            ValueError: If the manifest file contains invalid data.
        """
        try:
            # Load plugin metadata and template details
            data = load_data_file(self._manifest)
            self._info: PluginMetadata = data.pop('PLUGIN', {})
            self._templates: dict[str, ManifestTemplateDetails] = data.copy()
        except Exception as e:
            raise ValueError(f'Manifest file contains invalid data: {str(self._manifest)}') from e

    def load_manifest_json(self) -> None:
        """Load the legacy `manifest.json` data for this plugin.

        Raises:
            ValueError: If the manifest file contains invalid data.
        """
        try:
            # Load Plugin metadata
            data = load_data_file(self._manifest)
            self._info: PluginMetadata = data.pop('PLUGIN', {})
            templates: dict[str, dict[str, dict[str, str]]] = data.copy()
        except Exception as e:
            raise ValueError(f'Manifest file contains invalid data: {str(self._manifest)}') from e

        # Re-format templates dict for TemplateDetails
        self._templates: dict[str, ManifestTemplateDetails] = {}
        for t, temps in templates.items():
            for name, details in temps.items():
                # Add new file
                file_name = details.get('file', '')
                class_name = details.get('class', '')
                self._templates.setdefault(
                    file_name, {
                        'file': file_name,
                        'templates': {}
                    })
                # Add Google Drive ID
                if details.get('id'):
                    self._templates[file_name].setdefault('id', details['id'])
                # Existing name
                if name in self._templates[file_name]['templates']:
                    # Existing class name
                    if class_name in self._templates[file_name]['templates'][name]:
                        self._templates[file_name]['templates'][name][class_name].append(t)
                        continue
                    # Add new class
                    self._templates[file_name]['templates'][name][class_name] = [t]
                # Add new template
                self._templates[file_name]['templates'][name] = {name: {class_name: [t]}}

    def load_templates(self) -> None:
        """Load the dictionary of AppTemplate's pulled from this plugin's manifest file.

        Returns:
            A dictionary where keys are PSD/PSB filenames and values are AppTemplate objects.
        """
        for file_name, data in self._templates.items():
            data['file'] = file_name
            self.template_map[file_name] = AppTemplate(
                con=self.con,
                env=self.env,
                data=data,
                plugin=self)

    def get_template_list(self) -> list['AppTemplate']:
        """list[AppTemplate]: Returns a list of AppTemplate's pulled from this plugin."""
        return list(self.template_map.values())


class AppTemplate:
    """Represents a template definition from a `manifest.yml` file.

    Args:
        con: Global application constants object.
        data: Template data pulled from `manifest.yml` file.
        plugin: Loaded Proxyshop plugin object representing a given plugin directory from `/plugins/`.

    Attributes:
        plugin (AppPlugin): The `plugin` this template was loaded from, if provided.
        _info (TemplateMetadata): This template's metadata info.
        _map (TemplateClassMap): Template's display names mapped to classes, mapped to template types.
    """

    def __init__(
            self,
            con: AppConstants,
            env: AppEnvironment,
            data: ManifestTemplateDetails,
            plugin: Optional[AppPlugin] = None):

        # Save a reference to the global application constants
        self.con: AppConstants = con
        self.env: AppEnvironment = env

        # Save the template's plugin and class map
        self.plugin: Optional[AppPlugin] = plugin
        self._map: ManifestTemplateMap = {
            name: ({mapped: ['normal']} if isinstance(mapped, str) else {
                k: ([v] if isinstance(v, str) else v) for k, v in mapped.items()
            }) for name, mapped in data['templates'].items()}

        # Save the template's metadata
        self._info: TemplateMetadata = data.copy()
        self._info.pop('templates')

    """
    * Template Mappings
    """

    @auto_prop_cached
    def map(self) -> TemplateTypeMap:
        """TemplateTypeMap: The configuration of types mapped to names mapped to a dictionary containing:
            - 'class_name': python class name
            - 'config': ConfigManager object
            - 'object': AppTemplate object
        """
        mapped: TemplateTypeMap = {}
        configs = {}
        for name, classes in self._map.items():
            for class_name, types in classes.items():
                for t in types:

                    # Reuse ConfigManager object for identical class names
                    if class_name not in configs:
                        configs[class_name] = ConfigManager(
                            template_class=class_name, template=self)

                    # Add to the map
                    mapped.setdefault(t, {})[name] = {
                        'name': name,
                        'class_name': class_name,
                        'config': configs[class_name],
                        'object': self}

        # Return the complete map
        return mapped

    @auto_prop_cached
    def map_config(self) -> dict[str, ConfigManager]:
        """dict[str, ConfigManager]: Maps template class names to their respective ConfigManager object."""
        # TODO: Evaluate whether this is necessary
        mapped = {}
        for t, class_map in self.map.items():
            for name, details in class_map.items():
                mapped[details['class_name']] = details['config']
        return mapped

    """
    * Template Metadata
    """

    @auto_prop_cached
    def name(self) -> str:
        """str: Name of the template displayed in download manager menus."""
        return self._info.get('name', self.generate_template_name())

    @auto_prop_cached
    def file_name(self) -> str:
        """str: File name of the template PSD/PSB file."""
        file_name = self._info.get('file')
        if not file_name:
            raise ValueError(f"Template '{self.name}' did not provide a file name!")
        return file_name

    @auto_prop_cached
    def google_drive_id(self) -> Optional[str]:
        """Optional[str]: The template's Google Drive file ID, fallback to None."""
        return self._info.get('id', None)

    @auto_prop_cached
    def description(self) -> Optional[str]:
        """Optional[str]: The template's displayed description, fallback to None."""
        return self._info.get('desc', None)

    @property
    def version(self) -> Optional[str]:
        """Optional[str]: The template's currently logged version."""
        if not self.google_drive_id:
            return
        return self.con.versions.get(self.google_drive_id)

    """
    * Template Update Data
    """

    @auto_prop_cached
    def _update(self) -> TemplateUpdate:
        """TemplateUpdate: Returns the current dictionary of update details for this template. Value is set
        dynamically when checking for updates."""
        return {}

    @property
    def update_file(self) -> Optional[str]:
        """Optional[str]: Returns the filename of the fetched updated version of this template."""
        return self._update.get('name')

    @property
    def update_size(self) -> Optional[int]:
        """Optional[int]: Returns the size in bytes of the fetched updated version of this template."""
        return self._update.get('size')

    @property
    def update_version(self) -> Optional[str]:
        """Optional[str]: Returns the version number of the fetched updated version of this template."""
        return self._update.get('version')

    """
    * Boolean Properties
    """

    @auto_prop_cached
    def is_installed(self) -> bool:
        """bool: Whether PSD/PSB file for this template is installed."""
        return self.path_psd.is_file()

    """
    * Template Paths
    """

    @auto_prop_cached
    def path_psd(self) -> Path:
        """Path: Path to the PSD/PSB file."""
        root = self.plugin.path_templates if self.plugin else PATH.TEMPLATES
        return root / self.file_name

    @auto_prop_cached
    def path_7z(self) -> Path:
        """Path: Path to the 7z archive downloaded for this plugin."""
        return self.path_psd.with_suffix('.7z')

    @property
    def path_download(self) -> Optional[Path]:
        """Optional[Path]: Path the file should be saved to when downloaded, if update ready."""
        if self.update_file:
            root = self.plugin.path_templates if self.plugin else PATH.TEMPLATES
            return root / self.update_file
        return

    """
    * Template URLs
    """

    @property
    def url_amazon(self) -> Optional[yarl.URL]:
        """yarl.URL: Amazon download URL for this template."""
        if self.env.API_AMAZON and self.update_file:
            with suppress(Exception):
                base = yarl.URL(self.env.API_AMAZON)
                # Add plugin name to URL
                if self.plugin:
                    base = base / self.plugin._root.name
                return base / self.update_file
        return

    @property
    def url_google_drive(self) -> Optional[yarl.URL]:
        """yarl.URL: Google Drive download URL for this template."""
        if self.env.API_GOOGLE and self.update_file and self.google_drive_id:
            with suppress(Exception):
                # Return Google Drive URL with file ID
                return yarl.URL(
                    'https://drive.google.com/uc'
                ).with_query({'id': self.google_drive_id})
        return

    """
    * Collections
    """

    @auto_prop_cached
    def types_supported(self) -> set[str]:
        """set[str]: A set of all types supported by this template."""
        return {
            t for class_map in self._map.values()
            for types in class_map.values()
            for t in types
        }

    @auto_prop_cached
    def all_names(self) -> set[str]:
        """set[str]: A set of all display names used by this template."""
        return {name for name in self._map.keys()}

    @auto_prop_cached
    def all_classes(self) -> set[str]:
        """set[str]: A set of all python classes used by this template."""
        return {cls_name for class_map in self._map.values() for cls_name in class_map.keys()}

    """
    * Template Utils
    """

    def get_template_class(self, class_name: str) -> Any:
        """Loads the template class for a template of a given class name.

        Args:
            class_name: Name of the template's python class.

        Returns:
            The template's loaded python class.
        """

        # Is this a plugin template?
        module = self.plugin.py_module if self.plugin else 'src.templates'

        # Load the plugin module, use hot-loading if enabled
        with suppress(Exception):
            module = get_loaded_module(module)
            loaded_class = getattr(module, class_name)
            return loaded_class
        return

    def generate_template_name(self) -> str:
        """Generate an automatic name when name isn't manually defined."""

        # Use first name on the list and look for types supported for that name
        name = self.all_names[0]
        supported = self.types_supported if len(self.all_names) == 1 else {
            t for types in self._map[name].values() for t in types}

        # When 'normal' type is present, just use the name
        if len(supported) == 1 or 'normal' in supported:
            return self.all_names[0]

        # When other types are present, build a type list
        type_line = ', '.join([
            layout_map_types_display[t] for t in supported
            if t in layout_map_types_display])
        return f'{self.all_names[0]} ({type_line})'

    """
    * Update Utils
    """

    def check_for_update(self) -> bool:
        """Check if a template is up-to-date based on the live file metadata.

        Returns:
            True if Template needs to be updated, otherwise False.
        """
        # Get our metadata
        data = get_google_drive_metadata(self.google_drive_id, self.env.API_GOOGLE)
        if not data:
            # File couldn't be located on Google Drive
            print(f"{self.name} ({self.file_name}) not found on Google Drive!")
            return False

        # Cache update data
        self._update: TemplateUpdate = {
            'version': data.get('description', 'v1.0.0'),
            'name': data.get('name', self.file_name),
            'size': data['size']
        }

        # Compare the versions
        self.validate_version()
        if not self.version:
            return True
        if normalize_ver(self.version) == normalize_ver(self.update_version):
            return False

        # Template needs an update
        return True

    def validate_version(self) -> None:
        """Checks the current on-file version of this template and if the template is installed,
        updates the version tracker accordingly."""

        # If installed but version is not logged, log default version
        if self.is_installed and not self.version:
            self.con.versions[self.google_drive_id] = '1.0.0'
            self.con.update_version_tracker()
            return

        # If installed but version mistakenly logged, reset
        if not self.is_installed and self.version:
            del self.con.versions[self.google_drive_id]
            self.con.update_version_tracker()

    def update_template(self, callback: Callable) -> bool:
        """Update a given template to the latest version.

        Args:
            callback: Callback method to update progress bar.

        Returns:
            True if succeeded, False if failed.
        """

        # Download using Google Drive
        result = download_google_drive(
            url=self.url_google_drive,
            path=self.path_download,
            path_cookies=PATH.LOGS_COOKIES,
            callback=callback
        ) if self.google_drive_id else False

        # Google Drive failed or isn't an option, download from Amazon S3
        if not result:
            result = download_cloudfront(
                url=self.url_amazon,
                path=self.path_download,
                callback=callback)

        # Return result status
        return result

    """
    * Pathing Utils
    """

    def get_path_preview(self, class_name: str, class_type: str) -> Path:
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
        path = (root / f'{class_name}[{class_type}]').with_suffix('.jpg')
        path = path if path.is_dir() else (root / f'{class_name}').with_suffix('.jpg')
        return path if path.is_dir() else PATH.SRC_IMG_NOTFOUND

    def get_path_config(self, class_name: str) -> Path:
        """Gets the path to a config definition file for a given template class.

        Args:
            class_name: Name of the template class.

        Returns:
            Path: Path to the 'json' or 'toml' config file for this template.
        """
        # Get plugin template config
        if self.plugin:
            json_path = (self.plugin.path_config / class_name).with_suffix('.json')
            if json_path.is_file:
                return json_path
            return json_path.with_suffix('.toml')

        # Get app template config
        return (PATH.SRC_DATA_CONFIG / class_name).with_suffix('.toml')

    def get_path_ini(self, class_name: str) -> Path:
        """Gets the path to an INI config file for a given template class.

        Args:
            class_name: Name of the template class.

        Returns:
            Path: Path to the 'ini' config file for this template.
        """
        # Is this a plugin template?
        if self.plugin:
            return (self.plugin.path_ini / class_name).with_suffix('.ini')
        return (PATH.SRC_DATA_CONFIG_INI / class_name).with_suffix('.ini')


"""
* Plugin Utils
"""


def get_all_plugins(con: AppConstants, env: AppEnvironment) -> dict[str, AppPlugin]:
    """Gets a dict of 'AppPlugin' objects mapped by their name attribute.

    Args:
        con: Global constants object.
        env: Global environment object.

    Returns:
        A mapping of plugin names to their respective 'AppPlugin' object.
    """
    plugins: dict[str, AppPlugin] = {}

    # Load all plugins and plugin templates
    for folder in [p for p in PATH.PLUGINS.iterdir() if p.is_dir()]:
        try:
            plugin = AppPlugin(con=con, env=env, path=folder)
            plugins[plugin.name] = plugin
        except Exception as e:
            print(e)
    return dict(sorted(plugins.items()))


"""
* Template Utils
"""


def get_all_templates(con: AppConstants, env: AppEnvironment, plugins: dict[str, AppPlugin]) -> list[AppTemplate]:
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
    manifest: dict[str, ManifestTemplateDetails] = load_data_file(PATH.SRC_DATA_MANIFEST)

    # Build a TemplateDetails for each template
    for file_name, data in manifest.items():
        data['file'] = file_name
        templates.append(AppTemplate(con=con, env=env, data=data))

    # Load all plugins and plugin templates
    for p in plugins.values():
        templates.extend(p.get_template_list())
    return templates


def get_template_map(templates: list[AppTemplate]) -> dict[str, TemplateCategoryMap]:
    """Gets a 'TemplateCategoryMap' mapping all templates to their respective categories and types.

    Args:
        templates: A unordered list of all 'AppTemplate' objects.

    Returns:
        A 'TemplateCategoryMap' mapping all templates to their categories and types.
    """
    # Establish our core category map
    d: dict[str, TemplateCategoryMap] = {
        type_named: {'names': [], 'map': {}}
        for type_named in layout_map_category.keys()}

    # Track names for uniqueness
    names: dict[str, list[str]] = {}

    # Iterate over template list and add to the category map
    for template in templates:
        for t, class_map in template.map.items():
            for name, details in class_map.items():
                cat = layout_map_types[t]

                # Ensure name is unique
                if name in names.get(t, []):
                    # Add plugin to name if plugin provided
                    if details['object'].plugin:
                        # Swap this objects name
                        name = f"{name} ({details['object'].plugin.name})"

                    # Iterate over name until it is unique
                    i, n = 1, name
                    while name in names.get(t, []):
                        name, i = f"{n} ({i})", i + 1

                # Add template to map and tracked names
                d[cat]['map'][t][name] = details
                if name not in d[cat]['names']:
                    d[cat]['names'].append(name)
                names.setdefault(t, []).append(name)

    # Sort names
    for t, tcm in d.items():
        sorted_names = []
        if 'Normal' in tcm['names']:
            sorted_names.append('Normal')
            tcm['names'].remove('Normal')
        d[t]['names'] = [*sorted_names, *sorted(tcm['names'])]
    return d


def get_template_map_defaults(d: dict[str, TemplateCategoryMap]) -> TemplateSelectedMap:
    """Returns a map of selected defaults for a given 'TemplateCategoryMap'.

    Args:
        d: A 'TemplateCategoryMap' object mapping all templates to their respective types.

    Returns:
        A 'TemplateSelectedMap' mapping the default selected template for each existing template type.
    """
    sel: TemplateSelectedMap = {t: None for t in layout_map_types.keys()}
    first_items: dict[str, TemplateDetails] = {}
    for cat, tcm in d.items():
        for t, name_map in tcm['map'].items():
            for name, details in name_map.items():
                if t not in first_items:
                    first_items[t] = details
                if sel.get(t):
                    continue
                if name == 'Normal':
                    sel[t] = details.copy()

    # Ensure each type has a value, fallback on 'first' appearing items
    for t, details in sel.items():
        if not details:
            sel[t] = first_items.get(t, {}).copy()
    return sel


def get_template_map_selected(
    selected: TemplateSelectedMap,
    defaults: TemplateSelectedMap
) -> TemplateSelectedMap:
    """Merges the template's selected by the users with a provided mapping of default templates.

    Args:
        selected: A mapping of selected templates to template types.
        defaults: A mapping of each default template for every existing template type.

    Returns:
        A combined mapping of templates to every existing template type.
    """
    combined = defaults.copy()
    for layout, details in selected.items():
        combined[layout] = details.copy()
    return combined


"""
* Updating Templates
"""


def check_for_updates(templates: list[AppTemplate]) -> list[AppTemplate]:
    """Check our app and plugin manifests for template updates.

    Args:
        templates: List of all AppTemplate objects.

    Returns:
        List of AppTemplate objects needing an update, sorted by template name.
    """
    # Set up our list of templates needing an update
    updates: list[AppTemplate] = []

    # Perform threaded version check requests
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results: list[tuple[Future, AppTemplate]] = []

        # Check each template for updates
        for t in templates:
            results.append((executor.submit(t.check_for_update), t))

        # Add templates requiring updates
        for r in results:
            if r[0].result():
                updates.append(r[1])

    # Return templates needing updates
    return sorted(updates, key=lambda x: x.name)
