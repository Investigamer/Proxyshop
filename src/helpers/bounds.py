"""
BOUNDS HELPERS
"""
# Standard Library Imports
from typing import Union

# Third Party Imports
from photoshop.api import DialogModes, ActionReference, ElementPlacement, RasterizeType, LayerKind
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.constants import con
from src.helpers.document import undo_action
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


def get_bounds_no_effects(layer: Union[ArtLayer, LayerSet]) -> list[int, int, int, int]:
    """
    Returns the bounds of a given layer without its effects applied.
    @param layer: A layer object
    @return list: Pixel location top left, top right, bottom left, bottom right.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = app.executeActionGet(reference)
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


def get_dimensions_from_bounds(bounds: list) -> dict[str: Union[float, int]]:
    """
    Compute width and height based on a set of bounds given.
    @param bounds: List of bounds given.
    @return: Dict containing height, width, and positioning locations.
    """
    width = int(bounds[2]-bounds[0])
    height = int(bounds[3]-bounds[1])
    return {
        'width': width,
        'height': height,
        'center_x': (width / 2) + bounds[0],
        'center_y': (height / 2) + bounds[1],
        'left': bounds[0], 'right': bounds[2],
        'top': bounds[1], 'bottom': bounds[3]
    }


def get_dimensions_no_effects(layer: Union[ArtLayer, LayerSet]) -> dict[str: Union[float, int]]:
    """
    Compute the dimensions of a layer without its effects applied.
    @param layer: A layer object
    @return: Dict containing height, width, and positioning locations.
    """
    bounds = get_bounds_no_effects(layer)
    return get_dimensions_from_bounds(bounds)


def get_layer_dimensions(layer: Union[ArtLayer, LayerSet]) -> dict[str: Union[float, int]]:
    """
    Compute the width and height dimensions of a layer.
    @param layer: A layer object
    @return: Dict containing height, width, and positioning locations.
    """
    return get_dimensions_from_bounds(layer.bounds)


def check_textbox_overflow(layer: ArtLayer) -> bool:
    """
    Check if a TextLayer overflows the bounding box.
    @param layer: ArtLayer with "kind" of TextLayer.
    @return: True if text overflowing, else False.
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


def get_text_layer_bounds(layer: ArtLayer, legacy: bool = False) -> list[int, int, int, int]:
    """
    Returns a list of the text layer's bounds [left, top, right, bottom].
    @param layer: Layer to get the bounds of.
    @param legacy: Force old way for legacy Photoshop versions.
    @return: List of the bounds of a given layer.
    """
    if legacy or int(app.version[0:2]) < 21:
        layer_copy = layer.duplicate(app.activeDocument, ElementPlacement.PlaceInside)
        layer_copy.rasterize(RasterizeType.TextContents)
        layer_bounds = layer.bounds
        layer_copy.remove()
        return layer_bounds
    return layer.bounds


def get_textbox_bounds(layer: ArtLayer) -> list[int]:
    """
    Get the bounds of a TextLayer's bounding box.
    @param layer: ArtLayer with "kind" of TextLayer.
    @return: List of bounds integers.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = app.executeActionGet(reference)
    bounds = descriptor.getObjectValue(sID('boundingBox'))
    return [
        bounds.getInteger(sID('left')),
        bounds.getInteger(sID('top')),
        bounds.getInteger(sID('right')),
        bounds.getInteger(sID('bottom'))
    ]


def get_textbox_dimensions(layer: ArtLayer):
    """
    Get the dimensions of a TextLayer's bounding box.
    @param layer: ArtLayer with "kind" of TextLayer.
    @return: Dict containing width and height.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = app.executeActionGet(reference)
    bounds = descriptor.getObjectValue(sID('boundingBox'))
    return {
        'width': bounds.getInteger(sID('width')),
        'height': bounds.getInteger(sID('height'))
    }


def get_text_layer_dimensions(layer, legacy: bool = False) -> dict[str: Union[int, float]]:
    """
    Return an object with the specified text layer's width and height, on some versions of Photoshop
    a text layer must be rasterized before pulling accessing its true bounds.
    @param layer: Layer to get the dimensions of.
    @param legacy: Force old way for legacy text layers.
    @return: Dict containing height and width of the given layer.
    """
    if legacy or int(app.version[0:2]) < 21:
        layer_copy = layer.duplicate(app.activeDocument, ElementPlacement.PlaceInside)
        layer_copy.rasterize(RasterizeType.TextContents)
        dimensions = get_dimensions_from_bounds(layer_copy.bounds)
        layer_copy.remove()
        return dimensions
    return get_dimensions_from_bounds(layer.bounds)
