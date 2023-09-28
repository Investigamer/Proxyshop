"""
PROXYSHOP GUI LAUNCHER
"""
# Standard Library Imports
import sys
import json
import datetime
import win32clipboard
import os.path as osp
from io import BytesIO
from pathlib import Path
from threading import Event
from time import perf_counter
from os import environ, listdir
from typing import Union, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

# Third-party Imports
from PIL import Image as PImage
from photoshop.api._document import Document
from photoshop.api import SaveOptions, DialogModes

# Environment variables
environ["KIVY_LOG_MODE"] = "PYTHON"
environ["HEADLESS"] = "False"
from src.utils.env import ENV_VERSION, ENV_DEV_MODE

# Kivy Imports
from kivy.app import App
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.config import Config
from kivy.factory import Factory
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.resources import resource_add_path
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

# Local Imports
from src.utils.exceptions import get_photoshop_error_message, PS_EXCEPTIONS
from src.utils.files import remove_config_file
from src.gui.creator import CreatorPanels
from src.gui.dev import TestApp
from src.gui.tools import ToolsLayout
from src.gui.utils import HoverBehavior, HoverButton, GUI, DynamicTabPanel, DynamicTabItem
from src.gui.settings import SettingsPopup
from src.constants import con
from src.core import (
    card_types,
    get_templates,
    TemplateDetails,
    get_my_templates,
    get_template_class,
    check_app_version
)
from src.settings import cfg
from src.console import console
from src.utils.download import download_s3
from src.utils.fonts import check_app_fonts
from src.layouts import CardLayout, layout_map, assign_layout, join_dual_card_layouts
from src.utils.strings import (
    get_bullet_points,
    msg_success,
    msg_error,
    msg_warn,
    msg_info
)

# App configuration
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.remove_option('input', 'wm_touch')
Config.remove_option('input', 'wm_pen')
Config.set('kivy', 'log_level', 'error')
Config.write()

# Core vars
templates = get_templates()

"""
BASE CONTAINERS
"""


class ProxyshopPanels(BoxLayout):
    """Container for overall app."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AppTabs(TabbedPanel):
    """Container for both render and creator tabs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tab_layout.padding = '0dp', '0dp', '0dp', '0dp'


class MainTab(TabbedPanelItem):
    """Container for the main render tab."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CreatorTab(TabbedPanelItem):
    """Custom card creator tab."""

    def __init__(self, **kwargs):
        self.text = "Custom Creator"
        super().__init__(**kwargs)
        self.add_widget(CreatorPanels())


class ToolsTab(TabbedPanelItem):
    """Utility tools tab."""

    def __init__(self, **kwargs):
        self.text = "Custom Creator"
        super().__init__(**kwargs)
        self.add_widget(ToolsLayout())


"""
MAIN APP
"""


class ProxyshopApp(App):
    """Proxyshop's main Kivy App class that initiates render procedures and manages user settings."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Data
        self._templates_selected = {}
        self._current_render = None
        self._result = False

    """
    APP PROPERTIES
    """

    @property
    def title(self) -> str:
        """App name displayed at the top of the application window."""
        return f"Proxyshop v{ENV_VERSION}"

    @property
    def icon(self) -> str:
        """Icon displayed in the task bar and the corner of the window."""
        return osp.join(con.path_img, 'proxyshop.png')

    @property
    def cont_padding(self) -> float:
        """Padding for the main app container."""
        return dp(10)

    @property
    def console(self) -> type[console]:
        return console

    """
    RENDERING PROPERTIES
    """

    @property
    def templates_selected(self) -> dict[str, str]:
        """Tracks the templates currently selected by the user."""
        return self._templates_selected

    @templates_selected.setter
    def templates_selected(self, value):
        self._templates_selected = value

    @property
    def current_render(self):
        """Tracks the current template class being used for rendering."""
        return self._current_render

    @current_render.setter
    def current_render(self, value):
        self._current_render = value

    @property
    def docref(self) -> Optional[Document]:
        """Tracks the currently open Photoshop document."""
        if self.current_render and hasattr(self.current_render, 'docref'):
            return self.current_render.docref or None
        return None

    @property
    def cancel_render(self) -> Optional[Event]:
        """Tracks the current render threading Event."""
        if self.current_render and hasattr(self.current_render, 'event'):
            return self.current_render.event or None
        return None

    @property
    def timer(self) -> float:
        """Returns the current system time as a float to use as a timer comparison."""
        return perf_counter()

    """
    DECORATORS
    """

    @staticmethod
    def render_process_wrapper(func) -> Callable:
        """
        Decorator to handle state maintenance before and after an initiated render process.
        @param func: Function being wrapped.
        @return: The result of the wrapped function.
        """
        def wrapper(self, *args):
            while check := con.app.refresh_app():
                if not console.await_choice(
                    thr=Event(),
                    msg=get_photoshop_error_message(check),
                    end="Hit Continue to try again, or Cancel to end the operation.\n"
                ):
                    # Cancel this operation
                    return

            self.reset(disable_buttons=True, clear_console=True)
            result = func(self, *args)
            self.reset(enable_buttons=True, close_document=True)
            return result
        return wrapper

    """
    UTILITIES
    """

    def select_template(self, btn: ToggleButton) -> None:
        """
        Add selected template to the template dict.
        @param btn: Button that was pressed and represents a given template.
        """
        # Set the preview image
        btn.parent.image.parent.parent.set_preview_image(btn.parent.preview)

        # Select the template
        card_type = btn.parent.type
        if btn.state == "down":
            # Select the template, disable all other buttons
            self.templates_selected[card_type] = btn.text
            for name, button in GUI.template_btn[card_type].items():
                if name != btn.text:
                    button.disabled = False
                    button.state = "normal"
            btn.disabled = True

    @staticmethod
    def get_art_files(folder: str = 'art') -> list[str]:
        """
        Grab all supported image files within a given directory.
        @param folder: Path within the working directory containing images.
        @return: List of art files.
        """
        # Folder, file list, supported extensions
        folder = osp.join(con.cwd, folder)
        all_files = listdir(folder)
        ext = (".png", ".jpg", ".tif", ".jpeg", ".jpf")

        # Select all images in folder not prepended with !
        files = [osp.join(folder, f) for f in all_files if f.endswith(ext) and not f.startswith('!')]

        # Check for webp files
        files_webp = [osp.join(folder, f) for f in all_files if f.endswith('.webp') and not f.startswith('!')]

        # Check if Photoshop version supports webp
        if files_webp and not con.app.supports_webp:
            console.update(msg_warn('Skipped WEBP image, WEBP requires Photoshop ^23.2.0'))
        elif files_webp:
            files.extend(files_webp)
        return files

    def reset(
            self,
            reload_config: bool = True,
            reload_constants: bool = True,
            close_document: bool = False,
            enable_buttons: bool = False,
            disable_buttons: bool = False,
            clear_console: bool = False
    ) -> None:
        """
        Reset app config state to default.
        @param reload_config: Reload the configuration object using system and base settings.
        @param reload_constants: Reload the global constants object.
        @param close_document: Close the Photoshop document if still open.
        @param enable_buttons: Enable UI buttons.
        @param disable_buttons: Disable UI buttons.
        @param clear_console: Clear the console of all output.
        """
        # Reset current render thread
        if reload_config:
            cfg.load()
        if reload_constants:
            con.reload()
        if close_document:
            self.close_document()
        if enable_buttons:
            self.enable_buttons()
        if disable_buttons:
            self.disable_buttons()
        if clear_console:
            console.clear()

    @staticmethod
    def select_art() -> Optional[Union[str, list]]:
        """
        Open file select dialog in Photoshop, return the file.
        @return: File object.
        """
        while True:
            try:
                # Open a file select dialog in Photoshop
                if files := con.app.openDialog():
                    return files
                # No files selected
                return
            except PS_EXCEPTIONS as e:
                # Photoshop is busy or unresponsive, try again?
                if not console.await_choice(
                    Event(), get_photoshop_error_message(e),
                    end="Hit Continue to try again, or Cancel to end the operation.\n"
                ):
                    # Cancel the operation
                    return
                # Refresh Photoshop, try again
                con.app.refresh_app()

    def close_document(self) -> None:
        """Close Photoshop document if open."""
        try:
            # Close and set null
            if self.docref and isinstance(self.docref, Document):
                con.app.displayDialogs = DialogModes.DisplayNoDialogs
                self.docref.close(SaveOptions.DoNotSaveChanges)
                con.app.displayDialogs = DialogModes.DisplayErrorDialogs
                self.current_render = None
        except Exception as e:
            # Document wasn't available
            print("Couldn't close corresponding document!")
            console.log_exception(e)
            self.current_render = None

    """
    RENDER METHODS
    """

    @render_process_wrapper
    def render_target(self) -> None:
        """Open the file select dialog in Photoshop and pass the selected arts to render_all."""
        if not (files := self.select_art()):
            return
        return self.render_all(files)

    @render_process_wrapper
    def render_all(self, files: Optional[list[str]] = None) -> None:
        """
        Render cards using all images located in the art folder.
        @param files: List of art file paths, if not provided use valid images in the art folder.
        """
        # Get our templates
        temps = get_my_templates(self.templates_selected)

        # Get art files, make sure there's at least 1
        if not files and len(files := self.get_art_files()) == 0:
            console.update("No art images found!")
            return

        # Run through each file, assigning layout
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            cards = pool.map(assign_layout, files)

        # Join dual card layouts
        cards = join_dual_card_layouts(list(cards))

        # Remove failed strings
        layouts: dict = {}
        for c in cards:
            layouts.setdefault(
                'failed' if isinstance(c, str) else c.card_class, []
            ).append(c)

        # Did any cards fail to find?
        if failed := '\n'.join(layouts.pop('failed', [])):
            # Let the user choose to continue if only some failed
            proceed = False if not layouts else console.error(
                msg=f"\n[b]I can't render the following cards[/b] ...\n{failed}",
                end="\n[b]Should I continue anyway?[/b] ...\n"
            )
            # If all failed alert the user
            if not layouts:
                console.update(f"\n[b]Failed to render all cards[/b] ...\n{failed}")
            # Cancel the operation if required
            if not proceed:
                self.enable_buttons()
                return
        console.update()

        # Render each card type as a different batch
        for card_type, cards in layouts.items():
            # The template we'll use for this type
            template = temps[card_type].copy()
            template['loaded_class'] = get_template_class(template)
            for card in cards:
                # Start render thread
                if not self.start_render(template, card):
                    return
                # Card complete
                self.reset()
            # Render group complete
            self.close_document()

    @render_process_wrapper
    def render_custom(self, template: TemplateDetails, scryfall: dict) -> None:
        """
        Set up custom render job, then execute
        @param template: Dict of template details.
        @param scryfall: Dict of scryfall data.
        """
        # Open file in PS
        if not (file_name := self.select_art()):
            return

        # Instantiate layout object and get template class
        try:
            layout = layout_map[scryfall['layout']](
                scryfall,
                file={
                    'filename': file_name[0],
                    'name': scryfall.get('name', ''),
                    'artist': scryfall.get('artist', ''),
                    'set': scryfall.get('set', ''),
                    'creator': None
                }
            )
            template['loaded_class'] = get_template_class(template)
        except Exception as e:
            console.update(f"Custom card failed!\n", e)
            return

        # Start render
        console.update()
        self.start_render(template, layout)

    @render_process_wrapper
    def test_all(self, deep: bool = False) -> None:
        """
        Test all templates in series.
        @param deep: Tests every card case for each template if enabled.
        """
        # Load temps and test case cards
        with open(osp.join(con.cwd, "src/data/tests.json"), encoding="utf-8") as fp:
            cases = json.load(fp)

        # Loop through each template type
        for card_type, cards in cases.items():
            # Is this a deep test?
            cards = [cards[0]] if not deep else cards
            console.update(msg_success(f"\n---- {card_type.upper()} ----"))
            for template in templates[card_type]:
                # Loop through cards to test
                failures = []
                console.update(f"{template['class_name']} ... ", end="")
                # Is this template installed?
                if not osp.isfile(template['template_path']):
                    console.update(msg_warn(f"SKIPPED (Template not installed)"))
                    continue
                for card in cards:
                    # Assign a layout to this card
                    layout = assign_layout(card[0])
                    if isinstance(layout, str):
                        # Layout or Scryfall Fail
                        console.update(layout)
                        return
                    # Grab the template class and start the render thread
                    layout.filename = osp.join(con.cwd, "src/img/test.png")
                    template['loaded_class'] = get_template_class(template)
                    if not self.start_render(template, layout):
                        failures.append(card[0])
                    # Was the thread cancelled?
                    if self.cancel_render.is_set():
                        return
                    # Card finished
                    self.reset()

                # Template finished
                self.reset(close_document=True)
                console.update(
                    # Did any tests fail?
                    msg_error(f"FAILED ({', '.join(failures)})") if failures
                    else msg_success("SUCCESS")
                )

    @render_process_wrapper
    def test_target(self, card_type: str, template: TemplateDetails) -> None:
        """
        Tests a specific template, always tests every case.
        @param card_type: Type of card, corresponds to template type.
        @param template: Specific template to test.
        """
        # Load test case cards
        with open(osp.join(con.cwd, "src/data/tests.json"), encoding="utf-8") as fp:
            cards = json.load(fp)

        # Is this template installed?
        console.update(msg_success(f"\n---- {template['class_name']} ----"))
        if not osp.isfile(template['template_path']):
            console.update(msg_warn("SKIPPED (Template not installed)"))
            return

        # Render each test case
        for card in cards[card_type]:
            # Get the layout object
            layout = assign_layout(card[0])
            if isinstance(layout, str):
                # Layout or Scryfall Fail
                console.update(layout)
                return

            # Start the render
            layout.filename = osp.join(con.cwd, "src/img/test.png")
            console.update(f"{card[0]} ... ", end="")
            template['loaded_class'] = get_template_class(template)
            console.update(
                msg_success("SUCCESS") if self.start_render(template, layout)
                else msg_error(f"FAILED - {card[1]}")
            )
            # Card finished
            self.reset()
            # Was the thread cancelled?
            if self.cancel_render.is_set():
                return

    def start_render(self, template: TemplateDetails, card: CardLayout) -> bool:
        """
        Execute a render job using a given template and layout object.
        @param template: Template details containing class, plugin, etc.
        @param card: Layout object representing validated scryfall data.
        """
        # Track execution time
        start_time = self.timer
        try:
            # Notify the user
            if not cfg.test_mode:
                console.update(msg_success(f"---- {card.display_name} ----"))

            # Load this template's config
            cfg.load(template=template)

            # Set the PSD location of the template
            card.template_file = template['template_path']

            # Create the template class object
            self.current_render = template['loaded_class'](card)

            # Run a cancellation await in a separate thread using executor
            with ThreadPoolExecutor() as executor:
                executor.submit(console.start_await_cancel, self.current_render.event)

            # Render the card
            result = self.current_render.execute()

            # Report this results
            if result and not cfg.test_mode:
                console.update(f"[i]Time completed: {int(self.timer - start_time)} seconds[/i]\n")
            return result
        except Exception as e:
            # General error outside Template render process
            return console.log_error(
                self.cancel_render or Event(),
                card=card.name,
                template=template['name'],
                msg=msg_error(
                    "Encountered a general error!\n"
                    "Check [b]/logs/error.txt[/b] for details."
                ),
                exception=e
            )

    """
    UI METHODS
    """

    def disable_buttons(self) -> None:
        """Disable buttons while render process running."""
        if cfg.test_mode:
            self.root.ids.test_all.disabled = True
            self.root.ids.test_all_deep.disabled = True
            self.root.ids.test_target.disabled = True
        else:
            self.root.ids.rend_targ_btn.disabled = True
            self.root.ids.rend_all_btn.disabled = True
            self.root.ids.app_settings_btn.disabled = True
        console.ids.update_btn.disabled = True

    def enable_buttons(self) -> None:
        """Enable buttons after render process completes."""
        if cfg.test_mode:
            self.root.ids.test_all.disabled = False
            self.root.ids.test_all_deep.disabled = False
            self.root.ids.test_target.disabled = False
        else:
            self.root.ids.rend_targ_btn.disabled = False
            self.root.ids.rend_all_btn.disabled = False
            self.root.ids.app_settings_btn.disabled = False
        console.ids.update_btn.disabled = False

    """
    GUI METHODS
    """

    def toggle_window_locked(self):
        """Toggle whether to pin the window above all other windows."""
        window: Window = self.root_window
        window.always_on_top = not window.always_on_top

    def screenshot_window(self):
        """Take a screenshot of the Kivy window."""
        window: Window = self.root_window
        screenshot_path = osp.join(con.cwd, "out/screenshots")
        Path(screenshot_path).mkdir(mode=511, parents=True, exist_ok=True)
        img_path = osp.join(screenshot_path, datetime.datetime.now().strftime("%m-%d-%Y, %H%M%S.jpg"))
        img_path = window.screenshot(name=img_path)

        # Copy image to clipboard
        try:
            image = PImage.open(img_path)
            output = BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        except Exception as e:
            console.log_exception(e)

    @staticmethod
    async def open_app_settings() -> None:
        """Open the settings panel for app system and base configs."""
        cfg_panel = SettingsPopup()
        cfg_panel.open()

    def build(self) -> Union[TestApp, ProxyshopPanels]:
        """Build the app for display."""
        layout = TestApp() if cfg.test_mode else ProxyshopPanels()
        layout.add_widget(console)
        return layout

    def on_start(self) -> None:
        """Fired after build is fired. Run a diagnostic check to see what works."""
        console.update(msg_success("--- STATUS ---"))

        # Check if using latest version
        console.update(
            f"Proxyshop Version ... {msg_success('Proxyshop is up to date!')}" if (
                check_app_version()
            ) else f"Proxyshop Version ... {msg_info('New release available!')}"
        )

        # Update symbol library
        try:
            if not ENV_DEV_MODE:
                # Download updated library via Amazon S3 and update global constants
                if not download_s3(osp.join(con.path_data, 'symbols.yaml'), 'symbols.yaml'):
                    raise OSError("Amazon S3 download failed to write data to disk!")
                con.reload()
            console.update(f"Expansion Symbols ... {msg_success('Library updated!')}")
        except Exception as e:
            # Encountered an error while updating
            console.update(f"Expansion Symbols ... {msg_warn('Library update failed!')}")
            console.log_exception(e)

        # Check Photoshop status
        result = con.refresh_photoshop()
        if isinstance(result, OSError):
            # Photoshop test failed
            console.log_exception(result)
            console.update(f"Photoshop ... {msg_error('Cannot make connection with Photoshop!')}\n"
                           f"Check [b]logs/error.txt[/b] for more details.")
            console.update(f"Fonts ... {msg_warn('Cannot test fonts without Photoshop.')}")
            return
        # Photoshop test passed
        console.update(f"Photoshop ... {msg_success('Connection established!')}")

        # Check for missing or outdated fonts
        missing, outdated = check_app_fonts(con.path_fonts)

        # Font test passed
        if not missing and not outdated:
            console.update(f"Fonts ... {msg_success('All essential fonts installed!')}")
            return

        # Missing fonts
        console.update(f"Fonts ... {msg_warn(f'Missing or outdated fonts:')}", end='')
        if missing:
            console.update(
                get_bullet_points([f"{f['name']} — {msg_warn('Not Installed')}" for f in missing.values()]), end="")
        if outdated:
            console.update(
                get_bullet_points([f"{f['name']} — {msg_info('New Version')}" for f in outdated.values()]), end="")
        console.update()

    def on_stop(self):
        """Called when the app is closed."""
        if self.cancel_render and isinstance(self.cancel_render, Event):
            self.cancel_render.set()


"""
TEMPLATE MODULES
"""


class TemplateModule(DynamicTabPanel):
    """Module that loads template tabs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tab_layout.padding = '0dp', '10dp', '0dp', '0dp'
        temp_tabs = []

        # Add a list of buttons inside a scroll box to each tab
        for named_type, layout in card_types.items():

            # Get the list of templates for this type
            temps = templates[layout[0]]
            if len(temps) < 2:
                continue

            # Add tab
            tab = DynamicTabItem(text=named_type)
            tab.content = self.get_template_container(
                layout=layout[0],
                template_list=temps)
            temp_tabs.append(tab)

        # Only add tabs when all are generated
        [self.add_widget(t) for t in temp_tabs]

    @staticmethod
    def get_template_container(
        layout: str, template_list: list[TemplateDetails]
    ) -> 'TemplateTabContainer':
        """
        Return a template container for containing the list view and preview image.
        @param layout: Card layout type to remember.
        @param template_list: List of templates to house.
        @return: TemplateTabContainer object to add to the panel.
        """

        # Create a scroll box and container
        scroll_box = TemplateView()
        container = TemplateTabContainer(layout=layout)

        # Add template list to the scroll box
        scroll_box.add_widget(TemplateList(template_list, preview=container.ids.preview_image))

        # Set the current preview image
        container.set_preview_image(template_list[0]['preview_path'])

        # Add scroll box to the container and return it
        container.ids.template_view_container.add_widget(scroll_box)
        return container


class TemplateTabContainer(BoxLayout):
    """Container that holds template list within each tab."""

    def __init__(self, layout: str, **kwargs):
        super().__init__(**kwargs)
        self._layout = layout

    def toggle_preview_image(self):
        """Toggles the preview image on multi-side templates like Transform."""

        # Define source path, destination path, and toggle options
        dst = ""
        src = str(self.ids.preview_image.source)
        toggle_options = (
            ['[transform_front]', '[transform_back]'],
            ['[mdfc_front]', '[mdfc_back]'],
            ['[pw_tf_front]', '[pw_tf_back]'],
            ['[pw_mdfc_front]', '[pw_mdfc_back]']
        )

        # Check if any toggle options are present
        for option in toggle_options:
            if option[0] in src:
                dst = src.replace(option[0], option[1])
            elif option[1] in src:
                dst = src.replace(option[1], option[0])

        # Toggle image if opposing type exists
        if osp.exists(dst) and dst != src:
            self.ids.preview_image.source = dst

    def set_preview_image(self, path: str) -> None:
        """
        Sets the preview image in this container to a given image, allowing for layout
        specification and NotFound fallback image.
        @param path: Main preview image path for a template.
        """
        layout_specific = path.replace('.jpg', f'[{self._layout}].jpg')
        self.ids.preview_image.source = layout_specific if osp.exists(layout_specific) else (
            path if (osp.exists(path)) else osp.join(con.path_img, 'NotFound.jpg')
        )


class TemplateView(ScrollView):
    """Scrollable viewport for template list."""


class TemplateList(BoxLayout):
    """Builds a list of templates from a certain template type."""

    def __init__(self, temps: list[TemplateDetails], preview: Image, **kwargs):
        super().__init__(**kwargs)
        self.preview = preview
        self.temps = temps
        self.add_template_rows()

    def add_template_rows(self):
        """Add a row for each template in this list."""
        missing = []

        # Create a list of buttons
        for template in self.temps:
            # Is this template available?
            if not osp.exists(template['template_path']):
                missing.append([template, self.preview])
            else:
                self.add_widget(TemplateRow(
                    template=template,
                    preview=self.preview
                ))

        # Add the missing templates
        for m in missing:
            row = TemplateRow(template=m[0], preview=m[1])
            row.disabled = True
            self.add_widget(row)

    def reload_template_rows(self):
        """Remove existing rows and generate new ones using current template data."""
        self.clear_widgets()
        self.add_template_rows()


class TemplateRow(BoxLayout):
    """Row containing template selector and governing buttons."""

    def __init__(self, template: TemplateDetails, preview: Image, **kwargs):
        super().__init__(**kwargs)

        # Set up vars
        self.image = preview
        self.template = template
        self.name = template['name']
        self.type = template['type']
        self.preview = template['preview_path']
        self.ids.toggle_button.text = self.name

        # Normal template default selected
        if self.name == "Normal":
            self.ids.toggle_button.state = "down"
            self.ids.toggle_button.disabled = True

        # Check if config file is present
        self.default_settings_button_check()

        # Add to GUI Dict
        GUI.template_row[self.type][self.name] = self
        GUI.template_btn[self.type][self.name] = self.ids.toggle_button
        GUI.template_btn_cfg[self.type][self.name] = self.ids.settings_button

    def default_settings_button_check(self) -> None:
        """Checks for a template's config file and enables/disables the reset settings button."""
        self.ids.reset_default_button.disabled = True if (
            not osp.isfile(self.template['config_path'].replace('.json', '.ini'))
        ) else False


class TemplateSettingsButton(HoverButton):
    """Opens the settings panel for a given template."""

    async def open_settings(self):
        cfg_panel = SettingsPopup(self.parent.template)
        cfg_panel.open()
        self.parent.default_settings_button_check()


class TemplateResetDefaultButton(HoverButton):
    """Deletes the ini config file for a given template (resets its settings to default)."""

    async def reset_default(self):
        # Remove the config file and alert the user
        if remove_config_file(self.parent.template['config_path'].replace('.json', '.ini')):
            console.update(f"{self.parent.template['name']} has been reset to global settings!")
        self.disabled = True


if __name__ == '__main__':

    # Kivy packaging for PyInstaller
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(osp.join(sys._MEIPASS))

    # Ensure mandatory folders are created
    Path(osp.join(con.cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)
    Path(osp.join(con.cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
    Path(osp.join(con.cwd, "templates")).mkdir(mode=511, parents=True, exist_ok=True)
    Path(osp.join(con.cwd, "src/data/sets")).mkdir(mode=511, parents=True, exist_ok=True)

    # Launch the app
    Factory.register('HoverBehavior', HoverBehavior)
    Builder.load_file(osp.join(con.path_kv, "proxyshop.kv"))
    ProxyshopApp().run()
