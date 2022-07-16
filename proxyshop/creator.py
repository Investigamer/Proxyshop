"""
CARD CREATOR TAB
"""
import os
import threading
from typing import Callable

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem, TabbedPanel
from kivy.uix.textinput import TextInput
from proxyshop import core
cwd = os.getcwd()


"""
DISPLAY ELEMENTS
"""


class CreatorPanels(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Establish the tab contents
        self.creator_normal_layout = CreatorNormalLayout(self, "normal")
        self.creator_pw_layout = CreatorPlaneswalkerLayout(self, "planeswalker")
        self.creator_saga_layout = CreatorSagaLayout(self, "saga")

        # Add the widgets
        self.add_widget(CreatorTabItem(self.creator_normal_layout, text="Normal"))
        self.add_widget(CreatorTabItem(self.creator_pw_layout, text="Planeswalker"))
        self.add_widget(CreatorTabItem(self.creator_saga_layout, text="Saga"))
        self._tab_layout.padding = '0dp', '0dp', '0dp', '0dp'


class CreatorTabItem(TabbedPanelItem):
    def __init__(self, widget, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(widget)


class CreatorLayout(GridLayout):
    def __init__(self, parent: TabbedPanel, c_type: str, **kwargs):
        # Get our templates alphabetical
        self.root = parent
        self.selected_template = "Normal"
        temps_t = core.get_templates()[c_type]
        self.templates = ["Normal"]
        temps_t.pop("Normal")
        self.templates.extend(sorted(temps_t))
        del temps_t
        super().__init__(**kwargs)

    def select_template(self, spinner: Spinner):
        """
        Choose which template to render with.
        @param spinner: Spinner dropdown list object.
        """
        self.selected_template = spinner.text

    def disable_buttons(self):
        """
        Disable all creator tab render buttons.
        """
        self.root.creator_normal_layout.ids.render_norm.disabled = True
        self.root.creator_pw_layout.ids.render_pw.disabled = True
        self.root.creator_saga_layout.ids.render_saga.disabled = True

    def enable_buttons(self):
        """
        Enable all creator tab render buttons.
        """
        self.root.creator_normal_layout.ids.render_norm.disabled = False
        self.root.creator_pw_layout.ids.render_pw.disabled = False
        self.root.creator_saga_layout.ids.render_saga.disabled = False

    def render_custom(self, func: Callable, temp: list, scryfall: dict):
        self.disable_buttons()
        th = threading.Thread(target=func, args=(temp, scryfall), daemon=True)
        th.start()
        th.join()
        self.enable_buttons()


class CreatorNormalLayout(CreatorLayout):
    def render(self, root: App):
        oracle_text = self.ids.oracle_text.text.replace("~", self.ids.name.text)
        flavor_text = self.ids.flavor_text.text.replace("~", self.ids.name.text)
        scryfall = {
            "layout": "normal",
            "set": self.ids.set.text,
            "name": self.ids.name.text,
            "oracle_text": oracle_text,
            "flavor_text": flavor_text,
            "power": self.ids.power.text,
            "artist": self.ids.artist.text,
            "mana_cost": self.ids.mana_cost.text,
            "type_line": self.ids.type_line.text,
            "toughness": self.ids.toughness.text,
            "rarity": self.ids.rarity.text.lower(),
            "printed_size": self.ids.card_count.text,
            "keywords": self.ids.keywords.text.split(","),
            "collector_number": self.ids.collector_number.text,
            "color_identity": self.ids.color_identity.text.split()
        }
        temp = core.get_templates()["normal"][self.ids.template.text]
        self.render_custom(root.render_custom, temp, scryfall)


class CreatorPlaneswalkerLayout(CreatorLayout):
    def render(self, root: App):
        rules_text = "\n".join([
            self.ids.line_1.text.replace("~", self.ids.name.text),
            self.ids.line_2.text.replace("~", self.ids.name.text),
            self.ids.line_3.text.replace("~", self.ids.name.text),
            self.ids.line_4.text.replace("~", self.ids.name.text)
        ])
        scryfall = {
            "layout": "normal",
            "set": self.ids.set.text,
            "name": self.ids.name.text,
            "artist": self.ids.artist.text,
            "loyalty": self.ids.loyalty.text,
            "mana_cost": self.ids.mana_cost.text,
            "type_line": self.ids.type_line.text,
            "rarity": self.ids.rarity.text.lower(),
            "printed_size": self.ids.card_count.text,
            "oracle_text": rules_text, "flavor_text": "",
            "keywords": self.ids.keywords.text.split(","),
            "collector_number": self.ids.collector_number.text,
            "color_identity": self.ids.color_identity.text.split()
        }
        temp = core.get_templates()["planeswalker"][self.ids.template.text]
        self.render_custom(root.render_custom, temp, scryfall)


class CreatorSagaLayout(CreatorLayout):
    def render(self, root: App):
        text_arr = []
        num_lines = "I"
        if self.ids.line_1.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_1.text.replace("~", self.ids.name.text))
            num_lines+="I"
        if self.ids.line_2.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_2.text.replace("~", self.ids.name.text))
            num_lines += "I"
        if self.ids.line_3.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_3.text.replace("~", self.ids.name.text))
            if len(num_lines) == 3: num_lines = "IV"
            else: num_lines += "I"
        if self.ids.line_4.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_4.text.replace("~", self.ids.name.text))
        text_arr.insert(0, f"Empty words.")
        rules_text = "\n".join(text_arr)
        scryfall = {
            "layout": "saga",
            "flavor_text": "",
            "set": self.ids.set.text,
            "oracle_text": rules_text,
            "name": self.ids.name.text,
            "artist": self.ids.artist.text,
            "mana_cost": self.ids.mana_cost.text,
            "type_line": self.ids.type_line.text,
            "rarity": self.ids.rarity.text.lower(),
            "printed_size": self.ids.card_count.text,
            "keywords": self.ids.keywords.text.split(","),
            "collector_number": self.ids.collector_number.text,
            "color_identity": self.ids.color_identity.text.split()
        }
        temp = core.get_templates()["saga"][self.ids.template.text]
        self.render_custom(root.render_custom, temp, scryfall)


"""
CUSTOM FORM INPUTS
"""


class InputItem(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicked = False
        self.original = self.text

    def _on_focus(self, instance, value, *largs):
        if not self.clicked:
            self.clicked = True
            self.original = self.text
        super()._on_focus(instance, value, *largs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Enable tab to next or previous input
        """
        if keycode[1] == 'tab':  # deal with cycle
            if 'shift' in modifiers: nxt = self.get_focus_previous()
            else: nxt = self.get_focus_next()
            if nxt:
                self.focus = False
                nxt.focus = True
            return True
        if keycode[0] == 286:  # F5 to reset text
            self.clicked = False
            self.text = self.original
        super().keyboard_on_key_down(window, keycode, text, modifiers)


class NoEnterInputItem(InputItem):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Disable enter
        """
        if keycode[0] == 13:  # deal with cycle
            return False
        super().keyboard_on_key_down(window, keycode, text, modifiers)


class FourNumInput(InputItem):
    # Properties
    max_len = 4
    input_type = "number"

    def insert_text(self, substring, from_undo=False):
        """
        4 character max, numeric
        """
        if len(self.text) < self.max_len:
            if substring.isnumeric():
                return super().insert_text(substring, from_undo=from_undo)


class ThreeNumInput(InputItem):
    # Properties
    max_len = 3
    input_type = "number"
    whitelist = ("*", "X", "Y", "+", "-")

    def insert_text(self, substring, from_undo=False):
        """
        3 character max, numeric with a small whitelist
        """
        if len(self.text) < self.max_len:
            if substring.isnumeric() or substring in self.whitelist:
                return super().insert_text(substring, from_undo=from_undo)


class FourCharInput(InputItem):
    # Properties
    max_len = 4

    def insert_text(self, substring, from_undo=False):
        """
        4 character max
        """
        if len(self.text) < self.max_len:
            return super().insert_text(substring.upper(), from_undo=from_undo)
