from asyncio import Future, get_running_loop
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from src.utils.asynchronic import try_threadsafe_set_result


class MessageDialogContentModel(QObject):
    def __init__(
        self,
        /,
        title: str = "",
        text: str = "",
        informative_text: str = "",
        detailed_text: str = "",
        ok_callback: Callable[[], Any] | None = None,
        cancel_callback: Callable[[], Any] | None = None,
        parent: QObject | None = None,
        *,
        objectName: str | None = None,
    ) -> None:
        super().__init__(parent, objectName=objectName)
        self._title = title
        self._text = text
        self._informative_text = informative_text
        self._detailed_text = detailed_text
        self.ok_callback = ok_callback
        self.cancel_callback = cancel_callback

    _title_changed = Signal()

    @Property(str, notify=_title_changed)
    def title(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if value != self._title:
            self._title = value
            self._title_changed.emit()

    _text_changed = Signal()

    @Property(str, notify=_text_changed)
    def text(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value != self._text:
            self._text = value
            self._text_changed.emit()

    _informative_text_changed = Signal()

    @Property(str, notify=_informative_text_changed)
    def informative_text(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._informative_text

    @informative_text.setter
    def informative_text(self, value: str) -> None:
        if value != self._informative_text:
            self._informative_text = value
            self._informative_text_changed.emit()

    _detailed_text_changed = Signal()

    @Property(str, notify=_detailed_text_changed)
    def detailed_text(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._detailed_text

    @detailed_text.setter
    def detailed_text(self, value: str) -> None:
        if value != self._detailed_text:
            self._detailed_text = value
            self._detailed_text_changed.emit()

    @Slot()
    def ok(self) -> None:
        if self.ok_callback:
            self.ok_callback()

    @Slot()
    def cancel(self) -> None:
        if self.cancel_callback:
            self.cancel_callback()

    _dismissed = Signal(name="dismissed")

    def dismiss(self) -> None:
        self._dismissed.emit()

    dialog_requested = Signal(name="dialogRequested")

    def open_message_dialog(
        self,
        title: str = "",
        text: str = "",
        informative_text: str = "",
        detailed_text: str = "",
        ok_callback: Callable[[], Any] | None = None,
        cancel_callback: Callable[[], Any] | None = None,
    ) -> None:
        self.title = title  # pyright: ignore[reportAttributeAccessIssue]
        self.text = text  # pyright: ignore[reportAttributeAccessIssue]
        self.informative_text = informative_text  # pyright: ignore[reportAttributeAccessIssue]
        self.detailed_text = detailed_text  # pyright: ignore[reportAttributeAccessIssue]
        self.ok_callback = ok_callback
        self.cancel_callback = cancel_callback
        self.dialog_requested.emit()

    async def open_message_dialog_async(
        self,
        title: str = "",
        text: str = "",
        informative_text: str = "",
        detailed_text: str = "",
    ) -> bool:
        future: Future[bool] = get_running_loop().create_future()
        self.open_message_dialog(
            title=title,
            text=text,
            informative_text=informative_text,
            detailed_text=detailed_text,
            ok_callback=lambda: try_threadsafe_set_result(future, True),
            cancel_callback=lambda: try_threadsafe_set_result(future, False),
        )
        return await future
