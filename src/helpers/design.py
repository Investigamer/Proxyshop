"""
DESIGN HELPERs
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from photoshop.api import (
    DialogModes,
    ActionDescriptor,
    RasterizeType,
    ActionReference,
    BlendMode,
    SolidColor,
    ElementPlacement,
    SaveOptions
)
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document


# Local Imports
from src.constants import con
from src.helpers.layers import select_layer_pixels, select_layers, smart_layer, edit_smart_layer
from src.helpers.colors import rgb_black, fill_layer_primary
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
    Rasterizes a given layer (or active layer) and fills remaining pixels using content-aware fill.
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
    content_aware_fill()
    selection.deselect()


def content_aware_fill() -> None:
    """Fills the current selection using content aware fill."""
    desc = ActionDescriptor()
    desc.putEnumerated(sID("using"), sID("fillContents"), sID("contentAware"))
    desc.putUnitDouble(sID("opacity"), sID("percentUnit"), 100)
    desc.putEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    app.executeAction(sID("fill"), desc, NO_DIALOG)


def generative_fill_edges(layer: Optional[ArtLayer] = None) -> None:
    """
    Rasterizes a given layer (or active layer) and fills remaining pixels using AI powered generative fill.
    @param layer: Layer to use for the generative fill. Uses active if not provided.
    """
    # Set active layer if needed, then rasterize
    docref: Document = app.activeDocument
    if layer:
        docref.activeLayer = layer
    else:
        layer = docref.activeLayer
    docref.activeLayer.rasterize(RasterizeType.EntireLayer)

    # Create a fill layer the size of the document
    fill_layer: ArtLayer = docref.artLayers.add()
    fill_layer.move(layer, ElementPlacement.PlaceAfter)
    fill_layer_primary()
    fill_layer.opacity = 0
    select_layers([layer, fill_layer])
    smart = smart_layer()
    edit_smart_layer(smart)

    # Select pixels of active layer and invert
    docref = app.activeDocument
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

    # Call Generative fill
    generative_fill()
    selection.deselect()
    docref.close(SaveOptions.SaveChanges)


def generative_fill() -> None:
    """Call Photoshop's AI powered "Generative Fill" on the current selection."""
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    desc3 = ActionDescriptor()
    ref1.putEnumerated(sID("document"), sID("ordinal"), sID("targetEnum"))
    desc1.putReference(sID("target"), ref1)
    desc1.putString(sID("prompt"), """""")
    desc1.putString(sID("serviceID"), """clio""")
    desc1.putEnumerated(sID("mode"), sID("syntheticFillMode"), sID("inpaint"))
    desc3.putString(sID("gi_PROMPT"), """""")
    desc3.putString(sID("gi_MODE"), """ginp""")
    desc3.putInteger(sID("gi_SEED"), -1)
    desc3.putInteger(sID("gi_NUM_STEPS"), -1)
    desc3.putInteger(sID("gi_GUIDANCE"), 6)
    desc3.putInteger(sID("gi_SIMILARITY"), 0)
    desc3.putBoolean(sID("gi_CROP"), False)
    desc3.putBoolean(sID("gi_DILATE"), False)
    desc3.putInteger(sID("gi_CONTENT_PRESERVE"), 0)
    desc3.putBoolean(sID("gi_ENABLE_PROMPT_FILTER"), True)
    desc2.putObject(sID("clio"), sID("clio"), desc3)
    desc1.putObject(sID("serviceOptionsList"), sID("target"), desc2)
    app.executeaction(sID("syntheticFill"), desc1, NO_DIALOG)


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
