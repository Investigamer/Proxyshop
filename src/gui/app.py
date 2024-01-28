"""
* Proxyshop GUI Launcher
"""
# Standard Library Imports
import os
import json
from io import BytesIO
from pathlib import Path
from time import perf_counter
from contextlib import suppress
import win32clipboard as clipboard
from datetime import datetime as dt
from threading import Event, Thread, Lock
from multiprocessing import cpu_count
from typing import Union, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

# Third-party Imports
import requests
from PIL import Image as PImage
from photoshop.api._document import Document
from photoshop.api import SaveOptions, PurgeTarget
from packaging.version import parse

# Kivy Imports
from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
import asynckivy as ak

# Local Imports
from src._state import AppConstants, AppEnvironment, PATH
from src._config import AppConfig
from src.api.hexproof import update_hexproof_cache, get_api_key
from src.enums.mtg import layout_map_types
from src.gui.console import GUIConsole, ConsoleOutput
from src.gui.popup.settings import SettingsPopup
from src._loader import (
    AppPlugin,
    TemplateDetails,
    TemplateSelectedMap,
    TemplateCategoryMap,
    get_template_map_selected,
    AppTemplate)
from src.gui._state import GUI, GlobalAccess
from src.gui.popup.updater import UpdatePopup
from src.gui.tabs.creator import CreatorPanel
from src.gui.tabs.main import TemplateRow, MainPanel
from src.gui.tabs.tools import ToolsPanel
from src.gui.test import TestApp
from src.layouts import (
    CardLayout,
    layout_map,
    assign_layout,
    join_dual_card_layouts)
from src.templates import BaseTemplate
from src.utils.adobe import PhotoshopHandler
from src.utils.properties import auto_prop_cached
from src.utils.exceptions import get_photoshop_error_message, PS_EXCEPTIONS
from src.utils.files import load_data_file
from src.utils.fonts import check_app_fonts
from src.utils.strings import (
    get_bullet_points,
    msg_success,
    msg_error,
    msg_warn,
    msg_info, msg_bold)

"""
* App Tab Containers
"""


class AppContainer(BoxLayout, GlobalAccess):
    """Container for overall app."""

    def on_load(self, *args) -> None:
        """Add tab panel."""
        self.add_widget(AppTabs())


class AppTabs(TabbedPanel, GlobalAccess):
    """Container for both render and creator tabs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tab_layout.padding = (
            '0dp', '0dp', '0dp', '0dp')

    def on_load(self, *args) -> None:
        """Add tabs."""
        self.add_widget(MainTab())
        self.add_widget(CreatorTab())
        self.add_widget(ToolsTab())


class MainTab(TabbedPanelItem, GlobalAccess):
    """Main rendering tab."""

    def on_load(self, *args) -> None:
        """Add content."""
        self.content = MainPanel()


class CreatorTab(TabbedPanelItem, GlobalAccess):
    """Custom card creator tab."""

    def on_load(self, *args) -> None:
        """Add content."""
        self.content = CreatorPanel()


class ToolsTab(TabbedPanelItem, GlobalAccess):
    """Utility tools tab."""

    def on_load(self, *args) -> None:
        """Add content."""
        self.content = ToolsPanel()


"""
* Main GUI Application
"""


class ProxyshopGUIApp(App):
    """Proxyshop's main Kivy App class that initiates render procedures and manages user settings."""
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "app.kv"))

    def __init__(
            self,
            app: PhotoshopHandler,
            con: AppConstants,
            cfg: AppConfig,
            env: AppEnvironment,
            console: GUIConsole,
            plugins: dict[str, AppPlugin],
            templates: list[AppTemplate],
            template_map: dict[str, TemplateCategoryMap],
            templates_default: dict[str, TemplateDetails],
            **kwargs
    ):
        # Call super
        super().__init__(**kwargs)

        # Data
        self._app = app
        self._cfg = cfg
        self._con = con
        self._env = env
        self._console = console
        self._plugins = plugins
        self._templates = templates
        self._template_map = template_map
        self._templates_default = templates_default
        self._templates_selected = {}
        self._current_render = None
        self._result = False

    """
    * Kivy Window Properties
    """

    @property
    def title(self) -> str:
        """str: App name displayed at the top of the application window."""
        return f"Proxyshop v{self.env.VERSION}"

    @property
    def icon(self) -> str:
        """str: Path to icon displayed in the task bar and the corner of the window."""
        return str(PATH.SRC_IMG / 'proxyshop.png')

    @property
    def cont_padding(self) -> float:
        """float: Padding for the main app container."""
        return dp(10)

    """
    * Global Objects
    """

    @property
    def app(self) -> PhotoshopHandler:
        """PhotoshopHandler: Global Photoshop application object."""
        return self._app

    @property
    def cfg(self) -> AppConfig:
        """AppConfig: Global settings object."""
        return self._cfg

    @property
    def con(self) -> AppConstants:
        """AppConstants: Global constants object."""
        return self._con

    @property
    def env(self) -> AppEnvironment:
        """AppEnvironment: Global environment object."""
        return self._env

    @property
    def console(self) -> GUIConsole:
        """GUIConsole: Console output object."""
        return self._console

    """
    * Rendering Properties
    """

    @auto_prop_cached
    def _render_lock(self) -> Lock:
        """Lock: Thread locking mechanism for render operations."""
        return Lock()

    @auto_prop_cached
    def _dropped_files(self) -> list[Path]:
        """list[Path]: Tracks files dragged and dropped onto the app window."""
        return []

    @auto_prop_cached
    def plugins(self) -> dict[str, AppPlugin]:
        """dict[str, AppPlugin]: Tracks all plugins loaded by the app currently."""
        return self._plugins

    @auto_prop_cached
    def templates(self) -> list[AppTemplate]:
        """list[AppTemplate]: List of all templates available to the app."""
        return self._templates

    @auto_prop_cached
    def template_map(self) -> dict[str, TemplateCategoryMap]:
        """dict[str, TemplateCategoryMap]: Dictionary of category mapped templates available to the app."""
        return self._template_map

    @auto_prop_cached
    def templates_selected(self) -> TemplateSelectedMap:
        """TemplateSelectedMap: Tracks the templates currently selected for each type by the user."""
        return self._templates_selected

    @auto_prop_cached
    def templates_default(self) -> TemplateSelectedMap:
        """TemplateSelectedMap: Tracks the default template selections for every template type."""
        return self._templates_default

    @auto_prop_cached
    def current_render(self) -> BaseTemplate:
        """BaseTemplate: Tracks the current template class being used for rendering."""
        return self._current_render

    @property
    def docref(self) -> Optional[Document]:
        """Optional[Document]: Tracks the currently open Photoshop document."""
        if self.current_render and hasattr(self.current_render, 'docref'):
            return self.current_render.docref or None
        return None

    @property
    def thread(self) -> Optional[Event]:
        """Optional[Event]: Tracks the current render threading Event."""
        if self.current_render and hasattr(self.current_render, 'event'):
            return self.current_render.event or None
        return None

    @property
    def timer(self) -> float:
        """float: Returns the current system time as a float to use as a timer comparison."""
        return perf_counter()

    @property
    def thread_cancelled(self) -> bool:
        """bool: Whether the current render thread has been cancelled."""
        thr = self.thread
        return bool(not isinstance(thr, Event) or thr.is_set())

    """
    * UI Properties
    """

    @auto_prop_cached
    def toggle_buttons(self) -> list[Button]:
        """list[Button]: UI buttons to toggle when disable_buttons or enable_buttons is called."""
        return [self.console.update_btn]

    """
    * Wrappers
    """

    @staticmethod
    def render_process_wrapper(func) -> Callable:
        """Decorator to handle state maintenance before and after an initiated render process.

        Args:
            func: Function being wrapped.

        Returns:
            The result of the wrapped function.
        """

        def wrapper(self, *args):
            # Never render on two threads at once
            if self._render_lock.locked():
                return

            # Lock the render thread
            with self._render_lock:
                # Disable buttons / clear console on enter
                self.reset(disable_buttons=True, clear_console=True)

                # Ensure Photoshop is responsive
                while check := self.app.refresh_app():
                    if not self.console.await_choice(
                            thr=Event(),
                            msg=get_photoshop_error_message(check),
                            end="Hit Continue to try again, or Cancel to end the operation.\n"
                    ):
                        # Cancel this operation
                        return

                # Call the function
                result = func(self, *args)

                # Enable buttons / close document on exit
                self.reset(enable_buttons=True, close_document=True)
                return result

        return wrapper

    """
    * Art Loading Utilities
    """

    def get_art_files(self, folder: Path = PATH.ART) -> list[Path]:
        """Grab all supported image files within a given directory.

        Args:
            folder: Path within the working directory containing images.

        Returns:
            List of art file paths.
        """
        # Folder, file list, supported extensions
        all_files = os.listdir(folder)
        ext = (".png", ".jpg", ".tif", ".jpeg", ".jpf")

        # Select all images in folder not prepended with !
        files = [Path(folder, f) for f in all_files if f.endswith(ext) and not f.startswith('!')]

        # Check for webp files
        files_webp = [Path(folder, f) for f in all_files if f.endswith('.webp') and not f.startswith('!')]

        # Check if Photoshop version supports webp
        if files_webp and not self.app.supports_webp:
            self.console.update(msg_warn('Skipped WEBP image, WEBP requires Photoshop ^23.2.0'))
        elif files_webp:
            files.extend(files_webp)
        return sorted(files)

    def select_art(self) -> list[Path]:
        """Open file select dialog in Photoshop, return the paths of any selected files.

        Returns:
            A list of Path objects.
        """
        while True:
            try:
                # Open a file select dialog in Photoshop
                if files := self.app.openDialog():
                    return [Path(f) for f in files]
                return []
            except PS_EXCEPTIONS as e:
                # Photoshop is busy or unresponsive, try again?
                if not self.console.await_choice(
                        Event(), get_photoshop_error_message(e),
                        end="Hit Continue to try again, or Cancel to end the operation.\n"
                ):
                    # Cancel the operation
                    break
                # Refresh Photoshop, try again
                self.app.refresh_app()
        # No files selected
        return []

    """
    * Photoshop Utilities
    """

    def close_document(self) -> None:
        """Close Photoshop document if current document reference exists.."""
        if isinstance(self.docref, Document):
            try:
                self.docref.close(SaveOptions.DoNotSaveChanges)
                self.app.purge(PurgeTarget.AllCaches)
            except Exception as e:
                # Document wasn't available
                print("Couldn't close corresponding document!")
                self.console.log_exception(e)
        self.current_render = None

    """
    * Render Methods
    """

    @render_process_wrapper
    def render_all(self, target: bool = False, files: Optional[list[Path]] = None) -> None:
        """Render cards using all images located in the art folder.

        Args:
            target: Whether to do a targeted render operation.
            files: A lit of files to render instead of target or 'art' folder, if provided.
        """
        # Get our templates
        temps = get_template_map_selected(self.templates_selected, self.templates_default)

        # Get our art files
        if not files:
            files = self.select_art() if target else self.get_art_files()

        # No files provided
        if not files and target:
            return self.console.update(
                "No art images found!" if target else "No art images selected!")

        # Run through each file, assigning layout
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            cards = pool.map(assign_layout, files)

        # Join dual card layouts
        cards = join_dual_card_layouts(list(cards))

        # Remove failed strings
        layouts: dict[str, dict[str, list[CardLayout]]] = {}
        failed: list[str] = []
        for c in cards:

            # Add failed card
            if isinstance(c, str):
                failed.append(c)
                continue

            # Assign card as failure if template isn't installed
            if not temps[c.card_class]['object'].is_installed:
                c = msg_error(
                    msg=c.display_name,
                    reason=f"Template '{temps[c.card_class]['name']}' with type "
                           f"'{c.card_class}' is not installed!")

            # Map card to its template path and layout type
            layouts.setdefault(
                str(temps[c.card_class]['object'].path_psd), {}
            ).setdefault(c.card_class, []).append(c)

        # Did any cards fail to find?
        if failed:

            # If all failed alert the user and cancel
            failure_list = '\n'.join(failed)
            if not layouts:
                return self.console.update(
                    f"\n{msg_bold(msg_error('Failed to render all cards!'))}"
                    f"\n{failure_list}")

            # Let the user choose to continue if only some failed
            if not self.console.error(
                msg=f"\n{msg_error('Unable to render these cards:')}"
                    f"{failure_list}"
            ):
                return

        # Render in batches separated by PSD file
        self.console.update()
        times: list[float] = []
        for (i), (_path, class_map) in enumerate(layouts.items()):
            for layout, cards in class_map.items():

                # Initialize the template's python class module
                loaded_class = temps[layout]['object'].get_template_class(
                    temps[layout]['class_name'])
                if not loaded_class:

                    # Failed to load module or python class
                    self.console.update(msg_error(
                        "Unable to load Python class: "
                        f"{msg_bold(temps[layout]['class_name'])}"))

                    # If more templates in the queue, ask to continue
                    if (i + 1) < len(layouts):

                        # Get a list of cards using this template
                        failed_cards = get_bullet_points(
                            text=[str(c.display_name) for c in cards],
                            char='-')
                        if self.console.error(
                            msg=f"{msg_error('The following cards have been cancelled:')}"
                                f"{failed_cards}"
                        ):
                            # Continue to next template
                            self.console.update()
                            continue

                    # Cancel render process
                    return

                # Load constants and config for this template
                self.cfg.load(temps[layout]['config'])
                self.con.reload()

                # Render each card with this PSD and class
                for c in cards:
                    result = self.start_render(c, temps[layout], loaded_class)
                    if self.thread_cancelled:
                        return
                    if result is not None:
                        times.append(result)

            # Render group complete
            self.close_document()

        # Report the average render time
        self.console.update(msg_success('Renders Completed!'))
        if times:
            avg = round(sum(times) / len(times), 1)
            self.console.update(f'Average time: {avg} seconds')

    @render_process_wrapper
    def render_custom(self, template: TemplateDetails, scryfall: dict) -> None:
        """Set up custom render job, then execute.

        Args:
            template: Dict of template details.
            scryfall: Dict of scryfall data.
        """
        # Open file in PS
        if not (files := self.select_art()):
            return
        art_file = files.pop()

        # Instantiate layout object
        try:
            c = layout_map[scryfall['layout']](
                scryfall=scryfall,
                file={
                    'file': art_file,
                    'name': scryfall.get('name', ''),
                    'artist': scryfall.get('artist', ''),
                    'set': scryfall.get('set', ''),
                    'creator': None
                })
        except Exception as e:
            self.console.update(
                msg='Unable to create a layout object, make sure you input valid information.\n'
                    'Custom card failed!',
                exception=e)
            return

        # Ensure template is installed
        if not template['object'].is_installed:
            # Template is not installed
            self.console.update(
                f"Template '{template['name']}' for card type '{c.card_class}' is not installed!\n"
                'Custom card failed!')
            return

        # Initialize a python class for the template
        loaded_class = template['object'].get_template_class(template['class_name'])
        if not loaded_class:
            # Failed to load module or python class
            self.console.update(
                f"Unable to load Python class: {msg_bold(template['class_name'])}\n"
                'Custom card failed!')
            return

        # Start render
        self.console.update()
        self.start_render(c, template, loaded_class)

    @render_process_wrapper
    def test_all(self, deep: bool = False) -> None:
        """Test all templates in series.

        Args:
            deep: Tests every card case for each template if enabled.
        """
        # Load data file and loop through test case sections
        for card_type, cards in load_data_file(
                (PATH.SRC_DATA_TESTS / 'template_renders').with_suffix('.toml')
        ).items():

            # If not a deep test, only use first entry
            cards = {k: v for k, v in [next(iter(cards.items()))]} if not deep else cards
            self.console.update(msg_success(f'\n— {card_type.upper()}'))

            # Loop through templates to test
            for name, template in self.template_map[layout_map_types[card_type]]['map'][card_type].items():
                self.console.update(f"{template['class_name']} ... ", end="")

                # Is this template installed?
                if not template['object'].is_installed:
                    self.console.update(msg_warn('SKIPPED (Template not installed)'))
                    continue

                # Can this template's class be loaded?
                loaded_class = template['object'].get_template_class(template['class_name'])
                if not loaded_class:
                    self.console.update(msg_error('SKIPPED (Template class failed to load)'))
                    continue

                # Load constants and config for this template
                self.cfg.load(config=template['config'])
                self.con.reload()

                # Loop through cards to test
                failures: list[tuple[str, str, str]] = []
                times: list[float] = []
                for card_name, card_case in cards.items():

                    # Attempt to assign a layout
                    layout = assign_layout(Path(card_name))
                    if isinstance(layout, str):
                        failures.append((card_name, card_case, 'Failed to assign layout'))
                        continue

                    # Grab the template class and start the render thread
                    layout.art_file = PATH.SRC_IMG / 'test.jpg'
                    result = self.start_render(layout, template, loaded_class)
                    if result is None:
                        failures.append((card_name, card_case, 'Failed to render'))
                    else:
                        times.append(result)

                    # Was thread cancelled?
                    if self.thread_cancelled:
                        return

                # Create a summary message
                if failures:
                    fail_log = get_bullet_points([
                        f"{name} ({case}) — {reason}"
                        for name, case, reason in failures])
                    summary = msg_error(f'FAILED{fail_log}')
                else:
                    avg = round(sum(times) / len(times), 1)
                    summary = msg_success(f'{avg}s Avg.')

                # Log summary and continue to next template
                self.console.update(summary)
                self.close_document()

    @render_process_wrapper
    def test_target(self, card_type: str, template: TemplateDetails) -> None:
        """Tests a specific template, always tests every case.

        Args:
            card_type: Type of card, corresponds to template type.
            template: Specific template to test.
        """
        # Load test case cards
        cases = load_data_file((PATH.SRC_DATA_TESTS / 'template_renders').with_suffix('.toml'))
        title = f"\n— {template['class_name']}"
        self.console.update(msg_success(title))

        # Is this template installed?
        if not template['object'].is_installed:
            self.console.update(msg_warn("SKIPPED (Template not installed)"))
            return

        # Can this template's class be loaded?
        loaded_class = template['object'].get_template_class(template['class_name'])
        if not loaded_class:
            self.console.update(msg_error('SKIPPED (Template class failed to load)'))
            return

        # Render each test case
        times: list[float] = []
        for card_name in cases[card_type].keys():
            self.console.update(f"{card_name} ... ", end="")

            # Attempt to assign a layout
            layout = assign_layout(Path(card_name))
            if isinstance(layout, str):
                self.console.update(msg_error('Failed to assign layout'))
                continue

            # Start the render
            layout.art_file = PATH.SRC_IMG / 'test.jpg'
            result = self.start_render(
                card=layout,
                template=template,
                loaded_class=loaded_class,
                reload_config=True,
                reload_constants=True)

            # Was thread cancelled?
            if self.thread_cancelled:
                return
            if result is not None:
                times.append(result)

            # Was render successful?
            self.console.update(
                msg_error('Failed to render')
                if result is None else
                msg_success(f'{result}s'))

        # Report the average render time
        self.console.update(msg_success('\nTests Completed!'))
        if times:
            avg = round(sum(times) / len(times), 1)
            self.console.update(f'Average time: {avg} seconds')

    def start_render(
        self, card: CardLayout,
        template: TemplateDetails,
        loaded_class: type[BaseTemplate],
        reload_config: bool = False,
        reload_constants: bool = False
    ) -> Optional[float]:
        """Execute a render job using a given card layout, template, and template class.

        Args:
            card: Layout object representing an MTG card with validated data.
            template: Template details containing relevant data about the template.
            loaded_class: Python class loaded from the template's module which executes the render operation.
            reload_config: Whether to reload the config object for this render, defaults to False.
            reload_constants: Whether to reload the constants object for this render, defaults to False.

        Returns:
            True if render queue should continue, False if the remaining renders have been cancelled.
        """
        # Notify the user
        if not self.env.TEST_MODE:
            self.console.update(msg_success(f"---- {card.display_name} ----"))

        # Reload config and/or constants
        if reload_config:
            self.cfg.load(config=template['config'])
        if reload_constants:
            self.con.reload()

        # Catch any unexpected render exceptions
        try:

            # Set the PSD location of the template
            card.template_file = template['object'].path_psd

            # Create the template class object
            self.current_render = loaded_class(card)

            # Run a cancellation await in a separate thread using executor
            with ThreadPoolExecutor() as executor:
                executor.submit(self.console.start_await_cancel, self.current_render.event)

            # Render the card
            start_time = self.timer
            result = self.current_render.execute()
            timed = round(self.timer - start_time, 1)

            # Return execution time if successful
            if not self.thread.is_set() and result:
                if not self.env.TEST_MODE:
                    self.console.update(f"[i]Time completed: {timed} seconds[/i]\n")
                return timed

        # General error outside Template render process
        except Exception as error:

            # Reset document
            if self.docref:
                self.current_render.reset()

            # Log the error
            self.console.log_error(
                self.thread or Event(),
                card=card.name,
                template=template['name'],
                msg=msg_error(
                    'Encountered a general error!\n'
                    'Check [b]/logs/error.txt[/b] for details.'),
                e=error)

        # Card failed or thread cancelled
        return

    """
    * UI Utilities
    """

    def select_template(self, btn: ToggleButton) -> None:
        """Add selected template to the template dict.

        Args:
            btn: Button that was pressed and represents a given template.
        """
        # Set the preview image
        btn.parent.set_preview_image()

        # Select the template
        if btn.state == "down":
            obj: TemplateRow = btn.parent
            btn.disabled = True

            # Set the preview image
            obj.set_preview_image()

            # Select the template for its respective types
            for t in obj.types:
                if obj.template_map.get(t):
                    self.templates_selected[t] = obj.template_map[t]

            # Enable all other buttons in this template list
            for name, button in GUI.template_btn[btn.parent.category].items():
                if name != btn.text:
                    button.disabled = False
                    button.state = "normal"

    def reset(
        self,
        reload_config: bool = True,
        reload_constants: bool = True,
        close_document: bool = False,
        enable_buttons: bool = False,
        disable_buttons: bool = False,
        clear_console: bool = False
    ) -> None:
        """Reset app config state to default.

        Args:
            reload_config: Reload the configuration object using system and base settings.
            reload_constants: Reload the global constants object.
            close_document: Close the Photoshop document if still open.
            enable_buttons: Enable UI buttons.
            disable_buttons: Disable UI buttons.
            clear_console: Clear the console of all output.
        """
        # Reset current render thread
        if reload_config:
            self.cfg.load()
        if reload_constants:
            self.con.reload()
        if close_document:
            self.close_document()
        if enable_buttons:
            self.enable_buttons()
        if disable_buttons:
            self.disable_buttons()
        if clear_console:
            self.console.clear()

    def disable_buttons(self) -> None:
        """Disable buttons while render process running."""
        for b in self.toggle_buttons:
            b.disabled = True

    def enable_buttons(self) -> None:
        """Enable buttons after render process completes."""
        for b in self.toggle_buttons:
            b.disabled = False

    """
    GUI METHODS
    """

    def toggle_window_locked(self) -> None:
        """Toggle whether to pin the window above all other windows."""
        window: Window = self.root_window
        window.always_on_top = not window.always_on_top

    def screenshot_window(self) -> None:
        """Take a screenshot of the Kivy window."""
        path = (PATH.OUT / "screenshots" / dt.now().strftime(
            "%m-%d-%Y_")).with_suffix('.jpg')
        path.parent.mkdir(mode=711, parents=True, exist_ok=True)
        img_path = self.root_window.screenshot(name=str(path))

        # Copy image to clipboard
        with suppress(Exception):
            with PImage.open(img_path) as f:
                with BytesIO() as bmp:
                    # Load image data
                    f.convert("RGB").save(bmp, "BMP")
                    data = bmp.getvalue()[14:]

            # Apply data to the clipboard
            clipboard.OpenClipboard(), clipboard.EmptyClipboard()
            clipboard.SetClipboardData(clipboard.CF_DIB, data)
            clipboard.CloseClipboard()

    @staticmethod
    async def open_app_settings() -> None:
        """Open the settings panel for app system and base configs."""
        cfg_panel = SettingsPopup()
        cfg_panel.open()

    def build(self) -> Union[TestApp, AppContainer]:
        """Build the app for display.

        Returns:
            The root app layout.
        """
        self._app_layout = TestApp() if self.env.TEST_MODE else AppContainer()
        Window.bind(
            # Bind drop files event
            on_drop_file=self.queue_dropped_file,
            on_drop_end=self.render_dropped_files)
        self.add_console()
        return self._app_layout

    def queue_dropped_file(self, _window, path: bytes, _x, _y) -> None:
        """Queue a dropped in file for rendering."""
        if self._render_lock.locked():
            return
        self._dropped_files.append(Path(path.decode()))

    def render_dropped_files(self, _window, _x, _y) -> None:
        """Initiate a separate thread to render last dropped in cards."""
        if self._render_lock.locked():
            return
        files = [f for f in self._dropped_files if f.is_file()]
        folders = [f for f in self._dropped_files if f.is_dir()]
        [files.extend(self.get_art_files(f)) for f in folders]
        del self._dropped_files

        # Set up render job in separate thread
        Thread(target=self.render_all, args=(False, files), daemon=True).start()

    def on_start(self) -> None:
        """Fired after build is fired. Run a diagnostic check to see what works."""
        self.console.update(msg_success("--- STATUS ---"))

        # Check if using latest version
        self.console.update(
            f"Proxyshop Version ... {msg_success('Using latest version!')}" if (
                self.check_app_version()
            ) else f"Proxyshop Version ... {msg_info('New release available!')}"
        )

        # Update set data if needed
        check, error = update_hexproof_cache()
        if check:
            self.con.reload()
        message = msg_error(error) if error else msg_success(
            'Update was applied!' if check else 'Using latest data!')
        self.console.update(f"Hexproof API Data ... {message}")

        # Check if API keys are valid
        if not self.env.API_GOOGLE:
            self.env.API_GOOGLE = get_api_key('proxyshop.google.drive')
        if not self.env.API_AMAZON:
            self.env.API_AMAZON = get_api_key('proxyshop.amazon.s3')
        keys_missing = [k for k, v in [
            ('Google Drive', self.env.API_GOOGLE),
            ('Amazon S3', self.env.API_AMAZON)
        ] if not v]
        message = msg_warn(
            f"Keys disabled: {', '.join(keys_missing)}"
        ) if keys_missing else msg_success('Keys retrieved!')
        self.console.update(f"Updater API Keys ... {message}")

        # Check Photoshop status
        result = self.app.refresh_app()
        if isinstance(result, OSError):
            # Photoshop test failed
            self.console.log_exception(result)
            self.console.update(f"Photoshop ... {msg_error('Cannot make connection with Photoshop!')}\n"
                                f"Check [b]logs/error.txt[/b] for more details.")
            self.console.update(f"Fonts ... {msg_warn('Cannot test fonts without Photoshop.')}")
            return
        # Photoshop test passed
        self.console.update(f"Photoshop ... {msg_success('Connection established!')}")

        # Check for missing or outdated fonts
        missing, outdated = check_app_fonts(self.app, [PATH.FONTS])

        # Font test passed
        if not missing and not outdated:
            self.console.update(f"Fonts ... {msg_success('All essential fonts installed!')}")
            return

        # Missing fonts
        self.console.update(f"Fonts ... {msg_warn(f'Missing or outdated fonts:')}", end='')
        if missing:
            self.console.update(
                get_bullet_points([f"{f['name']} — {msg_warn('Not Installed')}" for f in missing.values()]), end="")
        if outdated:
            self.console.update(
                get_bullet_points([f"{f['name']} — {msg_info('New Version')}" for f in outdated.values()]), end="")
        self.console.update()

    def add_console(self) -> None:
        """Adds the console to the app window. Label gets frozen if loaded beforehand."""
        output = ConsoleOutput()
        self._app_layout.add_widget(self.console)
        self.console.ids.output_container.add_widget(output)
        self.console.output = output

    def on_stop(self) -> None:
        """Called when the app is closed."""
        if self.thread and isinstance(self.thread, Event):
            self.thread.set()

    """
    * App Updates
    """

    @staticmethod
    async def check_for_updates():
        """Open updater Popup."""
        Updater = UpdatePopup()
        Updater.open()
        await ak.run_in_thread(Updater.check_for_updates, daemon=True)
        ak.start(Updater.populate_updates())

    def check_app_version(self) -> bool:
        """Check if app is the latest version.

        Returns:
            Return True if up to date, otherwise False.
        """
        with suppress(requests.RequestException, json.JSONDecodeError):
            response = requests.get(
                "https://api.github.com/repos/MrTeferi/Proxyshop/releases/latest",
                timeout=(3, 3))
            latest = response.json().get("tag_name", self.env.VERSION)
            return bool(parse(self.env.VERSION.lstrip('v')) >= parse(latest.lstrip('v')))
        return True
