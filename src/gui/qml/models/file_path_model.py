from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from src._state import PATH


class FilePathModel(QObject):
    @Property(QUrl)
    def app_root(self) -> QUrl:
        return QUrl.fromLocalFile(PATH.CWD)

    @Property(QUrl)
    def out_directory(self) -> QUrl:
        return QUrl.fromLocalFile(PATH.OUT)

    @Property(QUrl)
    def templates_directory(self) -> QUrl:
        return QUrl.fromLocalFile(PATH.TEMPLATES)

    _plugins_directory_signal = Signal()

    @Property(QUrl, notify=_plugins_directory_signal)
    def plugins_directory(self) -> QUrl:
        return QUrl.fromLocalFile(PATH.PLUGINS)

    _preview_img_fallback_signal = Signal()

    @Property(str, notify=_preview_img_fallback_signal)
    def preview_img_fallback(self) -> str:
        return PATH.SRC_IMG_NOTFOUND.as_uri()

    @Slot(str, result=str)
    def get_preferences_path(self, file_name: str) -> str:
        return (PATH.SRC_DATA_PREFERENCES / file_name).as_uri()
