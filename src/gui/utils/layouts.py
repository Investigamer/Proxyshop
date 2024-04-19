"""
* GUI Utility Layouts
"""
# Standard Library Imports
import random

# Third Party Imports
from kivy.metrics import dp, sp
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.compat import string_types
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.tabbedpanel import (
    TabbedPanelException,
    TabbedPanelContent,
    TabbedPanelHeader,
    TabbedPanelStrip,
    TabbedPanel,
    StripLayout)
from kivy.utils import get_color_from_hex

# Local Imports
from src.gui.utils.behaviors import HoverBehavior
from src.gui.utils.fonts import get_font

"""
* Button Layouts
"""


class HoverButton(Button, HoverBehavior):
    """Button which adopts the hover behavior modifier."""
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
        """Fired when mouse enters the hover area."""
        if not self.disabled:
            self.org_color = self.background_color
            if len(self.options) > 0:
                self.org_text = self.text
                self.text = random.choice(self.options)
            self.background_color = get_color_from_hex(self.hover_color)

    def on_leave(self):
        """Fired when mouse leaves the hover area."""
        if self.org_color:
            self.background_color = self.org_color
            if len(self.options) > 0:
                self.text = self.org_text


"""
* Image Layouts
"""


class ButtonImage(ButtonBehavior, Image):
    """Image which adopts the hover behavior modifier."""
    pass


"""
* Tabbed Panel Layouts
"""


class DynamicTabHeader(TabbedPanelHeader):
    """Replacement for 'TabbedPanelHeader'."""


class DynamicTabItem(DynamicTabHeader, TabbedPanelHeader):
    """Replacement for 'Tabbed Panel Item'."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, 1)
        self.font_size = sp(16)
        self.bind(texture_size=self.resize_width)

    def resize_width(self, _, texture_size):
        self.width = texture_size[0] + dp(20)


class DynamicTabPanel(TabbedPanel):
    """Replacement for 'TabbedPanel'."""

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
