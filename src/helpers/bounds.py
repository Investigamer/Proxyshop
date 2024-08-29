"""
* Helpers: Bounds and Dimensions
"""
# Standard Library Imports
from contextlib import suppress
from typing import Union, TypedDict

# Third Party Imports
from photoshop.api import DialogModes
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.helpers.descriptors import get_layer_action_ref
from src.helpers.document import undo_action
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Types
"""

# Layer bounds: left, top, right, bottom
LayerBounds = tuple[int, int, int, int]


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
* Dimensions and Bounds
"""


def get_dimensions_from_bounds(bounds: LayerBounds) -> type[LayerDimensions]:
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
        top=int(bounds[1]), bottom=int(bounds[3]))


def get_layer_dimensions(layer: Union[ArtLayer, LayerSet]) -> type[LayerDimensions]:
    """Compute the width and height dimensions of a layer.

    Args:
        layer: A layer object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    return get_dimensions_from_bounds(layer.bounds)


def get_layer_width(layer: Union[ArtLayer, LayerSet]) -> Union[float, int]:
    """Returns the width of a given layer.

    Args:
        layer: A layer object

    Returns:
        int: Width of the layer in pixels.
    """
    bounds = layer.bounds
    return int(bounds[2]-bounds[0])


def get_layer_height(layer: Union[ArtLayer, LayerSet]) -> Union[float, int]:
    """Returns the height of a given layer.

    Args:
        layer: A layer object

    Returns:
        int: Height of the layer in pixels.
    """
    bounds = layer.bounds
    return int(bounds[3]-bounds[1])


"""
* Bounds and Dimensions, No Effects
"""


def get_bounds_no_effects(layer: Union[ArtLayer, LayerSet]) -> LayerBounds:
    """Returns the bounds of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        list: Pixel location top left, top right, bottom left, bottom right.
    """
    with suppress(Exception):
        d = get_layer_action_ref(layer)
        try:
            # Try getting bounds no effects
            bounds = d.getObjectValue(sID('boundsNoEffects'))
        except PS_EXCEPTIONS:
            # Try getting bounds
            bounds = d.getObjectValue(sID('bounds'))
        return (
            bounds.getInteger(sID('left')),
            bounds.getInteger(sID('top')),
            bounds.getInteger(sID('right')),
            bounds.getInteger(sID('bottom')))
    # Fallback to layer object bounds property
    return layer.bounds


def get_dimensions_no_effects(layer: Union[ArtLayer, LayerSet]) -> type[LayerDimensions]:
    """Compute the dimensions of a layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    bounds = get_bounds_no_effects(layer)
    return get_dimensions_from_bounds(bounds)


def get_width_no_effects(layer: Union[ArtLayer, LayerSet]) -> int:
    """Returns the width of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        int: Width of the layer in pixels.
    """
    with suppress(Exception):
        # Try getting bounds no effects
        d = get_layer_action_ref(layer)
        bounds = d.getObjectValue(sID('boundsNoEffects'))
        return bounds.getInteger(sID('right')) - bounds.getInteger(sID('left'))
    return get_layer_width(layer)


def get_height_no_effects(layer: Union[ArtLayer, LayerSet]) -> int:
    """Returns the height of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        int: Height of the layer in pixels.
    """
    with suppress(Exception):
        # Try getting bounds no effects
        d = get_layer_action_ref(layer)
        bounds = d.getObjectValue(sID('boundsNoEffects'))
        return bounds.getInteger(sID('bottom')) - bounds.getInteger(sID('top'))
    return get_layer_height(layer)


"""
* Text Layer Dimensions
"""


def check_textbox_overflow(layer: ArtLayer) -> bool:
    """Check if a TextLayer overflows the bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        True if text overflowing, else False.
    """
    # Create a test layer to check the difference
    height = get_layer_dimensions(layer)['height']
    layer.textItem.height = 1000
    dif = get_layer_dimensions(layer)['height'] - height
    undo_action()
    if dif > 0:
        return True
    return False


def get_textbox_bounds(layer: ArtLayer) -> LayerBounds:
    """Get the bounds of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        List of bounds integers.
    """
    d = get_layer_action_ref(layer)
    bounds = d.getObjectValue(sID('boundingBox'))
    return (
        bounds.getInteger(sID('left')),
        bounds.getInteger(sID('top')),
        bounds.getInteger(sID('right')),
        bounds.getInteger(sID('bottom'))
    )


def get_textbox_dimensions(layer: ArtLayer) -> type[TextboxDimensions]:
    """Get the dimensions of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        Dict containing width and height.
    """
    d = get_layer_action_ref(layer)
    bounds = d.getObjectValue(sID('boundingBox'))
    return {
        'width': bounds.getInteger(sID('width')),
        'height': bounds.getInteger(sID('height'))
    }


def get_textbox_width(layer: ArtLayer) -> int:
    """Get the width of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with 'kind' of TextLayer.

    Returns:
        Width of the textbox.
    """
    d = get_layer_action_ref(layer)
    bounds = d.getObjectValue(sID('boundingBox'))
    return bounds.getInteger(sID('width'))


def get_textbox_height(layer: ArtLayer) -> int:
    """Get the height of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with 'kind' of TextLayer.

    Returns:
        Height of the textbox.
    """
    d = get_layer_action_ref(layer)
    bounds = d.getObjectValue(sID('boundingBox'))
    return bounds.getInteger(sID('height'))
