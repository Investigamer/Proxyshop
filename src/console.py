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
from typing import Optional

# Local Imports
from src.settings import cfg
from src.constants import con
from src.utils.env import ENV_HEADLESS
from src.utils.objects import Singleton


class TerminalConsole:
    """Wrapper to return the correct global console object."""
    __metaclass__ = Singleton
    await_lock = Lock()
    running = True
    waiting = False

    """
    Logger Object
    """

    @cached_property
    def logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

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
        return dt.now().strftime("%m/%d/%Y %H:%M")

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
if not ENV_HEADLESS:
    from src.gui.console import GUIConsole as Console
else:
    Console = TerminalConsole

console = Console()
