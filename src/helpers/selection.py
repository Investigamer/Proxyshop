"""
* Helpers: Selection
"""

from contextlib import suppress

from photoshop.api import ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api._selection import Selection
from photoshop.api.enumerations import DialogModes, LayerKind

from src import APP
from src.utils.adobe import PS_EXCEPTIONS

"""
* Making Selections
"""


def select_bounds(
    bounds: tuple[float, float, float, float], selection: Selection | None = None
) -> None:
    """Create a selection using a list of bound values.

    Args:
        bounds: List of bound values (left, top, right, bottom).
        selection: App selection object, pull from active document if not provided.
    """
    selection = selection or APP.instance.activeDocument.selection
    left, top, right, bottom = bounds
    selection.select(((left, top), (right, top), (right, bottom), (left, bottom)))


def select_layer_bounds(
    layer: ArtLayer | LayerSet | None = None, selection: Selection | None = None
) -> None:
    """Select the bounding box of a given layer.

    Args:
        layer: Layer to select the pixels of. Uses active layer if not provided.
        selection: App selection object, pull from active document if not provided.
    """
    if not layer:
        layer = APP.instance.activeDocument.activeLayer
    select_bounds(layer.bounds, selection)


def select_overlapping(layer: ArtLayer) -> None:
    """Select pixels in the given layer overlapping the current selection.

    Args:
        layer: Layer with pixels to select.
    """
    with suppress(*PS_EXCEPTIONS):
        idChannel = APP.instance.sID("channel")
        desc1, ref1, ref2 = ActionDescriptor(), ActionReference(), ActionReference()
        ref1.putEnumerated(idChannel, idChannel, APP.instance.sID("transparencyEnum"))
        ref1.putIdentifier(APP.instance.sID("layer"), layer.id)
        desc1.putReference(APP.instance.sID("target"), ref1)
        ref2.putProperty(idChannel, APP.instance.sID("selection"))
        desc1.putReference(APP.instance.sID("with"), ref2)
        APP.instance.executeAction(
            APP.instance.sID("interfaceIconFrameDimmed"),
            desc1,
            DialogModes.DisplayNoDialogs,
        )


def select_canvas(docref: Document | None = None, bleed: int = 0):
    """Select the entire canvas of a provided or active document.

    Args:
        docref: Document reference, use active if not provided.
        bleed: Amount of bleed edge to leave around selection, defaults to 0.
    """
    docref = docref or APP.instance.activeDocument
    docref.selection.select(
        (
            (0 + bleed, 0 + bleed),
            (docref.width - bleed, 0 + bleed),
            (docref.width - bleed, docref.height - bleed),
            (0 + bleed, docref.height - bleed),
        )
    )


"""
* Layer Based Selections
"""


def select_layer_pixels(
    layer: ArtLayer | None = None, add_to_selection: bool = False
) -> Selection:
    """Select pixels of the active layer, or a target layer.

    Args:
        layer: Layer to select. Uses active layer if not provided.
    """
    if layer and layer.kind == LayerKind.SolidFillLayer:
        return select_vector_layer_pixels(layer, add_to_selection=add_to_selection)
    des1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putProperty(APP.instance.sID("channel"), APP.instance.sID("selection"))
    des1.putReference(APP.instance.sID("target"), ref1)
    ref2.putEnumerated(
        APP.instance.sID("channel"),
        APP.instance.sID("channel"),
        APP.instance.sID("transparencyEnum"),
    )
    if layer:
        ref2.putIdentifier(APP.instance.sID("layer"), layer.id)
    des1.putReference(APP.instance.sID("to"), ref2)
    APP.instance.executeAction(
        APP.instance.sID("add" if add_to_selection else "set"),
        des1,
        DialogModes.DisplayNoDialogs,
    )
    return APP.instance.activeDocument.selection


def select_vector_layer_pixels(
    layer: ArtLayer | None = None, add_to_selection: bool = False
) -> Selection:
    """Select pixels of the active vector layer, or a target layer.

    Args:
        layer: Layer to select. Uses active layer if not provided.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putProperty(APP.instance.sID("channel"), APP.instance.sID("selection"))
    desc1.putReference(APP.instance.sID("target"), ref1)
    ref2.putEnumerated(
        APP.instance.sID("path"),
        APP.instance.sID("path"),
        APP.instance.sID("vectorMask"),
    )
    if layer:
        ref2.putIdentifier(APP.instance.sID("layer"), layer.id)
    desc1.putReference(APP.instance.sID("to"), ref2)
    desc1.putBoolean(APP.instance.sID("vectorMaskParams"), True)
    APP.instance.executeAction(
        APP.instance.sID("addTo" if add_to_selection else "set"),
        desc1,
        DialogModes.DisplayNoDialogs,
    )
    return APP.instance.activeDocument.selection


"""
* Selection Checks
"""


def check_selection_bounds(
    selection: Selection | None = None,
) -> tuple[float, float, float, float] | None:
    """Verifies if a selection has valid bounds.

    Args:
        selection: Selection object to test, otherwise use current selection of active document.

    Returns:
        An empty list if selection is invalid, otherwise return bounds of selection.
    """
    selection = selection or APP.instance.activeDocument.selection
    with suppress(*PS_EXCEPTIONS):
        if selection.bounds != (0, 0, 0, 0):
            return selection.bounds
    return
