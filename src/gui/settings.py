"""
KIVY SETTINGS POPUPS
"""
import os.path as osp
from pathlib import Path
from typing import Optional
from kivy.config import ConfigParser

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingOptions, SettingSpacer, SettingNumeric, SettingString
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from src.core import TemplateDetails
from src.constants import con
from src.utils.files import verify_config_fields, get_valid_config_json

"""
AESTHETIC CLASSES
"""


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

    @property
    def path_ini(self) -> Optional:
        # Template INI config path
        if self.template and self.template.get('config_path'):
            return self.template.get('config_path', '').replace('json', 'ini')
        return osp.join(con.cwd, "config.ini")

    @property
    def path_template_json(self) -> Optional[str]:
        # Template JSON config path
        if self.template and osp.exists(self.template.get('config_path')):
            return self.template.get('config_path')
        return

    def __init__(self, template: Optional[TemplateDetails] = None, **kwargs):
        super().__init__(**kwargs)
        self.template = template

        # Configure settings panel
        s = Settings()
        s.bind(on_close=self.dismiss)
        s.register_type('options', FormattedSettingOptions)
        s.register_type('string', FormattedSettingString)
        s.register_type('numeric', FormattedSettingNumeric)

        # Load ini file
        self.verify_ini_file()
        app_config = ConfigParser(allow_no_value=True)
        app_config.optionxform = str
        app_config.read(self.path_ini)

        # Load JSON settings into panel
        if self.path_template_json:
            s.add_json_panel(
                f"{template['name']} Template", app_config,
                data=get_valid_config_json(self.path_template_json)
            )
        s.add_json_panel(
            'App Settings', app_config,
            data=get_valid_config_json(con.path_config_json)
        )
        self.add_widget(s)

    def verify_ini_file(self):
        """
        Verify that the ini file for the app/template contains necessary fields outlined in JSON.
        """
        # Ensure folder exists
        Path(osp.dirname(self.path_ini)).mkdir(mode=511, parents=True, exist_ok=True)

        # Ensure app fields exist
        verify_config_fields(self.path_ini, con.path_config_json)
        if self.path_template_json:
            # Ensure template fields exist
            verify_config_fields(self.path_ini, self.path_template_json)
