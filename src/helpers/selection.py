"""
* Helpers: Selection
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._selection import Selection
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    DialogModes,
    LayerKind)

# Local Imports
from src import APP
from src.utils.exceptions import PS_EXCEPTIONS

# Photoshop infrastructure
cID, sID = APP.charIDtoTypeID, APP.stringIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Making Selections
"""


def select_bounds(
    bounds: tuple[int, int, int, int],
    selection: Optional[Selection] = None
) -> None:
    """Create a selection using a list of bound values.

    Args:
        bounds: List of bound values (left, top, right, bottom).
        selection: App selection object, pull from active document if not provided.
    """
    selection = selection or APP.activeDocument.selection
    left, top, right, bottom = bounds
    selection.select([
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom]])


def select_layer_bounds(layer: ArtLayer = None, selection: Optional[Selection] = None) -> None:
    """Select the bounding box of a given layer.

    Args:
        layer: Layer to select the pixels of. Uses active layer if not provided.
        selection: App selection object, pull from active document if not provided.
    """
    if not layer:
        layer = APP.activeDocument.activeLayer
    select_bounds(layer.bounds, selection)


def select_overlapping(layer: ArtLayer) -> None:
    """Select pixels in the given layer overlapping the current selection.

    Args:
        layer: Layer with pixels to select.
    """
    with suppress(PS_EXCEPTIONS):
        idChannel = sID('channel')
        desc1, ref1, ref2 = ActionDescriptor(), ActionReference(), ActionReference()
        ref1.putEnumerated(idChannel, idChannel, sID("transparencyEnum"))
        ref1.putIdentifier(sID("layer"), layer.id)
        desc1.putReference(sID("target"), ref1)
        ref2.putProperty(idChannel, sID("selection"))
        desc1.putReference(sID("with"), ref2)
        APP.executeAction(sID("interfaceIconFrameDimmed"), desc1, NO_DIALOG)


def select_canvas(docref: Optional[Document] = None, bleed: int = 0):
    """Select the entire canvas of a provided or active document.

    Args:
        docref: Document reference, use active if not provided.
        bleed: Amount of bleed edge to leave around selection, defaults to 0.
    """
    docref = docref or APP.activeDocument
    docref.selection.select([
        [0 + bleed, 0 + bleed],
        [docref.width - bleed, 0 + bleed],
        [docref.width - bleed, docref.height - bleed],
        [0 + bleed, docref.height - bleed]
    ])


"""
* Layer Based Selections
"""


def select_layer_pixels(layer: Optional[ArtLayer] = None) -> None:
    """Select pixels of the active layer, or a target layer.

    Args:
        layer: Layer to select. Uses active layer if not provided.
    """
    if layer and layer.kind == LayerKind.SolidFillLayer:
        return select_vector_layer_pixels(layer)
    des1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putProperty(sID("channel"), sID("selection"))
    des1.putReference(sID("target"), ref1)
    ref2.putEnumerated(sID("channel"), sID("channel"), sID("transparencyEnum"))
    if layer:
        ref2.putIdentifier(sID("layer"), layer.id)
    des1.putReference(sID("to"), ref2)
    APP.executeAction(sID("set"), des1, NO_DIALOG)


def select_vector_layer_pixels(layer: Optional[ArtLayer] = None) -> None:
    """Select pixels of the active vector layer, or a target layer.

    Args:
        layer: Layer to select. Uses active layer if not provided.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putProperty(sID("channel"), sID("selection"))
    desc1.putReference(sID("target"), ref1)
    ref2.putEnumerated(sID("path"), sID("path"), sID("vectorMask"))
    if layer:
        ref2.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("to"), ref2)
    desc1.putInteger(sID("version"), 1)
    desc1.putBoolean(sID("vectorMaskParams"), True)
    APP.executeAction(sID("set"), desc1, NO_DIALOG)


"""
* Selection Checks
"""


def check_selection_bounds(selection: Optional[Selection] = None) -> Optional[tuple[int, int, int, int]]:
    """Verifies if a selection has valid bounds.

    Args:
        selection: Selection object to test, otherwise use current selection of active document.

    Returns:
        An empty list if selection is invalid, otherwise return bounds of selection.
    """
    selection = selection or APP.activeDocument.selection
    with suppress(PS_EXCEPTIONS):
        if selection.bounds != (0, 0, 0, 0):
            return selection.bounds
    return
