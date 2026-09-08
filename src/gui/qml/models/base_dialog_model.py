from PySide6.QtCore import Property, QObject, Qt, Signal


class BaseDialogModel(QObject):
    def __init__(
        self, /, parent: QObject | None = None, *, objectName: str | None = None
    ) -> None:
        super().__init__(parent, objectName=objectName)
        self._modality: Qt.WindowModality = Qt.WindowModality.WindowModal
        self._title = ""

    _modality_changed = Signal()

    @Property(Qt.WindowModality, notify=_modality_changed)
    def modality(self) -> Qt.WindowModality:  # pyright: ignore[reportRedeclaration]
        return self._modality

    @modality.setter
    def modality(self, value: Qt.WindowModality) -> None:
        if value != self._modality:
            self._modality = value
            self._modality_changed.emit()

    _title_changed = Signal()

    @Property(str, notify=_title_changed)
    def title(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if value != self._title:
            self._title = value
            self._title_changed.emit()
