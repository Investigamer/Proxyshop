"""
* Helpers: Bounds and Dimensions
"""

from contextlib import suppress
from typing import TypedDict

from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet

from src import APP
from src.helpers.descriptors import get_layer_action_descriptor
from src.helpers.document import undo_action
from src.helpers.layers import duplicate_group
from src.utils.adobe import LayerBounds

"""
* Types
"""


class LayerDimensions(TypedDict):
    """Calculated layer dimension info for a layer."""

    width: int | float
    height: int | float
    center_x: int | float
    center_y: int | float
    left: int | float
    right: int | float
    top: int | float
    bottom: int | float


class TextboxDimensions(TypedDict):
    """Calculated width and height of paragraph text layer bounding box."""

    width: int
    height: int


"""
* Dimensions and Bounds
"""


def get_dimensions_from_bounds(bounds: LayerBounds) -> LayerDimensions:
    """Compute width and height based on a set of bounds given.

    Args:
        bounds: List of bounds given.

    Returns:
        Dict containing height, width, and positioning locations.
    """
    width = int(bounds[2] - bounds[0])
    height = int(bounds[3] - bounds[1])
    return LayerDimensions(
        width=width,
        height=height,
        center_x=round((width / 2) + bounds[0]),
        center_y=round((height / 2) + bounds[1]),
        left=int(bounds[0]),
        right=int(bounds[2]),
        top=int(bounds[1]),
        bottom=int(bounds[3]),
    )


def get_layer_dimensions(layer: ArtLayer | LayerSet) -> LayerDimensions:
    """Compute the width and height dimensions of a layer.

    Args:
        layer: A layer object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    return get_dimensions_from_bounds(layer.bounds)


def get_group_dimensions(group: LayerSet) -> LayerDimensions:
    """
    Compute the dimensions of a group.

    Uses a workaround to avoid erroneous dimensions, which might occur
    when the group contains shapes.
    """
    group_copy = duplicate_group(group, group.name)
    group_copy.visible = True
    merged = group_copy.merge()
    dims = get_layer_dimensions(merged)
    merged.remove()
    return dims


def get_layer_width(layer: ArtLayer | LayerSet) -> float | int:
    """Returns the width of a given layer.

    Args:
        layer: A layer object

    Returns:
        int: Width of the layer in pixels.
    """
    bounds = layer.bounds
    return int(bounds[2] - bounds[0])


def get_layer_height(layer: ArtLayer | LayerSet) -> float | int:
    """Returns the height of a given layer.

    Args:
        layer: A layer object

    Returns:
        int: Height of the layer in pixels.
    """
    bounds = layer.bounds
    return int(bounds[3] - bounds[1])


def get_document_dimensions(document: Document) -> LayerDimensions:
    """Compute the width and height dimensions of a document.

    Args:
        document: A document object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    doc_width: float = int(document.width)
    doc_height: float = int(document.height)
    return get_dimensions_from_bounds((0, 0, doc_width, doc_height))


def get_card_dimensions(document: Document) -> LayerDimensions:
    """Compute the width and height dimensions of a document.

    Args:
        document: A document object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    bleed = int(document.resolution / 8)
    doc_width: float = int(document.width)
    doc_height: float = int(document.height)
    return get_dimensions_from_bounds(
        (bleed, bleed, doc_width - bleed, doc_height - bleed)
    )


"""
* Bounds and Dimensions, No Effects
"""


def get_bounds_no_effects(layer: ArtLayer | LayerSet) -> LayerBounds:
    """Returns the bounds of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        list: Pixel location top left, top right, bottom left, bottom right.
    """
    d = get_layer_action_descriptor(layer)
    # Try getting bounds no effects
    bounds = d.getObjectValue(APP.instance.sID("boundsNoEffects"))
    return (
        bounds.getInteger(APP.instance.sID("left")),
        bounds.getInteger(APP.instance.sID("top")),
        bounds.getInteger(APP.instance.sID("right")),
        bounds.getInteger(APP.instance.sID("bottom")),
    )


def get_dimensions_no_effects(layer: ArtLayer | LayerSet) -> LayerDimensions:
    """Compute the dimensions of a layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        Dict containing height, width, and positioning locations.
    """
    bounds = get_bounds_no_effects(layer)
    return get_dimensions_from_bounds(bounds)


def get_width_no_effects(layer: ArtLayer | LayerSet) -> float | int:
    """Returns the width of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        int: Width of the layer in pixels.
    """
    with suppress(Exception):
        # Try getting bounds no effects
        d = get_layer_action_descriptor(layer)
        bounds = d.getObjectValue(APP.instance.sID("boundsNoEffects"))
        return bounds.getInteger(APP.instance.sID("right")) - bounds.getInteger(
            APP.instance.sID("left")
        )
    return get_layer_width(layer)


def get_height_no_effects(layer: ArtLayer | LayerSet) -> float | int:
    """Returns the height of a given layer without its effects applied.

    Args:
        layer: A layer object

    Returns:
        int: Height of the layer in pixels.
    """
    with suppress(Exception):
        # Try getting bounds no effects
        d = get_layer_action_descriptor(layer)
        bounds = d.getObjectValue(APP.instance.sID("boundsNoEffects"))
        return bounds.getInteger(APP.instance.sID("bottom")) - bounds.getInteger(
            APP.instance.sID("top")
        )
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
    height = get_layer_dimensions(layer)["height"]
    layer.textItem.height = 1000
    dif = get_layer_dimensions(layer)["height"] - height
    undo_action()
    return dif > 0


def get_textbox_bounds(layer: ArtLayer) -> LayerBounds:
    """Get the bounds of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        List of bounds integers.
    """
    d = get_layer_action_descriptor(layer)
    bounds = d.getObjectValue(APP.instance.sID("boundingBox"))
    return (
        bounds.getInteger(APP.instance.sID("left")),
        bounds.getInteger(APP.instance.sID("top")),
        bounds.getInteger(APP.instance.sID("right")),
        bounds.getInteger(APP.instance.sID("bottom")),
    )


def get_textbox_dimensions(layer: ArtLayer) -> TextboxDimensions:
    """Get the dimensions of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.

    Returns:
        Dict containing width and height.
    """
    d = get_layer_action_descriptor(layer)
    bounds = d.getObjectValue(APP.instance.sID("boundingBox"))
    return {
        "width": bounds.getInteger(APP.instance.sID("width")),
        "height": bounds.getInteger(APP.instance.sID("height")),
    }


def get_textbox_width(layer: ArtLayer) -> int:
    """Get the width of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with 'kind' of TextLayer.

    Returns:
        Width of the textbox.
    """
    d = get_layer_action_descriptor(layer)
    bounds = d.getObjectValue(APP.instance.sID("boundingBox"))
    return bounds.getInteger(APP.instance.sID("width"))


def get_textbox_height(layer: ArtLayer) -> int:
    """Get the height of a TextLayer's bounding box.

    Args:
        layer: ArtLayer with 'kind' of TextLayer.

    Returns:
        Height of the textbox.
    """
    d = get_layer_action_descriptor(layer)
    bounds = d.getObjectValue(APP.instance.sID("boundingBox"))
    return bounds.getInteger(APP.instance.sID("height"))
