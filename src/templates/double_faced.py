"""
* DOUBLE FACED TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src.templates._core import NormalTemplate
from src.enums.photoshop import Dimensions
from src.enums.mtg import TransformIcons
import src.text_layers as text_classes
from src.enums.layers import LAYERS
import src.helpers as psd


class TransformTemplate (NormalTemplate):
    """
    * Template for double faced Transform cards introduced in Innistrad block.

    Adds:
        * Flipside power/toughness on the front if opposite side is a Creature.
        * Transform icon, inherited from BaseTemplate, is made visible.
    Modifies:
        * Rules text layer has 2 new options: a creature and noncreature option with flipside PT cutout.
        * PT, name, and type text are all white UNLESS this is an eldrazi, e.g. Eldritch Moon transform cards.
    """

    @cached_property
    def has_flipside_pt(self) -> bool:
        """Whether this card should display flipside Power/Toughness."""
        return bool(self.is_front and self.is_flipside_creature)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # Does it have flipside PT cutout?
        if self.has_flipside_pt:
            if self.is_creature:
                return psd.getLayer(LAYERS.RULES_TEXT_CREATURE_FLIP, self.text_group)
            # Disable PT
            if self.text_layer_pt:
                self.text_layer_pt.visible = False
            return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE_FLIP, self.text_group)
        return super().text_layer_rules

    def enable_frame_layers(self):
        # Add transform icon
        if self.transform_icon_layer:
            self.transform_icon_layer.visible = True
        super().enable_frame_layers()

    def basic_text_layers(self):
        # For eldrazi cards: Rules text, typeline, and power/toughness have black text
        if self.layout.transform_icon == TransformIcons.MOONELDRAZI:
            self.text_layer_name.textItem.color = psd.rgb_black()
            self.text_layer_type.textItem.color = psd.rgb_black()
            self.text_layer_pt.textItem.color = psd.rgb_black()
        super().basic_text_layers()

    def rules_text_and_pt_layers(self):
        # Add flipside PT
        if self.has_flipside_pt:
            self.text.append(
                text_classes.TextField(
                    layer=psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_group),
                    contents=str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness)
                )
            )
        super().rules_text_and_pt_layers()


class MDFCTemplate (NormalTemplate):
    """
    * Template for Modal Double Faced cards.

    Adds:
        * MDFC Left text layer (back side type)
        * MDFC Right text layer (back side cost, or land tap ability)
        * Top (arrow icon) and bottom (back side info) MDFC layer elements
    """

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        """The back face card type."""
        return psd.getLayer(LAYERS.LEFT, self.dfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        """The back face mana cost or land tap ability."""
        return psd.getLayer(LAYERS.RIGHT, self.dfc_group)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add mdfc text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_mdfc_right,
                contents = self.layout.other_face_right
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_mdfc_left,
                contents = self.layout.other_face_left,
                reference = self.text_layer_mdfc_right,
            )
        ])

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # MDFC elements at the top and bottom of the card
        psd.getLayer(
            self.twins,
            psd.getLayerSet(LAYERS.TOP, self.dfc_group)
        ).visible = True
        psd.getLayer(
            self.layout.other_face_twins,
            psd.getLayerSet(LAYERS.BOTTOM, self.dfc_group)
        ).visible = True


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
            text_classes.TextField(
                layer = self.text_layer_name,
                contents = self.layout.name
            ),
            text_classes.TextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line
            )
        ])

    def enable_frame_layers(self):
        # Only background frame layer
        self.background_layer.visible = True
