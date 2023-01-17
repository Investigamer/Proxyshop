import os
import random

from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import get_color_from_hex

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
