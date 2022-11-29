"""
GUI Functions
Console Display
"""

import ctypes
import os
import random
import sys
import threading
import time
from traceback import print_tb
from typing import Union
import asynckivy as ak
from datetime import datetime as dt
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.utils import get_color_from_hex
from proxyshop.core import (
    check_for_updates,
    update_template,
    get_templates
)
from proxyshop.settings import cfg
cwd = os.getcwd()


"""
CONSOLE MODULES
"""


class Console (BoxLayout):
    """
    Main console class
    """
    Builder.load_file(os.path.join(cwd, "proxyshop/kivy/console.kv"))
    lines = 1

    def __init__(self, **kwargs):
        super(Console, self).__init__(**kwargs)
        if not cfg.dev_mode: self.size_hint = (1, .58)

    def update(self, msg="", e=None, end="\n"):
        """
        Add text to console
        """
        output = self.ids.console_output

        # Enforce maximum number of lines
        if self.lines == 300:
            text = output.text.split("\n", 1)[1]
        else:
            text = output.text
            self.lines += 1

        # Add message to the output label
        output.text = f"{text}{msg}{end}"
        self.ids.viewport.scroll_y = 0
        if e: self.log_exception(e)

    def log_error(self, msg, card, template=None, e=None):
        """
        Log failed card in tmp
        Then prompt error request
        """
        cur_time = dt.now().strftime("%m/%d/%Y %H:%M")
        if template: log_text = f"{card} ({template}) [{cur_time}]\n"
        else: log_text = f"{card} [{cur_time}]\n"
        with open(os.path.join(cwd, "tmp/failed.txt"), "a", encoding="utf-8") as log:
            log.write(log_text)
        return self.error(msg, e)

    def error(self, msg, e=None, color=True, continue_msg="Continue to next card?"):
        """
        Display error, wait for user to cancel or continue.
        """
        # End waiting to cancel
        self.end_await()

        # Log exception if given
        if e: self.log_exception(e)

        # Are we in dev mode?
        if cfg.dev_mode:
            return False

        # Color message?
        if color: msg = f"[color=#a84747]{msg}[/color]"
        if cfg.skip_failed:
            continue_msg = "Skipping this card!!"

        # Notify user
        self.update(f"[color=#a84747]{msg}[/color]\n{continue_msg}")

        # Enable buttons
        self.ids.continue_btn.disabled = False
        self.ids.cancel_btn.disabled = False

        # Prompt user response
        if cfg.skip_failed: result = True
        else: result = self.ids.console_controls.wait()

        # Cancel or don't
        if not result: self.update("Understood! Canceling render operation.")

        # Disable buttons
        self.ids.continue_btn.disabled = True
        self.ids.cancel_btn.disabled = True
        return result

    def wait(self, msg):
        """
        Wait for user to continue.
        """
        self.end_await()
        self.update(msg)
        self.ids.continue_btn.disabled = False
        self.ids.console_controls.wait()
        self.ids.continue_btn.disabled = True
        return True

    def await_cancel(self, thr):
        """
        Await for user to cancel the operation.
        Auto-returns if the render finishes.
        """
        self.ids.console_controls.success = False
        self.ids.cancel_btn.disabled = False
        self.ids.console_controls.await_cancel()
        if not self.ids.console_controls.success:
            self.ids.cancel_btn.disabled = True
            App.get_running_app().enable_buttons()
            self.kill_thread(thr)
            self.update("Canceling render process!\n")
            sys.exit()
        else: return True

    def end_await(self):
        """
        Ends the await cancel loop
        """
        self.ids.console_controls.success = True
        self.ids.console_controls.running = False
        self.ids.cancel_btn.disabled = True

    @staticmethod
    def log_exception(e: Union[Exception, str], log_file: str = "tmp/error.txt"):
        """
        Log python exception.
        """
        # Is this an Exception object?
        if hasattr(e, '__traceback__'):

            # Evaluate error for developer output
            tb = e.__traceback__
            print_tb(tb)

            # Create readable info locating the error
            while True:
                line = tb.tb_lineno
                location = tb.tb_frame.f_code.co_filename
                if tb.tb_next: tb = tb.tb_next
                else: break

            # Formatting for end user troubleshoot log
            cur_time = dt.now().strftime("%m/%d/%Y %H:%M")
            e = f"[{cur_time}] Line: {line}\n{location}: {e}\n"

        # Log the file
        with open(os.path.join(cwd, log_file), "a", encoding="utf-8") as log:
            log.write(e)

    @staticmethod
    def kill_thread(thr: threading.Thread):
        """
        Kill current render thread.
        @param thr: Thread object to kill
        """
        thread_id = thr.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1: ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)


class ConsoleOutput (Label):
    """
    Label displaying console output
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if cfg.dev_mode: self.text = "Test mode enabled!\n"
        else: self.text = "All systems go! Let's make a proxy.\n"


class ConsoleControls (BoxLayout):
    """
    Console control buttons
    """
    running = True
    waiting = False
    success = True
    choice = False

    def wait(self):
        """
        Force wait until user makes a choice
        """
        self.waiting = True
        while self.waiting:
            time.sleep(.5)
        return self.choice

    def choose(self, confirm=True):
        """
        Define the response, end wait
        """
        if confirm: self.choice = True
        else:
            self.choice = False
            self.running = False
            self.success = False
        self.waiting = False

    def await_cancel(self):
        """
        Await for user cancelling during render process
        """
        self.running = True
        while self.running:
            time.sleep(1)
        return None

    @staticmethod
    async def check_for_updates():
        """
        Open updater Popup.
        """
        # We are Authenticated
        Updater = UpdatePopup()
        Updater.open()
        await ak.run_in_thread(Updater.check_for_updates, daemon=True)
        ak.start(Updater.populate_updates())


"""
SETTINGS PANEL
"""


# TODO: Move settings into a popup panel


"""
Updater
"""


class UpdatePopup(Popup):
    """
    Popup modal for updating templates.
    """
    loading = True
    updates = {}
    categories = {}
    entries = {}

    def check_for_updates(self):
        """
        Runs the check_for_updates core function, then lists needed updates.
        """
        self.updates = check_for_updates()

    async def populate_updates(self):
        """
        Load the list of updates available.
        """
        # Binary tracker for alternating color
        chk = 0

        # Remove loading screen
        if self.loading:
            self.ids.container.remove_widget(self.ids.loading)
            self.ids.container.padding = [0, 0, 0, 0]
            self.loading = False

        # Loop through categories
        for cat, temps in self.updates.items():

            # Loop through updates within this category
            for i, temp in enumerate(temps):
                # Alternate table item color
                if chk == 0: chk, bg_color = 1, "#101010"
                else: chk, bg_color = 0, "#181818"
                self.entries[temp['id']] = UpdateEntry(self, temp, bg_color)
                self.ids.container.add_widget(self.entries[temp['id']])

        # Remove loading text
        if len(self.updates) == 0:
            self.ids.loading_text.text = " [i]No updates found![/i]"
        else: self.ids.loading_text.text = " [i]Updates Available[/i]"


class UpdateEntry(BoxLayout):
    def __init__(self, parent: Popup, temp: dict, bg_color: str, **kwargs):
        if temp['plugin']: plugin = f" [size=18]({temp['plugin']})[/size]"
        else: plugin = ""
        self.bg_color = bg_color
        self.name = f"{temp['type']} - {temp['name']}{plugin}"
        self.status = f"[color=#59d461]{temp['version_new']}[/color]"
        self.data = temp
        self.root = parent
        super().__init__(**kwargs)

    async def download_update(self, download: BoxLayout) -> None:
        self.progress = UpdateProgress(self.data['size'])
        download.clear_widgets()
        download.add_widget(self.progress)
        result = await ak.run_in_thread(
            lambda: update_template(self.data, self.progress.update_progress, self.progress.s3_update_progress
        ), daemon=True)
        await ak.sleep(.5)
        if result:
            self.root.ids.container.remove_widget(self.root.entries[self.data['id']])
        else:
            download.clear_widgets()
            download.add_widget(Label(text="[color=#a84747]FAILED[/color]", markup=True))

    def update_progress(self, tran: int, total: int) -> None:
        progress = int((tran/total)*100)
        self.progress.value = progress


class UpdateProgress(ProgressBar):
    def __init__(self, size, **kwargs):
        super().__init__(**kwargs)
        self.download_size = int(size)
        self.current = 0

    def update_progress(self, tran: int, total: int) -> None:
        self.value = int((tran / total) * 100)

    def s3_update_progress(self, tran: int) -> None:
        self.current += tran
        self.value = int((self.current / self.download_size) * 100)


"""
UTILITY FUNCTIONS
"""


def get_font(name: str, default: str = "Roboto"):
    """
    Instantiate font if exists, otherwise return False
    """
    basename = name[0:-4]
    try:
        LabelBase.register(name=basename, fn_regular=name)
        return basename
    except OSError:
        try:
            LabelBase.register(name=basename, fn_regular=f"fonts/{name}")
            return basename
        except OSError:
            try:
                LabelBase.register(
                    name=basename,
                    fn_regular=f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Microsoft\\Windows\\Fonts\\{name}"
                )
                return basename
            except OSError: return default


"""
UTILITY CLASSES
"""


class HoverBehavior(object):
    """
    Hover behavior.
    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget
    """
    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return  # do proceed if I'm not displayed <=> If I have no parent
        pos = args[1]
        # Next line to_widget allowed to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            # We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside: self.dispatch('on_enter')
        else: self.dispatch('on_leave')


class HoverButton(Button, HoverBehavior):
    """
    Animated button to run new render operation
    """
    options = [
            "Do it!", "Let's GO!", "Ready?",
            "PROXY", "Hurry up!", "GAME ON",
            "Let's DUEL", "Prox it up!", "Go for it!"
    ]
    hover_color = "#a4c5eb"
    org_text = None
    org_color = None

    def __init__(self, **kwargs):
        # Set the default font
        self.font_name = get_font("Beleren Small Caps.ttf")
        super().__init__(**kwargs)

    def on_enter(self):
        """
        When hovering
        """
        if not self.disabled:
            Window.set_system_cursor('hand')
            self.org_text = self.text
            self.org_color = self.background_color
            self.text = random.choice(self.options)
            self.background_color = get_color_from_hex(self.hover_color)

    def on_leave(self):
        """
        When leave
        """
        if self.org_text:
            Window.set_system_cursor('arrow')
            self.text = self.org_text
            self.background_color = self.org_color


"""
DEV MODE
"""


class TestApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = None

    def select_template(self):
        self.selector = TemplateSelector(self)
        self.selector.open()

    def test_target(self, temp):
        self.selector.dismiss()
        threading.Thread(
            target=App.get_running_app().test_target,
            args=(temp[0], temp[1]), daemon=True
        ).start()


class TemplateSelector(Popup):
    def __init__(self, test_app, **kwargs):
        self.test_app = test_app
        self.size_hint = (.8, .8)
        super().__init__(**kwargs)

        # Add template buttons
        for k, v in get_templates().items():
            self.ids.content.add_widget(Label(
                text=k.replace("_", " ").title(),
                size_hint=(1, None),
                font_size=25,
                height=45
            ))
            for key, val in v.items():
                self.ids.content.add_widget(SelectorButton(
                    self.test_app,
                    [k, val],
                    text=key
                ))


class SelectorButton(HoverButton):
    def __init__(self, root, temp, **kwargs):
        super().__init__(**kwargs)
        self.test_app = root
        self.temp = temp
        self.size_hint = (1, None)
        self.font_size = 20
        self.height = 35

    def on_release(self, **kwargs):
        self.test_app.test_target(self.temp)


console = Console()
