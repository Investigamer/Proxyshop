"""
DESIGN HELPERs
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, RasterizeType, ActionReference, BlendMode, SolidColor
from photoshop.api._artlayer import ArtLayer


# Local Imports
from src.constants import con
from src.helpers.layers import select_layer_pixels
from src.helpers.colors import rgb_black
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
FILLING SPACE
"""


def fill_empty_area(reference: ArtLayer, color: Optional[SolidColor] = None) -> ArtLayer:
    """
    Fills empty gaps on an art layer, such as an expansion symbol, with a solid color.
    @param reference: Reference layer to put the new fill layer underneath
    @param color: Color of the background fill
    """
    # Magic Wand contiguous outside symbol
    coords = ActionDescriptor()
    coords.putUnitDouble(cID("Hrzn"), cID("#Pxl"), 5)
    coords.putUnitDouble(cID("Vrtc"), cID("#Pxl"), 5)
    click1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putProperty(cID("Chnl"), cID("fsel"))
    click1.putReference(sID("target"), ref1)
    click1.putObject(cID("T   "), cID("Pnt "), coords)
    click1.putInteger(cID("Tlrn"), 12)
    click1.putBoolean(cID("AntA"), True)
    app.executeAction(cID("setd"), click1)

    # Invert selection
    app.activeDocument.selection.invert()
    app.activeDocument.selection.contract(1)

    # Make a new layer
    layer = app.activeDocument.artLayers.add()
    layer.name = "Expansion Mask"
    layer.blendMode = BlendMode.NormalBlend
    layer.moveAfter(reference)

    # Fill selection with stroke color
    app.foregroundColor = color or rgb_black()
    click3 = ActionDescriptor()
    click3.putObject(cID("From"), cID("Pnt "), coords)
    click3.putInteger(cID("Tlrn"), 0)
    click3.putEnumerated(cID("Usng"), cID("FlCn"), cID("FrgC"))
    click3.putBoolean(cID("Cntg"), False)
    app.executeAction(cID("Fl  "), click3)

    # Clear Selection
    app.activeDocument.selection.deselect()
    return layer


def content_aware_fill_edges(layer: Optional[ArtLayer] = None) -> None:
    """
    Helper function intended to streamline the workflow of making extended art cards.
    This script rasterizes the active layer and fills all empty pixels in the canvas
    on the layer using content-aware fill.
    @param layer: Layer to use for the content aware fill. Uses active if not provided.
    """
    # Set active layer if needed, then rasterize
    docref = app.activeDocument
    if layer:
        docref.activeLayer = layer
    docref.activeLayer.rasterize(RasterizeType.EntireLayer)

    # Select pixels of active layer and invert
    select_layer_pixels(docref.activeLayer)
    selection = docref.selection
    selection.invert()

    # Guard against no selection made
    try:
        _ = selection.bounds
    except PS_EXCEPTIONS:
        return

    # Expand and smooth selection
    selection.expand(8)
    selection.smooth(4)

    # Content aware fill
    desc = ActionDescriptor()
    desc.putEnumerated(sID("using"), sID("fillContents"), sID("contentAware"))
    desc.putUnitDouble(sID("opacity"), sID("percentUnit"), 100)
    desc.putEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    app.executeAction(sID("fill"), desc, NO_DIALOG)
    selection.deselect()


def repair_edges(edge: int = 6) -> None:
    """
    Select a small area at the edges of an image and content aware fill to repair upscale damage.
    @param edge: How many pixels to select at the edge.
    """
    # Select all
    desc632724 = ActionDescriptor()
    ref489 = ActionReference()
    ref489.putProperty(sID("channel"), sID("selection"))
    desc632724.putReference(sID("target"), ref489)
    desc632724.putEnumerated(sID("to"), sID("ordinal"), sID("allEnum"))
    app.ExecuteAction(sID("set"), desc632724, NO_DIALOG)

    # Contract selection
    contract = ActionDescriptor()
    contract.putUnitDouble(sID("by"), sID("pixelsUnit"), edge)
    contract.putBoolean(sID("selectionModifyEffectAtCanvasBounds"), True)
    app.ExecuteAction(sID("contract"), contract, NO_DIALOG)

    # Inverse the selection
    app.ExecuteAction(sID("inverse"), None, NO_DIALOG)

    # Content aware fill
    desc_caf = ActionDescriptor()
    desc_caf.putEnumerated(
        sID("cafSamplingRegion"),
        sID("cafSamplingRegion"),
        sID("cafSamplingRegionRectangular")
    )
    desc_caf.putBoolean(sID("cafSampleAllLayers"), False)
    desc_caf.putEnumerated(
        sID("cafColorAdaptationLevel"),
        sID("cafColorAdaptationLevel"),
        sID("cafColorAdaptationDefault")
    )
    desc_caf.putEnumerated(
        sID("cafRotationAmount"),
        sID("cafRotationAmount"),
        sID("cafRotationAmountNone")
    )
    desc_caf.putBoolean(sID("cafScale"), False)
    desc_caf.putBoolean(sID("cafMirror"), False)
    desc_caf.putEnumerated(
        sID("cafOutput"),
        sID("cafOutput"),
        sID("cafOutputToNewLayer")
    )
    app.ExecuteAction(sID("cafWorkspace"), desc_caf, NO_DIALOG)

    # Deselect
    app.activeDocument.selection.deselect()
