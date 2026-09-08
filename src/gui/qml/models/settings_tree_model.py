from collections.abc import Iterable
from logging import getLogger
from typing import override

from pydantic import BaseModel
from PySide6.QtCore import Property, QModelIndex, QObject, Signal, Slot

from src._config import AppConfig, ConfigHandler
from src._loader import AppPlugin, AssembledTemplate, PluginLibrary, TemplateLibrary
from src.gui.qml.models.pydantic_q_list_model import PydanticQItemModel, TreeItem

_logger = getLogger(__name__)


class SettingSectionItem(BaseModel):
    id: str
    name: str
    config: ConfigHandler | None = None
    has_config: bool = True

    model_config = {"arbitrary_types_allowed": True}


class SettingsTreeModel(PydanticQItemModel[SettingSectionItem]):
    item_model = SettingSectionItem

    def __init__(
        self,
        /,
        parent: QObject | None = None,
        *,
        app_config: AppConfig,
        plugin_library: PluginLibrary,
    ) -> None:
        super().__init__(parent)

        self._app_config = app_config
        self._plugin_library = plugin_library
        self._selected_model_index: QModelIndex = QModelIndex()
        self._selected_title: str = ""

        self._prepare_items()

        plugin_library.plugins_changed.add_listener(self._on_plugins_changed)
        plugin_library.template_library_changed.add_listener(
            self._on_template_library_changed
        )

    @property
    def _template_library(self) -> TemplateLibrary:
        return self._plugin_library.template_library

    def _prepare_items(self) -> None:
        template_library = self._plugin_library.template_library

        self._root = TreeItem(data=SettingSectionItem(id="root", name="root"))
        self._app_leaf: TreeItem[SettingSectionItem] = TreeItem(
            data=SettingSectionItem(
                id="application", name="Application", config=self._app_config.app_config
            ),
            parent=self._root,
        )
        _template_defaults_leaf: TreeItem[SettingSectionItem] = TreeItem(
            data=SettingSectionItem(
                id="template_defaults",
                name="Template defaults",
                config=self._app_config.base_config,
            ),
            parent=self._root,
        )

        templates_branch: TreeItem[SettingSectionItem] = TreeItem(
            data=SettingSectionItem(id="templates", name="Templates"), parent=self._root
        )
        self._built_in_templates_branch: TreeItem[SettingSectionItem] = TreeItem(
            data=SettingSectionItem(id="built-in", name="Built-in"),
            parent=templates_branch,
        )
        self._construct_template_branch(
            self._built_in_templates_branch, template_library.built_in_templates_by_name
        )
        self._plugin_templates_branch: TreeItem[SettingSectionItem] = TreeItem(
            data=SettingSectionItem(id="plugins", name="Plugins"),
            parent=templates_branch,
        )
        for plugin_id, templates in template_library.plugin_templates_by_name.items():
            plugin = self._plugin_library.plugins[plugin_id]
            plugin_branch = TreeItem(
                data=SettingSectionItem(id=plugin_id, name=plugin.name),
                parent=self._plugin_templates_branch,
            )
            self._construct_template_branch(plugin_branch, templates)

    def _construct_template_branch(
        self,
        root: TreeItem[SettingSectionItem],
        templates: dict[str, AssembledTemplate],
    ) -> None:
        for name, template in templates.items():
            assembled_branch: TreeItem[SettingSectionItem] = TreeItem(
                data=SettingSectionItem(id=name, name=name), parent=root
            )
            duplicate_check: set[ConfigHandler] = set()
            for named_template in template.templates:
                for (
                    template_class_name,
                    details,
                ) in named_template.template_classes.items():
                    conf = details["config"]
                    if conf not in duplicate_check:
                        tree_item = TreeItem(
                            data=SettingSectionItem(
                                id=template_class_name,
                                name=template_class_name,
                                config=conf,
                                has_config=conf.has_config,
                            ),
                            parent=assembled_branch,
                        )
                        conf.config_added.add_listener(
                            lambda _, item=tree_item: self._on_config_state_changed(
                                item, True
                            )
                        )
                        conf.config_deleted.add_listener(
                            lambda _, item=tree_item: self._on_config_state_changed(
                                item, False
                            )
                        )
                        duplicate_check.add(conf)

    # region Properties

    @override
    def _set_selected_model_index(self, value: QModelIndex) -> None:
        if not value.isValid():
            super()._set_selected_model_index(value)
            return

        item: TreeItem[SettingSectionItem] | None = value.internalPointer()

        if not item or not item.data.config:
            return

        super()._set_selected_model_index(value)

        self.selected_title = item.data.name  # pyright: ignore[reportAttributeAccessIssue]

    _selected_title_changed = Signal()

    @Property(str, notify=_selected_title_changed)
    def selected_title(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._selected_title

    @selected_title.setter
    def selected_title(self, value: str) -> None:
        if value != self._selected_title:
            self._selected_title = value
            self._selected_title_changed.emit()

    @property
    def selected_section(self) -> ConfigHandler | None:
        idx = self._selected_model_index
        if idx.isValid():
            item: TreeItem[SettingSectionItem] = idx.internalPointer()
            return item.data.config

    # endregion Properties

    @Slot(str, str, str)
    def select_settings_section(
        self,
        template_name: str | None = None,
        class_name: str | None = None,
        plugin: str | None = None,
    ) -> None:
        if not template_name:
            self.selected_model_index = self.index_of_item(self._app_leaf)  # pyright: ignore[reportAttributeAccessIssue]
            return

        templates_root: TreeItem[SettingSectionItem] | None = None
        if plugin:
            for tree_item in self._plugin_templates_branch.children:
                if plugin == tree_item.data.id:
                    templates_root = tree_item
                    break
            if not templates_root:
                _logger.error(
                    f"Requested plugin '{plugin}' is not present in the settings tree."
                )
                return
        else:
            templates_root = self._built_in_templates_branch

        matched_item: TreeItem[SettingSectionItem] | None = None
        for tree_item in templates_root.children:
            if template_name == tree_item.data.id:
                if not class_name:
                    matched_item = tree_item.children[0]
                else:
                    for class_item in tree_item.children:
                        if class_name == class_item.data.id:
                            matched_item = class_item
                            break
                break

        if not matched_item:
            _logger.error(
                f"Requested template name <i>{template_name}</i> or class name <i>{
                    class_name
                }</i> is not present in the settings tree."
            )
            return

        self.selected_model_index = self.index_of_item(matched_item)  # pyright: ignore[reportAttributeAccessIssue]

    @Slot()
    def save_configs(self) -> None:
        self._app_config.app_config.save()
        self._app_config.base_config.save()
        self._save_all_template_configs()

    def _save_template_configs(self, templates: Iterable[AssembledTemplate]) -> None:
        for assembled_template in templates:
            for named_temaplate in assembled_template.templates:
                for template_details in named_temaplate.template_classes.values():
                    template_details["config"].save()

    def _save_all_template_configs(self) -> None:
        self._save_template_configs(
            self._template_library.built_in_templates_by_name.values()
        )
        for (
            plugin_templates
        ) in self._template_library.plugin_templates_by_name.values():
            self._save_template_configs(plugin_templates.values())

    def _on_config_state_changed(
        self, tree_item: TreeItem[SettingSectionItem], has_config: bool
    ) -> None:
        tree_item.data.has_config = has_config
        q_idx = self.index_of_item(tree_item)
        self.dataChanged.emit(q_idx, q_idx, [self.get_role("has_config")])

    def _find_item_by_config(
        self, config: ConfigHandler | None
    ) -> TreeItem[SettingSectionItem] | None:
        if config is None:
            return None

        def recurse(
            item: TreeItem[SettingSectionItem],
        ) -> TreeItem[SettingSectionItem] | None:
            if item.data.config and config.id == item.data.config.id:
                return item
            for child in item.children:
                if found := recurse(child):
                    return found
            return None

        return recurse(self._root)

    def _on_plugins_changed(self, plugins: dict[str, AppPlugin]) -> None:
        self._save_all_template_configs()

    def _on_template_library_changed(self, template_library: TemplateLibrary) -> None:
        selected_section = self.selected_section

        self.beginResetModel()
        self._prepare_items()
        self.endResetModel()

        if selected_section:
            if selected_item := self._find_item_by_config(selected_section):
                self.selected_model_index = self.index_of_item(selected_item)  # pyright: ignore[reportAttributeAccessIssue]
            else:
                self.selected_model_index = QModelIndex()  # pyright: ignore[reportAttributeAccessIssue]
