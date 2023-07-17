"""
MASK HELPERS
"""
# Standard Library Imports
from typing import Union

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.constants import con

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


def copy_layer_mask(
    layer_from: Union[ArtLayer, LayerSet],
    layer_to: Union[ArtLayer, LayerSet]
) -> None:
    """
    Copies layer mask from one layer to another.
    @param layer_from: Layer to copy from.
    @param layer_to: Layer to copy to.
    """
    desc1 = ActionDescriptor()
    ref17 = ActionReference()
    ref18 = ActionReference()
    desc1.putClass(sID("new"), sID("channel"))
    ref17.putEnumerated(sID("channel"), sID("channel"), sID("mask"))
    ref17.putIdentifier(sID("layer"), layer_to.id)
    desc1.putReference(sID("at"), ref17)
    ref18.putEnumerated(sID("channel"), sID("channel"), sID("mask"))
    ref18.putIdentifier(sID("layer"), layer_from.id)
    desc1.putReference(sID("using"), ref18)
    app.executeAction(sID("make"), desc1, NO_DIALOG)


def apply_mask_to_layer_fx(layer: Union[ArtLayer, LayerSet] = None) -> None:
    """
    Sets the layer mask to apply only to layer effects in blending options.
    @param layer: ArtLayer or LayerSet object.
    """
    if not layer:
        layer = app.activeDocument.activeLayer
    ref = ActionReference()
    ref.putIdentifier(sID("layer"), layer.id)
    desc = app.executeActionGet(ref)
    layer_fx = desc.getObjectValue(sID('layerEffects'))
    layer_fx.putBoolean(sID("layerMaskAsGlobalMask"), True)
    desc = ActionDescriptor()
    desc.putReference(sID("target"), ref)
    desc.PutObject(sID("to"), sID("layer"), layer_fx)
    app.executeAction(sID("set"), desc,  NO_DIALOG)


def set_layer_mask(
    layer: Union[ArtLayer, LayerSet, None] = None,
    visible: bool = True
) -> None:
    """
    Set the visibility of a layer's mask.
    @param layer: ArtLayer object.
    @param visible: Whether to make the layer mask visible.
    """
    if not layer:
        layer = app.activeDocument.activeLayer
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(cID("Lyr "), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putBoolean(cID("UsrM"), visible)
    desc1.putObject(cID("T   "), cID("Lyr "), desc2)
    app.executeAction(cID("setd"), desc1, NO_DIALOG)


def enable_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """
    Enables a given layer's mask.
    @param layer: ArtLayer object.
    """
    set_layer_mask(layer, True)


def disable_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """
    Disables a given layer's mask.
    @param layer: ArtLayer object.
    """
    set_layer_mask(layer, False)


def delete_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """
    Removes a given layer's mask.
    @param layer: ArtLayer ore LayerSet object, use active layer if not provided.
    """
    if layer:
        app.activeDocument.activeLayer = layer
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutEnumerated(sID("channel"), sID("ordinal"), sID("targetEnum"))
    desc1.PutReference(sID("target"), ref1)
    app.executeAction(sID("delete"), desc1, NO_DIALOG)


def set_layer_vector_mask(
    layer: Union[ArtLayer, LayerSet, None] = None,
    visible: bool = False
) -> None:
    """
    Set the visibility of a layer's vector mask.
    @param layer: ArtLayer object.
    @param visible: Whether to make the vector mask visible.
    """
    if not layer:
        layer = app.activeDocument.activeLayer
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putBoolean(sID("vectorMaskEnabled"), visible)
    desc1.putObject(sID("to"), sID("layer"), desc2)
    app.executeAction(sID("set"), desc1, NO_DIALOG)


def enable_vector_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """
    Enables a given layer's vector mask.
    @param layer: ArtLayer object.
    """
    set_layer_vector_mask(layer, True)


def disable_vector_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """
    Disables a given layer's vector mask.
    @param layer: ArtLayer object.
    """
    set_layer_vector_mask(layer, False)
