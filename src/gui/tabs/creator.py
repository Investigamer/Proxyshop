"""
* GUI Tab: Custom Card Creator
"""
# Standard Library Imports
import os

# Third Party Imports
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem, TabbedPanel

# Local Imports
from src._state import PATH
from src._loader import TemplateCategoryMap, TemplateSelectedMap
from src.gui._state import GlobalAccess
from src.utils.properties import auto_prop_cached
from src.utils.strings import msg_bold

"""
* Layout Classes
"""


class CreatorPanel(TabbedPanel, GlobalAccess):
    """Panel tab the 'Creator' tab which renders custom cards."""
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "creator.kv"))

    @auto_prop_cached
    def creator_tabs(self) -> list[type['CreatorLayout']]:
        """Defined creator tabs."""
        return [
            CreatorNormalLayout,
            CreatorPlaneswalkerLayout,
            CreatorSagaLayout
        ]

    def on_load(self, *args) -> None:
        """Add creator tabs."""
        for tab in self.creator_tabs:
            self.add_widget(CreatorTabItem(tab))
        self._tab_layout.padding = (
            '0dp', '0dp', '0dp', '0dp')


class CreatorTabItem(TabbedPanelItem, GlobalAccess):
    """Represents a single tab in the CreatorPanels tabbed panel."""

    def __init__(self, widget: type['CreatorLayout'], **kwargs):
        super().__init__(text=widget._category, **kwargs)
        self.add_widget(widget())


class CreatorLayout(GridLayout, GlobalAccess):
    """Represents the content of a specific 'CreatorTabItem' tab."""
    _category = ''

    def __init__(self, **kwargs):

        # Key attributes
        self._templates: TemplateCategoryMap = self.main.template_map[self._category]
        self._template_names: list[str] = self._templates['names']
        self._types: list[str] = list(self._templates['map'].keys())
        self._templates_selected: TemplateSelectedMap = self.main.templates_default.copy()

        # Call super
        super().__init__(**kwargs)

    @auto_prop_cached
    def toggle_buttons(self) -> list[Button]:
        """Add render button."""
        return [self.ids.render_btn]

    """
    * Template Utils
    """

    def select_template(self, spinner: Spinner) -> None:
        """Choose which template to render with.

        Args:
            spinner: Spinner dropdown list element.
        """
        for t in self._types:
            if spinner.text in self._templates['map'][t]:
                self._templates_selected[t] = self._templates['map'][t][spinner.text]
            else:
                # Notify the user one face type isn't supported
                face = 'Front' if 'back' in t else 'Back'
                self.console.update(
                    msg_bold(f"NOTE: Template '{spinner.text}' only supports '{face}' face cards."))

    def render(self) -> None:
        """Initiate a custom card render operation."""
        scryfall = self.format_card_data(self.get_card_data())
        template = self._templates_selected[scryfall.get('layout', 'normal')]
        self.main.render_custom(template, scryfall)

    """
    * Data Utils
    """

    def get_card_data(self) -> dict:
        """Extend this method to extract card data from UI form fields."""
        return {}

    def format_card_data(self, data: dict) -> dict:
        """Post-process card data for layout validation or other cases.

        Args:
            data: Dict containing card data, mirrors Scryfall data in the main app.

        Returns:
            Formatted and validated card data dict.
        """
        # Shared data
        data['object'] = 'card'
        data['lang'] = self.cfg.lang

        # Is this an alternate language card?
        if data['lang'] != 'en':
            data['printed_name'] = data['name']
            data['printed_text'] = data['oracle_text']
            data['printed_type_line'] = data['type_line']
        return data


class CreatorNormalLayout(CreatorLayout):
    _category = 'Normal'

    def get_card_data(self) -> dict:
        oracle_text = self.ids.oracle_text.text.replace("~", self.ids.name.text)
        flavor_text = self.ids.flavor_text.text.replace("~", self.ids.name.text)
        return {
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


class CreatorPlaneswalkerLayout(CreatorLayout):
    _category = 'Planeswalker'

    def get_card_data(self) -> dict:
        rules_text = "\n".join(n for n in [
            self.ids.line_1.text.replace("~", self.ids.name.text),
            self.ids.line_2.text.replace("~", self.ids.name.text),
            self.ids.line_3.text.replace("~", self.ids.name.text),
            self.ids.line_4.text.replace("~", self.ids.name.text)
        ] if n)
        return {
            "layout": "planeswalker",
            "set": self.ids.set.text,
            "name": self.ids.name.text,
            "oracle_text": rules_text,
            "artist": self.ids.artist.text,
            "loyalty": self.ids.loyalty.text,
            "mana_cost": self.ids.mana_cost.text,
            "type_line": self.ids.type_line.text,
            "rarity": self.ids.rarity.text.lower(),
            "printed_size": self.ids.card_count.text,
            "keywords": self.ids.keywords.text.split(","),
            "collector_number": self.ids.collector_number.text,
            "color_identity": self.ids.color_identity.text.split()
        }


class CreatorSagaLayout(CreatorLayout):
    _category = 'Saga'

    def get_card_data(self) -> dict:
        text_arr, num_lines = [], 'I'
        if self.ids.line_1.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_1.text.replace("~", self.ids.name.text))
            num_lines += "I"
        if self.ids.line_2.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_2.text.replace("~", self.ids.name.text))
            num_lines += "I"
        if self.ids.line_3.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_3.text.replace("~", self.ids.name.text))
            num_lines = "IV" if len(num_lines) == 3 else num_lines + "I"
        if self.ids.line_4.text != "":
            text_arr.append(f"{num_lines} — " + self.ids.line_4.text.replace("~", self.ids.name.text))
        text_arr.insert(0, f"(As this Saga enters and after your draw step, add a lore counter. "
                           f"Sacrifice after {num_lines}.)")
        rules_text = "\n".join(text_arr)
        return {
            "layout": "saga",
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
