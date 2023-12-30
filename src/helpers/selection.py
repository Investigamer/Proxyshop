"""
* Helpers: Selection
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional, Union

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._selection import Selection
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    DialogModes)

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


"""
* Selection Bounds
"""


def check_selection_bounds(selection: Optional[Selection] = None) -> list[Union[int, float]]:
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
    return []
