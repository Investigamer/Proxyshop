"""
GUI Element Tracking Module
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton

from proxyshop.core import card_types


class GUIResources:
    def __init__(self):
        self.template_row: dict[str, [str, BoxLayout]] = {k: {} for k in card_types}
        self.template_btn: dict[str, [str, ToggleButton]] = {k: {} for k in card_types}
        self.template_btn_cfg: dict[str, [str, Button]] = {k: {} for k in card_types}

GUI = GUIResources()
