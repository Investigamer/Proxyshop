"""
* TOKEN TEMPLATES
"""
# Standard Library Imports
from typing import Optional
from functools import cached_property

# Third Party Imports
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._core import StarterTemplate
from src.utils.strings import is_multiline
import src.text_layers as text_classes
from src.templates import FullartMod
from src.enums.layers import LAYERS
from src.constants import con
import src.helpers as psd


class TokenTemplate(FullartMod, StarterTemplate):
    """
    * A template for Token cards.
    * Allows for three types of oracle text: None, One-Line, and Full size.

    Adds:
        * Multiple textbox groups for different rules text layers and references.
        * A name and typeline reference that allows for scaling based on horizontal dimension.
    Modifies:
        * Only supports a singular frame layer which is the Background layer.
    """
    frame_suffix = 'Token'

    """
    * Layers
    """

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        # Background is based on Legendary toggle as well as Creature toggle
        return psd.getLayer(self.layout.pinlines, [
            LAYERS.FRAME,
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NON_LEGENDARY,
            LAYERS.CREATURE if self.is_creature else LAYERS.NON_CREATURE
        ])

    """
    GROUPS
    """

    @cached_property
    def textbox_group(self) -> LayerSet:
        """A group containing background, text, and reference based upon oracle text requirements."""
        if not self.layout.oracle_text and not self.layout.flavor_text:
            # No Rules Text
            group = LAYERS.NONE
        elif not any(is_multiline([self.layout.oracle_text, self.layout.flavor_text])) and (
            not self.layout.oracle_text or not self.layout.flavor_text
        ) and len(self.layout.rules_text) <= 50:
            # One Line Rules Text
            group = LAYERS.ONE_LINE
        else:
            # Full Sized Rules Text
            group = LAYERS.FULL
        group = psd.getLayerSet(group, LAYERS.TEXTBOX)
        group.visible = True
        return group

    """
    REFERENCES
    """

    @property
    def art_reference(self) -> ArtLayer:
        # Only one frame for art reference
        return psd.getLayer(LAYERS.ART_FRAME)

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        # Pull from the textbox group
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE, self.textbox_group)

    @cached_property
    def type_line_reference(self) -> ArtLayer:
        """Reference to scale the TypeLine."""
        return psd.getLayer(LAYERS.TYPE_LINE_REFERENCE, self.textbox_group)

    @cached_property
    def name_reference(self) -> ArtLayer:
        """Reference to scale the Card Name"""
        if self.is_legendary:
            return psd.getLayer(LAYERS.NAME_REFERENCE_LEGENDARY, self.text_group)
        return psd.getLayer(LAYERS.NAME_REFERENCE_NON_LEGENDARY, self.text_group)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_type(self) -> ArtLayer:
        # Pull from the textbox group
        return psd.getLayer(LAYERS.TYPE_LINE, self.textbox_group)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # Full textbox group has both creature and noncreature option
        if self.textbox_group.name == LAYERS.FULL:
            return psd.getLayer(
                LAYERS.RULES_TEXT_CREATURE if (
                    self.is_creature
                ) else LAYERS.RULES_TEXT_NONCREATURE,
                self.textbox_group
            )
        return psd.getLayer(LAYERS.RULES_TEXT, self.textbox_group)

    """
    METHODS
    """

    def expansion_symbol(self) -> None:
        # Does not support expansion symbol
        pass

    def enable_frame_layers(self) -> None:
        # Only need to enable the background layer
        if self.background_layer:
            self.background_layer.visible = True

    def basic_text_layers(self) -> None:
        # Don't include the mana cost in basic text layers
        self.text.extend([
            text_classes.ScaledWidthTextField(
                layer = self.text_layer_name,
                contents = self.layout.name,
                reference = self.name_reference
            ),
            text_classes.ScaledWidthTextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line,
                reference = self.type_line_reference
            )
        ])

    def rules_text_and_pt_layers(self) -> None:
        # Adjust the default linebreak lead
        con.line_break_lead = 3

        # Rules Text
        if self.textbox_group.name == LAYERS.ONE_LINE:
            self.text.append(
                text_classes.FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    color=psd.rgb_white(),
                    flavor=self.layout.flavor_text,
                    reference=self.textbox_reference,
                    scale_height=False,
                    scale_width=True
                )
            )
        elif self.textbox_group.name == LAYERS.FULL:
            self.text.append(
                text_classes.FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    color=psd.rgb_white(),
                    flavor=self.layout.flavor_text,
                    reference=self.textbox_reference
                )
            )

        # PT Layer
        if self.is_creature:
            # Enable cutout
            psd.enable_vector_mask(self.textbox_group.parent)
            self.text.append(
                text_classes.TextField(
                    layer=self.text_layer_pt,
                    contents=f"{self.layout.power}/{self.layout.toughness}"
                )
            )
        else:
            self.text_layer_pt.visible = False

    def post_text_layers(self) -> None:
        # Vertically center the name after it's been scaled
        psd.align_all(self.text_layer_name, self.name_reference)

        # Align the typeline and rules
        psd.align_horizontal(self.text_layer_type, self.type_line_reference)
        if self.textbox_reference and self.text_layer_rules:
            psd.align_horizontal(self.text_layer_rules, self.textbox_reference)
