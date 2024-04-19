"""
* Managing Global State (GUI)
"""
# Standard Library Imports
from dataclasses import dataclass
from functools import cache
import os
from typing import Any

# Third Party Imports
from kivy.app import App
from kivy.config import Config
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.layout import Layout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.core.window import Window

# Local Imports
from src._config import AppConfig
from src._state import PATH, AppConstants, AppEnvironment
from src.enums.mtg import layout_map_category
from src.gui.utils import HoverBehavior
from src.utils.adobe import PhotoshopHandler
from src.utils.properties import auto_prop_cached

"""
* Enums
"""


@dataclass
class KivyStyles:
    """Define the `kv` stylesheet files to loaded at initialization."""
    App = os.path.join(PATH.SRC_DATA_KV, 'app.kv')
    Main = os.path.join(PATH.SRC_DATA_KV, 'main.kv')
    Console = os.path.join(PATH.SRC_DATA_KV, 'console.kv')
    Creator = os.path.join(PATH.SRC_DATA_KV, 'creator.kv')
    Test = os.path.join(PATH.SRC_DATA_KV, 'test.kv')
    Tools = os.path.join(PATH.SRC_DATA_KV, 'tools.kv')
    Updater = os.path.join(PATH.SRC_DATA_KV, 'updater.kv')


"""
* Cached Utils
"""


@cache
def get_root_app():
    """Cache and return the running application object."""
    return App.get_running_app()


class GlobalAccess(Layout):
    """Utility class giving Kivy GUI elements access to the main app and its
    global objects."""

    def __init__(self, *args, **kwargs):
        self.bind(on_kv_post=self.on_load)
        super().__init__(**kwargs)

    """
    * Layout Methods
    """

    def on_load(self, *args) -> None:
        """Fired when object is loaded into the GUI."""
        self.main.toggle_buttons.extend(self.toggle_buttons)

    """
    * Utility Properties
    """

    @auto_prop_cached
    def toggle_buttons(self) -> list[Button]:
        """Buttons that should be toggled during a locked operation."""
        return []

    """
    * Global Object Properties
    """

    @auto_prop_cached
    def main(self) -> Any:
        """ProxyshopGUIApp: Get the running application."""
        return get_root_app()

    @property
    def app(self) -> PhotoshopHandler:
        """PhotoshopHandler: Global Photoshop application object."""
        return self.main.app

    @property
    def cfg(self) -> AppConfig:
        """AppConfig: Global settings object."""
        return self.main.cfg

    @property
    def con(self) -> AppConstants:
        """AppConstants: Global constants object."""
        return self.main.con

    @property
    def env(self) -> AppEnvironment:
        """AppEnvironment: Global environment object."""
        return self.main.env

    @property
    def console(self) -> Any:
        """GUIConsole: Console output object."""
        return self.main.console


"""
* GUI Loader Funcs
"""


def load_kv_config():
    """Loads app-wide Kivy configuration."""

    # Kivy configuration
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.remove_option('input', 'wm_touch')
    Config.remove_option('input', 'wm_pen')
    Config.set('kivy', 'log_level', 'error')
    Config.write()

    # Window configuration
    Window.minimum_width = dp(650)
    Window.minimum_height = dp(540)
    Window.size = (dp(840), dp(720))


def register_kv_classes():
    """Loads app-wide GUI classes into Kivy Factory."""
    Factory.register('HoverBehavior', HoverBehavior)


"""
* Tracked Elements
"""


class GUIResources:
    def __init__(self):
        self.template_row: dict[str, dict[str, BoxLayout]] = {k: {} for k in layout_map_category}
        self.template_btn: dict[str, dict[str, ToggleButton]] = {k: {} for k in layout_map_category}
        self.template_btn_cfg: dict[str, dict[str, Button]] = {k: {} for k in layout_map_category}
        self.template_list: dict[str, list[BoxLayout]] = {k: [] for k in layout_map_category}


GUI = GUIResources()
