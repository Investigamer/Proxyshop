from asyncio import Future, get_running_loop
from collections.abc import Iterable
from enum import IntEnum
from os import PathLike
from pathlib import Path

from PySide6.QtCore import Property, QObject, Qt, QUrl, Signal, Slot

from src._state import PATH
from src.gui.qml.models.base_dialog_model import BaseDialogModel
from src.utils.asynchronic import try_threadsafe_set_result


class FileMode(IntEnum):
    OpenFile = 0
    OpenFiles = 1
    SaveFile = 2


class FileDialogModel(BaseDialogModel):
    ALL_FILTER = "All (*)"
    PSD_FILTER = "PSD (*.psd)"
    IMAGES_FILTER = "Images (*.png *.jpg *.jpeg *.jxl *.avif *.webp)"
    IMAGES_AND_DATA_FILTER = (
        "Images and data (*.png *.jpg *.jpeg *.jxl *.avif *.webp *.json *.yaml *.yml)"
    )

    def __init__(
        self, parent: QObject | None = None, *, objectName: str | None = None
    ) -> None:
        super().__init__(parent, objectName=objectName)
        self._response_future: Future[list[QUrl]] | None = None
        self._current_folder: QUrl = QUrl.fromLocalFile(str(PATH.CWD))
        self._file_mode = FileMode.OpenFile
        self._name_filters = []
        self._dialog_id = "default"

    # region Properties

    _current_folder_changed = Signal()

    @Property(QUrl, notify=_current_folder_changed)
    def current_folder(self) -> QUrl:  # pyright: ignore[reportRedeclaration]
        return self._current_folder

    @current_folder.setter
    def current_folder(self, value: QUrl) -> None:
        if value != self._current_folder:
            self._current_folder = value
            self._current_folder_changed.emit()

    _file_mode_changed = Signal()

    @Property(int, notify=_file_mode_changed)
    def file_mode(self) -> FileMode:  # pyright: ignore[reportRedeclaration]
        return self._file_mode

    @file_mode.setter
    def file_mode(self, value: FileMode) -> None:
        if value != self._file_mode:
            self._file_mode = value
            self._file_mode_changed.emit()

    _name_filters_changed = Signal()

    @Property(list, notify=_name_filters_changed)
    def name_filters(self) -> list[str]:  # pyright: ignore[reportRedeclaration]
        return self._name_filters

    @name_filters.setter
    def name_filters(self, value: list[str]) -> None:
        if value != self._name_filters:
            self._name_filters = value
            self._name_filters_changed.emit()

    _dialog_id_changed = Signal()

    @Property(str, notify=_dialog_id_changed)
    def dialog_id(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._dialog_id

    @dialog_id.setter
    def dialog_id(self, value: str) -> None:
        if value != self._dialog_id:
            self._dialog_id = value
            self._dialog_id_changed.emit()

    # endregion Properties

    # region Events

    @Slot("QVariantList")
    def on_accepted(self, files: list[QUrl]) -> None:
        if self._response_future:
            try_threadsafe_set_result(self._response_future, files)

    @Slot()
    def on_rejected(self) -> None:
        if self._response_future:
            arg: list[QUrl] = []
            try_threadsafe_set_result(self._response_future, arg)

    # endregion Events

    _select_files_called = Signal(name="selectFiles")

    async def select_files(
        self,
        title: str = "",
        initial_dir: str | PathLike[str] = PATH.CWD,
        file_mode: FileMode = FileMode.OpenFiles,
        filters: Iterable[str] = (),
        modality: Qt.WindowModality = Qt.WindowModality.WindowModal,
        dialog_id: str = "default",
    ) -> list[QUrl]:
        if self._response_future:
            await self._response_future

        self.title = title  # pyright: ignore[reportAttributeAccessIssue]
        self.current_folder = QUrl.fromLocalFile(initial_dir)  # pyright: ignore[reportAttributeAccessIssue]
        self.file_mode = file_mode  # pyright: ignore[reportAttributeAccessIssue]
        self.name_filters = list(filters)  # pyright: ignore[reportAttributeAccessIssue]
        self.modality = modality  # pyright: ignore[reportAttributeAccessIssue]
        self.dialog_id = dialog_id  # pyright: ignore[reportAttributeAccessIssue]

        loop = get_running_loop()
        self._response_future = loop.create_future()
        self._select_files_called.emit()
        return await self._response_future

    async def select_images(
        self,
        title: str = "Select images",
        initial_dir: str | PathLike[str] = PATH.CWD,
        filters: Iterable[str] = (IMAGES_FILTER, ALL_FILTER),
        dialog_id: str = "default",
    ) -> list[Path]:
        return [
            Path(path.toLocalFile())
            for path in await self.select_files(
                title=title,
                initial_dir=initial_dir,
                file_mode=FileMode.OpenFiles,
                filters=filters,
                dialog_id=dialog_id,
            )
        ]
