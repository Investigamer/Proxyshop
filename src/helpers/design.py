"""
* Helpers: Design
"""

from collections.abc import Callable
from contextlib import suppress
from logging import getLogger

from photoshop.api import ActionDescriptor, ActionReference, SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._selection import Selection
from photoshop.api.enumerations import (
    BlendMode,
    DialogModes,
    ElementPlacement,
    RasterizeType,
    SaveOptions,
)

from src import APP
from src.helpers.colors import fill_layer_primary, rgb_black
from src.helpers.layers import edit_smart_layer, select_layers, smart_layer
from src.helpers.selection import select_layer_pixels
from src.utils.adobe import PS_EXCEPTIONS

_logger = getLogger(__name__)

"""
* Filling Space
"""


def fill_empty_area(reference: ArtLayer, color: SolidColor | None = None) -> ArtLayer:
    """Fills empty gaps on an art layer, such as a symbol, with a solid color.

    Args:
        reference: Reference layer to put the new fill layer underneath
        color: Color of the background fill
    """
    # Magic Wand contiguous outside symbol
    docref = APP.instance.activeDocument
    docsel = docref.selection
    coords = ActionDescriptor()
    click1 = ActionDescriptor()
    ref1 = ActionReference()
    idPaint = APP.instance.sID("paint")
    idPixel = APP.instance.sID("pixelsUnit")
    idTolerance = APP.instance.sID("tolerance")
    coords.putUnitDouble(APP.instance.sID("horizontal"), idPixel, 5)
    coords.putUnitDouble(APP.instance.sID("vertical"), idPixel, 5)
    ref1.putProperty(APP.instance.sID("channel"), APP.instance.sID("selection"))
    click1.putReference(APP.instance.sID("target"), ref1)
    click1.putObject(APP.instance.sID("to"), idPaint, coords)
    click1.putInteger(idTolerance, 12)
    click1.putBoolean(APP.instance.sID("antiAlias"), True)
    APP.instance.executeAction(APP.instance.sID("set"), click1)

    # Invert selection
    docsel.invert()
    docsel.contract(1)

    # Make a new layer
    layer = docref.artLayers.add()
    layer.name = "Expansion Mask"
    layer.blendMode = BlendMode.NormalBlend
    layer.move(reference, ElementPlacement.PlaceAfter)

    # Fill selection with stroke color
    APP.instance.foregroundColor = color or rgb_black()
    click3 = ActionDescriptor()
    click3.putObject(APP.instance.sID("from"), idPaint, coords)
    click3.putInteger(idTolerance, 0)
    click3.putEnumerated(
        APP.instance.sID("using"),
        APP.instance.sID("fillContents"),
        APP.instance.sID("foregroundColor"),
    )
    click3.putBoolean(APP.instance.sID("contiguous"), False)
    APP.instance.executeAction(APP.instance.sID("fill"), click3)

    # Clear Selection
    docsel.deselect()
    return layer


def content_aware_fill_edges(
    layer: ArtLayer | None = None,
    contract: int = 10,
    smooth: int = 0,
    feather: int = 5,
    art_selection_hook: Callable[[ArtLayer, Selection], None] | None = None,
) -> None:
    """Fills pixels outside art layer using content-aware fill.

    Args:
        layer: Layer to use for the content aware fill. Uses active if not provided.
        feather: Whether to feather the selection before performing the fill operation.
    """
    # Set active layer if needed, then rasterize
    docref = APP.instance.activeDocument
    if layer:
        docref.activeLayer = layer
        active_layer = layer
    elif not isinstance((active_layer := docref.activeLayer), ArtLayer):
        _logger.warning(
            "Skipping content aware fill as active layer is not an ArtLayer."
        )
        return
    active_layer.rasterize(RasterizeType.EntireLayer)

    # Select pixels of the active layer
    select_layer_pixels(active_layer)
    selection = docref.selection

    if art_selection_hook:
        art_selection_hook(active_layer, selection)

    # Guard against no selection made
    try:
        # Adjust selection, then invert
        if contract:
            selection.contract(contract)
        if smooth:
            selection.smooth(smooth)
        if feather:
            selection.feather(feather)
        selection.invert()
        content_aware_fill()
    except PS_EXCEPTIONS as exc:
        # Unable to fill due to invalid selection
        _logger.warning(
            "Couldn't make a valid selection. Skipping automated fill.", exc_info=exc
        )

    # Clear selection
    with suppress(Exception):
        selection.deselect()


def generative_fill_edges(
    layer: ArtLayer | None = None,
    contract: int = 10,
    smooth: int = 0,
    feather: int = 5,
    close_doc: bool = True,
    docref: Document | None = None,
    art_selection_hook: Callable[[ArtLayer, Selection], None] | None = None,
) -> Document | None:
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
    docref = docref or APP.instance.activeDocument
    if layer:
        docref.activeLayer = layer
        active_layer = layer
    elif not isinstance((active_layer := docref.activeLayer), ArtLayer):
        print("Skipping content aware fill as active layer is not an ArtLayer.")
        return
    active_layer.rasterize(RasterizeType.EntireLayer)

    # Create a fill layer the size of the document
    fill_layer: ArtLayer = docref.artLayers.add()
    fill_layer.move(active_layer, ElementPlacement.PlaceAfter)
    fill_layer_primary()
    fill_layer.opacity = 0

    # Create a smart layer document and enter it
    select_layers([active_layer, fill_layer])
    smart_layer()
    edit_smart_layer()

    # Select pixels of active layer and invert
    docref = APP.instance.activeDocument
    select_layer_pixels(active_layer)
    selection = docref.selection

    if art_selection_hook and isinstance((art_layer := docref.activeLayer), ArtLayer):
        art_selection_hook(art_layer, selection)

    # Guard against no selection made
    try:
        # Adjust selection, then invert
        if contract:
            selection.contract(contract)
        if smooth:
            selection.smooth(smooth)
        if feather:
            selection.feather(feather)
        selection.invert()
        try:
            generative_fill()
        except PS_EXCEPTIONS:
            # Generative fill call not responding
            _logger.warning(
                "Generative fill failed. Falling back to Content Aware Fill."
            )
            active_layer.rasterize(RasterizeType.EntireLayer)
            content_aware_fill()
            close_doc = True
    except PS_EXCEPTIONS:
        # Unable to fill due to invalid selection
        _logger.warning("Couldn't make a valid selection. Skipping automated fill.")
        close_doc = True

    # Deselect
    with suppress(Exception):
        selection.deselect()

    # Doc requested and operation successful
    if not close_doc:
        return docref
    docref.close(SaveOptions.SaveChanges)
    return


def remove_content_fill_edges(
    layer: ArtLayer | None = None,
    contract: int = 10,
    smooth: int = 0,
    feather: int = 5,
    art_selection_hook: Callable[[ArtLayer, Selection], None] | None = None,
) -> None:
    """Fills pixels outside art layer using remove content fill.

    Args:
        layer: Layer to use for the fill. Uses active if not provided.
        feather: Whether to feather the selection before performing the fill operation.
    """
    # Set active layer if needed
    docref = APP.instance.activeDocument
    if layer:
        docref.activeLayer = layer
        active_layer = layer
    elif not isinstance((active_layer := docref.activeLayer), ArtLayer):
        _logger.warning(
            "Skipping remove content fill as active layer is not an ArtLayer."
        )
        return

    # Create a fill layer the size of the document in order to
    # ensure that the smart document retains the document's size
    fill_layer: ArtLayer = docref.artLayers.add()
    fill_layer.move(active_layer, ElementPlacement.PlaceAfter)
    fill_layer_primary()
    fill_layer.opacity = 0

    # Create a smart layer document and enter it in order to
    # ensure that content is sampled only from the art layer
    select_layers([active_layer, fill_layer])
    smart_layer()
    edit_smart_layer()

    # Select pixels of the active layer
    docref = APP.instance.activeDocument
    if isinstance((layer_in_smart_doc := docref.activeLayer), ArtLayer):
        select_layer_pixels(layer_in_smart_doc)
    selection = docref.selection

    if art_selection_hook and isinstance((art_layer := docref.activeLayer), ArtLayer):
        art_selection_hook(art_layer, selection)

    # Guard against no selection made
    try:
        # Adjust selection, then invert
        if contract:
            selection.contract(contract)
        if smooth:
            selection.smooth(smooth)
        if feather:
            selection.feather(feather)
        selection.invert()

        remove_content_fill()
    except PS_EXCEPTIONS as exc:
        # Unable to fill due to invalid selection
        _logger.warning(
            "Couldn't complete remove content fill. Skipping automated fill.",
            exc_info=exc,
        )

    # Clear selection
    with suppress(Exception):
        selection.deselect()

    docref.close(SaveOptions.SaveChanges)


def content_aware_fill() -> None:
    """Fills the current selection using content aware fill."""
    desc = ActionDescriptor()
    desc.putEnumerated(
        APP.instance.sID("using"),
        APP.instance.sID("fillContents"),
        APP.instance.sID("contentAware"),
    )
    desc.putUnitDouble(
        APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), 100
    )
    desc.putEnumerated(
        APP.instance.sID("mode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID("normal"),
    )
    APP.instance.executeAction(
        APP.instance.sID("fill"), desc, DialogModes.DisplayNoDialogs
    )


def generative_fill() -> None:
    """Call Photoshop's AI powered "Generative Fill" on the current selection."""
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    desc3 = ActionDescriptor()
    ref1.putEnumerated(
        APP.instance.sID("document"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc1.putString(APP.instance.sID("prompt"), """""")
    desc1.putString(APP.instance.sID("serviceID"), """clio""")
    desc1.putEnumerated(
        APP.instance.sID("mode"),
        APP.instance.sID("syntheticFillMode"),
        APP.instance.sID("inpaint"),
    )
    desc3.putString(APP.instance.sID("gi_PROMPT"), """""")
    desc3.putString(APP.instance.sID("gi_MODE"), """ginp""")
    desc3.putInteger(APP.instance.sID("gi_SEED"), -1)
    desc3.putInteger(APP.instance.sID("gi_NUM_STEPS"), -1)
    desc3.putInteger(APP.instance.sID("gi_GUIDANCE"), 6)
    desc3.putInteger(APP.instance.sID("gi_SIMILARITY"), 0)
    desc3.putBoolean(APP.instance.sID("gi_CROP"), False)
    desc3.putBoolean(APP.instance.sID("gi_DILATE"), False)
    desc3.putInteger(APP.instance.sID("gi_CONTENT_PRESERVE"), 0)
    desc3.putBoolean(APP.instance.sID("gi_ENABLE_PROMPT_FILTER"), True)
    desc3.putBoolean(APP.instance.sID("dualCrop"), True)
    desc3.putString(APP.instance.sID("gi_ADVANCED"), """{"enable_mts":true}""")
    desc2.putObject(APP.instance.sID("clio"), APP.instance.sID("clio"), desc3)
    desc1.putObject(
        APP.instance.sID("serviceOptionsList"), APP.instance.sID("target"), desc2
    )
    APP.instance.executeAction(
        APP.instance.sID("syntheticFill"), desc1, DialogModes.DisplayNoDialogs
    )


def remove_content_fill() -> None:
    """Call Photoshop's "Remove" action on the current selection."""
    APP.instance.executeAction(
        APP.instance.sID("removeButton"), display_dialogs=DialogModes.DisplayNoDialogs
    )


def repair_edges(edge: int = 6) -> None:
    """Select a small area at the edges of an image and content aware fill to repair upscale damage.

    Args:
        edge: How many pixels to select at the edge.
    """
    # Select all
    desc632724 = ActionDescriptor()
    ref489 = ActionReference()
    ref489.putProperty(APP.instance.sID("channel"), APP.instance.sID("selection"))
    desc632724.putReference(APP.instance.sID("target"), ref489)
    desc632724.putEnumerated(
        APP.instance.sID("to"), APP.instance.sID("ordinal"), APP.instance.sID("allEnum")
    )
    APP.instance.executeAction(
        APP.instance.sID("set"), desc632724, DialogModes.DisplayNoDialogs
    )

    # Contract selection
    contract = ActionDescriptor()
    contract.putUnitDouble(APP.instance.sID("by"), APP.instance.sID("pixelsUnit"), edge)
    contract.putBoolean(APP.instance.sID("selectionModifyEffectAtCanvasBounds"), True)
    APP.instance.executeAction(
        APP.instance.sID("contract"), contract, DialogModes.DisplayNoDialogs
    )

    # Inverse the selection
    APP.instance.executeAction(
        APP.instance.sID("inverse"), None, DialogModes.DisplayNoDialogs
    )

    # Content aware fill
    desc_caf = ActionDescriptor()
    desc_caf.putEnumerated(
        APP.instance.sID("cafSamplingRegion"),
        APP.instance.sID("cafSamplingRegion"),
        APP.instance.sID("cafSamplingRegionRectangular"),
    )
    desc_caf.putBoolean(APP.instance.sID("cafSampleAllLayers"), False)
    desc_caf.putEnumerated(
        APP.instance.sID("cafColorAdaptationLevel"),
        APP.instance.sID("cafColorAdaptationLevel"),
        APP.instance.sID("cafColorAdaptationDefault"),
    )
    desc_caf.putEnumerated(
        APP.instance.sID("cafRotationAmount"),
        APP.instance.sID("cafRotationAmount"),
        APP.instance.sID("cafRotationAmountNone"),
    )
    desc_caf.putBoolean(APP.instance.sID("cafScale"), False)
    desc_caf.putBoolean(APP.instance.sID("cafMirror"), False)
    desc_caf.putEnumerated(
        APP.instance.sID("cafOutput"),
        APP.instance.sID("cafOutput"),
        APP.instance.sID("cafOutputToNewLayer"),
    )
    APP.instance.executeAction(
        APP.instance.sID("cafWorkspace"), desc_caf, DialogModes.DisplayNoDialogs
    )

    # Deselect
    APP.instance.activeDocument.selection.deselect()
