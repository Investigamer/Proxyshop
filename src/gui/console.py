"""
CONSOLE MODULES
"""
# Standard Library Imports
import os
import time
import traceback
from threading import Thread, Event, Lock
from typing import Optional, Any
from datetime import datetime as dt

# Third Party Imports
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.logger import Logger

# Local Imports
from src._config import AppConfig
from src._state import AppEnvironment, PATH
from src.gui._state import get_root_app
from src.gui.utils import HoverButton
from src.utils.properties import auto_prop_cached


class GUIConsole(BoxLayout):
    """GUI console handler layout."""
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "console.kv"))
    max_lines = 250
    running = True
    waiting = False
    lock = Lock()

    def __init__(
        self,
        cfg: AppConfig,
        env: AppEnvironment,
        **kwargs
    ):
        # Establish global objects
        super().__init__(**kwargs)
        self.cfg = cfg
        self.env = env

        # Test mode uses larger console
        if not self.env.TEST_MODE:
            self.size_hint = (1, .58)

    @auto_prop_cached
    def main(self) -> Any:
        """ProxyshopGUIApp: Get the running application."""
        return get_root_app()

    """
    * Console GUI Objects
    """

    @auto_prop_cached
    def output(self) -> 'ConsoleOutput':
        """Label where console output is stored."""
        return self.ids.console_output

    @auto_prop_cached
    def continue_btn(self) -> HoverButton:
        """Button that continues to the next render operation."""
        return self.ids.continue_btn

    @auto_prop_cached
    def cancel_btn(self) -> HoverButton:
        """Button that cancels the current render operation."""
        return self.ids.cancel_btn

    @auto_prop_cached
    def update_btn(self) -> HoverButton:
        """Button that launches the updater popup."""
        return self.ids.update_btn

    """
    * Reusable Strings
    """

    @property
    def message_cancel(self) -> str:
        """Boilerplate message for canceling the render process."""
        return "Understood! Canceling render operation.\n"

    @property
    def message_waiting(self) -> str:
        """Boilerplate message for awaiting a user response."""
        return "Manual editing enabled! Click Continue to proceed ..."

    @property
    def message_skipping(self):
        """Boilerplate message for skipping a render process."""
        return "Skipping this card!"

    @property
    def time(self) -> str:
        """Current date and time in human-readable format."""
        return dt.now().strftime("%m/%d/%Y %H:%M")

    @property
    def current_output(self) -> str:
        """str: Text currently contained in the console output label. Remove lines from
        the top when the total linebreaks exceed 250."""
        output = self.output.text
        line_count = output.count('\n') + 1
        if line_count <= self.max_lines:
            return output
        return output.split('\n', line_count-self.max_lines)[-1]

    """
    * Utility Methods
    """

    def enable_buttons(self) -> None:
        """Enable both user signal buttons (Continue and Cancel)."""
        self.continue_btn.disabled = False
        self.cancel_btn.disabled = False

    def disable_buttons(self) -> None:
        """Enable both user signal buttons (Continue and Cancel)."""
        self.continue_btn.disabled = True
        self.cancel_btn.disabled = True

    def log_exception(self, error: Exception, log_file: str = "error.txt") -> None:
        """Log python exception.

        Args:
            error: Exception object to log.
            log_file: Text file to log the exception to.
        """
        # Is this a proper Exception object?
        if not hasattr(error, '__traceback__'):
            return

        # Print the error for dev testing
        Logger.exception(error)

        # Choose the path
        path = PATH.LOGS / log_file

        # Add to log file
        with open(path, "a", encoding="utf-8") as log:
            log.write("============================================================================\n")
            log.write(f"> {self.time}\n")
            log.write("============================================================================\n")
            traceback.print_exception(error, file=log)

    def clear(self) -> None:
        """Clear the console output."""
        self.output.text = ''

    """
    * Console Operations
    """

    def update(
        self,
        msg: str = "",
        exception: Optional[Exception] = None,
        end: str = "\n"
    ) -> None:
        """Add text to console output.

        Args:
            msg: Message to add to the console output, blank if not provided.
            exception: Exception object to log, if provided.
            end: String to append at the end of the message, adds a newline if not provided.
        """
        # Add message to the output label
        self.output.text = f"{self.current_output}{msg}{end}"
        self.ids.viewport.scroll_y = 0
        if exception:
            self.log_exception(exception)

    def log_error(
        self,
        thr: Event,
        card: str,
        template: Optional[str] = None,
        msg: str = 'Encountered a general error!',
        e: Optional[Exception] = None
    ) -> bool:
        """Log failed card and exception if provided, then prompt user to make a decision.

        Args:
            thr: Event object representing the status of the render thread.
            card: Card to log in /logs/failed.txt.
            template: Template to log in /logs/failed.txt.
            msg: Message to add to the console output.
            e: Exception to log in /logs/error.txt.

        Returns:
            True if user wishes to continue, otherwise False.
        """
        with open(PATH.LOGS_FAILED, "a", encoding="utf-8") as log:
            log.write(f"{card}{f' ({template})' if template else ''} [{self.time}]\n")
        return self.error(thr=thr, msg=msg, exception=e)

    def error(
        self,
        thr: Optional[Event] = None,
        msg: str = 'Encountered a general error!',
        exception: Optional[Exception] = None,
        end: str = ' Continue to next card?\n'
    ) -> bool:
        """Display error, wait for user to cancel or continue.

        Args:
            thr: Event object representing the status of the render thread.
            msg: Message to add to the console output.
            exception: Exception to log in /logs/error.txt.
            end: String to append to the end of the message.

        Returns:
            True if user wishes to continue, otherwise False.
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
    * User Prompt Signals
    """

    def await_choice(self, thr: Event, msg: Optional[str] = None, end: str = "\n") -> bool:
        """Prompt the user to either continue or cancel.

        Args:
            thr: Event object representing the status of the render thread.
            msg: Message to prompt the user with, uses boilerplate waiting message if not provided.
            end: String to append to the end of a message, adds a newline if not provided.

        Returns:
            True if user wishes to continue, otherwise False.
        """
        # Clear other await procedures, then begin awaiting a user signal
        self.end_await()
        self.update(msg=msg or self.message_waiting, end=end)
        self.enable_buttons()
        self.start_await()

        # Cancel the current thread or continue based on user signal
        if thr:
            self.cancel_thread(thr) if not self.running else self.start_await_cancel(thr)
        return self.running

    def signal(self, choice: bool) -> None:
        """Signal the user decision to any prompts awaiting a response.

        Args:
            choice: True if continuing, False if canceling.
        """
        # Ensure buttons can't be spammed
        self.disable_buttons()

        # Continue if True, otherwise False
        self.running = choice

        # End await
        self.end_await()

    """
    * Await Cancelling Procedures
    """

    def start_await_cancel(self, thr: Event) -> None:
        """Starts an await_cancel loop in a separate thread.
        @param thr: Event object representing the status of the render thread.
        """
        Thread(target=self.await_cancel, args=(thr,), daemon=True).start()

    def await_cancel(self, thr: Event):
        """Await a signal from the user to cancel the operation.

        Args:
            thr: Event object representing the status of the render thread.
        """
        # Await a signal from the user to cancel the operation
        self.cancel_btn.disabled = False
        self.start_await()

        # Cancel the current thread if running flag set to False
        if not self.running:
            self.cancel_thread(thr)

    """
    * Await Loop Handlers
    """

    def end_await(self) -> None:
        """Clears the console of any procedures awaiting a response."""
        # Set the waiting flag
        self.waiting = False

        # Ensure await is complete before returning
        with self.lock:
            return

    def start_await(self) -> None:
        """Starts an await loop that finishes when waiting is flagged as False."""
        # Set initial running and waiting flags
        self.waiting = True
        self.running = True

        # Await can only start if others have finished
        with self.lock:
            while self.waiting:
                time.sleep(.1)
        self.disable_buttons()

    """
    * Thread Management
    """

    def cancel_thread(self, thr: Event) -> None:
        """Initiate cancellation of a given thread operation.

        Args:
            thr: Thread event to signal the cancellation.
        """
        # Kill the thread and notify
        thr.set()
        self.update(self.message_cancel)


class ConsoleOutput(Label):
    """Label displaying console output."""


class ConsoleControls(BoxLayout):
    """Layout containing console control."""
