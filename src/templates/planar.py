"""
* PLANAR TEMPLATES
"""

from functools import cached_property

from photoshop.api._artlayer import ArtLayer

import src.helpers as psd
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import NormalLayout
from src.templates._core import StarterTemplate

"""
* Template Classes
"""


class PlanarTemplate(StarterTemplate):
    """Planar template for Planar and Phenomenon cards introduced in the Planechase block.

    Todo:
        Needs a complete rework and a 'Modifier' class.
    """

    def __init__(self, layout: NormalLayout):
        super().__init__(layout)
        self.config.exit_early = True

    @cached_property
    def text_layer_static_ability(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.STATIC_ABILITY, self.text_group)

    @cached_property
    def text_layer_chaos_ability(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.CHAOS_ABILITY, self.text_group)

    def basic_text_layers(self):
        """No mana cost, don't scale name layer."""
        if self.text_layer_name:
            self.text.append(
                text_classes.TextField(
                    layer=self.text_layer_name, contents=self.layout.name
                )
            )
        if self.text_layer_type:
            self.text.append(
                text_classes.ScaledTextField(
                    layer=self.text_layer_type,
                    contents=self.layout.type_line,
                    reference=self.type_reference,
                )
            )

    def rules_text_and_pt_layers(self):
        # Phenomenon card?
        if self.layout.type_line == LAYERS.PHENOMENON:
            # Insert oracle text into static ability layer and disable chaos ability & layer mask on textbox
            if self.text_layer_static_ability:
                self.text.append(
                    text_classes.FormattedTextField(
                        layer=self.text_layer_static_ability,
                        contents=self.layout.oracle_text,
                    )
                )
            psd.enable_mask(psd.getLayerSet(LAYERS.TEXTBOX))
            if layer := psd.getLayer(LAYERS.CHAOS_SYMBOL, self.text_group):
                layer.visible = False
            if self.text_layer_chaos_ability:
                self.text_layer_chaos_ability.visible = False

        else:
            # Split oracle text on last line break, insert everything before into static, the rest into chaos
            linebreak_index = self.layout.oracle_text.rindex("\n")
            if self.text_layer_static_ability:
                self.text.append(
                    text_classes.FormattedTextField(
                        layer=self.text_layer_static_ability,
                        contents=self.layout.oracle_text[0:linebreak_index],
                    )
                )
            if self.text_layer_chaos_ability:
                self.text.append(
                    text_classes.FormattedTextField(
                        layer=self.text_layer_chaos_ability,
                        contents=self.layout.oracle_text[linebreak_index + 1 :],
                    )
                )

    def paste_scryfall_scan(
        self, rotate: bool = False, visible: bool = False
    ) -> ArtLayer | None:
        """Ensure we rotate the scan for Planar cards."""
        return super().paste_scryfall_scan(rotate=True, visible=visible)
