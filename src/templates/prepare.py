"""
* Prepare Templates
"""

from collections.abc import Callable
from functools import cached_property

from photoshop.api._artlayer import ArtLayer

import src.helpers as psd
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import PrepareLayout
from src.templates._core import NormalTemplate


class PrepareMod(NormalTemplate):
    """A modifier class which adds functionality required by Prepare cards,
    introduced in Secrets of Strixhaven.

    Adds:
        * Spell side text layers (Mana cost, name, typeline, and oracle text) and textbox reference.
    """

    @cached_property
    def is_prepare(self) -> bool:
        return isinstance(self.layout, PrepareLayout)

    # region Text Layers

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Prepare text layers step."""
        funcs = super().text_layer_methods
        if isinstance(self.layout, PrepareLayout):
            funcs.append(self.text_layers_prepare)
        return funcs

    @cached_property
    def text_layer_name_prepare(self) -> ArtLayer | None:
        """Name for the prepare side."""
        return psd.getLayer(LAYERS.NAME_PREPARE, self.text_group)

    @cached_property
    def text_layer_mana_prepare(self) -> ArtLayer | None:
        """Mana cost for the prepare side."""
        return psd.getLayer(LAYERS.MANA_COST_PREPARE, self.text_group)

    @cached_property
    def text_layer_type_prepare(self) -> ArtLayer | None:
        """Type line for the prepare side."""
        return psd.getLayer(LAYERS.TYPE_LINE_PREPARE, self.text_group)

    @cached_property
    def text_layer_rules_prepare(self) -> ArtLayer | None:
        """Rules text for the prepare side."""
        return psd.getLayer(LAYERS.RULES_TEXT_PREPARE, self.text_group)

    @cached_property
    def divider_layer_prepare(self) -> ArtLayer | None:
        """Flavor divider for the prepare side."""
        return psd.getLayer(LAYERS.DIVIDER_PREPARE, self.text_group)

    # region Text Layers

    # region References

    @cached_property
    def textbox_reference_prepare(self) -> ArtLayer | None:
        return psd.get_reference_layer(
            LAYERS.TEXTBOX_REFERENCE_PREPARE, self.text_group
        )

    # endregion References

    # region Methods

    def text_layers_prepare(self) -> None:
        if isinstance(self.layout, PrepareLayout):
            # Add prepare text layers
            if self.text_layer_mana_prepare:
                self.text.append(
                    text_classes.FormattedTextField(
                        layer=self.text_layer_mana_prepare,
                        contents=self.layout.mana_prepare,
                    )
                )
            if self.text_layer_name_prepare:
                self.text.append(
                    text_classes.ScaledTextField(
                        layer=self.text_layer_name_prepare,
                        contents=self.layout.name_prepare,
                        reference=self.text_layer_mana_prepare,
                    )
                )
            if self.text_layer_rules_prepare:
                self.text.append(
                    text_classes.FormattedTextArea(
                        layer=self.text_layer_rules_prepare,
                        contents=self.layout.oracle_text_prepare,
                        reference=self.textbox_reference_prepare,
                        flavor=self.layout.flavor_text_prepare,
                        centered=False,
                    )
                )
            if self.text_layer_type_prepare:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_type_prepare,
                        contents=self.layout.type_line_prepare,
                    )
                )

    # endregion Methods
