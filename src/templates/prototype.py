"""
* Templates: Prototype
"""
# Standard Library
from typing import Callable

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import CFG
from src.enums.layers import LAYERS
import src.helpers as psd
from src.layouts import PrototypeLayout
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.utils.adobe import ReferenceLayer
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

    """
    * Mixin Methods
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
    * Prototype References
    """

    @auto_prop_cached
    def prototype_reference(self) -> ReferenceLayer:
        """ReferenceLayer: Reference used to size and position the prototype text."""
        return self.proto_textbox_layer

    """
    * Prototype Groups
    """

    @auto_prop_cached
    def proto_manabox_group(self) -> LayerSet:
        """LayerSet: Layer group containing the colors and shape for the Prototype mana box."""
        return psd.getLayerSet(LAYERS.PROTO_MANABOX, self.docref)

    @auto_prop_cached
    def proto_textbox_group(self) -> LayerSet:
        """LayerSet: Layer group containing textures for the Prototype textbox."""
        return psd.getLayerSet(LAYERS.PROTO_TEXTBOX, self.docref)

    @auto_prop_cached
    def proto_pt_group(self) -> LayerSet:
        """LayerSet: Layer group containing textures for the Prototype PT box."""
        return psd.getLayerSet(LAYERS.PROTO_PTBOX, self.docref)

    """
    * Prototype Shapes
    """

    @auto_prop_cached
    def proto_manabox_shape(self) -> ArtLayer:
        """ArtLayer: Vector shape containing the Prototype mana text."""
        size = '2' if self.layout.proto_mana_cost.count('{') <= 2 else '3'
        return psd.getLayer(size, [self.proto_manabox_group, LAYERS.SHAPE])

    """
    * Prototype Layers
    """

    @auto_prop_cached
    def proto_textbox_layer(self) -> ReferenceLayer:
        """ReferenceLayer: Colored and outlined box containing the Prototype ability text."""
        return psd.get_reference_layer(
            self.layout.proto_color,
            self.proto_textbox_group)

    @auto_prop_cached
    def proto_manabox_layer(self) -> ArtLayer:
        """ArtLayer: Solid color adjustment layer used to color the Prototype manabox."""
        return psd.getLayer(
            self.layout.proto_color,
            self.proto_manabox_group)

    @auto_prop_cached
    def proto_pt_layer(self) -> ArtLayer:
        """ArtLayer: Box for the P/T of the Prototype version of this card."""
        return psd.getLayer(
            self.layout.proto_color,
            self.proto_pt_group)

    """
    * Prototype Text Layers
    """

    @auto_prop_cached
    def text_layer_proto(self) -> ArtLayer:
        """ArtLayer: Text layer containing the Prototype rules text."""
        return psd.getLayer(LAYERS.PROTO_RULES, self.text_group)

    @auto_prop_cached
    def text_layer_proto_mana(self) -> ArtLayer:
        """ArtLayer: Text layer containing the Prototype mana cost."""
        return psd.getLayer(LAYERS.PROTO_MANA_COST, self.text_group)

    @auto_prop_cached
    def text_layer_proto_pt(self) -> ArtLayer:
        """ArtLayer: Text layer containing the Prototype power/toughness."""
        return psd.getLayer(LAYERS.PROTO_PT, self.text_group)

    """
    * Prototype Frame Layers
    """

    def frame_layers_prototype(self):
        """Enable layers required by Prototype cards."""

        # Prototype Textbox
        if self.proto_textbox_layer:
            self.proto_textbox_layer.visible = True

        # Prototype Mana Box
        if self.proto_manabox_layer:
            self.proto_manabox_shape.visible = True
            self.proto_manabox_layer.visible = True

        # Prototype PT
        if self.proto_pt_layer:
            self.proto_pt_layer.visible = True

    """
    * Prototype Text Layers
    """

    def text_layers_prototype(self):
        """Add and modify text layers required by Prototype cards."""

        # Add prototype PT and Mana Cost
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_proto_mana,
                contents = self.layout.proto_mana_cost),
            text_classes.TextField(
                layer = self.text_layer_proto_pt,
                contents = self.layout.proto_pt)])

        # Remove reminder text if necessary
        if CFG.remove_reminder:
            self.text_layer_proto.textItem.size = psd.get_text_scale_factor(self.text_layer_proto) * 9
            self.text.append(
                text_classes.FormattedTextArea(
                    layer = self.text_layer_proto,
                    contents = 'Prototype',
                    reference = self.prototype_reference))


"""
* Template Classes
"""


class PrototypeTemplate(PrototypeMod, NormalTemplate):
    """A raster template for Prototype cards introduced in The Brothers' War."""
