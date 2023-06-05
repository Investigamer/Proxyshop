"""
* PROTOTYPE TEMPLATES
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
from src.layouts import CardLayout
from src.settings import cfg
import src.helpers as psd
from src.utils.regex import Reg


class PrototypeTemplate (NormalTemplate):
    """
    * A template for Prototype cards introduced in The Brothers' War.

    Adds:
        * Textbox, manabox, and PT for Prototype casting case.
        * Description, mana cost, and PT text layers for Prototype casting case.
    """

    def __init__(self, layout: CardLayout):

        # Split self.oracle_text between prototype text and rules text
        split_rules_text = layout.oracle_text.split("\n")
        layout.oracle_text = "\n".join(split_rules_text[1:])

        # Set up the prototype elements
        match = Reg.PROTOTYPE.match(split_rules_text[0])
        self.proto_mana_cost, self.proto_pt = match[1], match[2]
        super().__init__(layout)

    """
    PROPERTIES
    """

    @cached_property
    def proto_color(self) -> Optional[str]:
        if len(self.layout.color_identity) > 0:
            return self.layout.color_identity[0]
        return "Artifact"

    """
    FRAME LAYERS
    """

    @cached_property
    def proto_textbox_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.proto_color, LAYERS.PROTO_TEXTBOX)

    @cached_property
    def proto_manabox_layer(self) -> Optional[ArtLayer]:
        if self.proto_mana_cost.count('{') == 2:
            manabox_group = psd.getLayerSet(LAYERS.PROTO_MANABOX_SMALL)
        else:
            manabox_group = psd.getLayerSet(LAYERS.PROTO_MANABOX_MEDIUM)
        manabox_group.visible = True
        return psd.getLayer(self.proto_color, manabox_group)

    @cached_property
    def proto_pt_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.proto_color, LAYERS.PROTO_PTBOX)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_proto(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_RULES, self.text_group)

    @cached_property
    def text_layer_proto_mana(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_MANA_COST, self.text_group)

    @cached_property
    def text_layer_proto_pt(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_PT, self.text_group)

    """
    METHODS
    """

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add prototype PT and Mana Cost
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_proto_mana,
                contents = self.proto_mana_cost
            ),
            text_classes.TextField(
                layer = self.text_layer_proto_pt,
                contents = self.proto_pt
            )
        ])

        # Remove reminder text if necessary
        if cfg.remove_reminder:
            self.text_layer_proto.textItem.size = psd.get_text_scale_factor(
                self.text_layer_proto) * 8.93
            self.text.append(
                text_classes.FormattedTextArea(
                    layer = self.text_layer_proto,
                    contents = 'Prototype',
                    reference = self.proto_textbox_layer
                )
            )

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add prototype layers
        if self.proto_textbox_layer:
            self.proto_textbox_layer.visible = True
        if self.proto_manabox_layer:
            self.proto_manabox_layer.visible = True
        if self.proto_pt_layer:
            self.proto_pt_layer.visible = True
