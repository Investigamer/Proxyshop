"""
* Mutate Templates
"""
# Standard Library
from typing import Optional, Callable

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src import CFG
from src.cards import strip_reminder_text
from src.enums.layers import LAYERS
import src.helpers as psd
from src.layouts import MutateLayout
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.utils.adobe import ReferenceLayer
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
    * Mixin Methods
    """

    @auto_prop_cached
    def text_layer_methods(self) -> list[Callable]:
        """Add Mutate text layers."""
        funcs = [self.text_layers_mutate] if isinstance(self.layout, MutateLayout) else []
        return [*super().text_layer_methods, *funcs]

    """
    * Mutate Text Layers
    """

    @auto_prop_cached
    def text_layer_mutate(self) -> Optional[ArtLayer]:
        """Text layer containing the mutate text."""
        return psd.getLayer(LAYERS.MUTATE, self.text_group)

    """
    * Mutate References
    """

    @auto_prop_cached
    def mutate_reference(self) -> Optional[ReferenceLayer]:
        """Mutate textbox reference."""
        return psd.get_reference_layer(LAYERS.MUTATE_REFERENCE, self.text_group)

    """
    * Processing Methods
    """

    def process_layout_data(self) -> None:
        """Remove reminder text for mutate text if required."""
        if CFG.remove_reminder:
            self.layout.mutate_text = strip_reminder_text(
                self.layout.mutate_text)
        super().process_layout_data()

    """
    * Mutate Text Layer Methods
    """

    def text_layers_mutate(self):
        """Add text layers required by Mutate cards."""

        # Add mutate text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_mutate,
                contents = self.layout.mutate_text,
                reference = self.mutate_reference))


"""
* Template Classes
"""


class MutateTemplate (MutateMod, NormalTemplate):
    """Raster template for Mutate cards introduced in Ikoria: Lair of Behemoths."""
