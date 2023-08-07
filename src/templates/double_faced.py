"""
* DOUBLE FACED TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src.templates._mods import MDFCMod, TransformMod
from src.templates._core import NormalTemplate
from src.enums.photoshop import Dimensions
from src.text_layers import TextField
from src.enums.layers import LAYERS
import src.helpers as psd


class TransformTemplate (TransformMod, NormalTemplate):
    """Template for double faced Transform cards introduced in Innistrad block."""


class MDFCTemplate (MDFCMod, NormalTemplate):
    """Template for Modal Double Faced cards introduced in Zendikar Rising."""


class IxalanTemplate (NormalTemplate):
    """Template for the back face lands for transforming cards from Ixalan block."""

    @property
    def is_creature(self) -> bool:
        # Only lands for this one
        return False

    @property
    def is_name_shifted(self) -> bool:
        # No transform icon to shift name
        return False

    @cached_property
    def expansion_symbol_alignments(self) -> list[Dimensions]:
        # Expansion symbol is entirely centered
        return [Dimensions.CenterX, Dimensions.CenterY]

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        # Uses pinline color for background choice
        return psd.getLayer(self.pinlines, LAYERS.BACKGROUND)

    def basic_text_layers(self):
        # No mana cost layer, no scaling typeline
        self.text.extend([
            TextField(
                layer = self.text_layer_name,
                contents = self.layout.name
            ),
            TextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line
            )
        ])

    def enable_frame_layers(self):
        # Only background frame layer
        self.background_layer.visible = True
