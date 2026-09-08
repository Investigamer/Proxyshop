import shutil
import subprocess
import tempfile
from asyncio import ensure_future, to_thread
from collections.abc import Callable
from enum import Enum
from functools import cached_property
from logging import getLogger
from pathlib import Path
from threading import Lock

import yaml
from omnitils.fetch.download import download_file
from omnitils.files.archive import ArchType, unpack_archive
from pathvalidate import sanitize_filename
from pydantic import BaseModel, RootModel, computed_field
from pydantic_core import Url
from PySide6.QtCore import Property, QModelIndex, QObject, Signal, Slot

from src import DEFAULT_HEADERS
from src._loader import (
    AppPlugin,
    PluginLibrary,
    PluginManifest,
    RemoteGithubPluginDefinition,
    RemoteGitPluginDefinition,
    RemotePluginDefinitions,
)
from src._state import PATH, AppConstants, AppEnvironment
from src.gui.qml.models.pydantic_q_list_model import PydanticQListModel
from src.utils.data_structures import dump_model, find_item, parse_model
from src.utils.git import get_latest_remote_git_commit_hash, is_git_available
from src.utils.github import (
    download_github_repository_archive_zip,
    get_github_file_contents,
    get_github_releases,
    get_latest_github_repo_commit_hash,
)

_logger = getLogger(__name__)


class PluginSourceType(Enum):
    GIT = 1
    GITHUB = 2


class PluginItem(BaseModel):
    id: str
    name: str
    author: str = ""
    url: str = ""
    source: str
    source_type: PluginSourceType
    path: str = ""
    license: str = ""
    description: str = ""
    installed_version: str = ""
    available_version: str = ""
    downloading: bool = False
    is_user_defined: bool
    handler: AppPlugin | None = None

    @computed_field
    @property
    def installed(self) -> bool:
        return bool(self.handler)

    model_config = {"arbitrary_types_allowed": True}


PluginVersionsModel = RootModel[dict[str, str]]


_user_file_dirs = ("config_ini", "templates")
_data_fetch_lock = Lock()
_added_plugins_lock = Lock()
_plugin_versions_lock = Lock()


class PluginUpdaterModel(PydanticQListModel[PluginItem]):
    item_model = PluginItem

    def __init__(
        self,
        app_env: AppEnvironment,
        con: AppConstants,
        plugin_library: PluginLibrary,
        parent: QObject | None = None,
        items: list[PluginItem] | None = None,
        selected_index: int = -1,
    ) -> None:
        self._app_env = app_env
        self._con = con
        self._plugin_library = plugin_library
        self._fetching_data = False
        self._predefined: RemotePluginDefinitions = self._read_predefined_plugins()
        super().__init__(parent, items, selected_index)

    @cached_property
    def _git_is_available(self) -> bool:
        return is_git_available()

    @cached_property
    def _added_plugins(
        self,
    ) -> dict[str, RemoteGitPluginDefinition | RemoteGithubPluginDefinition]:
        with _added_plugins_lock:
            if PATH.SRC_DATA_ADDED_PLUGINS.exists():
                try:
                    return parse_model(
                        PATH.SRC_DATA_ADDED_PLUGINS, RemotePluginDefinitions
                    ).root
                except Exception as exc:
                    _logger.exception(
                        "Failed to parse added plugins file", exc_info=exc
                    )
            return {}

    @cached_property
    def _plugin_versions(self) -> dict[str, str]:
        with _plugin_versions_lock:
            if PATH.SRC_DATA_PLUGIN_VERSIONS.exists():
                try:
                    return parse_model(
                        PATH.SRC_DATA_PLUGIN_VERSIONS, PluginVersionsModel
                    ).root
                except Exception as exc:
                    _logger.exception(
                        "Failed to parse plugin versions file", exc_info=exc
                    )
            return {}

    _fetching_data_changed = Signal(name="fetchingDataChanged")

    @Property(bool, notify=_fetching_data_changed)
    def fetching_data(self) -> bool:  # pyright: ignore[reportRedeclaration]
        return self._fetching_data

    @fetching_data.setter
    def fetching_data(self, value: bool) -> None:
        if value != self._fetching_data:
            self._fetching_data = value
            self._fetching_data_changed.emit()

    @Slot()
    def fetch_data(self) -> None:
        ensure_future(to_thread(self.handle_fetch_data))

    def _create_plugin_item(
        self,
        id: str,
        definition: RemoteGitPluginDefinition | RemoteGithubPluginDefinition,
        installed_version: str,
        installed_plugin: AppPlugin | None,
    ) -> PluginItem:
        return PluginItem(
            id=id,
            name=definition.name,
            author=definition.author,
            url=self._url_for_plugin(definition),
            source=self._source_for_plugin(definition),
            source_type=PluginSourceType.GITHUB
            if isinstance(definition, RemoteGithubPluginDefinition)
            else PluginSourceType.GIT,
            path=str(installed_plugin.root) if installed_plugin else "",
            license=installed_plugin.license or "" if installed_plugin else "",
            description=installed_plugin.description or "" if installed_plugin else "",
            installed_version=installed_version,
            available_version=self._get_available_version(definition),
            is_user_defined=id in self._added_plugins,
            handler=installed_plugin,
        )

    _update_available = Signal(name="updateAvailable")

    def handle_fetch_data(self) -> bool:
        if not _data_fetch_lock.acquire(False):
            return False

        try:
            self.fetching_data = True  # pyright: ignore[reportAttributeAccessIssue]

            predefined_plugins = self._predefined.root
            installed_plugins = self._plugin_library.plugins.copy()

            items: list[PluginItem] = []

            for plugin_id, plugin_definition in [
                *predefined_plugins.items(),
                *self._added_plugins.items(),
            ]:
                installed_plugin = installed_plugins.pop(plugin_id, None)
                installed_version = self._plugin_versions.get(plugin_id, "")
                if installed_plugin and not installed_version:
                    installed_version = installed_plugin.version
                items.append(
                    self._create_plugin_item(
                        plugin_id,
                        plugin_definition,
                        installed_version,
                        installed_plugin,
                    )
                )

            for plugin in installed_plugins.values():
                items.append(
                    PluginItem(
                        id=plugin.id,
                        name=plugin.name,
                        author=plugin.author or "Unknown",
                        url=plugin.source or "",
                        source=plugin.source or "",
                        source_type=PluginSourceType.GIT,
                        path=str(plugin.root),
                        license=plugin.license or "",
                        description=plugin.description or "",
                        installed_version=plugin.version,
                        is_user_defined=True,
                        handler=plugin,
                    )
                )

            items.sort(key=lambda value: value.name.lower())
            self.beginResetModel()
            self.items = items
            self.selected_index = 0  # pyright: ignore[reportAttributeAccessIssue]
            self.endResetModel()

            self.fetching_data = False  # pyright: ignore[reportAttributeAccessIssue]

            if update_available := bool(
                find_item(
                    self.items,
                    lambda item: bool(
                        item.installed_version
                        and item.available_version
                        and item.installed_version != item.available_version
                    ),
                )
            ):
                self._update_available.emit()
            return update_available
        finally:
            _data_fetch_lock.release()

    def _read_predefined_plugins(self) -> RemotePluginDefinitions:
        if PATH.SRC_DATA_PREDEFINED_PLUGINS.exists():
            try:
                return parse_model(
                    PATH.SRC_DATA_PREDEFINED_PLUGINS, RemotePluginDefinitions
                )
            except Exception as exc:
                _logger.exception(
                    "Failed to parse predefined plugins file", exc_info=exc
                )
        return RemotePluginDefinitions({})

    def _url_for_plugin(
        self,
        plugin_definition: RemoteGithubPluginDefinition | RemoteGitPluginDefinition,
    ) -> str:
        if isinstance(plugin_definition, RemoteGithubPluginDefinition):
            return f"https://github.com/{plugin_definition.github_author}/{plugin_definition.github_repo}"
        return str(plugin_definition.git_repo)

    def _source_for_plugin(
        self,
        plugin_definition: RemoteGithubPluginDefinition | RemoteGitPluginDefinition,
    ) -> str:
        if isinstance(plugin_definition, RemoteGithubPluginDefinition):
            return f"{plugin_definition.github_author}/{plugin_definition.github_repo}"
        return str(plugin_definition.git_repo)

    def _parse_github_repository(self, url: str) -> tuple[str, str, str] | None:
        """Extracts the author/repo portion from a GitHub url.
        E.g. https://github.com/Investigamer/Proxyshop.git -> (Investigamer/Proxyshop, Investigamer, Proxyshop)"""
        if url.startswith("https://github.com/"):
            repo = url.split("github.com/")[-1]
        elif url.startswith("git@github.com:"):
            repo = url.split(":git@github.com:")[-1]
        else:
            return None
        repo = repo.removesuffix(".git")
        parts = repo.split("/")
        return (repo, parts[0], parts[1])

    def _get_available_version(
        self, plugin: RemoteGitPluginDefinition | RemoteGithubPluginDefinition
    ) -> str:
        try:
            if isinstance(plugin, RemoteGithubPluginDefinition):
                repo = f"{plugin.github_author}/{plugin.github_repo}"
                if releases := get_github_releases(repo, per_page=1):
                    return releases[0].tag_name
                return get_latest_github_repo_commit_hash(repo)

            if not self._git_is_available:
                _logger.warning(
                    f"Can't retrieve latest version information for plugin {plugin.name} since Git isn't available. Make sure Git is available in your PATH if you want to install plugins from generic Git repositories."
                )
                return ""

            return get_latest_remote_git_commit_hash(str(plugin.git_repo)) or ""
        except Exception:
            _logger.exception(
                f"Failed to retrieve latest version information for plugin {plugin.name}"
            )
        return ""

    def _prepare_destination(self, dest: Path) -> None:
        if dest.exists():
            for child in dest.iterdir():
                if child.name in _user_file_dirs:
                    continue
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        else:
            dest.mkdir(parents=True, exist_ok=True)

    def _install_extracted_archive(
        self,
        extracted: Path,
        dest: Path,
        item: PluginItem,
        version: str,
    ) -> None:
        self._prepare_destination(dest)
        for child in extracted.iterdir():
            shutil.move(child, dest / child.name)
        item.installed_version = version

    def _download_and_extract_archive[T](
        self,
        download: Callable[[Path], T],
        dest: Path,
        item: PluginItem,
        version: str,
    ) -> bool:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
            tmp = Path(tmp_dir)
            archive_path = tmp / "plugin.zip"
            download(archive_path)
            unpack_archive(archive_path, remove=True)

            if (tmp / "manifest.yml").is_file():
                extracted = tmp
            elif not (
                (extracted := next(tmp.iterdir(), None))
                and (extracted / "manifest.yml").is_file()
            ):
                return False

            self._install_extracted_archive(extracted, dest, item, version)
            return True

    def _download_from_github(
        self, repository: str, dest: Path, item: PluginItem
    ) -> bool:
        try:
            if (releases := get_github_releases(repository, per_page=1)) and (
                release_assets := releases[0].assets
            ):
                for _ in (None,):
                    rel = releases[0]
                    url = release_assets[0].browser_download_url

                    if "." not in url or (url[url.rindex(".") :]) not in ArchType:
                        _logger.error(
                            f"Release '{url}' has an unsupported filetype. Supported types include {list(ArchType)}. Falling back to downloading the repository's files."
                        )
                        break

                    if self._download_and_extract_archive(
                        lambda path, download_url=url: download_file(
                            download_url, path, header=DEFAULT_HEADERS
                        ),
                        dest,
                        item,
                        rel.tag_name,
                    ):
                        return True
                    else:
                        _logger.error(
                            f"Release '{url}' has an unsupported file structure. Falling back to downloading the repository's files."
                        )

            version = get_latest_github_repo_commit_hash(repository)
            if self._download_and_extract_archive(
                lambda path: download_github_repository_archive_zip(repository, path),
                dest,
                item,
                version,
            ):
                return True
            else:
                _logger.error(
                    f"Failed to download plugin '{item.name}' from GitHub {repository}. The repository archive doesn't contain a root directory."
                )
        except Exception:
            _logger.exception(
                f"Failed to download plugin '{item.name}' from GitHub repository {repository}"
            )

        return False

    def _clone_git_source(self, url: str, dest: Path, item: PluginItem) -> bool:
        if not self._git_is_available:
            _logger.warning(
                f"Can't clone Git source '{url}' since Git isn't available. Make sure Git is available in your PATH if you want to install plugins from generic Git repositories."
            )
            return False

        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
                tmp = Path(tmp_dir)
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, tmp_dir],
                    check=True,
                )
                sha = (
                    subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp)
                    .decode()
                    .strip()
                )
                self._prepare_destination(dest)
                for child in tmp.iterdir():
                    if child.name in [".git", *_user_file_dirs]:
                        continue
                    shutil.move(child, dest / child.name)
                item.installed_version = sha
                return True
        except Exception:
            _logger.exception(
                f"Failed to download plugin <b>{item.name}</b> from {url}"
            )
        return False

    @Slot(int)
    def download_plugin(self, index: int) -> None:
        if index < 0 or index >= self.rowCount():
            return
        ensure_future(to_thread(self._handle_download_plugin, index))

    def _handle_download_plugin(self, index: int) -> None:
        item = self.items[index]
        q_index = self.createIndex(index, 0)

        item.downloading = True
        changed_fields = [self.get_role("downloading")]
        self.dataChanged.emit(q_index, q_index, changed_fields)

        try:
            source = item.source
            if not source:
                _logger.error(
                    f"Can't download plugin <b>{item.name}</b> since it has no source"
                )
                return

            dest = PATH.PLUGINS / item.id

            if self._download_from_github(source, dest, item) or self._clone_git_source(
                source, dest, item
            ):
                self._plugin_versions[item.id] = item.installed_version or ""
            else:
                return

            self.save_versions()
            item.handler = self._plugin_library.add_plugin(dest)
            item.path = str(dest)
            item.available_version = item.installed_version
            changed_fields.extend(
                (
                    self.get_role("installed_version"),
                    self.get_role("installed"),
                    self.get_role("path"),
                    self.get_role("available_version"),
                )
            )
        finally:
            item.downloading = False
            self.dataChanged.emit(q_index, q_index, changed_fields)

    @Slot(str)
    def add_plugin(self, url: str) -> None:
        ensure_future(to_thread(self._handle_add_plugin, url))

    def _check_existing_plugin_definition(
        self, plugin_id: str, plugin_url: str
    ) -> bool:
        if existing_plugin := self._predefined.root.get(
            plugin_id
        ) or self._added_plugins.get(plugin_id):
            _logger.warning(
                f"Plugin at <b>{plugin_url}</b> is already registered to the system with the name <b>{existing_plugin.name}</b>."
            )
            return True
        return False

    def _handle_add_plugin(self, url: str) -> None:
        if not url:
            return

        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
                tmp = Path(tmp_dir)

                if github_repo := self._parse_github_repository(url):
                    repo, author, name = github_repo
                    plugin_id = f"{name}-{author}"

                    if self._check_existing_plugin_definition(plugin_id, url):
                        return

                    try:
                        data = get_github_file_contents(repo, "manifest.yml")
                        manifest = PluginManifest.model_validate(yaml.safe_load(data))
                    except Exception:
                        _logger.exception(
                            "Failed to add plugin from GitHub url {url}. The repository doesn't contain a valid manifest.yml at root level."
                        )
                        return

                    plugin_definition = RemoteGithubPluginDefinition(
                        name=manifest.plugin.name or name,
                        author=manifest.plugin.author or author,
                        github_author=author,
                        github_repo=name,
                    )
                    self._save_added_plugins()
                elif self._git_is_available:
                    plugin_id = sanitize_filename(url, replacement_text="-")

                    if self._check_existing_plugin_definition(plugin_id, url):
                        return

                    subprocess.run(
                        (
                            "git",
                            "clone",
                            "--no-checkout",
                            "--depth",
                            "1",
                            "--filter=tree:0",
                            url,
                        ),
                        cwd=tmp,
                        check=True,
                    )
                    repo_dir = next(tmp.iterdir())
                    default_branch = subprocess.check_output(
                        ("git", "rev-parse", "--abbrev-ref", "origin/HEAD"),
                        cwd=repo_dir,
                    )
                    try:
                        checkout_manifest_args = (
                            "git",
                            "checkout",
                            default_branch,
                            "--",
                            "manifest.yml",
                        )
                        # For some reason Git usually fails to checkout the file on first attempt
                        subprocess.run(
                            checkout_manifest_args, cwd=repo_dir, check=False
                        )
                        subprocess.run(checkout_manifest_args, cwd=repo_dir, check=True)
                    except subprocess.CalledProcessError:
                        _logger.exception(
                            f"Failed to add plugin from Git url {url}. The repository doesn't contain a manifest.yml at root level."
                        )
                        return

                    manifest = parse_model(repo_dir / "manifest.yml", PluginManifest)

                    plugin_definition = RemoteGitPluginDefinition(
                        name=manifest.plugin.name or plugin_id,
                        author=manifest.plugin.author or "Unknown",
                        git_repo=Url(url),
                    )
                else:
                    _logger.error(
                        f"Can't add plugin from Git repository {url} since Git is not available. Make sure Git is available in your PATH if you want to install plugins from generic Git repositories."
                    )
                    return

                self._added_plugins[plugin_id] = plugin_definition
                self._save_added_plugins()

                plugin_item = self._create_plugin_item(
                    plugin_id, plugin_definition, "", None
                )

                row_count = self.rowCount()
                self.beginInsertRows(QModelIndex(), row_count, row_count)
                self.items.append(plugin_item)
                self.endInsertRows()
        except Exception:
            _logger.exception(f"Failed to add plugin from url {url}")

    @Slot(int)
    def remove_plugin(self, index: int) -> None:
        if index < 0 or index >= self.rowCount():
            return

        plugin = self.items[index]

        self._plugin_library.remove_plugin(plugin.id)
        self._plugin_versions.pop(plugin.id, None)
        self.save_versions()

        plugin.path = ""
        plugin.installed_version = ""
        plugin.handler = None

        q_idx = self.createIndex(index, 0)
        self.dataChanged.emit(
            q_idx,
            q_idx,
            (
                self.get_role("installed_version"),
                self.get_role("installed"),
                self.get_role("path"),
            ),
        )

    @Slot(int)
    def remove_added_plugin(self, index: int) -> None:
        if index < 0 or index >= self.rowCount():
            return

        plugin = self.items[index]
        if not plugin.is_user_defined:
            return

        if plugin.installed:
            self._plugin_library.remove_plugin(plugin.id)
            self._plugin_versions.pop(plugin.id, None)
            self.save_versions()

        if self._added_plugins.pop(plugin.id, None):
            self._save_added_plugins()

        self.beginRemoveRows(QModelIndex(), index, index)
        self.items.pop(index)
        self.endRemoveRows()
        self.selected_index = min(self._selected_index, self.rowCount() - 1)  # pyright: ignore[reportAttributeAccessIssue]

    @Slot()
    def save_versions(self) -> None:
        versions = self._plugin_versions
        with _plugin_versions_lock:
            dump_model(PATH.SRC_DATA_PLUGIN_VERSIONS, PluginVersionsModel(versions))

    def _save_added_plugins(self) -> None:
        added_plugins = self._added_plugins
        with _added_plugins_lock:
            dump_model(
                PATH.SRC_DATA_ADDED_PLUGINS, RemotePluginDefinitions(added_plugins)
            )
