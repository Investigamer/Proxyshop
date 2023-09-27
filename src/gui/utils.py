"""
GUI UTILITIES
"""
# Standard Library Imports
import os
import random

# Third Party Imports
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.compat import string_types
from kivy.factory import Factory
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import (
    TabbedPanelException,
    TabbedPanelContent,
    TabbedPanelHeader,
    TabbedPanelStrip,
    TabbedPanel,
    StripLayout
)
from kivy.utils import get_color_from_hex

# Local Imports
from src.core import card_types

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
            except OSError:
                return default


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
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    """
    BLANK METHODS - Overwritten by Extend Class, e.g. Button
    """

    def dispatch(self, action):
        return

    @staticmethod
    def collide_point(point: float):
        if point:
            return True
        return False

    @staticmethod
    def to_widget(point: list):
        return point

    @staticmethod
    def get_root_window():
        return App.root_window

    @staticmethod
    def register_event_type(event: str):
        return


"""
BUTTONS
"""


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
            self.org_color = self.background_color
            if len(self.options) > 0:
                self.org_text = self.text
                self.text = random.choice(self.options)
            self.background_color = get_color_from_hex(self.hover_color)

    def on_leave(self):
        """
        When leave
        """
        if self.org_color:
            self.background_color = self.org_color
            if len(self.options) > 0:
                self.text = self.org_text


class ButtonImage(ButtonBehavior, Image):
    pass


"""
INPUTS
"""


class InputItem(TextInput):
    """Track hint text in perpetuity, add QOL key binds."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicked = False
        self.original = self.text

    def _on_focus(self, instance, value, *args):
        """Preserve hint text."""
        if not self.clicked:
            self.clicked = True
            self.original = self.text
        super()._on_focus(instance, value, *args)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Enable tab to next or previous input and F5 to reset."""
        if keycode[1] == 'tab':
            # Deal with tabbing between inputs
            if 'shift' in modifiers:
                nxt = self.get_focus_previous()
            else:
                nxt = self.get_focus_next()
            if nxt:
                self.focus = False
                nxt.focus = True
            return True
        if keycode[0] == 286:
            # F5 to reset text to hint text
            self.clicked = False
            self.text = self.original
        super().keyboard_on_key_down(window, keycode, text, modifiers)


class NoEnterInputItem(InputItem):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Disable next line."""
        if keycode[0] == 13:  # deal with cycle
            return False
        super().keyboard_on_key_down(window, keycode, text, modifiers)


class ValidatedInput(InputItem):
    """Limit text input based on numeric, length, and whitelisted terms."""
    def __init__(self, **kwargs):
        self._max_len = int(kwargs.pop('max_len', 0))
        self._whitelist = kwargs.pop('whitelist', [])
        self._numeric = bool(kwargs.pop('numeric', False))
        self._numeric_range = kwargs.pop('numeric_range', [0, 0])
        super().__init__(**kwargs)

    def insert_text(self, substring, from_undo=False) -> None:
        """
        3 character max, numeric with a small whitelist
        """
        # Character length requirement
        if self._max_len != 0 and len(self.text) > (self._max_len - 1):
            return

        # Numeric value or whitelisted value requirement
        if self._numeric and not (substring.isnumeric() or substring in self._whitelist):
            return

        # Numeric value in accepted range requirement
        if self._numeric and not (self._numeric_range[1] == 0 or (
            self._numeric_range[0] <= int(self.text + str(substring)) <= self._numeric_range[1]
        )):
            return

        # Value is validated
        return super().insert_text(substring, from_undo=from_undo)


class FourNumInput(ValidatedInput):
    """Utility definition, 4 numeric characters with whitelisted operators."""
    def __init__(self, **kwargs):
        super().__init__(max_len=4, numeric=True, whitelist=["*", "X", "Y", "+", "-"], **kwargs)


class ThreeNumInput(ValidatedInput):
    """Utility definition, 3 numeric characters with whitelisted operators."""
    def __init__(self, **kwargs):
        super().__init__(max_len=3, numeric=True, whitelist=["*", "X", "Y", "+", "-"], **kwargs)


class FourCharInput(ValidatedInput):
    """Utility definition, 4 of any kind of characters."""
    def __init__(self, **kwargs):
        super().__init__(max_len=4, **kwargs)


class Range100NumInput(ValidatedInput):
    """Utility definition, number between 1 and 100."""
    def __init__(self, **kwargs):
        super().__init__(numeric=True, numeric_range=[1, 100], **kwargs)


"""
TABBED LAYOUTS
"""


class DynamicTabHeader(TabbedPanelHeader):
    """
    Replacement for 'TabbedPanelHeader'.
    """


class DynamicTabItem(DynamicTabHeader, TabbedPanelHeader):
    """
    Replacement for 'Tabbed Panel Item'.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, 1)
        self.font_size = sp(16)
        self.bind(texture_size=self.resize_width)

    def resize_width(self, _, texture_size):
        self.width = texture_size[0] + dp(20)


class DynamicTabPanel(TabbedPanel):
    """
    Replacement for 'TabbedPanel'.
    """

    # Overwrite the default 'TabbedPanelHeader'
    default_tab_cls = ObjectProperty(DynamicTabHeader)

    def set_def_tab(self, new_tab):
        if not issubclass(new_tab.__class__, DynamicTabHeader):
            raise TabbedPanelException('`default_tab_class` should be'
                                       'subclassed from `DynamicTabHeader`')
        if self._default_tab == new_tab:
            return
        oltab = self._default_tab
        self._default_tab = new_tab
        self.remove_widget(oltab)
        self._original_tab = None
        self.switch_to(new_tab)
        new_tab.state = 'down'

    def __init__(self, **kwargs):
        # these variables need to be initialized before the kv lang is
        # processed set up the base layout for the tabbed panel
        self._childrens = []
        self._tab_layout = StripLayout(rows=1)
        self.rows = 1
        self._tab_strip = TabbedPanelStrip(
            tabbed_panel=self,
            rows=1, size_hint=(None, None),
            height=self.tab_height, width=self.tab_width)

        self._partial_update_scrollview = None
        self.content = TabbedPanelContent()
        self._current_tab = self._original_tab = self._default_tab = DynamicTabHeader()

        super(TabbedPanel, self).__init__(**kwargs)

        self.fbind('size', self._reposition_tabs)
        if not self.do_default_tab:
            Clock.schedule_once(self._switch_to_first_tab)
            return
        self._setup_default_tab()
        self.switch_to(self.default_tab)

    def add_widget(self, widget, *args, **kwargs):
        content = self.content
        if content is None:
            return
        parent = widget.parent
        if parent:
            parent.remove_widget(widget)
        if widget in (content, self._tab_layout):
            super(TabbedPanel, self).add_widget(widget, *args, **kwargs)
        elif isinstance(widget, DynamicTabHeader):
            self_tabs = self._tab_strip
            self_tabs.add_widget(widget, *args, **kwargs)
            widget.group = '__tab%r__' % self_tabs.uid
            self.on_tab_width()
        else:
            widget.pos_hint = {'x': 0, 'top': 1}
            self._childrens.append(widget)
            content.disabled = self.current_tab.disabled
            content.add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget, *args, **kwargs):
        content = self.content
        if content is None:
            return
        if widget in (content, self._tab_layout):
            super(TabbedPanel, self).remove_widget(widget, *args, **kwargs)
        elif isinstance(widget, DynamicTabHeader):
            if not (self.do_default_tab and widget is self._default_tab):
                self_tabs = self._tab_strip
                self_tabs.width -= widget.width
                self_tabs.remove_widget(widget)
                if widget.state == 'down' and self.do_default_tab:
                    self._default_tab.on_release()
                self._reposition_tabs()
            else:
                Logger.info('DynamicTabPanel: default tab! can\'t be removed.\n' +
                            'Change `default_tab` to a different tab.')
        else:
            if widget in self._childrens:
                self._childrens.remove(widget)
            if widget in content.children:
                content.remove_widget(widget, *args, **kwargs)

    def _setup_default_tab(self):
        if self._default_tab in self.tab_list:
            return
        content = self._default_tab.content
        _tabs = self._tab_strip
        cls = self.default_tab_cls

        if isinstance(cls, string_types):
            cls = Factory.get(cls)

        if not issubclass(cls, DynamicTabHeader):
            raise TabbedPanelException('`default_tab_class` should be\
                subclassed from `DynamicTabHeader`')

        # no need to instantiate if class is DynamicTabHeader
        if cls != DynamicTabHeader:
            # noinspection PyCallingNonCallable
            self._current_tab = self._original_tab = self._default_tab = cls()

        default_tab = self.default_tab
        if self._original_tab == self.default_tab:
            default_tab.text = self.default_tab_text

        default_tab.height = self.tab_height
        default_tab.group = '__tab%r__' % _tabs.uid
        default_tab.state = 'down'
        default_tab.width = self.tab_width if self.tab_width else 100
        default_tab.content = content

        tl = self.tab_list
        if default_tab not in tl:
            _tabs.add_widget(default_tab, len(tl))

        if default_tab.content:
            self.clear_widgets()
            self.add_widget(self.default_tab.content)
        else:
            Clock.schedule_once(self._load_default_tab_content)
        self._current_tab = default_tab


"""
RESOURCES
"""


class GUIResources:
    def __init__(self):
        self.template_row: dict[str, dict[str, BoxLayout]] = {k: {} for k in card_types}
        self.template_btn: dict[str, dict[str, ToggleButton]] = {k: {} for k in card_types}
        self.template_btn_cfg: dict[str, dict[str, Button]] = {k: {} for k in card_types}


GUI = GUIResources()
