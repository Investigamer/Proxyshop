from asyncio import CancelledError, Future, Task, create_task, get_running_loop
from collections.abc import Callable, Iterable, Mapping
from logging import getLogger
from time import perf_counter
from typing import TYPE_CHECKING, TypedDict

from src import CON, ENV
from src._config import AppConfig, ConfigHandler
from src._loader import RenderableTemplate, TemplateLibrary, get_template_class
from src.cards import CardDetails
from src.enums.mtg import LayoutCategory
from src.layouts import NormalLayout, assign_layout, join_dual_card_layouts
from src.templates._core import BaseTemplate
from src.utils.asynchronic import async_to_sync, try_threadsafe_set_result
from src.utils.event import SubscribableEvent
from src.utils.scryfall import ScryfallCard

if TYPE_CHECKING:
    from src.gui.qml.models.file_dialog_model import FileDialogModel
    from src.gui.qml.models.message_dialog_content_model import (
        MessageDialogContentModel,
    )

_logger = getLogger(__name__)


class PausedEventArgs(TypedDict):
    message: str | None


class RenderOperation:
    def __init__(
        self,
        template_class: type[BaseTemplate],
        layout: NormalLayout,
        config: ConfigHandler,
        file_dialog: FileDialogModel,
        message_dialog: MessageDialogContentModel,
    ) -> None:
        self._file_dialog = file_dialog
        self._message_dialog = message_dialog

        self.template_class = template_class
        self.layout = layout
        self.config = config
        self.template_instance: BaseTemplate | None = None
        self.before_render_callback: (
            Callable[[RenderOperation, AppConfig], None] | None
        ) = None
        self.do_not_pause: bool = False
        self.render_task: Task[bool] | None = None
        self._waiting: Future[bool] | None = None
        self._paused: SubscribableEvent[PausedEventArgs] = SubscribableEvent()

    @property
    def paused(self):
        return self._paused

    async def render(self) -> bool:
        card_display_name = f"<b>{self.layout.display_name} ({self.layout.artist}) [{self.layout.set}] {{{self.layout.collector_number_raw}}} |{self.layout.category.value}| \\{self.template_class.__name__}/</b>"
        _logger.info(f"Starting rendering of {card_display_name}")

        try:
            self.layout.config = self.layout.config.copy(self.config)
            CON.reload()

            self.template_instance = self.template_class(self.layout)
            self.template_instance.render_operation = self
            self.template_instance.file_dialog = self._file_dialog
            self.template_instance.message_dialog = self._message_dialog

            if self.before_render_callback:
                self.before_render_callback(self, self.layout.config)

            start_time = perf_counter()

            self.render_task = create_task(self.template_instance.execute())
            try:
                result = await self.render_task
            except CancelledError:
                result = False

            if not result:
                self.template_instance.docref.close()

            _logger.info(
                f"{'Finished' if result else 'Cancelled'} rendering {
                    card_display_name
                }<br>Rendering took <i>{
                    round(perf_counter() - start_time, 1)
                }</i> seconds"
            )
            return result
        except Exception:
            _logger.exception(f"Failed rendering {card_display_name}")
            return False

    def cancel(self) -> None:
        if self.template_instance:
            self.template_instance.cancel()
        if (task := self.render_task) and not task.done():
            task.get_loop().call_soon_threadsafe(task.cancel)
        if (waiting := self._waiting) and not waiting.done():
            try_threadsafe_set_result(waiting, False)

    async def pause(
        self, message: str | None = None, show_photoshop: bool = True
    ) -> bool:
        if self.do_not_pause:
            return True

        if waiting := self._waiting:
            await waiting

        self._waiting = get_running_loop().create_future()
        if show_photoshop and self.template_instance:
            self.template_instance.app.bringToFront()
        self._paused.trigger({"message": message})

        return await self._waiting

    def pause_sync(
        self, message: str | None = None, show_photoshop: bool = True
    ) -> bool:
        return async_to_sync(self.pause(message, show_photoshop))

    def resume(self) -> None:
        if (waiting := self._waiting) and not waiting.done():
            try_threadsafe_set_result(waiting, True)


def prepare_render_operations(
    template_choices: RenderableTemplate | Mapping[LayoutCategory, RenderableTemplate],
    template_library: TemplateLibrary,
    assets: Iterable[CardDetails | tuple[CardDetails, ScryfallCard]],
    file_dialog: FileDialogModel,
    message_dialog: MessageDialogContentModel,
) -> list[RenderOperation]:
    if not template_choices:
        _logger.warning(
            "No template choices were provided, so no cards can be rendered. Please select some installed templates in the <i>Batch mode</i> in order to render cards with that feature."
        )
        return []

    layouts: list[NormalLayout] = []
    layout_template_class_mapping: dict[
        NormalLayout, tuple[str, type[BaseTemplate], RenderableTemplate]
    ] = {}

    for asset in assets:
        if isinstance(asset, tuple):
            card, scryfall_override = asset
        else:
            card = asset
            scryfall_override = None

        if not (
            layout := assign_layout(
                card,
                scryfall_override=scryfall_override,
            )
        ):
            # assign_layout reports its own errors
            continue

        template_to_use: RenderableTemplate | None = None

        if template_name := card["kwargs"].get("tmpl"):
            if (
                builtin_template := template_library.built_in_templates_by_name.get(
                    template_name, None
                )
            ) and layout.category in builtin_template.layout_categories:
                template_to_use = builtin_template
            if template_to_use is None:
                for templates in template_library.plugin_templates_by_name.values():
                    if (
                        plugin_template := templates.get(template_name, None)
                    ) and layout.category in plugin_template.layout_categories:
                        template_to_use = plugin_template
                        break

        if template_to_use is None:
            if isinstance(template_choices, Mapping):
                if not (template_to_use := template_choices.get(layout.category, None)):
                    _logger.error(
                        f"Skipping image <i>{
                            card['file'].name
                        }</i> because no template was specified for layout <i>{
                            layout.category
                        }</i>."
                    )
                    continue
            else:
                template_to_use = template_choices

        if not (
            class_name_and_file := template_to_use.get_class_name_and_file_for_layout(
                layout.type
            )
        ):
            _logger.error(
                f"Failed to find a template class name from template <i>{
                    template_to_use.name
                }</i> for layout <i>{layout.type}</i>."
            )
            continue

        class_name, file_path = class_name_and_file

        if not file_path.is_file():
            _logger.error(
                f"The PSD file <i>{file_path}</i> for template <i>{
                    template_to_use.name
                }</i> is not available. This might be becuase you haven't downloaded it using the Template updater."
            )
            continue

        # Store PSD path to layout
        layout.template_file = file_path

        try:
            template_class = get_template_class(
                class_name, template_to_use.plugin, ENV.FORCE_RELOAD
            )
        except Exception:
            _logger.exception(
                f"Failed to load class <i>{class_name}</i> for template <i>{template_to_use.name}</i>"
            )
            continue

        if not issubclass(template_class, BaseTemplate):
            _logger.error(
                f"Class <i>{class_name}</i> of template <i>{
                    template_to_use.name
                }</i> is not a subclass of BaseTemplate."
            )
            continue

        layouts.append(layout)
        layout_template_class_mapping[layout] = (
            class_name,
            template_class,
            template_to_use,
        )

    layouts = join_dual_card_layouts(layouts)

    render_operations: list[RenderOperation] = []

    for layout in layouts:
        class_name, template_class, template_to_use = layout_template_class_mapping[
            layout
        ]

        if not (conf := template_to_use.get_config(class_name)):
            _logger.error(
                f"Failed to get config for class <i>{class_name}</i> of template <i>{
                    template_to_use.name
                }</i>."
            )
            continue

        render_operations.append(
            RenderOperation(
                template_class,
                layout,
                conf,
                file_dialog=file_dialog,
                message_dialog=message_dialog,
            )
        )

    return render_operations
