from asyncio import ensure_future, gather, to_thread
from collections.abc import Awaitable, Callable, Iterable, Sequence
from functools import cached_property
from logging import getLogger

from PySide6.QtCore import Property, QObject, Signal, Slot

from src._config import AppConfig
from src._loader import AssembledTemplate, PluginLibrary, TemplateLibrary
from src._state import PATH
from src.cards import CardDetails, parse_card_info, process_card_data
from src.enums.mtg import (
    LayoutCategory,
    LayoutType,
    layout_map_category,
    scryfall_layout_category_map,
)
from src.gui.qml.models.file_dialog_model import FileDialogModel
from src.gui.qml.models.message_dialog_content_model import MessageDialogContentModel
from src.render.render_queue import RenderQueue, cancel_with_render
from src.render.setup import prepare_render_operations
from src.utils.inputs import get_cards_from_details
from src.utils.scryfall import ScryfallCard
from src.utils.tests import get_template_render_test_cases, prepare_test_render

_logger = getLogger(__name__)


class TestRendersModel(QObject):
    def __init__(
        self,
        render_queue: RenderQueue,
        plugin_library: PluginLibrary,
        file_dialog_model: FileDialogModel,
        message_dialog_model: MessageDialogContentModel,
        app_config: AppConfig,
        /,
        parent: QObject | None = None,
        *,
        objectName: str | None = None,
    ) -> None:
        super().__init__(parent, objectName=objectName)
        self._render_queue = render_queue
        self._plugin_library = plugin_library
        self._file_dialog_model = file_dialog_model
        self._message_dialog_model = message_dialog_model
        self._app_config = app_config
        self._layout_categories = list(LayoutCategory)

    @property
    def _template_library(self) -> TemplateLibrary:
        return self._plugin_library.template_library

    @cached_property
    def template_render_test_cases(self) -> dict[LayoutType, dict[str, str]]:
        return get_template_render_test_cases()

    _layout_categories_changed = Signal()

    @Property(list, notify=_layout_categories_changed)
    def layout_categories(self) -> list[LayoutCategory]:
        return self._layout_categories

    @Slot(str, result=list)
    def get_test_cases_for_layout(self, layout: str) -> list[str]:
        layout_category = LayoutCategory(layout)
        all_cases: list[str] = []
        for layout_type in layout_map_category.get(layout_category, []):
            all_cases.extend(
                self.template_render_test_cases.get(layout_type, {}).keys()
            )
        return all_cases

    async def _run_action_per_layout_test_case(
        self,
        callback: Callable[
            [Sequence[tuple[CardDetails, ScryfallCard]]], Awaitable[None]
        ],
        layout_categories: Iterable[LayoutCategory],
        quick: bool,
        case: str | None = None,
    ) -> None:
        cards: list[CardDetails] = []
        for layout_category in layout_categories:
            layout_types = layout_map_category[layout_category]
            for layout_type in layout_types:
                if test_cases := self.template_render_test_cases.get(layout_type, None):
                    for idx, test_case in enumerate(test_cases):
                        if quick and idx > 0:
                            break
                        if case is not None and test_case != case:
                            continue
                        cards.append(
                            parse_card_info(PATH.SRC_IMG_TEST, name_override=test_case)
                        )
                        if case:
                            break
        await get_cards_from_details(cards, callback, self._app_config)

    def _collect_categories(
        self, templates: Iterable[AssembledTemplate]
    ) -> set[LayoutCategory]:
        layout_categories: set[LayoutCategory] = set()
        for template in templates:
            for category in template.layout_categories:
                layout_categories.add(category)
        return layout_categories

    async def test_renders(
        self,
        templates: dict[LayoutCategory, Iterable[AssembledTemplate] | None]
        | None = None,
        quick: bool = False,
        case: str | None = None,
    ) -> None:
        """Queues test renders.

        Args:
            templates: The layout categories and templates to queue tests for. Falsy value means that all tests should be queued. A falsy iterable of templates means that all applicable templates should be tested.
            quick: Queue only the first test for each layout category and template combination.
            case: Test only a specific case."""
        if templates:
            layout_categories_to_test: Iterable[LayoutCategory] = templates.keys()
            for layout_category, test_templates in templates.items():
                if not test_templates:
                    templates[layout_category] = (
                        self._template_library.get_templates_for_layout_category(
                            layout_category
                        )
                    )
        else:
            templates_to_test: list[AssembledTemplate] = list(
                self._template_library.built_in_templates_by_name.values()
            )
            for (
                plugin_templates
            ) in self._template_library.plugin_templates_by_name.values():
                templates_to_test.extend(plugin_templates.values())

            layout_categories_to_test = self._collect_categories(templates_to_test)

            # Test all templates when a more specific configuration isn't provided
            templates = {
                layout_category: [
                    template
                    for template in templates_to_test
                    if template.is_installed(layout_category)
                ]
                for layout_category in layout_categories_to_test
            }

        def process_test_render(
            card: tuple[CardDetails, ScryfallCard], template: AssembledTemplate
        ) -> None:
            render_operations = prepare_render_operations(
                template,
                self._template_library,
                (card,),
                self._file_dialog_model,
                self._message_dialog_model,
            )
            for op in render_operations:
                op.before_render_callback = prepare_test_render
                self._render_queue.enqueue(op)

        async def queue_test_render(
            cards: Sequence[tuple[CardDetails, ScryfallCard]],
        ) -> None:
            operations: list[Awaitable[None]] = []
            for card in cards:
                processed_scryfall_data = process_card_data(card[1], card[0])
                layout_category = scryfall_layout_category_map[
                    processed_scryfall_data.layout
                ]
                if test_templates := templates.get(layout_category):
                    for template in test_templates:
                        operations.append(
                            to_thread(process_test_render, card, template)
                        )
            await gather(*operations)

        await self._run_action_per_layout_test_case(
            queue_test_render, layout_categories_to_test, quick, case=case
        )

    @Slot(str, bool)
    @Slot(str, bool, str)
    def test_all(
        self, layout: str | None = None, quick: bool = False, case: str | None = None
    ) -> None:
        _logger.info(
            f"Queueing {'quick' if quick else 'all'} test renders{
                f' for layout {layout}' if layout else ''
            }"
        )
        cancel_with_render(
            ensure_future(
                self.test_renders(
                    {LayoutCategory(layout): None} if layout else None, quick, case=case
                )
            ),
            self._render_queue,
        )
