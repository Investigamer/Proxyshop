"""
* Helpers: Masks
"""
# Standard Library Imports
from typing import Union

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.helpers.layers import select_layer

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
* Copying Masks
"""


def copy_layer_mask(
    layer_from: Union[ArtLayer, LayerSet],
    layer_to: Union[ArtLayer, LayerSet]
) -> None:
    """Copies mask from one layer to another.

    Args:
        layer_from: Layer to copy from.
        layer_to: Layer to copy to.
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
    APP.executeAction(sID("make"), desc1, NO_DIALOG)


def copy_vector_mask(
    layer_from: Union[ArtLayer, LayerSet],
    layer_to: Union[ArtLayer, LayerSet]
) -> None:
    """Copies vector mask from one layer to another.

    Args:
        layer_from: Layer to copy from.
        layer_to: Layer to copy to.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref3 = ActionReference()
    ref1.putClass(sID("path"))
    desc1.putReference(sID("target"),  ref1)
    ref2.putEnumerated(sID("path"), sID("path"), sID("vectorMask"))
    ref2.putIdentifier(sID("layer"),  layer_to.id)
    desc1.putReference(sID("at"),  ref2)
    ref3.putEnumerated(sID("path"), sID("path"), sID("vectorMask"))
    ref3.putIdentifier(sID("layer"), layer_from.id)
    desc1.putReference(sID("using"),  ref3)
    APP.executeAction(sID("make"), desc1, NO_DIALOG)


"""
* Applying Masks
"""


def apply_mask_to_layer_fx(layer: Union[ArtLayer, LayerSet] = None) -> None:
    """Sets the layer mask to apply only to layer effects in blending options.

    Args:
        layer: ArtLayer or LayerSet object.
    """
    if not layer:
        layer = APP.activeDocument.activeLayer
    ref = ActionReference()
    ref.putIdentifier(sID("layer"), layer.id)
    desc = APP.executeActionGet(ref)
    layer_fx = desc.getObjectValue(sID('layerEffects'))
    layer_fx.putBoolean(sID("layerMaskAsGlobalMask"), True)
    desc = ActionDescriptor()
    desc.putReference(sID("target"), ref)
    desc.putObject(sID("to"), sID("layer"), layer_fx)
    APP.executeAction(sID("set"), desc,  NO_DIALOG)


def set_layer_mask(
    layer: Union[ArtLayer, LayerSet, None] = None,
    visible: bool = True
) -> None:
    """Set the visibility of a layer's mask.

    Args:
        layer: ArtLayer object.
        visible: Whether to make the layer mask visible.
    """
    if not layer:
        layer = APP.activeDocument.activeLayer
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(cID("Lyr "), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putBoolean(cID("UsrM"), visible)
    desc1.putObject(cID("T   "), cID("Lyr "), desc2)
    APP.executeAction(cID("setd"), desc1, NO_DIALOG)


def enable_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """Enables a given layer's mask.

    Args:
        layer: ArtLayer object.
    """
    set_layer_mask(layer, True)


def disable_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """Disables a given layer's mask.

    Args:
        layer: ArtLayer object.
    """
    set_layer_mask(layer, False)


def apply_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """Applies a given layer's mask.

    Args:
        layer: ArtLayer or LayerSet object, use active layer if not provided.
    """
    if layer:
        select_layer(layer)
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putEnumerated(sID("channel"), sID("channel"), sID("mask"))
    desc1.putReference(sID("target"),  ref1)
    desc1.putBoolean(sID("apply"), True)
    APP.executeAction(sID("delete"), desc1, NO_DIALOG)


def set_layer_vector_mask(
    layer: Union[ArtLayer, LayerSet, None] = None,
    visible: bool = False
) -> None:
    """Set the visibility of a layer's vector mask.

    Args:
        layer: ArtLayer object.
        visible: Whether to make the vector mask visible.
    """
    if not layer:
        layer = APP.activeDocument.activeLayer
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putBoolean(sID("vectorMaskEnabled"), visible)
    desc1.putObject(sID("to"), sID("layer"), desc2)
    APP.executeAction(sID("set"), desc1, NO_DIALOG)


def enable_vector_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """Enables a given layer's vector mask.

    Args:
        layer: ArtLayer object.
    """
    set_layer_vector_mask(layer, True)


def disable_vector_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """Disables a given layer's vector mask.

    Args:
        layer: ArtLayer object.
    """
    set_layer_vector_mask(layer, False)


"""
* Removing Masks
"""


def delete_mask(layer: Union[ArtLayer, LayerSet, None] = None) -> None:
    """Removes a given layer's mask.

    Args:
        layer: ArtLayer ore LayerSet object, use active layer if not provided.
    """
    if layer:
        APP.activeDocument.activeLayer = layer
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putEnumerated(sID("channel"), sID("ordinal"), sID("targetEnum"))
    desc1.putReference(sID("target"), ref1)
    APP.executeAction(sID("delete"), desc1, NO_DIALOG)
