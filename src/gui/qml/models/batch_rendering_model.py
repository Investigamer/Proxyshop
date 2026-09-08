from asyncio import ensure_future, gather, to_thread
from collections.abc import Iterable, Sequence
from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import override
from urllib.request import url2pathname

from pydantic import BaseModel, RootModel, ValidationError
from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, QUrl, Slot

from src._config import AppConfig
from src._loader import (
    AssembledTemplate,
    AssembledTemplateInstalledArgs,
    PluginLibrary,
    TemplateLibrary,
)
from src.cards import CardDetails
from src.enums.mtg import LayoutCategory
from src.gui.qml.models.file_dialog_model import FileDialogModel
from src.gui.qml.models.message_dialog_content_model import MessageDialogContentModel
from src.gui.qml.models.pydantic_q_list_model import PydanticQListModel
from src.gui.qml.models.test_renders_model import TestRendersModel
from src.render.render_queue import RenderQueue, cancel_with_render
from src.render.setup import prepare_render_operations
from src.utils.inputs import get_cards_from_inputs
from src.utils.scryfall import ScryfallCard

_logger = getLogger(__name__)


class TemplateOption(BaseModel):
    name: str
    plugin: str
    plugin_id: str
    is_installed: bool
    preview_img_path: str

    @cached_property
    def full_name(self) -> str:
        return self.name + (f" ({self.plugin})" if self.plugin else "")


class LayoutCategoryItem(BaseModel):
    name: str
    options_details: list[TemplateOption]
    options: list[str]
    options_installed: list[bool]
    options_preview_img_path: list[str]
    selected: int


class _TemplateSelectionPreferences(RootModel[dict[str, str]]):
    root: dict[str, str] = {}


class BatchRenderingModel(PydanticQListModel[LayoutCategoryItem]):
    item_model = LayoutCategoryItem

    def __init__(
        self,
        file_dialog_model: FileDialogModel,
        message_dialog_model: MessageDialogContentModel,
        render_queue: RenderQueue,
        plugin_library: PluginLibrary,
        test_renders_model: TestRendersModel,
        app_config: AppConfig,
        parent: QObject | None = None,
        selected_index: int = -1,
    ) -> None:
        self._file_dialog_model = file_dialog_model
        self._message_dialog_model = message_dialog_model
        self._render_queue = render_queue
        self._test_renders_model = test_renders_model
        self._plugin_library = plugin_library
        self._template_library = plugin_library.template_library
        self._app_config = app_config

        self._plugin_library.template_library_changed.add_listener(
            self._on_template_library_changed
        )

        super().__init__(parent, self._prepare_items(), selected_index)

    def _prepare_items(self) -> list[LayoutCategoryItem]:
        template_library = self._plugin_library.template_library

        self.built_in_templates_by_layout: dict[
            LayoutCategory, dict[str, AssembledTemplate]
        ] = {}
        self.plugin_templates_by_layout: dict[
            LayoutCategory, dict[str, dict[str, AssembledTemplate]]
        ] = {}
        """dict[layout, dict[plugin, dict[template_name, template]]]"""

        for layout_category in LayoutCategory:
            self.built_in_templates_by_layout.setdefault(layout_category, {})
            self.plugin_templates_by_layout.setdefault(
                layout_category,
                {plugin.id: {} for plugin in self._plugin_library.plugins.values()},
            )

        for name, template in template_library.built_in_templates_by_name.items():
            for layout_category in template.layout_categories:
                self.built_in_templates_by_layout[layout_category][name] = template

            template.template_installed.add_listener(self._on_template_installed)

        for plugin, templates in template_library.plugin_templates_by_name.items():
            for name, template in templates.items():
                for layout_category in template.layout_categories:
                    self.plugin_templates_by_layout[layout_category].setdefault(
                        plugin, {}
                    )
                    self.plugin_templates_by_layout[layout_category][plugin][name] = (
                        template
                    )

                template.template_installed.add_listener(self._on_template_installed)

        layout_cat_items: list[LayoutCategoryItem] = []
        for (
            layout_category,
            template_options,
        ) in self.built_in_templates_by_layout.items():
            opts = [
                TemplateOption(
                    name=opt_name,
                    plugin="",
                    plugin_id="",
                    is_installed=opt.is_installed(layout_category),
                    preview_img_path=path.as_uri()
                    if (path := opt.get_preview_image_path(layout_category))
                    else "",
                )
                for opt_name, opt in template_options.items()
            ]

            for plugin, plugin_opts in self.plugin_templates_by_layout[
                layout_category
            ].items():
                for opt_name, opt in plugin_opts.items():
                    opts.append(
                        TemplateOption(
                            name=opt_name,
                            plugin=opt.plugin.name if opt.plugin else plugin,
                            plugin_id=plugin,
                            is_installed=opt.is_installed(layout_category),
                            preview_img_path=path.as_uri()
                            if (path := opt.get_preview_image_path(layout_category))
                            else "",
                        )
                    )

            layout_cat_item = LayoutCategoryItem(
                name=layout_category,
                selected=-1,
                options_details=opts,
                options=[opt.full_name for opt in opts],
                options_installed=[opt.is_installed for opt in opts],
                options_preview_img_path=[opt.preview_img_path for opt in opts],
            )
            layout_cat_items.append(layout_cat_item)

        return layout_cat_items

    @override
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex) -> int:
        return 2

    @property
    def template_choices(self) -> dict[LayoutCategory, AssembledTemplate]:
        template_choices: dict[LayoutCategory, AssembledTemplate] = {}
        for item in self.items:
            if item.selected < 0:
                continue

            selected_opt = item.options_details[item.selected]

            if not selected_opt.is_installed:
                continue

            layout_category = LayoutCategory(item.name)
            if selected_opt.plugin_id:
                template_choices[layout_category] = self.plugin_templates_by_layout[
                    layout_category
                ][selected_opt.plugin_id][selected_opt.name]
            else:
                template_choices[layout_category] = self.built_in_templates_by_layout[
                    layout_category
                ][selected_opt.name]
        return template_choices

    # layout, selected index
    @Slot(int, int)
    def select_template_for_layout(
        self, layout_category_idx: int, selected_index: int
    ) -> None:
        item = self.items[layout_category_idx]
        item.selected = selected_index
        q_idx = self.createIndex(layout_category_idx, 0)
        self.dataChanged.emit(q_idx, q_idx, [self.get_role("selected")])

    async def render_files(self, paths: list[Path]) -> None:
        if paths:
            _logger.info(
                f"Queueing {
                    len(paths)
                } batch mode inputs for render. Do note that the actual amount of renders might be different if you selected JSON or YAML files or art for split cards."
            )

            def add_render(
                input: CardDetails | tuple[CardDetails, ScryfallCard],
            ) -> None:
                if render_operations := prepare_render_operations(
                    self.template_choices,
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
                dialog_id="batch_mode_render",
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

            if layout_category and not (
                (template := self.template_choices.get(layout_category))
                and template.is_installed(layout_category)
            ):
                _logger.info(
                    f"A template hasn't been chosen/installed for {layout_category} so there are no tests to queue."
                )
                return

            if layout_category:
                conf: dict[LayoutCategory, Iterable[AssembledTemplate] | None] = {
                    layout_category: (self.template_choices[layout_category],)
                }
            else:
                conf = {
                    cat: (template,)
                    for cat, template in self.template_choices.items()
                    if template.is_installed(cat)
                }

            if not conf:
                _logger.info(
                    "No installed templates have been chosen so there are no tests to queue."
                )
                return

            _logger.info(
                f"Queueing {
                    layout_category.value + ' ' if layout_category else ''
                }tests for batch mode selections."
            )

            await self._test_renders_model.test_renders(conf, quick, case=case)

        cancel_with_render(ensure_future(action()), self._render_queue)

    @Slot(result=str)
    def get_template_selections_json(self) -> str:
        selections = _TemplateSelectionPreferences()
        for item in self.items:
            if item.selected > -1:
                selections.root[item.name] = item.options[item.selected]
        return selections.model_dump_json() if selections.root else ""

    @Slot(str)
    def restore_template_selections(self, data: str) -> None:
        try:
            parsed_data = _TemplateSelectionPreferences.model_validate_json(data).root
            for item_idx, item in enumerate(self.items):
                if selection := parsed_data.get(item.name):
                    for idx, opt in enumerate(item.options):
                        if opt == selection:
                            item.selected = idx
                            q_idx = self.index(item_idx, 0)
                            self.dataChanged.emit(q_idx, q_idx, ["selected"])
        except ValidationError:
            _logger.exception("Failed to restore batch model selection preferences.")

    @Slot(result="QVariantList")
    def layout_names(self) -> list[str]:
        return [item.name for item in self.items]

    def _on_template_installed(
        self, event_args: AssembledTemplateInstalledArgs
    ) -> None:
        origin = event_args["origin"]
        for idx, item in enumerate(self.items):
            for opt_idx, opt in enumerate(item.options_details):
                if (
                    opt.plugin_id if origin.plugin else not opt.plugin_id
                ) and opt.name in origin.named_templates:
                    opt.is_installed = True
                    item.options_installed[opt_idx] = True
                    q_idx = self.createIndex(idx, 0)
                    self.dataChanged.emit(
                        q_idx, q_idx, [self.get_role("options_installed")]
                    )

    def _on_template_library_changed(self, template_library: TemplateLibrary) -> None:
        current_selections = {item.name: item.selected for item in self.items}

        self._template_library = template_library

        self.beginResetModel()
        self.items = self._prepare_items()
        for item in self.items:
            item.selected = current_selections.get(item.name, -1)
        self.endResetModel()
