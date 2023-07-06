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
from src.settings import cfg
import src.helpers as psd


class PrototypeTemplate (NormalTemplate):
    """
    * A template for Prototype cards introduced in The Brothers' War.

    Adds:
        * Textbox, manabox, and PT for Prototype casting case.
        * Description, mana cost, and PT text layers for Prototype casting case.
    """

    """
    LAYERS
    """

    @cached_property
    def proto_textbox_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_TEXTBOX)

    @cached_property
    def proto_manabox_layer(self) -> Optional[ArtLayer]:
        if self.layout.proto_mana_cost.count('{') == 2:
            return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_MANABOX_SMALL)
        return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_MANABOX_MEDIUM)

    @cached_property
    def proto_pt_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_PTBOX)

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
                contents = self.layout.proto_mana_cost
            ),
            text_classes.TextField(
                layer = self.text_layer_proto_pt,
                contents = self.layout.proto_pt
            )
        ])

        # Remove reminder text if necessary
        if cfg.remove_reminder:
            self.text_layer_proto.textItem.size = psd.get_text_scale_factor(self.text_layer_proto) * 9
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
            self.proto_manabox_layer.parent.visible = True
            self.proto_manabox_layer.visible = True
        if self.proto_pt_layer:
            self.proto_pt_layer.visible = True
