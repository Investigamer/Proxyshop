"""
* MUTATE TEMPLATES
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


class MutateTemplate (NormalTemplate):
    """
    * A template for mutate cards introduced in Ikoria: Lair of Behemoths.

    Adds:
        * Mutate text property that formats the mutate ability text.
        * Mutate text layer for mutate ability.
    """

    @cached_property
    def text_layer_mutate(self) -> Optional[ArtLayer]:
        """Text layer containing the mutate text."""
        return psd.getLayer(LAYERS.MUTATE, self.text_group)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add mutate text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_mutate,
                contents = self.layout.mutate_text,
                flavor = self.layout.flavor_text,
                reference = psd.getLayer(LAYERS.MUTATE_REFERENCE, self.text_group),
            )
        )
