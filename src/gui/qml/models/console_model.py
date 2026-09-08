from logging import DEBUG, Formatter, LogRecord, getLogger
from re import Match, compile

from pydantic import BaseModel
from PySide6.QtCore import QModelIndex, QObject, Slot
from PySide6.QtGui import QGuiApplication

from src.console import (
    DEFAULT_LOG_DATE_FORMAT,
    DEFAULT_LOG_FORMAT,
    LOG_MESSAGE_COLORS_MAP,
    CustomLogHandler,
    MessageSeverity,
)
from src.gui.qml.models.pydantic_q_list_model import PydanticQListModel

_logger = getLogger()


def _colorize_severity(match: Match[str], color: str) -> str:
    return f'{match.group(1)}<font color="{color}">{match.group(2)}</font>'


class _ColorizingFormatter(Formatter):
    _severity_regex = compile(r"(\[[^\[\]]+\])(\[[^\s\[\]]+\])")

    def format(self, record: LogRecord) -> str:
        return "<br>".join(
            self._severity_regex.sub(
                lambda match: _colorize_severity(
                    match, LOG_MESSAGE_COLORS_MAP[record.levelno]
                ),
                super().format(record),
                1,
            ).splitlines()
        )


class LogEntry(BaseModel):
    message: str
    severity: int
    color: str


class ConsoleModel(PydanticQListModel[LogEntry]):
    item_model = LogEntry

    def __init__(
        self,
        parent: QObject | None = None,
        items: list[LogEntry] | None = None,
        selected_index: int = 0,
    ) -> None:
        log_handler = CustomLogHandler(self._add_to_log, level=DEBUG)
        log_handler.setFormatter(
            _ColorizingFormatter(
                fmt=DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT
            )
        )
        _logger.addHandler(log_handler)
        super().__init__(parent, items, selected_index)

    def _add_to_log(self, message: str, severity: MessageSeverity) -> None:
        row_count = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_count, row_count)
        self.items.append(
            LogEntry(
                message=message,
                severity=severity,
                color=LOG_MESSAGE_COLORS_MAP[severity],
            )
        )
        self.endInsertRows()

    @Slot()
    def copy_log(self) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText("\n".join([item.message for item in self.items]))
