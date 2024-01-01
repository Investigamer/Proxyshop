"""
* Templates: Prototype
"""
# Standard Library
from typing import Optional, Callable

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src import CFG
from src.enums.layers import LAYERS
import src.helpers as psd
from src.layouts import PrototypeLayout
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.utils.properties import auto_prop_cached

"""
* Modifier Classes
"""


class PrototypeMod (NormalTemplate):
    """
    * A modifier for Prototype cards introduced in The Brothers' War.

    Adds:
        * Textbox, manabox, and PT for Prototype casting case.
        * Description, mana cost, and PT text layers for Prototype casting case.
    """

    @auto_prop_cached
    def text_layer_methods(self) -> list[Callable]:
        """Add Prototype text layers."""
        funcs = [self.text_layers_prototype] if isinstance(self.layout, PrototypeLayout) else []
        return [*super().text_layer_methods, *funcs]

    @auto_prop_cached
    def frame_layer_methods(self) -> list[Callable]:
        """Enable Prototype frame layers."""
        funcs = [self.frame_layers_prototype] if isinstance(self.layout, PrototypeLayout) else []
        return [*super().frame_layer_methods, *funcs]

    """
    LAYERS
    """

    @auto_prop_cached
    def proto_textbox_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_TEXTBOX)

    @auto_prop_cached
    def proto_manabox_layer(self) -> Optional[ArtLayer]:
        if self.layout.proto_mana_cost.count('{') == 2:
            return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_MANABOX_SMALL)
        return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_MANABOX_MEDIUM)

    @auto_prop_cached
    def proto_pt_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.proto_color, LAYERS.PROTO_PTBOX)

    """
    TEXT LAYERS
    """

    @auto_prop_cached
    def text_layer_proto(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_RULES, self.text_group)

    @auto_prop_cached
    def text_layer_proto_mana(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_MANA_COST, self.text_group)

    @auto_prop_cached
    def text_layer_proto_pt(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_PT, self.text_group)

    """
    METHODS
    """

    def text_layers_prototype(self):
        """Add and modify text layers required by Prototype cards."""

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
        if CFG.remove_reminder:
            self.text_layer_proto.textItem.size = psd.get_text_scale_factor(self.text_layer_proto) * 9
            self.text.append(
                text_classes.FormattedTextArea(
                    layer = self.text_layer_proto,
                    contents = 'Prototype',
                    reference = self.proto_textbox_layer
                )
            )

    def frame_layers_prototype(self):
        """Enable layers required by Prototype cards."""

        # Add prototype layers
        if self.proto_textbox_layer:
            self.proto_textbox_layer.visible = True
        if self.proto_manabox_layer:
            self.proto_manabox_layer.parent.visible = True
            self.proto_manabox_layer.visible = True
        if self.proto_pt_layer:
            self.proto_pt_layer.visible = True


"""
* Template Classes
"""


class PrototypeTemplate(PrototypeMod, NormalTemplate):
    """A raster template for Prototype cards introduced in The Brothers' War."""
