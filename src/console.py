"""
* CONSOLE MODULE
"""
# Standard Library
import logging
import os
import os.path as osp
import time
import traceback
from threading import Lock, Event, Thread
from datetime import datetime as dt
from functools import cached_property
from typing import Optional, Type

# Local Imports
from src.settings import cfg
from src.constants import con
from src.utils.env import ENV
from src.utils.objects import Singleton
from src.utils.strings import StrEnum


class LogColors (StrEnum):
    """Logging message colors."""
    GRAY = '\x1b[97m'
    BLUE = '\x1b[38;5;39m'
    YELLOW = '\x1b[38;5;226m'
    ORANGE = '\x1b[38;5;202m'
    RED = '\x1b[38;5;196m'
    RED_BOLD = '\x1b[31;1m'
    WHITE = '\x1b[97m'
    RESET = '\x1b[0m'


class LogFormats (StrEnum):
    """Logging message formats."""
    MSG = '%(message)s'
    DATE = '%(asctime)s'
    FILE = '%(filename)s: %(lineno)d'
    DATE_MSG = f'[{DATE}] {MSG}'
    FILE_MSG = f'[{FILE}] {MSG}'
    DATE_FILE_MSG = f'[{DATE}] [{FILE}] {MSG}'


class DateFormats (StrEnum):
    """Logging date formats."""
    MONTH = '%m'
    DAY = '%d'
    YEAR = '%Y'
    HOUR = '%H'
    MINUTE = '%M'
    DATE = f'{MONTH}/{DAY}/{YEAR}'
    TIME = f'{HOUR}:{MINUTE}'
    DATE_TIME = f'{DATE} {TIME}'


class LogFormatter(logging.Formatter):
    """Loger interface formatter class."""

    # Define log formats
    def __init__(self, fmt: str, datefmt: str):
        super().__init__(fmt, datefmt)
        self.FORMATS = {
            logging.DEBUG: LogColors.GRAY + fmt + LogColors.RESET,
            logging.INFO: LogColors.BLUE + fmt + LogColors.RESET,
            logging.WARNING: LogColors.YELLOW + fmt + LogColors.RESET,
            logging.ERROR: LogColors.ORANGE + fmt + LogColors.RESET,
            logging.CRITICAL: LogColors.RED_BOLD + fmt + LogColors.RESET
        }

    def format(self, record: logging.LogRecord):
        """Format a logging record using the appropriate color."""
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, self.datefmt)
        return formatter.format(record)


class TerminalConsole:
    """Wrapper to return the correct global console object."""
    __metaclass__ = Singleton

    # Logger formatting
    _default_log_format = LogFormats.DATE_MSG
    _default_date_format = DateFormats.DATE_TIME

    # Managing threaded operations
    await_lock = Lock()
    running = True
    waiting = False

    def __init__(self, log_format: Optional[str] = None, date_format: Optional[str] = None):
        # Establish logging format
        self._log_format = log_format or self._default_log_format
        self._date_format = date_format or self._default_date_format

    """
    Logger Object Properties
    """

    @cached_property
    def logger(self) -> logging.Logger:
        """Logger interface handling console output."""
        console_logger = logging.getLogger('console')
        console_logger.setLevel(logging.DEBUG)
        console_logger.addHandler(self.log_handler)
        return console_logger

    @cached_property
    def log_formatter(self) -> LogFormatter:
        """Logging Formatter interface handling color formatting in console output."""
        return LogFormatter(self._log_format, self._date_format)

    @cached_property
    def log_handler(self) -> logging.Handler:
        """Logging stream handler."""
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.log_formatter)
        return handler

    @property
    def level(self):
        """Current log level. Supports NOTSET, DEBUG, INFO, WARN, ERROR, CRITICAL."""
        return self.logger.level

    @level.setter
    def level(self, level: int):
        self.logger.setLevel(level)

    """
    Logger Colors
    """

    @cached_property
    def COLORS(self) -> Type[LogColors]:
        return LogColors

    """
    Logger Object Methods
    """

    def debug(self, *args, **kwargs):
        return self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.logger.warning(*args, **kwargs)

    def failed(self, *args, **kwargs):
        return self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.logger.critical(*args, **kwargs)

    def set_level(self, *args):
        return self.logger.setLevel(*args)

    """
    Reusable Strings
    """

    @property
    def message_cancel(self) -> str:
        """
        Boilerplate message for canceling the render process.
        """
        return "Understood! Canceling render operation.\n"

    @property
    def message_waiting(self) -> str:
        """
        Boilerplate message for awaiting a user response.
        """
        return "Manual editing enabled!\nClick continue to proceed..."

    @property
    def message_skipping(self):
        """
        Boilerplate message for skipping a render process!
        """
        return "Skipping this card!"

    @property
    def time(self) -> str:
        """
        Current date and time in human-readable format.
        """
        return dt.now().strftime(DateFormats.DATE_TIME)

    """
    Utility Methods
    """

    def log_exception(self, error: Exception, log_file: str = "error.txt") -> None:
        """
        Log python exception.
        @param error: Exception object to log.
        @param log_file: Text file to log the exception to.
        """
        # Is this a proper Exception object?
        if not hasattr(error, '__traceback__'):
            return

        # Print the error for dev testing
        self.logger.exception(error)

        # Add to log file
        with open(osp.join(con.path_logs, log_file), "a", encoding="utf-8") as log:
            log.write("============================================================================\n")
            log.write(f"> {self.time}\n")
            log.write("============================================================================\n")
            traceback.print_exception(error, file=log)

    @staticmethod
    def clear() -> None:
        """Clear the console output."""
        os.system('cls')

    """
    Console Operations
    """

    def update(
        self,
        msg: str = "",
        exception: Optional[Exception] = None,
        end: str = "\n"
    ) -> None:
        """
        Add text to console output.
        @param msg: Message to add to the console output, blank if not provided.
        @param exception: Exception object to log, if provided.
        @param end: String to append at the end of the message, adds a newline if not provided.
        """
        # Add message to the output label
        print(msg, end=end)
        if exception:
            self.log_exception(exception)

    def log_error(
        self,
        thr: Event,
        card: str,
        template: Optional[str] = None,
        msg: str = "Encountered a general error!",
        exception: Optional[Exception] = None
    ) -> bool:
        """
        Log failed card and exception if provided, then prompt user to make a decision.
        @param thr: Event object representing the status of the render thread.
        @param card: Card to log in /logs/failed.txt.
        @param template: Template to log in /logs/failed.txt.
        @param msg: Message to add to the console output.
        @param exception: Exception to log in /logs/error.txt.
        """
        with open(osp.join(con.path_logs, "failed.txt"), "a", encoding="utf-8") as log:
            log.write(f"{card}{f' ({template})' if template else ''} [{self.time}]\n")
        return self.error(thr=thr, msg=msg, exception=exception)

    def error(
        self,
        thr: Optional[Event] = None,
        msg: str = "Encountered a general error!",
        exception: Optional[Exception] = None,
        end: str = " Continue to next card?\n"
    ) -> bool:
        """
        Display error, wait for user to cancel or continue.
        @param thr: Event object representing the status of the render thread.
        @param msg: Message to add to the console output.
        @param exception: Exception to log in /logs/error.txt.
        @param end: String to append to the end of the message.
        """
        # Stop awaiting any signals
        self.end_await()

        # Log exception if provided
        if exception:
            self.log_exception(exception)

        # Skip the prompts for Dev Mode
        if cfg.test_mode:
            return False

        # Notify the user, then wait for a continue signal if needed
        if cfg.skip_failed:
            self.update(f"{msg}\n{self.message_skipping}")
            return True
        # Previous error already handled
        if thr and thr.is_set():
            return False
        # Wait for user response
        if self.await_choice(thr, msg, end):
            return True
        # Relay the cancellation
        self.update(self.message_cancel)
        return False

    """
    User Prompt Signals
    """

    def await_choice(self, thr: Event, msg: Optional[str] = None, end: str = "\n") -> bool:
        """
        Prompt the user to either continue or cancel.
        @param thr: Event object representing the status of the render thread.
        @param msg: Message to prompt the user with, uses boilerplate waiting message if not provided.
        @param end: String to append to the end of a message, adds a newline if not provided.
        @return: True if continued, False if canceled.
        """
        # Clear other await procedures, then begin awaiting a user signal
        self.end_await()
        self.update(msg=msg or self.message_waiting, end=end)
        response = input("[Y / Enter] Continue — [N] Cancel")

        # Signal the choice
        choice = True if not response or response == 'Y' else False
        self.signal(choice)

        # Cancel the current thread or continue based on user signal
        if thr:
            self.cancel_thread(thr) if not choice else self.start_await_cancel(thr)
        return choice

    def signal(self, choice: bool):
        """
        Signal the user decision to any prompts awaiting a response.
        @param choice: True if continuing, False if canceling.
        """
        # Continue if True, otherwise False
        self.running = choice

        # End await
        self.end_await()

    """
    Await Cancelling Procedures
    """

    def start_await_cancel(self, thr: Event) -> None:
        """
        Starts an await_cancel loop in a separate thread.
        @param thr: Event object representing the status of the render thread.
        """
        Thread(target=self.await_cancel, args=(thr,), daemon=True).start()

    def await_cancel(self, thr: Event):
        """
        Await a signal from the user to cancel the operation.
        @param thr: Event object representing the status of the render thread.
        """
        # Await a signal from the user to cancel the operation
        self.start_await()

        # Cancel the current thread if running flag set to False
        if not self.running:
            self.cancel_thread(thr)

    """
    Await Loop Handlers
    """

    def end_await(self) -> None:
        """Clears the console of any procedures awaiting a response."""
        # Set the waiting flag
        self.waiting = False

        # Ensure await is complete before returning
        with self.await_lock:
            return

    def start_await(self) -> None:
        """Starts an await loop that finishes when waiting is flagged as False."""
        # Set initial running and waiting flags
        self.waiting = True
        self.running = True

        # Await can only start if others have finished
        with self.await_lock:
            while self.waiting:
                time.sleep(.1)

    """
    Thread Management
    """

    def cancel_thread(self, thr: Event) -> None:
        """
        Initiate cancellation of a given thread operation.
        @param thr: Thread event to signal the cancellation.
        """
        # Kill the thread and notify
        self.kill_thread(thr)
        self.update(self.message_cancel)

    @staticmethod
    def kill_thread(thr: Event) -> None:
        """
        Kill a given thread.
        @param thr: Thread event to signal the cancellation.
        """
        thr.set()


# Conditionally import the GUI console
if not ENV.HEADLESS:
    from src.gui.console import GUIConsole as Console
else:
    Console = TerminalConsole

console = Console()
