"""
* Mutate Templates
"""
# Standard Library
from typing import Optional, Callable

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src.enums.layers import LAYERS
import src.helpers as psd
from src.layouts import MutateLayout
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.utils.properties import auto_prop_cached

"""
* Modifier Classes
"""


class MutateMod (NormalTemplate):
    """
    * A modifier for mutate cards introduced in Ikoria: Lair of Behemoths.

    Adds:
        * Mutate text layer for mutate ability.
    """

    """
    DETAILS
    """

    @auto_prop_cached
    def text_layer_methods(self) -> list[Callable]:
        """Add Mutate text layers."""
        funcs = [self.text_layers_mutate] if isinstance(self.layout, MutateLayout) else []
        return [*super().text_layer_methods, *funcs]

    """
    TEXT LAYERS
    """

    @auto_prop_cached
    def text_layer_mutate(self) -> Optional[ArtLayer]:
        """Text layer containing the mutate text."""
        return psd.getLayer(LAYERS.MUTATE, self.text_group)

    """
    REFERENCES
    """

    @auto_prop_cached
    def mutate_reference(self) -> Optional[ArtLayer]:
        """Mutate textbox reference."""
        return psd.getLayer(LAYERS.MUTATE_REFERENCE, self.text_group)

    """
    METHODS
    """

    def text_layers_mutate(self):
        """Add text layers required by Mutate cards."""

        # Add mutate text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_mutate,
                contents = self.layout.mutate_text,
                flavor = self.layout.flavor_text,
                reference = self.mutate_reference))


"""
* Template Classes
"""


class MutateTemplate (MutateMod, NormalTemplate):
    """Raster template for Mutate cards introduced in Ikoria: Lair of Behemoths."""
