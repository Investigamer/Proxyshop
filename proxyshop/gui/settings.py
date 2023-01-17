"""
KIVY SETTINGS POPUPS
"""
import os
import os.path as osp
import json
import shutil
from pathlib import Path
from typing import TypedDict, Optional
from kivy.config import ConfigParser
import configparser
from kivy.uix.modalview import ModalView
from kivy.uix.settings import SettingsWithNoMenu, Settings

cwd = os.getcwd()

"""
FUNCTIONS
"""


def build_ini_from_config():
    pass


"""
CLASSES
"""


class TemplateInfo(TypedDict):
    name: str
    type: str
    plugin: str


class SettingsPopup(ModalView):

    @property
    def app_ini(self) -> str:
        return osp.join(cwd, "config.ini")

    @property
    def app_json(self) -> str:
        return osp.join(cwd, "proxyshop/app_settings.json")

    def __init__(self, template: Optional[TemplateInfo] = None, **kwargs):
        super().__init__(**kwargs)

        # Create ini if one doesn't exist
        if template:
            self.create_config(template)
        else:
            self.path_ini = self.app_ini

        # Get template configs
        custom_json = None
        if template:
            filename = f"[{template['type']}] {template['name']}.json"
            if template['plugin']:
                custom_json = osp.join(osp.dirname(template['plugin']), f"configs/{filename}")
            else:
                custom_json = osp.join(cwd, f"proxyshop/configs/{filename}")

            # Check if json exists
            if not osp.exists(custom_json):
                custom_json = None

            # Import json data into template ini
            if custom_json:
                custom_json = self.update_config(custom_json)

        app_config = ConfigParser(allow_no_value=True)
        app_config.optionxform = str
        app_config.read(self.path_ini)

        s = Settings()
        s.bind(on_close=self.dismiss)
        if custom_json:
            s.add_json_panel(f"{template['name']} Template", app_config, data=custom_json)
        s.add_json_panel('App Settings', app_config, 'proxyshop/app_settings.json')
        self.add_widget(s)

    def create_config(self, template: TemplateInfo):
        """
        Check this template's ini exists, if it doesn't create one.
        @param template:
        @return:
        """
        filename = f"[{template['type']}] {template['name']}.ini"
        if template['plugin']:
            self.path_ini = osp.join(osp.dirname(template['plugin']), f"configs/{filename}")
        else:
            self.path_ini = osp.join(cwd, f"proxyshop/configs/{filename}")
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
