"""
* Templates: Token
* Treated as 'Normal' templates, separated for better organization.
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import CON
from src.enums.layers import LAYERS
import src.helpers as psd
from src.templates._core import StarterTemplate
from src.templates._cosmetic import FullartMod
import src.text_layers as text_classes
from src.utils.adobe import ReferenceLayer
from src.utils.properties import auto_prop_cached
from src.utils.strings import is_multiline

"""
* Template Classes
"""


class TokenTemplate(FullartMod, StarterTemplate):
    """A generic template for Token cards.

    Adds:
        * Support for three modes of oracle text: None, One-Line, and Full size.
        * Multiple textbox groups for different rules text layers and references.
        * A name and typeline reference that allows for scaling based on horizontal dimension.

    Modifies:
        * Only supports a singular frame layer which is the Background layer.
    """
    frame_suffix = 'Token'

    """
    * Mixin Methods
    """

    @property
    def post_text_methods(self):
        """Make some text positioning adjustments after text is formatted."""
        return [*super().post_text_methods, self.text_adjustments]

    """
    * Layers
    """

    @auto_prop_cached
    def background_layer(self) -> ArtLayer:
        """ArtLayer: Background governed by Legendary and creature checks."""
        return psd.getLayer(self.layout.pinlines, [
            LAYERS.FRAME,
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NON_LEGENDARY,
            LAYERS.CREATURE if self.is_creature else LAYERS.NON_CREATURE
        ])

    """
    * Groups
    """

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """A group containing background, text, and reference based upon oracle text requirements."""

        # Decide the textbox size
        group = LAYERS.ONE_LINE
        if not any([self.layout.oracle_text, self.layout.flavor_text]):
            # No card text
            group = LAYERS.NONE
        if all([self.layout.oracle_text, self.layout.flavor_text]):
            # Both rules and flavor text
            group = LAYERS.FULL
        if any(is_multiline([self.layout.oracle_text, self.layout.flavor_text])):
            # Multi-line text
            group = LAYERS.FULL
        if len(self.layout.oracle_text) > 50:
            # Long rules text
            group = LAYERS.FULL

        # Enable and return group
        group = psd.getLayerSet(group, LAYERS.TEXTBOX)
        group.visible = True
        return group

    """
    * References
    """

    @auto_prop_cached
    def textbox_reference(self) -> ReferenceLayer:
        """Pull from the textbox group."""
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.textbox_group)

    @auto_prop_cached
    def type_line_reference(self) -> ReferenceLayer:
        """Reference to scale the TypeLine."""
        return psd.get_reference_layer(LAYERS.TYPE_LINE_REFERENCE, self.textbox_group)

    @auto_prop_cached
    def name_reference(self) -> ReferenceLayer:
        """Reference to scale the Card Name"""
        if self.is_legendary:
            return psd.get_reference_layer(LAYERS.NAME_REFERENCE_LEGENDARY, self.text_group)
        return psd.get_reference_layer(LAYERS.NAME_REFERENCE_NON_LEGENDARY, self.text_group)

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_type(self) -> ArtLayer:
        """Pull from the textbox group."""
        return psd.getLayer(LAYERS.TYPE_LINE, self.textbox_group)

    @auto_prop_cached
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Full textbox group has both creature and non-creature option."""
        if self.textbox_group.name == LAYERS.FULL:
            return psd.getLayer(
                LAYERS.RULES_TEXT_CREATURE if (
                    self.is_creature
                ) else LAYERS.RULES_TEXT_NONCREATURE,
                self.textbox_group
            )
        return psd.getLayer(LAYERS.RULES_TEXT, self.textbox_group)

    """
    * Methods
    """

    def expansion_symbol(self) -> None:
        """Does not support expansion symbol."""
        pass

    def enable_frame_layers(self) -> None:
        """Only need to enable the background layer."""
        if self.background_layer:
            self.background_layer.visible = True

    def basic_text_layers(self) -> None:
        """Don't include the mana cost in basic text layers."""
        self.text.extend([
            text_classes.ScaledWidthTextField(
                layer=self.text_layer_name,
                contents=self.layout.name,
                reference=self.name_reference
            ),
            text_classes.ScaledWidthTextField(
                layer=self.text_layer_type,
                contents=self.layout.type_line,
                reference=self.type_reference
            )
        ])

    def rules_text_and_pt_layers(self) -> None:
        """3 rules text modes: None, One-Line, and Full"""

        # Adjust the default linebreak lead
        CON.line_break_lead = 3

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
                    scale_width=True,
                    centered=True
                )
            )
        elif self.textbox_group.name == LAYERS.FULL:
            self.text.append(
                text_classes.FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    color=psd.rgb_white(),
                    flavor=self.layout.flavor_text,
                    reference=self.textbox_reference,
                    centered=True
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

    def text_adjustments(self) -> None:

        # Vertically center the name after it's been scaled
        psd.align_all(self.text_layer_name, self.name_reference)

        # Align the typeline and rules
        psd.align_horizontal(self.text_layer_type, self.type_line_reference)
        if self.textbox_reference and self.text_layer_rules:
            psd.align_horizontal(self.text_layer_rules, self.textbox_reference.dims)
