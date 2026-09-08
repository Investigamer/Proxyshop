from functools import cached_property

from pydantic import BaseModel
from PySide6.QtCore import Property, QModelIndex, QObject, Signal, Slot

from src.gui.qml.models.message_dialog_content_model import MessageDialogContentModel
from src.gui.qml.models.pydantic_q_list_model import PydanticQListModel
from src.render.render_queue import QueuedOperation, RenderQueue, RenderResult
from src.render.setup import PausedEventArgs, RenderOperation


class RenderOperationDetails(BaseModel):
    image_name: str
    image_path: str
    card_name: str
    card_artist: str
    card_set: str
    card_collector_number: str
    layout_name: str
    class_name: str

    @cached_property
    def render_operation(self) -> RenderOperation:
        raise ValueError("Render operation not set")


class RenderOperationsModel(PydanticQListModel[RenderOperationDetails]):
    item_model = RenderOperationDetails

    def __init__(
        self,
        render_queue: RenderQueue,
        render_message_dialog_model: MessageDialogContentModel,
        parent: QObject | None = None,
        items: list[RenderOperationDetails] | None = None,
        selected_index: int = -1,
    ) -> None:
        super().__init__(parent, items, selected_index)

        self._render_queue = render_queue
        self._render_message_dialog_model = render_message_dialog_model
        self._is_rendering: bool = False
        self._active_operation: RenderOperationDetails | None = None

        render_queue.queued.add_listener(self._on_queued)
        render_queue.dequeued.add_listener(self._on_dequeued)
        render_queue.started.add_listener(self._on_started)
        render_queue.finished.add_listener(self._on_finished)

    # region Queue

    def _on_queued(self, queued_operation: QueuedOperation) -> None:
        render_operation = queued_operation["operation"]
        idx = queued_operation["index"]
        render_op_details = RenderOperationDetails(
            image_name=render_operation.layout.art_file.name,
            image_path=str(render_operation.layout.art_file),
            card_name=render_operation.layout.name,
            card_artist=render_operation.layout.artist,
            card_set=render_operation.layout.set,
            card_collector_number=render_operation.layout.collector_number_raw or "",
            layout_name=render_operation.layout.category,
            class_name=render_operation.template_class.__name__,
        )
        render_op_details.render_operation = render_operation
        self.beginInsertRows(QModelIndex(), idx, idx)
        self.items.insert(idx, render_op_details)
        self.endInsertRows()

    def _on_dequeued(self, data: tuple[RenderOperation, int]) -> None:
        index = data[1]
        self.beginRemoveRows(QModelIndex(), index, index)
        self.items.pop(index)
        self.endRemoveRows()

    def _on_started(self, render_operation: RenderOperation) -> None:
        render_operation.paused.add_listener(self._on_render_paused)
        self.beginRemoveRows(QModelIndex(), 0, 0)
        self.active_operation = self.items.pop(0)
        self.endRemoveRows()
        self.is_rendering = True  # pyright: ignore[reportAttributeAccessIssue]

    def _on_finished(self, render_result: RenderResult) -> None:
        render_result["operation"].paused.remove_listener(self._on_render_paused)
        self.is_rendering = False  # pyright: ignore[reportAttributeAccessIssue]
        self.active_operation = None

    @Slot(int)
    def dequeue(self, index: int) -> None:
        self._render_queue.dequeue(index)

    @Slot()
    def clear(self) -> None:
        self._render_queue.clear()

    # endregion Queue

    # region Properties

    _is_rendering_changed = Signal()

    @Property(bool, notify=_is_rendering_changed)
    def is_rendering(self) -> bool:  # pyright: ignore[reportRedeclaration]
        return self._is_rendering

    @is_rendering.setter
    def is_rendering(self, value: bool) -> None:
        if value != self._is_rendering:
            self._is_rendering = value
            self._is_rendering_changed.emit()

    _active_operation_changed = Signal()

    @property
    def active_operation(self) -> RenderOperationDetails | None:
        return self._active_operation

    @active_operation.setter
    def active_operation(self, value: RenderOperationDetails | None) -> None:
        if self._active_operation != value:
            self._active_operation = value
            self._active_operation_changed.emit()

    @Property(str, notify=_active_operation_changed)
    def rendering_image_name(self) -> str:
        if self._active_operation:
            return self._active_operation.image_name
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_image_path(self) -> str:
        if self._active_operation:
            return self._active_operation.image_path
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_card_name(self) -> str:
        if self._active_operation:
            return self._active_operation.card_name
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_card_artist(self) -> str:
        if self._active_operation:
            return self._active_operation.card_artist
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_card_set(self) -> str:
        if self._active_operation:
            return self._active_operation.card_set
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_card_collector_number(self) -> str:
        if self._active_operation:
            return self._active_operation.card_collector_number
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_layout_name(self) -> str:
        if self._active_operation:
            return self._active_operation.layout_name
        return ""

    @Property(str, notify=_active_operation_changed)
    def rendering_class_name(self) -> str:
        if self._active_operation:
            return self._active_operation.class_name
        return ""

    # endregion Properties

    # region Pause dialog

    def _cancel_queue(self) -> None:
        self._render_queue.cancel()

    @Slot()
    def cancel(self) -> None:
        self._render_message_dialog_model.dismiss()
        self._cancel_queue()

    @Slot()
    def resume(self) -> None:
        if op := self._render_queue.active_operation:
            op.resume()
        else:
            self._render_queue.execute_render()

    def _on_render_paused(self, args: PausedEventArgs) -> None:
        self._render_message_dialog_model.open_message_dialog(
            "Rendering paused",
            text=args["message"] or "Rendering paused.",
            informative_text="Press <b>OK</b> to resume rendering or <b>Cancel</b> to discard the current render.",
            ok_callback=self.resume,
            cancel_callback=self._cancel_queue,
        )

    # endregion Pause dialog
