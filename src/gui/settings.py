"""
KIVY SETTINGS POPUPS
"""
# Standard Library Imports
import os.path as osp
from functools import cached_property
from typing import Optional

# Third Party Imports
import kivy.utils as utils
from kivy.uix.colorpicker import ColorPicker
from kivy.config import ConfigParser
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
from src.core import TemplateDetails
from src.constants import con
from src.utils.files import (
    verify_config_fields,
    get_valid_config_json,
    ensure_path_exists,
    copy_config_or_verify
)

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
    """
    Create custom SettingString class to allow Markup in title.
    """
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
    """
    Create custom SettingNumeric class to allow Markup in title.
    """
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
    """
    Create custom SettingOptions class to allow Markup in title.
    """
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

    """
    Settings governing entire APP
    """

    @cached_property
    def path_app_ini(self) -> str:
        return con.path_config_ini_app

    @cached_property
    def path_app_json(self):
        # System json configuration
        return con.path_config_json_app

    """
    Settings that can be applied to templates
    """

    @cached_property
    def path_base_ini(self) -> str:
        # Main template settings INI
        return con.path_config_ini_base

    @cached_property
    def path_base_json(self) -> str:
        # Main template settings JSON
        return con.path_config_json_base

    """
    Settings applying to only this template
    """

    @cached_property
    def path_template_json(self) -> Optional[str]:
        # Template JSON config path
        if self.template and osp.isfile(self.template.get('config_path')):
            return self.template.get('config_path')
        return

    @cached_property
    def path_template_ini(self) -> Optional[str]:
        # Template INI config path
        if self.template and self.template.get('config_path'):
            return self.template.get('config_path', '').replace('json', 'ini')
        return

    """
    Checks
    """

    @cached_property
    def has_template(self) -> bool:
        return bool(self.template and self.path_template_ini)

    """
    Generate Settings Page
    """

    def __init__(self, template: Optional[TemplateDetails] = None, **kwargs):
        super().__init__(**kwargs)
        self.template = template

        # Ensure the base and system app configs are valid:
        self.validate_app_configs()

        # Is this global or for a template?
        if not self.has_template:
            settings = self.load_global_settings()
        else:
            settings = self.load_template_settings()
        self.add_widget(settings)

    def load_global_settings(self) -> Settings:

        # Create a settings panel
        s = self.get_settings_panel()

        # Load ini files
        base_config = self.get_config_object(self.path_base_ini)
        app_config = self.get_config_object(self.path_app_ini)

        # Load JSON settings into panel
        s.add_json_panel(
            'Main Settings', base_config,
            data=get_valid_config_json(self.path_base_json)
        )
        s.add_json_panel(
            'System Settings', app_config,
            data=get_valid_config_json(self.path_app_json)
        )
        return s

    def load_template_settings(self) -> Settings:

        # Create a settings panel
        s = self.get_settings_panel()

        # Load ini files
        self.validate_template_config()
        config = self.get_config_object(self.path_template_ini)

        # Load JSON settings into panel
        if self.path_template_json:
            s.add_json_panel(
                f"{self.template['name']} Template", config,
                data=get_valid_config_json(self.path_template_json)
            )
        s.add_json_panel(
            'Main Settings', config,
            data=get_valid_config_json(self.path_base_json)
        )
        return s

    """
    Validate Settings
    """

    def validate_app_configs(self) -> None:
        """
        Validate both our BASE config and APP config.
        """
        verify_config_fields(self.path_app_ini, self.path_app_json)
        verify_config_fields(self.path_base_ini, self.path_base_json)

    def validate_template_config(self) -> None:
        """
        Verify that the ini file for the app/template contains necessary fields outlined in JSON.
        """
        # Ensure folder exists
        ensure_path_exists(self.path_template_ini)

        # Ensure app fields exist
        copy_config_or_verify(self.path_base_ini, self.path_template_ini, self.path_base_json)
        if self.path_template_json:
            verify_config_fields(self.path_template_ini, self.path_template_json)

    """
    Handle Needed Objects
    """

    @staticmethod
    def get_config_object(path: str) -> ConfigParser:
        """
        Returns a config option using a valid ini path.
        @param path: Path to ini file.
        @return: ConfigParser option that loaded the ini file.
        """
        config = ConfigParser(allow_no_value=True)
        config.optionxform = str
        config.read(path)
        return config

    def get_settings_panel(self) -> Settings:
        """
        Create a settings panel to register our JSON settings to.
        @return: Settings object.
        """
        # Configure settings panel
        s = Settings()
        s.bind(on_close=self.dismiss)
        s.register_type('options', FormattedSettingOptions)
        s.register_type('string', FormattedSettingString)
        s.register_type('numeric', FormattedSettingNumeric)
        s.register_type('color', FormattedSettingColor)
        return s
