from _ctypes import COMError
from asyncio import Future, Task
from logging import getLogger
from threading import Lock
from typing import TypedDict

from src.render.setup import RenderOperation
from src.utils.asynchronic import run_in_thread
from src.utils.data_structures import find_last_index
from src.utils.event import SubscribableEvent

_logger = getLogger(__name__)


class RenderResult(TypedDict):
    operation: RenderOperation
    result: bool


class QueuedOperation(TypedDict):
    operation: RenderOperation
    index: int


class RenderQueue:
    """Queue for render operations. Runs the render loop in a separate thread."""

    _render_lock = Lock()

    def __init__(self) -> None:
        self._queue: list[RenderOperation] = []
        self._queue_lock = Lock()

        self._active_operation: RenderOperation | None = None
        self._cancel: bool = False

        self.queued: SubscribableEvent[QueuedOperation] = SubscribableEvent()
        self.dequeued: SubscribableEvent[tuple[RenderOperation, int]] = (
            SubscribableEvent()
        )
        self.started: SubscribableEvent[RenderOperation] = SubscribableEvent()
        self.finished: SubscribableEvent[RenderResult] = SubscribableEvent()
        self.cancelled: SubscribableEvent[None] = SubscribableEvent()

    @property
    def active_operation(self) -> RenderOperation | None:
        return self._active_operation

    def enqueue(self, operation: RenderOperation) -> None:
        with self._queue_lock:
            # Order renders so that that the template document has to be switched
            # as few times as possible
            idx = find_last_index(
                self._queue,
                lambda item: (
                    item.layout.template_file == operation.layout.template_file
                ),
            )

            # Active operation has to be checked separately if no match was found otherwise
            if (
                idx == -1
                and self.active_operation
                and operation.layout.template_file
                == self.active_operation.layout.template_file
            ):
                idx = 0

            if idx > -1:
                idx += 1
                self._queue.insert(idx, operation)
            else:
                idx = len(self._queue)
                self._queue.append(operation)
        self.queued.trigger({"operation": operation, "index": idx})
        self.execute_render()

    def dequeue(self, index: int) -> RenderOperation | None:
        try:
            with self._queue_lock:
                self.dequeued.trigger((self._queue.pop(index), index))
        except IndexError:
            return

    def clear(self) -> None:
        with self._queue_lock:
            for idx in reversed(range(len(self._queue))):
                self.dequeued.trigger((self._queue.pop(), idx))

    def cancel(self) -> None:
        if self._active_operation:
            self._cancel = True
            self._active_operation.cancel()
            self.cancelled.trigger(None)

    def execute_render(self) -> None:
        if self._render_lock.locked():
            return

        async def loop_render():
            locked = self._render_lock.acquire(blocking=False)
            if locked:
                try:
                    try:
                        while not self._cancel and (
                            render_operation := self._queue.pop(0)
                        ):
                            self._active_operation = render_operation
                            self.started.trigger(render_operation)
                            result = False
                            try:
                                result = await render_operation.render()
                            finally:
                                try:
                                    # As an optimization the document isn't closed if
                                    # the next render also uses the same document
                                    if (
                                        render_operation.template_instance
                                        and result
                                        and (
                                            len(self._queue) == 0
                                            or self._queue[0].layout.template_file
                                            != render_operation.layout.template_file
                                        )
                                    ):
                                        render_operation.template_instance.docref.close()
                                except COMError as exc:
                                    _logger.debug(
                                        f"Couldn't close the document for {
                                            f'<b>{
                                                render_operation.layout.display_name
                                            } ({render_operation.layout.artist}) [{
                                                render_operation.layout.set
                                            }] {{{
                                                render_operation.layout.collector_number_raw
                                            }}} |{
                                                render_operation.layout.category.value
                                            }| \\{
                                                render_operation.template_class.__name__
                                            }/</b>'
                                        }. It might have already been closed.",
                                        exc_info=exc,
                                    )
                                self.finished.trigger(
                                    {"operation": render_operation, "result": result}
                                )
                    except IndexError:
                        return
                    finally:
                        self._active_operation = None
                        self._cancel = False
                finally:
                    self._render_lock.release()

        run_in_thread(loop_render())


def cancel_with_render[T](
    task: Future[T] | Task[T], queue: RenderQueue, msg: str | None = None
) -> None:
    def on_cancel(_: None = None) -> None:
        task.cancel()

    queue.cancelled.listen_once(on_cancel)
    task.add_done_callback(lambda _: queue.cancelled.remove_listener(on_cancel))
