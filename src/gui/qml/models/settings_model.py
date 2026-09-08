from functools import cached_property
from typing import Literal, override

from pydantic import BaseModel
from PySide6.QtCore import (
    Property,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)

from src._config import (
    BoolSetting,
    ConfigHandler,
    FloatSetting,
    IntSetting,
    NumericSetting,
    SectionTitle,
    StringSetting,
)
from src.gui.qml.models.pydantic_q_list_model import PydanticQListModel
from src.gui.qml.models.settings_tree_model import SettingsTreeModel


class HybridSettingItem(BaseModel):
    type: Literal["title", "bool", "string", "numeric", "options", "int", "float"]
    title: str
    desc: str | None = None
    value: bool | str | int | float | None = None
    default_value: bool | str | int | float | None = None
    options: list[str] | None = None

    @cached_property
    def section(self) -> str:
        return ""

    @cached_property
    def key(self) -> str:
        return ""


class SettingsModel(PydanticQListModel[HybridSettingItem]):
    item_model = HybridSettingItem

    def __init__(
        self,
        settings_tree_model: SettingsTreeModel,
        parent: QObject | None = None,
        items: list[HybridSettingItem] | None = None,
        selected_index: int = -1,
    ) -> None:
        super().__init__(parent, items, selected_index)
        self._current_config_handler: ConfigHandler | None = None
        self.settings_tree_model = settings_tree_model
        settings_tree_model.selected_model_index_changed.connect(
            self.on_settings_section_change
        )

    @property
    def current_config_handler(self) -> ConfigHandler | None:
        return self._current_config_handler

    @current_config_handler.setter
    def current_config_handler(self, value: ConfigHandler | None) -> None:
        if self._current_config_handler:
            self._current_config_handler.config_deleted.remove_listener(self._on_clear)
            self._current_config_handler.config_reset.remove_listener(self._on_reset)

        self._current_config_handler = value
        if value:
            if not value.has_config:
                value.save(force=True)
            value.config_deleted.add_listener(self._on_clear)
            value.config_reset.add_listener(self._on_reset)
        self._valid_changed.emit()

    @cached_property
    def _value_role(self) -> int:
        for role, name in self._roles.items():
            if name == "value":
                return role
        raise ValueError("Value role doesn't exist")

    @override
    def setData(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: float | str | bool,
        /,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if index.isValid() or self._roles.get(role) == "value":
            item = self.items[index.row()]
            if self._current_config_handler and self._current_config_handler.set_value(
                item.section, item.key, value
            ):
                item.value = value
                self.dataChanged.emit(index, index, [role])
                return True
        return False

    def populate_settings(self, config_handler: ConfigHandler) -> None:
        new_items: list[HybridSettingItem] = []
        schemas = (
            (config_handler.base_schema.root, config_handler.schema.root)
            if config_handler.schema
            else (config_handler.base_schema.root,)
        )
        for schema in schemas:
            for section in schema:
                if isinstance(section, SectionTitle):
                    new_item = HybridSettingItem(type=section.type, title=section.title)
                elif isinstance(
                    section,
                    (
                        BoolSetting,
                        StringSetting,
                        NumericSetting,
                        FloatSetting,
                        IntSetting,
                    ),
                ):
                    new_item = HybridSettingItem(
                        type=section.type,
                        title=section.title,
                        desc=section.desc,
                        value=config_handler.setting_values[section.section][
                            section.key
                        ],
                        default_value=section.default,
                    )
                    new_item.section = section.section
                    new_item.key = section.key
                else:
                    new_item = HybridSettingItem(
                        type=section.type,
                        title=section.title,
                        desc=section.desc,
                        value=config_handler.setting_values[section.section][
                            section.key
                        ],
                        default_value=section.default,
                        options=section.options,
                    )
                    new_item.section = section.section
                    new_item.key = section.key
                new_items.append(new_item)
        self.beginResetModel()
        self.items = new_items
        self.current_config_handler = config_handler
        self.endResetModel()

    @Slot(QModelIndex)
    def on_settings_section_change(self, value: QModelIndex) -> None:
        if selected := self.settings_tree_model.selected_section:
            self.populate_settings(selected)
        else:
            self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
            self.items = []
            self.current_config_handler = None
            self.endRemoveRows()

    def _set_value(self, index: int, value: bool | str | float) -> None:
        self.setData(self.createIndex(index, 0), value)

    @Slot(int, bool)
    def bool_value_changed(self, index: int, value: bool) -> None:
        self._set_value(index, value)

    @Slot(int, str)
    def str_value_changed(self, index: int, value: str) -> None:
        self._set_value(index, value)

    @Slot(int, int)
    def int_value_changed(self, index: int, value: int) -> None:
        self._set_value(index, value)

    @Slot(int, float)
    def float_value_changed(self, index: int, value: float) -> None:
        self._set_value(index, value)

    @Slot()
    def reset(self) -> None:
        if self._current_config_handler:
            self._current_config_handler.reset()

    def _on_reset(self, conf_handler: ConfigHandler) -> None:
        if self._current_config_handler:
            self.populate_settings(self._current_config_handler)

    @Slot()
    def clear(self) -> None:
        if self._current_config_handler:
            self._current_config_handler.delete()

    def _on_clear(self, conf_handler: ConfigHandler) -> None:
        if self._current_config_handler:
            self.settings_tree_model.selected_model_index = QModelIndex()  # pyright: ignore[reportAttributeAccessIssue]

    _valid_changed = Signal()

    @Property(bool, notify=_valid_changed)
    def valid(self) -> bool:
        return self._current_config_handler is not None
