"""
* Helpers: Design
"""
# Standard Library Imports
from typing import Optional
from contextlib import suppress

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
from src import APP, CONSOLE
from src.helpers.layers import select_layers, smart_layer, edit_smart_layer
from src.helpers.colors import rgb_black, fill_layer_primary
from src.helpers.selection import select_layer_pixels
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Filling Space
"""


def fill_empty_area(reference: ArtLayer, color: Optional[SolidColor] = None) -> ArtLayer:
    """Fills empty gaps on an art layer, such as a symbol, with a solid color.

    Args:
        reference: Reference layer to put the new fill layer underneath
        color: Color of the background fill
    """
    # Magic Wand contiguous outside symbol
    docref = APP.activeDocument
    docsel = docref.selection
    coords = ActionDescriptor()
    click1 = ActionDescriptor()
    ref1 = ActionReference()
    idPaint = sID('paint')
    idPixel = sID('pixelsUnit')
    idTolerance = sID('tolerance')
    coords.putUnitDouble(sID('horizontal'), idPixel, 5)
    coords.putUnitDouble(sID('vertical'), idPixel, 5)
    ref1.putProperty(sID('channel'), sID('selection'))
    click1.putReference(sID('target'), ref1)
    click1.putObject(sID('to'), idPaint, coords)
    click1.putInteger(idTolerance, 12)
    click1.putBoolean(sID('antiAlias'), True)
    APP.executeAction(sID('set'), click1)

    # Invert selection
    docsel.invert()
    docsel.contract(1)

    # Make a new layer
    layer = docref.artLayers.add()
    layer.name = 'Expansion Mask'
    layer.blendMode = BlendMode.NormalBlend
    layer.moveAfter(reference)

    # Fill selection with stroke color
    APP.foregroundColor = color or rgb_black()
    click3 = ActionDescriptor()
    click3.putObject(sID('from'), idPaint, coords)
    click3.putInteger(idTolerance, 0)
    click3.putEnumerated(sID('using'), sID('fillContents'), sID('foregroundColor'))
    click3.putBoolean(sID('contiguous'), False)
    APP.executeAction(sID('fill'), click3)

    # Clear Selection
    docsel.deselect()
    return layer


def content_aware_fill_edges(layer: Optional[ArtLayer] = None, feather: bool = False) -> None:
    """Fills pixels outside art layer using content-aware fill.

    Args:
        layer: Layer to use for the content aware fill. Uses active if not provided.
        feather: Whether to feather the selection before performing the fill operation.
    """
    # Set active layer if needed, then rasterize
    docref = APP.activeDocument
    if layer:
        docref.activeLayer = layer
    docref.activeLayer.rasterize(RasterizeType.EntireLayer)

    # Select pixels of the active layer
    select_layer_pixels(docref.activeLayer)
    selection = docref.selection

    # Guard against no selection made
    try:
        # Create a feathered or smoothed selection, then invert
        if feather:
            selection.contract(22)
            selection.feather(8)
        else:
            selection.contract(10)
            selection.smooth(5)
        selection.invert()
        content_aware_fill()
    except PS_EXCEPTIONS:
        # Unable to fill due to invalid selection
        CONSOLE.update(
            "Couldn't make a valid selection!\n"
            "Skipping automated fill.")

    # Clear selection
    with suppress(Exception):
        selection.deselect()


def generative_fill_edges(
    layer: Optional[ArtLayer] = None,
    feather: bool = False,
    close_doc: bool = True,
    docref: Optional[Document] = None
) -> Optional[Document]:
    """Fills pixels outside an art layer using AI powered generative fill.

    Args:
        layer: Layer to use for the generative fill. Uses active if not provided.
        feather: Whether to feather the selection before performing the fill operation.
        close_doc: Whether to close the smart layer document after the fill operation.
        docref: Reference document, use active if not provided.

    Returns:
        Smart layer document if Generative Fill operation succeeded, otherwise None.
    """
    # Set docref and use active layer if not provided
    docref = docref or APP.activeDocument
    if not layer:
        layer = docref.activeLayer
    docref.activeLayer = layer

    # Create a fill layer the size of the document
    fill_layer: ArtLayer = docref.artLayers.add()
    fill_layer.move(layer, ElementPlacement.PlaceAfter)
    fill_layer_primary()
    fill_layer.opacity = 0

    # Create a smart layer document and enter it
    select_layers([layer, fill_layer])
    smart_layer()
    edit_smart_layer()

    # Select pixels of active layer and invert
    docref = APP.activeDocument
    select_layer_pixels(docref.activeLayer)
    selection = docref.selection

    # Guard against no selection made
    try:
        # Create a feathered or smoothed selection, then invert
        if feather:
            selection.contract(22)
            selection.feather(8)
        else:
            selection.contract(10)
            selection.smooth(5)
        selection.invert()
        try:
            generative_fill()
        except PS_EXCEPTIONS:
            # Generative fill call not responding
            CONSOLE.update("Generative fill failed!\n"
                           "Falling back to Content Aware Fill.")
            docref.activeLayer.rasterize(RasterizeType.EntireLayer)
            content_aware_fill()
            close_doc = True
    except PS_EXCEPTIONS:
        # Unable to fill due to invalid selection
        CONSOLE.update("Couldn't make a valid selection!\n"
                       "Skipping automated fill.")
        close_doc = True

    # Deselect
    with suppress(Exception):
        selection.deselect()

    # Doc requested and operation successful
    if not close_doc:
        return docref
    docref.close(SaveOptions.SaveChanges)
    return


def content_aware_fill() -> None:
    """Fills the current selection using content aware fill."""
    desc = ActionDescriptor()
    desc.putEnumerated(sID("using"), sID("fillContents"), sID("contentAware"))
    desc.putUnitDouble(sID("opacity"), sID("percentUnit"), 100)
    desc.putEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    APP.executeAction(sID("fill"), desc, NO_DIALOG)


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
    desc3.putBoolean(sID("dualCrop"), True)
    desc3.putString(sID("gi_ADVANCED"), """{"enable_mts":true}""")
    desc2.putObject(sID("clio"), sID("clio"), desc3)
    desc1.putObject(sID("serviceOptionsList"), sID("target"), desc2)
    APP.executeAction(sID("syntheticFill"), desc1, NO_DIALOG)


def repair_edges(edge: int = 6) -> None:
    """Select a small area at the edges of an image and content aware fill to repair upscale damage.

    Args:
        edge: How many pixels to select at the edge.
    """
    # Select all
    desc632724 = ActionDescriptor()
    ref489 = ActionReference()
    ref489.putProperty(sID("channel"), sID("selection"))
    desc632724.putReference(sID("target"), ref489)
    desc632724.putEnumerated(sID("to"), sID("ordinal"), sID("allEnum"))
    APP.executeAction(sID("set"), desc632724, NO_DIALOG)

    # Contract selection
    contract = ActionDescriptor()
    contract.putUnitDouble(sID("by"), sID("pixelsUnit"), edge)
    contract.putBoolean(sID("selectionModifyEffectAtCanvasBounds"), True)
    APP.executeAction(sID("contract"), contract, NO_DIALOG)

    # Inverse the selection
    APP.executeAction(sID("inverse"), None, NO_DIALOG)

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
    APP.executeAction(sID("cafWorkspace"), desc_caf, NO_DIALOG)

    # Deselect
    APP.activeDocument.selection.deselect()
