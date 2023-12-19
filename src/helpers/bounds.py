"""
* Helpers: Bounds and Dimensions
"""
# Standard Library Imports
from typing import Union, TypedDict

# Third Party Imports
from photoshop.api import DialogModes, ActionReference, ElementPlacement, RasterizeType, LayerKind
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.helpers.document import undo_action
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Types
"""

# Layer bounds: left, top, right, bottom
LayerBounds = list[int, int, int, int]


class LayerDimensions(TypedDict):
    """Calculated layer dimension info for a layer."""
    width: int
    height: int
    center_x: int
    center_y: int
    left: int
    right: int
    top: int
    bottom: int


class TextboxDimensions(TypedDict):
    """Calculated width and height of paragraph text layer bounding box."""
    width: int
    height: int


"""
* Funcs
"""


def get_bounds_no_effects(layer: Union[ArtLayer, LayerSet]) -> LayerBounds:
    """Returns the bounds of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        list: Pixel location top left, top right, bottom left, bottom right.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = APP.executeActionGet(reference)
    try:
        bounds = descriptor.getObjectValue(sID('boundsNoEffects'))
    except PS_EXCEPTIONS:
        bounds = descriptor.getObjectValue(sID('bounds'))
    return [
        bounds.getInteger(sID('left')),
        bounds.getInteger(sID('top')),
        bounds.getInteger(sID('right')),
        bounds.getInteger(sID('bottom'))
    ]


def get_dimensions_from_bounds(bounds: list) -> type[LayerDimensions]:
    """Compute width and height based on a set of bounds given.

    Args:
        bounds: List of bounds given.

    Returns:
        Dict containing height, width, and positioning locations.
    """
    width = int(bounds[2]-bounds[0])
    height = int(bounds[3]-bounds[1])
    return LayerDimensions(
        width=width,
        height=height,
        center_x=round((width / 2) + bounds[0]),
        center_y=round((height / 2) + bounds[1]),
        left=int(bounds[0]), right=int(bounds[2]),
        top=int(bounds[1]), bottom=int(bounds[3])
    )


def get_dimensions_no_effects(layer: Union[ArtLayer, LayerSet]) -> type[LayerDimensions]:
    """Compute the dimensions of a layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    bounds = get_bounds_no_effects(layer)
    return get_dimensions_from_bounds(bounds)


def get_layer_dimensions(layer: Union[ArtLayer, LayerSet]) -> type[LayerDimensions]:
    """Compute the width and height dimensions of a layer.

    Args:
        layer: A layer object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    return get_dimensions_from_bounds(layer.bounds)


def check_textbox_overflow(layer: ArtLayer) -> bool:
    """Check if a TextLayer overflows the bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        True if text overflowing, else False.
    """
    if layer.kind != LayerKind.TextLayer:
        return False

    # Create a test layer to check the difference
    height = get_text_layer_dimensions(layer)['height']
    layer.textItem.height = 1000
    dif = get_text_layer_dimensions(layer)['height'] - height
    undo_action()
    if dif > 0:
        return True
    return False


def get_text_layer_bounds(layer: ArtLayer, legacy: bool = False) -> LayerBounds:
    """Returns a list of the text layer's bounds [left, top, right, bottom].

    Notes:
        DEPRECATED — Might have been useful on older versions of Photoshop where bounds
            of text layers were not accurately reported?

    Args:
        layer: Layer to get the bounds of.
        legacy: Force old way for legacy Photoshop versions.

    Returns:
        List of the bounds of a given layer.
    """
    if legacy or int(APP.version[0:2]) < 21:
        layer_copy = layer.duplicate(APP.activeDocument, ElementPlacement.PlaceInside)
        layer_copy.rasterize(RasterizeType.TextContents)
        layer_bounds = layer.bounds
        layer_copy.remove()
        return layer_bounds
    return layer.bounds


def get_textbox_bounds(layer: ArtLayer) -> LayerBounds:
    """Get the bounds of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        List of bounds integers.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = APP.executeActionGet(reference)
    bounds = descriptor.getObjectValue(sID('boundingBox'))
    return [
        bounds.getInteger(sID('left')),
        bounds.getInteger(sID('top')),
        bounds.getInteger(sID('right')),
        bounds.getInteger(sID('bottom'))
    ]


def get_textbox_dimensions(layer: ArtLayer) -> type[TextboxDimensions]:
    """Get the dimensions of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        Dict containing width and height.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = APP.executeActionGet(reference)
    bounds = descriptor.getObjectValue(sID('boundingBox'))
    return {
        'width': bounds.getInteger(sID('width')),
        'height': bounds.getInteger(sID('height'))
    }


def get_text_layer_dimensions(layer, legacy: bool = False) -> type[LayerDimensions]:
    """Return an object with the specified text layer's width and height, on some versions of Photoshop
    a text layer must be rasterized before pulling accessing its true bounds.

    Args:
        layer: Layer to get the dimensions of.
        legacy: Force old way for legacy text layers.

    Returns:
        Dict containing height and width of the given layer.
    """
    if legacy or int(APP.version[0:2]) < 21:
        layer_copy = layer.duplicate(APP.activeDocument, ElementPlacement.PlaceInside)
        layer_copy.rasterize(RasterizeType.TextContents)
        dimensions = get_dimensions_from_bounds(layer_copy.bounds)
        layer_copy.remove()
        return dimensions
    return get_dimensions_from_bounds(layer.bounds)
