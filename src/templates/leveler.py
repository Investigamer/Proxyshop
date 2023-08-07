"""
* LEVELER TEMPLATES
"""
# Standard Library
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
import src.helpers as psd


class LevelerTemplate (NormalTemplate):
    """
    * Template for Level-Up cards introduced in Rise of the Eldrazi.

    Adds:
        * First, second, and third level ability text.
        * First, second, and third level power/toughness.
        * Level requirements for second and third stage.
    """

    """
    PROPERTIES
    """

    @property
    def is_land(self) -> bool:
        return False

    """
    LAYERS
    """

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.twins, LAYERS.PT_AND_LEVEL_BOXES)

    """
    METHODS
    """

    def rules_text_and_pt_layers(self):

        # Overwrite to add level abilities
        leveler_text_group = psd.getLayerSet("Leveler Text", self.text_group)
        self.text.extend([
            text_classes.FormattedTextArea(
                layer = psd.getLayer("Rules Text - Level Up", leveler_text_group),
                contents = self.layout.level_up_text,
                reference = psd.getLayer(LAYERS.TEXTBOX_REFERENCE + " - Level Text", leveler_text_group)
            ),
            text_classes.TextField(
                layer = psd.getLayer("Top Power / Toughness", leveler_text_group),
                contents = str(self.layout.power) + "/" + str(self.layout.toughness)
            ),
            text_classes.TextField(
                layer = psd.getLayer("Middle Level", leveler_text_group),
                contents = self.layout.middle_level
            ),
            text_classes.TextField(
                layer = psd.getLayer("Middle Power / Toughness", leveler_text_group),
                contents = self.layout.middle_power_toughness
            ),
            text_classes.FormattedTextArea(
                layer = psd.getLayer("Rules Text - Levels X-Y", leveler_text_group),
                contents = self.layout.levels_x_y_text,
                reference = psd.getLayer(LAYERS.TEXTBOX_REFERENCE + " - Level X-Y", leveler_text_group)
            ),
            text_classes.TextField(
                layer = psd.getLayer("Bottom Level", leveler_text_group),
                contents = self.layout.bottom_level
            ),
            text_classes.TextField(
                layer = psd.getLayer("Bottom Power / Toughness", leveler_text_group),
                contents = self.layout.bottom_power_toughness
            ),
            text_classes.FormattedTextArea(
                layer = psd.getLayer("Rules Text - Levels Z+", leveler_text_group),
                contents = self.layout.levels_z_plus_text,
                reference = psd.getLayer(LAYERS.TEXTBOX_REFERENCE + " - Levels Z+", leveler_text_group)
            )
        ])
