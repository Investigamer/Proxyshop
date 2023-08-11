"""
* ADVENTURE TEMPLATES
"""
# Standard Library
from functools import cached_property
from typing import Callable, Optional

# Third Party Imports
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.layouts import AdventureLayout
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
import src.helpers as psd


"""
* ADVENTURE MODIFIER CLASSES
"""


class AdventureMod (NormalTemplate):
    """
    * A modifier for adding steps required for Adventure type cards introduced in Throne of Eldraine.

    Adds:
        * Adventure side text layers (Mana cost, name, typeline, and oracle text) and textbox reference.
    """

    """
    DETAILS
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Add Adventure text layers."""
        funcs = [self.text_layers_adventure] if isinstance(self.layout, AdventureLayout) else []
        return [*super().text_layer_methods, *funcs]

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name_adventure(self) -> Optional[ArtLayer]:
        """Name for the adventure side."""
        return psd.getLayer(LAYERS.NAME_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_mana_adventure(self) -> Optional[ArtLayer]:
        """Mana cost for the adventure side."""
        return psd.getLayer(LAYERS.MANA_COST_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_type_adventure(self) -> Optional[ArtLayer]:
        """Type line for the adventure side."""
        return psd.getLayer(LAYERS.TYPE_LINE_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_rules_adventure(self) -> Optional[ArtLayer]:
        """Rules text for the adventure side."""
        return psd.getLayer(LAYERS.RULES_TEXT_ADVENTURE, self.text_group)

    """
    REFERENCES
    """

    @cached_property
    def textbox_reference_adventure(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE_ADVENTURE, self.text_group)

    """
    ADVENTURE METHODS
    """

    def text_layers_adventure(self):

        # Add adventure text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_mana_adventure,
                contents = self.layout.mana_adventure
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_name_adventure,
                contents = self.layout.name_adventure,
                reference = self.text_layer_mana_adventure,
            ),
            text_classes.FormattedTextArea(
                layer = self.text_layer_rules_adventure,
                contents = self.layout.oracle_text_adventure,
                reference = self.textbox_reference_adventure,
                flavor = "", centered = False
            ),
            text_classes.TextField(
                layer = self.text_layer_type_adventure,
                contents = self.layout.type_line_adventure
            )
        ])


"""
* ADVENTURE TEMPLATE CLASSES
"""


class AdventureTemplate(AdventureMod, NormalTemplate):
    """Raster template for Adventure cards introduced in Throne of Eldraine."""
