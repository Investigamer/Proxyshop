"""
* Console Module
"""
# Standard Library
import os
import time
from threading import Lock, Event, Thread
from datetime import datetime as dt
from functools import cached_property
from typing import Optional

# Third Party Imports
from omnitils.enums import StrConstant
from omnitils.logs import logger, Logger
from omnitils.metaclass import Singleton

# Local Imports
from src._config import AppConfig
from src._state import AppEnvironment, PATH

"""
* Enums
"""


class LogColors (StrConstant):
    """Logging message colors."""
    GRAY = '\x1b[97m'
    BLUE = '\x1b[38;5;39m'
    YELLOW = '\x1b[38;5;226m'
    ORANGE = '\x1b[38;5;202m'
    RED = '\x1b[38;5;196m'
    RED_BOLD = '\x1b[31;1m'
    WHITE = '\x1b[97m'
    RESET = '\x1b[0m'


class ConsoleMessages(StrConstant):
    error = "#a84747"
    warning = "#d4c53d"
    success = "#59d461"
    info = "#6bbcfa"


"""
* Console Format Utils
"""


def msg_bold(msg: str) -> str:
    """Wraps a console string with a bold tag.

    Args:
        msg: Text to wrap in a bold tag.

    Returns:
        Wrapped message.
    """
    return f"[b]{msg}[/b]"


def msg_italics(msg: str) -> str:
    """Wraps a console string with an italics tag.

    Args:
        msg: Message to wrap in an italics tag.

    Returns:
        Wrapped message.
    """
    return f"[i]{msg}[/i]"


def msg_error(msg: str, reason: Optional[str] = None) -> str:
    """Adds a defined 'error' color tag to Proxyshop console message.

    Args:
        msg: String wrap in color tag.
        reason: Reason for the error to include in the message, if provided.

    Returns:
        Formatted string.
    """
    msg = f'[color={ConsoleMessages.error}]{msg}[/color]'
    return f"{msg_bold(msg)} - {msg_italics(reason)}" if reason else msg


def msg_warn(msg: str, reason: Optional[str] = None) -> str:
    """Adds a defined 'warning' color tag to Proxyshop console message.

    Args:
        msg: String to wrap in color tag.
        reason: Reason for the warning to include in the message, if provided.

    Returns:
        Formatted string.
    """
    msg = f'[color={ConsoleMessages.warning}]{msg}[/color]'
    return f"{msg_bold(msg)} - {msg_italics(reason)}" if reason else msg


def msg_success(msg: str) -> str:
    """Adds a defined 'success' color tag to Proxyshop console message.

    Args:
        msg: String to wrap in color tag.

    Returns:
        Formatted string.
    """
    return f'[color={ConsoleMessages.success}]{msg}[/color]'


def msg_info(msg: str) -> str:
    """Adds defined 'info' color tag to Proxyshop console message.

    Args:
        msg: String to wrap in color tag.

    Returns:
        Formatted string.
    """
    return f'[color={ConsoleMessages.info}]{msg}[/color]'


def get_bullet_points(text: list[str], char: str = '•') -> str:
    """Turns a list of strings into a joined bullet point list string.

    Args:
        text: List of strings.
        char: Character to use as bullet.

    Returns:
        Joined string with bullet points and newlines.
    """
    if not text:
        return ""
    bullet = f"\n{char} "
    return str(bullet + bullet.join(text))


"""
* Base Terminal Class
"""


class TerminalConsole:
    """Wrapper to return the correct global console object."""
    __metaclass__ = Singleton

    # Managing threaded operations
    await_lock = Lock()
    running = True
    waiting = False
    continue_next_line = False

    def __init__(
        self,
        cfg: AppConfig,
        env: AppEnvironment
    ):

        # Establish global objects
        self.cfg: AppConfig = cfg
        self.env: AppEnvironment = env

    """
    Logger Object Properties
    """

    @cached_property
    def logger(self) -> Logger:
        """Logger interface handling console output."""
        return logger

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

    """
    Reusable Strings
    """

    @property
    def message_cancel(self) -> str:
        """Boilerplate message for canceling the render process."""
        return "Understood! Canceling render operation.\n"

    @property
    def message_waiting(self) -> str:
        """Boilerplate message for awaiting a user response."""
        return "Manual editing enabled!\nClick continue to proceed..."

    @property
    def message_skipping(self):
        """Boilerplate message for skipping a render process."""
        return "Skipping this card!"

    @property
    def time(self) -> str:
        """Current date and time in human-readable format."""
        return dt.now().strftime('%m-%d-%Y %H:%M')

    """
    Utility Methods
    """

    def log_exception(self, error: Exception, *_) -> None:
        """Log python exception.

        Args:
            error: Exception object to log.
        """
        self.logger.exception(error)

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

        # Check if line is a continuation
        if self.continue_next_line:
            msg = '[>]' + msg
            self.continue_next_line = False

        # Check if line has alternate ending
        if end.endswith('\n'):
            msg = msg + end[:-1]
        else:
            msg = msg + end + '[>]'
            self.continue_next_line = True
        self.logger.info(msg)
        if exception:
            self.log_exception(exception)

    def log_error(
        self,
        thr: Event,
        card: str,
        template: Optional[str] = None,
        msg: str = "Encountered a general error!",
        e: Optional[Exception] = None
    ) -> bool:
        """
        Log failed card and exception if provided, then prompt user to make a decision.
        @param thr: Event object representing the status of the render thread.
        @param card: Card to log in /logs/failed.txt.
        @param template: Template to log in /logs/failed.txt.
        @param msg: Message to add to the console output.
        @param e: Exception to log in /logs/error.txt.
        """
        with open(PATH.LOGS_FAILED, 'a', encoding='utf-8') as log:
            log.write(f"{card}{f' ({template})' if template else ''} [{self.time}]\n")
        return self.error(thr=thr, msg=msg, exception=e)

    def error(
        self,
        thr: Optional[Event] = None,
        msg: str = 'Encountered a general error!',
        exception: Optional[Exception] = None,
        end: str = '\nShould I continue?\n'
    ) -> bool:
        """Display error, wait for user to cancel or continue.

        Args:
            thr: Event object representing the status of the render thread.
            msg: Message to add to the console output.
            exception: Exception to log in /logs/error.txt.
            end: String to append to the end of the message.
        """
        # Stop awaiting any signals
        self.end_await()

        # Log exception if provided
        if exception:
            self.log_exception(exception)

        # Skip the prompts for Dev Mode
        if self.env.TEST_MODE:
            return False

        # Notify the user, then wait for a continue signal if needed
        if self.cfg.skip_failed:
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
        """Initiate cancellation of a given thread operation.

        Args:
            thr: Thread event to signal the cancellation.
        """
        # Kill the thread and notify
        thr.set()
        self.update(self.message_cancel)
