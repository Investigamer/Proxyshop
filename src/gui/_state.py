"""
* Managing Global State (GUI)
"""
# Standard Library Imports
from functools import cache

# Third Party Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button

# Local Imports
from src.enums.mtg import layout_map_category

"""
* Cached Utils
"""


@cache
def get_main_app():
    """Cache and return the running application object."""
    return App.get_running_app()


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
