"""
KIVY SETTINGS POPUPS
"""
# Standard Library Imports
from functools import cached_property
from os import PathLike
from typing import Union

# Third Party Imports
import kivy.utils as utils
from kivy.properties import ConfigParser
from kivy.uix.colorpicker import ColorPicker
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.settings import (
    Settings,
    SettingOptions,
    SettingSpacer,
    SettingNumeric,
    SettingString,
    SettingColor
)
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

# Local Imports
from src.loader import TemplateDetails
from src.settings import ConfigManager


"""
AESTHETIC CLASSES
"""


class FormattedSettingColor(SettingColor):
    """Create custom SettingColor class to allow Markup in title."""
    def _create_popup(self, instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            title=self.title, content=content, size_hint=(None, 0.9),
            width=popup_width)
        popup.children[0].children[-1].markup = True

        self.colorpicker = colorpicker = ColorPicker(color=utils.get_color_from_hex(self.value))
        colorpicker.bind(on_color=self._validate)

        self.colorpicker = colorpicker
        content.add_widget(colorpicker)
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()


class FormattedSettingString(SettingString):
    """Create custom SettingString class to allow Markup in title."""
    def _create_popup(self, instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            title=self.title, content=content, size_hint=(None, None),
            size=(popup_width, '250dp'))
        popup.children[0].children[-1].markup = True

        # create the textinput used for numeric input
        self.textinput = textinput = TextInput(
            text=self.value, font_size='24sp', multiline=False,
            size_hint_y=None, height='42sp')
        textinput.bind(on_text_validate=self._validate)
        self.textinput = textinput

        # construct the content, widget are used as a spacer
        content.add_widget(Widget())
        content.add_widget(textinput)
        content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()


class FormattedSettingNumeric(SettingNumeric):
    """Create custom SettingNumeric class to allow Markup in title."""
    def _create_popup(self, instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            title=self.title, content=content, size_hint=(None, None),
            size=(popup_width, '250dp'))
        popup.children[0].children[-1].markup = True

        # create the textinput used for numeric input
        self.textinput = textinput = TextInput(
            text=self.value, font_size='24sp', multiline=False,
            size_hint_y=None, height='42sp')
        textinput.bind(on_text_validate=self._validate)
        self.textinput = textinput

        # construct the content, widget are used as a spacer
        content.add_widget(Widget())
        content.add_widget(textinput)
        content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()


class FormattedSettingOptions(SettingOptions):
    """Create custom SettingOptions class to allow Markup in title."""
    def _create_popup(self, instance):
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))
        popup.height = len(self.options) * dp(55) + dp(150)
        popup.children[0].children[-1].markup = True

        # add all the options
        content.add_widget(Widget(size_hint_y=None, height=1))
        uid = str(self.uid)
        for option in self.options:
            state = 'down' if option == self.value else 'normal'
            btn = ToggleButton(text=option, state=state, group=uid)
            btn.bind(on_release=self._set_option)
            content.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        content.add_widget(SettingSpacer())
        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # and open the popup !
        popup.open()


"""
SETTINGS POPUP
"""


class SettingsPopup(ModalView):
    """Popup menu for changing app or template settings."""

    """
    * ConfigParser objects
    """

    @staticmethod
    def get_config(ini_file: Union[str, PathLike]) -> ConfigParser:
        config = ConfigParser(allow_no_value=True)
        config.optionxform = str
        config.read(str(ini_file))
        return config

    """
    * Settings Panel instance
    """

    @cached_property
    def cfg_panel(self) -> Settings:
        """Settings panel to load JSON validated config data into."""
        s = Settings()
        s.bind(on_close=self.dismiss)
        s.register_type('options', FormattedSettingOptions)
        s.register_type('string', FormattedSettingString)
        s.register_type('numeric', FormattedSettingNumeric)
        s.register_type('color', FormattedSettingColor)
        return s

    """
    * Generate Settings Page
    """

    def __init__(self, template: TemplateDetails = None, **kwargs):
        super().__init__(**kwargs)

        # Load and validate ConfigManager
        self.template = template
        self.manager = template['config'] if template else ConfigManager()
        self.manager.validate_configs()
        if template:
            self.manager.validate_template_configs()

        # Is this global or template specific?
        self.load_template_config() if self.manager.has_template_ini else self.load_global_config()
        self.add_widget(self.cfg_panel)

    def load_global_config(self) -> None:
        """Load base and app settings into global config panel."""

        # Add main settings
        self.cfg_panel.add_json_panel(
            title='Main Settings',
            config=self.get_config(self.manager.base_path_ini),
            data=self.manager.base_json)

        # Add system settings
        self.cfg_panel.add_json_panel(
            title='System Settings',
            config=self.get_config(self.manager.app_path_ini),
            data=self.manager.app_json)

    def load_template_config(self) -> None:
        """Load a template-specific settings into config panel."""

        # Add custom template settings if provided
        config = self.get_config(self.manager.template_path_ini)
        if self.manager.template_path_schema:
            self.cfg_panel.add_json_panel(
                title=f"{self.template['name']} Template",
                config=config, data=self.manager.template_json)

        # Add main settings
        self.cfg_panel.add_json_panel(
            title='Main Settings',
            config=config, data=self.manager.base_json)
