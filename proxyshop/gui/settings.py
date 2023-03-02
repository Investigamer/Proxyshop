"""
KIVY SETTINGS POPUPS
"""
import os.path as osp
import json
import shutil
from pathlib import Path
from typing import Optional
from kivy.config import ConfigParser
import configparser

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

from proxyshop.core import TemplateDetails
from proxyshop.constants import con


"""
AESTHETIC CLASSES
"""


class FormattedSettingString(SettingString):
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
    def app_ini(self) -> str:
        return osp.join(con.cwd, "config.ini")

    @property
    def app_json(self) -> str:
        return osp.join(con.cwd, "proxyshop/app_settings.json")

    def __init__(self, template: Optional[TemplateDetails] = None, **kwargs):
        super().__init__(**kwargs)

        # Create ini if one doesn't exist
        if template:
            self.create_config(template)
            custom_json = self.update_config(template['config_path']) if osp.exists(template['config_path']) else None
        else:
            self.path_ini = self.app_ini
            custom_json = None

        app_config = ConfigParser(allow_no_value=True)
        app_config.optionxform = str
        app_config.read(self.path_ini)

        s = Settings()
        s.bind(on_close=self.dismiss)
        s.register_type('options', FormattedSettingOptions)
        s.register_type('string', FormattedSettingString)
        s.register_type('numeric', FormattedSettingNumeric)
        if custom_json:
            s.add_json_panel(f"{template['name']} Template", app_config, data=custom_json)
        s.add_json_panel('App Settings', app_config, 'proxyshop/app_settings.json')
        self.add_widget(s)

    def create_config(self, template: TemplateDetails):
        """
        Check this template's ini exists, if it doesn't create one.
        @param template:
        @return:
        """
        self.path_ini = template['config_path'].replace('json', 'ini')
        if not osp.exists(self.path_ini):
            Path(osp.dirname(self.path_ini)).mkdir(mode=511, parents=True, exist_ok=True)
            shutil.copyfile('config.ini', self.path_ini)

    def update_config(self, json_path) -> str:
        # Load the json
        changed = False
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Load the config
        conf_file = configparser.ConfigParser(allow_no_value=True)
        conf_file.optionxform = str
        with open(self.path_ini, "r", encoding="utf-8") as f:
            conf_file.read_file(f)

        # Build a dictionary of the necessary values
        data = {}
        for row in raw:
            if row['type'] == 'title':
                continue
            if row['section'] not in data:
                data[row['section']] = []
            data[row['section']].append({
                'key': row['key'],
                'value': row['default'] if 'default' in row else 0
            })
            if 'default' in row:
                row.pop('default')

        # Build the sections and rows into the ini
        for section, settings in data.items():
            # Check if the section exists
            if not conf_file.has_section(section):
                conf_file.add_section(section)
                changed = True
            # Check if each setting exists
            for setting in settings:
                if not conf_file.has_option(section, setting['key']):
                    conf_file.set(section, setting['key'], str(setting['value']))
                    changed = True

        # If ini has changed, write changes
        if changed:
            with open(self.path_ini, "w", encoding="utf-8") as f:
                conf_file.write(f)

        # Return json data
        return json.dumps(raw)
