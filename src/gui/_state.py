"""
* Managing Global State (GUI)
"""
# Standard Library Imports
from dataclasses import dataclass
from functools import cache
import os

# Third Party Imports
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button

# Local Imports
from src._state import PATH
from src.enums.mtg import layout_map_category
from src.gui.utils import HoverBehavior

"""
* Enums
"""


@dataclass
class KivyStyles:
    """Define the `kv` stylesheet files to loaded at initialization."""
    App = os.path.join(PATH.SRC_DATA_KV, 'app.kv')
    Console = os.path.join(PATH.SRC_DATA_KV, 'console.kv')
    Creator = os.path.join(PATH.SRC_DATA_KV, 'creator.kv')
    Dev = os.path.join(PATH.SRC_DATA_KV, 'dev.kv')
    Tools = os.path.join(PATH.SRC_DATA_KV, 'tools.kv')
    Updater = os.path.join(PATH.SRC_DATA_KV, 'updater.kv')


"""
* Cached Utils
"""


@cache
def get_main_app():
    """Cache and return the running application object."""
    return App.get_running_app()


"""
* GUI Loader Funcs
"""


def load_kv_config():
    """Loads app-wide Kivy configuration."""
    # App configuration
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.remove_option('input', 'wm_touch')
    Config.remove_option('input', 'wm_pen')
    Config.set('kivy', 'log_level', 'error')
    Config.write()


def register_kv_classes():
    """Loads app-wide GUI classes into Kivy Factory."""
    Factory.register('HoverBehavior', HoverBehavior)


def load_kv_files():
    """Loads app-wide `kv` files into the Kivy Builder."""
    kv = [
        KivyStyles.App,
        KivyStyles.Console,
        KivyStyles.Creator,
        KivyStyles.Dev,
        KivyStyles.Tools,
        KivyStyles.Updater
    ]
    for k in kv:
        Builder.load_file(k)


"""
* Tracked Elements
"""


class GUIResources:
    def __init__(self):
        empty = {k: {} for k in layout_map_category}
        self.template_row: dict[str, dict[str, BoxLayout]] = empty.copy()
        self.template_btn: dict[str, dict[str, ToggleButton]] = empty.copy()
        self.template_btn_cfg: dict[str, dict[str, Button]] = empty.copy()


GUI = GUIResources()
