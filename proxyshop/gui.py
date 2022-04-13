import os
import random
import time
from datetime import datetime as dt
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
cwd = os.getcwd()


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
    border_point= ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        # Next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            # We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')


def get_font(name, default="Roboto"):
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


class Console (BoxLayout):
    def __init__(self, **kwargs):
        kv = Builder.load_file(os.path.join(cwd, "proxyshop/console.kv"))
        super().__init__(**kwargs)
        self.view = None

    def update(self, msg):
        output = self.ids.console_output
        output.text += msg+"\n"
        self.ids.viewport.scroll_y = 0

    def log_error(self, msg, card, template=None):
        time = dt.now().strftime("%m/%d/%Y %H:%M")
        if template: log_text = f"{card} ({template}) [{time}]\n"
        else: log_text = f"{card} [{time}]\n"
        with open(os.path.join(cwd, "tmp/failed.txt"), "a", encoding="utf-8") as log:
            log.write(log_text)
        return self.error(msg)

    def error(self, msg):
        msg = f"[color=#a84747]{msg}[/color]\nContinue to next card?"
        self.update(msg)
        self.ids.continue_btn.disabled = False
        self.ids.cancel_btn.disabled = False
        result = self.ids.console_controls.wait()
        if not result:
            self.update("Understood! Canceling render operation.\n")
        else: self.update("Alrighty, starting next card!\n")
        self.ids.continue_btn.disabled = True
        self.ids.cancel_btn.disabled = True
        return result

    def wait(self, msg):
        self.update(msg)
        self.ids.continue_btn.disabled = False
        self.ids.console_controls.wait()
        self.ids.continue_btn.disabled = True
        return True


class ConsoleOutput (Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ConsoleControls (BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.waiting = False
        self.choice = False

    def wait(self):
        self.waiting = True
        while self.waiting:
            time.sleep(1)
        return self.choice

    def choose(self, confirm=True):
        if confirm: self.choice = True
        else: self.choice = False
        self.waiting = False


class HoverButton(Button, HoverBehavior):
    """
    Animated button to run new render operation
    """
    font_name = get_font("Beleren Small Caps.ttf")
    options = [
            "Do it!", "Let's GO!", "Ready?",
            "PROXY", "Hurry up!", "GAME ON",
            "Let's DUEL", "Prox it up!", "Go for it!"
    ]
    hover_color = "#a4c5eb"
    org_text = None
    org_color = None

    def on_enter(self, *args):
        """
        When hovering
        """
        if not self.disabled:
            Window.set_system_cursor('hand')
            self.org_text = self.text
            self.org_color = self.background_color
            self.text = random.choice(self.options)
            self.background_color = get_color_from_hex(self.hover_color)

    def on_leave(self, *args):
        """
        When leave
        """
        if self.org_text:
            Window.set_system_cursor('arrow')
            self.text = self.org_text
            self.background_color = self.org_color


console_handler = Console()