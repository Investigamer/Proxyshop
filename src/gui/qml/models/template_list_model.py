from asyncio import ensure_future, gather, to_thread
from collections.abc import Sequence
from functools import cached_property
from logging import getLogger
from pathlib import Path
from urllib.request import url2pathname

from pydantic import BaseModel
from PySide6.QtCore import QObject, QUrl, Slot

from src._config import AppConfig
from src._loader import (
    AssembledTemplate,
    AssembledTemplateConfigChangedArgs,
    AssembledTemplateInstalledArgs,
    PluginLibrary,
    TemplateLibrary,
    sort_layout_categories,
)
from src.cards import CardDetails
from src.enums.mtg import LayoutCategory
from src.gui.qml.models.file_dialog_model import FileDialogModel
from src.gui.qml.models.message_dialog_content_model import MessageDialogContentModel
from src.gui.qml.models.pydantic_q_list_model import PydanticQListModel
from src.gui.qml.models.test_renders_model import TestRendersModel
from src.render.render_queue import RenderQueue, cancel_with_render
from src.render.setup import prepare_render_operations
from src.utils.data_structures import find_index, first, get_item
from src.utils.inputs import get_cards_from_inputs
from src.utils.scryfall import ScryfallCard

_logger = getLogger(__name__)


class TemplateData(BaseModel):
    name: str
    img: str | None
    card_layouts: list[LayoutCategory]
    installed_template_files: list[str]
    missing_template_files: list[str]
    is_installed: bool
    has_config: bool
    plugin: str
    plugin_id: str

    @cached_property
    def assembled_template(self) -> AssembledTemplate:
        raise ValueError("Assembled template is not set")

    @cached_property
    def full_name(self) -> str:
        return self.name + (f" ({self.plugin})" if self.plugin else "")


class TemplateListModel(PydanticQListModel[TemplateData]):
    item_model = TemplateData

    def __init__(
        self,
        render_queue: RenderQueue,
        file_dialog_model: FileDialogModel,
        message_dialog_model: MessageDialogContentModel,
        plugin_library: PluginLibrary,
        test_renders_model: TestRendersModel,
        app_config: AppConfig,
        parent: QObject | None = None,
        selected_index: int = 0,
    ) -> None:
        self._render_queue = render_queue
        self._file_dialog_model = file_dialog_model
        self._message_dialog_model = message_dialog_model
        self._plugin_library = plugin_library
        self._template_library = plugin_library.template_library
        self._test_renders_model = test_renders_model
        self._app_config = app_config

        plugin_library.template_library_changed.add_listener(
            self._on_template_library_changed
        )

        super().__init__(
            parent,
            items=self._prepare_items(),
            selected_index=selected_index,
        )

    def _prepare_items(self) -> list[TemplateData]:
        self.built_in_templates = self._template_library.built_in_templates_by_name
        self.plugin_templates = self._template_library.plugin_templates_by_name

        template_datas: list[TemplateData] = []

        for name, assembled_template in self.built_in_templates.items():
            template_data = TemplateData(
                name=name,
                card_layouts=(
                    layouts := sort_layout_categories(
                        assembled_template.layout_categories, LayoutCategory.Normal
                    )
                ),
                installed_template_files=assembled_template.installed_template_files,
                missing_template_files=assembled_template.missing_template_files,
                is_installed=assembled_template.is_installed(),
                has_config=assembled_template.has_config(),
                plugin="",
                plugin_id="",
                img=str(path.as_uri())
                if (path := assembled_template.get_preview_image_path(first(layouts)))
                else None,
            )
            template_data.assembled_template = assembled_template
            template_datas.append(template_data)

        for plugin_id, templates_by_name in self.plugin_templates.items():
            for name, assembled_template in templates_by_name.items():
                template_data = TemplateData(
                    name=name,
                    card_layouts=(
                        layouts := sort_layout_categories(
                            assembled_template.layout_categories,
                            LayoutCategory.Normal,
                        )
                    ),
                    installed_template_files=assembled_template.installed_template_files,
                    missing_template_files=assembled_template.missing_template_files,
                    is_installed=assembled_template.is_installed(),
                    has_config=assembled_template.has_config(),
                    plugin=assembled_template.plugin.name
                    if assembled_template.plugin
                    else plugin_id,
                    plugin_id=plugin_id,
                    img=str(path.as_uri())
                    if (
                        path := assembled_template.get_preview_image_path(
                            first(layouts)
                        )
                    )
                    else None,
                )
                template_data.assembled_template = assembled_template
                template_datas.append(template_data)

        for template_data in template_datas:
            template_data.assembled_template.template_installed.add_listener(
                self._on_template_installed
            )
            template_data.assembled_template.config_state_changed.add_listener(
                self._on_template_config_state_changed
            )

        return template_datas

    async def render_files(self, paths: list[Path]) -> None:
        if paths:
            _logger.info(
                f"Queueing {
                    len(paths)
                } inputs for render. Do note that the actual amount of renders might be different if you selected JSON or YAML files or art for split cards."
            )

            selected_template_entry = self.items[self._selected_index]
            if selected_template_entry.plugin_id:
                template = self.plugin_templates[selected_template_entry.plugin_id][
                    selected_template_entry.name
                ]
            else:
                template = self.built_in_templates[selected_template_entry.name]

            def add_render(
                input: CardDetails | tuple[CardDetails, ScryfallCard],
            ) -> None:
                if render_operations := prepare_render_operations(
                    template,
                    self._template_library,
                    (input,),
                    file_dialog=self._file_dialog_model,
                    message_dialog=self._message_dialog_model,
                ):
                    self._render_queue.enqueue(render_operations[0])

            async def add_renders(cards: Sequence[tuple[CardDetails, ScryfallCard]]):
                await gather(*[to_thread(add_render, card) for card in cards])

            await get_cards_from_inputs(paths, add_renders, self._app_config)

    @Slot()
    def render_selections(self) -> None:
        async def action():
            # Choose images
            selections = await self._file_dialog_model.select_images(
                dialog_id="template_list_render",
                filters=[
                    FileDialogModel.IMAGES_AND_DATA_FILTER,
                    FileDialogModel.ALL_FILTER,
                ],
            )

            await self.render_files(selections)

        cancel_with_render(ensure_future(action()), self._render_queue)

    @Slot("QVariantList")
    def render_targets(self, urls: list[QUrl]) -> None:
        paths: list[Path] | None = None
        try:
            paths = [Path(url2pathname(url.path())) for url in urls]
        except Exception:
            _logger.exception("Failed to process drag & dropped files.")
        if paths:
            cancel_with_render(
                ensure_future(self.render_files(paths)), self._render_queue
            )

    @Slot(str, bool)
    @Slot(str, bool, str)
    def test_render(
        self, layout: str | None = None, quick: bool = False, case: str | None = None
    ) -> None:
        async def action() -> None:
            layout_category = LayoutCategory(layout) if layout else None

            selected_template_entry = self.items[self._selected_index]
            if selected_template_entry.plugin_id:
                template = self.plugin_templates[selected_template_entry.plugin_id][
                    selected_template_entry.name
                ]
            else:
                template = self.built_in_templates[selected_template_entry.name]

            _logger.info(
                f"Queueing {
                    layout_category.value + ' ' if layout_category else ''
                }tests for template {template.name}."
            )

            await self._test_renders_model.test_renders(
                {layout_category: (template,)}
                if layout_category
                else {category: (template,) for category in template.layout_categories},
                quick,
                case=case,
            )

        cancel_with_render(ensure_future(action()), self._render_queue)

    @Slot(result=str)
    def selected_template_name(self) -> str:
        if self._selected_index > -1:
            return self.items[self._selected_index].full_name
        return ""

    @Slot(str)
    def select_template(self, name: str) -> None:
        for idx, item in enumerate(self.items):
            if item.full_name == name:
                self.selected_index = idx  # pyright: ignore[reportAttributeAccessIssue]

    @Slot(int)
    def clear_settings(self, idx: int) -> None:
        item = self.items[idx]
        for named_template in item.assembled_template.templates:
            for template_details in named_template.template_classes.values():
                template_details["config"].delete()

    def _on_template_installed(
        self, event_args: AssembledTemplateInstalledArgs
    ) -> None:
        changed_template = event_args["sender"]
        for idx, item in enumerate(self.items):
            if item.assembled_template == changed_template:
                item.is_installed = changed_template.is_installed()
                item.installed_template_files = (
                    changed_template.installed_template_files
                )
                item.missing_template_files = changed_template.missing_template_files
                q_idx = self.createIndex(idx, 0)
                self.dataChanged.emit(
                    q_idx,
                    q_idx,
                    [
                        self.get_role("is_installed"),
                        self.get_role("installed_template_files"),
                        self.get_role("missing_template_files"),
                    ],
                )
                return

        _logger.warning(
            f"Installed template was not found from the template list: {changed_template.name}"
        )

    def _on_template_config_state_changed(
        self, event_args: AssembledTemplateConfigChangedArgs
    ) -> None:
        changed_template = event_args["sender"]
        for idx, item in enumerate(self.items):
            if item.assembled_template == changed_template:
                old_value = item.has_config
                if old_value != (new_value := event_args["has_config"]):
                    item.has_config = new_value
                    q_idx = self.createIndex(idx, 0)
                    self.dataChanged.emit(q_idx, q_idx, [self.get_role("has_config")])
                return

        _logger.warning(
            f"Template with changed config state was not found from the template list: {changed_template.name}"
        )

    def _on_template_library_changed(self, template_library: TemplateLibrary) -> None:
        current_template = get_item(self.items, self._selected_index)

        self._template_library = template_library
        self.beginResetModel()
        self.items = self._prepare_items()
        self.endResetModel()

        if (
            current_template
            and (
                found := find_index(
                    self.items,
                    lambda item: item.full_name == current_template.full_name,
                )
            )
            > -1
        ):
            self.selected_index = found  # pyright: ignore[reportAttributeAccessIssue]
        else:
            self.selected_index = 0  # pyright: ignore[reportAttributeAccessIssue]
