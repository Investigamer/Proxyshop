"""
* ADVENTURE TEMPLATES
"""
# Local Imports
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
import src.helpers as psd


class AdventureTemplate (NormalTemplate):
    """
    * A template for Adventure cards introduced in Throne of Eldraine.

    Adds:
        * Mana cost, name, typeline, and oracle text layers for the adventure side.
    """

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add adventure text layers
        mana_cost = psd.getLayer(LAYERS.MANA_COST_ADVENTURE, self.text_group)
        self.text.extend([
            text_classes.FormattedTextField(
                layer = mana_cost,
                contents = self.layout.adventure['mana_cost']
            ),
            text_classes.ScaledTextField(
                layer = psd.getLayer(LAYERS.NAME_ADVENTURE, self.text_group),
                contents = self.layout.adventure['name'],
                reference = mana_cost,
            ),
            text_classes.FormattedTextArea(
                layer = psd.getLayer(LAYERS.RULES_TEXT_ADVENTURE, self.text_group),
                contents = self.layout.adventure['oracle_text'],
                flavor = "",
                centered = False,
                reference = psd.getLayer(LAYERS.TEXTBOX_REFERENCE_ADVENTURE, self.text_group),
            ),
            text_classes.TextField(
                layer = psd.getLayer(LAYERS.TYPE_LINE_ADVENTURE, self.text_group),
                contents = self.layout.adventure['type_line']
            )
        ])