"""
* Console Module
"""

from collections.abc import Callable
from enum import IntEnum, StrEnum
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    Formatter,
    Handler,
    LogRecord,
    StreamHandler,
    getLogger,
)

from src import ENV
from src._state import PATH

DEFAULT_LOG_FORMAT = "[%(asctime)s.%(msecs)03d][%(levelname)s] %(message)s"
DETAILED_LOG_FORMAT = (
    "[%(asctime)s.%(msecs)03d][%(levelname)s][%(name)s][%(funcName)s] %(message)s"
)
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_FORMATTER = Formatter(
    fmt=DEFAULT_LOG_FORMAT,
    datefmt=DEFAULT_LOG_DATE_FORMAT,
)
DETAILED_LOG_FORMATTER = Formatter(
    fmt=DETAILED_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT
)

_logger = getLogger()
_logger.setLevel(ENV.LOG_LEVEL)
_default_console_handler = StreamHandler()
_default_console_handler.setLevel(ENV.LOG_LEVEL)
_default_console_handler.setFormatter(DETAILED_LOG_FORMATTER)
_logger.addHandler(_default_console_handler)
_error_log_file_handler = FileHandler(PATH.LOGS_ERROR, "a", encoding="utf-8")
_error_log_file_handler.setLevel(ERROR)
_error_log_file_handler.setFormatter(DETAILED_LOG_FORMATTER)
_logger.addHandler(_error_log_file_handler)

# region Enums


class MessageSeverity(IntEnum):
    DEBUG = DEBUG
    INFO = INFO
    WARNING = WARNING
    ERROR = ERROR
    CRITICAL = CRITICAL


class LogColors(StrEnum):
    """Logging message colors."""

    GRAY = "\x1b[97m"
    BLUE = "\x1b[38;5;39m"
    YELLOW = "\x1b[38;5;226m"
    ORANGE = "\x1b[38;5;202m"
    RED = "\x1b[38;5;196m"
    RED_BOLD = "\x1b[31;1m"
    WHITE = "\x1b[97m"
    RESET = "\x1b[0m"


class LogMessageColor(StrEnum):
    DEBUG = "#d8d8d8"
    SUCCESS = "#59d461"
    INFO = "#6bbcfa"
    WARNING = "#d4c53d"
    ERROR = "#ff3a3a"
    CRITICAL = "#ba86c0"


LOG_MESSAGE_COLORS_MAP: dict[int, LogMessageColor] = {
    MessageSeverity.DEBUG: LogMessageColor.DEBUG,
    MessageSeverity.INFO: LogMessageColor.INFO,
    MessageSeverity.WARNING: LogMessageColor.WARNING,
    MessageSeverity.ERROR: LogMessageColor.ERROR,
    MessageSeverity.CRITICAL: LogMessageColor.CRITICAL,
}

# endregion Enums

# region Handlers


class CustomLogHandler(Handler):
    def __init__(
        self, on_log: Callable[[str, MessageSeverity], None], level: int | str = 0
    ) -> None:
        super().__init__(level)
        self.on_log = on_log

    def emit(self, record: LogRecord) -> None:
        try:
            self.on_log(self.format(record), MessageSeverity(record.levelno))
        except Exception:  # noqa: BLE001
            self.handleError(record)


# endregion Handlers
