# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference, AnchorPosition
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet


# Local Imports
from src.constants import con
from src.helpers.bounds import get_layer_dimensions, get_text_layer_dimensions
from src.helpers.layers import select_layer_bounds
from src.enums.photoshop import Alignment

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
ALIGNMENT
"""


def align(
    align_type: Alignment = Alignment.CenterHorizontal,
    layer: Optional[Union[ArtLayer, LayerSet]] = None,
    reference: Optional[Union[ArtLayer, LayerSet]] = None
) -> None:
    """
    Align the currently active layer to current selection, vertically or horizontally.
    Used with align_vertical() or align_horizontal().
    @param align_type: "AdCV" vertical, "AdCH" horizontal.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    # Optionally create a selection based on given reference
    if reference:
        select_layer_bounds(reference)

    # Optionally make a given layer the active layer
    if layer:
        app.activeDocument.activeLayer = layer

    # Align the current layer to selection
    desc = ActionDescriptor()
    ref = ActionReference()
    ref.putEnumerated(sID('layer'), sID('ordinal'), sID('targetEnum'))
    desc.putReference(sID('null'), ref)
    desc.putEnumerated(sID('using'), cID('ADSt'), align_type.value)
    app.executeAction(sID('align'), desc, NO_DIALOG)


def align_vertical(
    layer: Optional[Union[ArtLayer, LayerSet]] = None,
    reference: Optional[ArtLayer] = None
) -> None:
    """
    Align the currently active layer vertically with respect to the current selection.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    align(Alignment.CenterVertical, layer, reference)


def align_horizontal(
    layer: Optional[Union[ArtLayer, LayerSet]] = None,
    reference: Optional[Union[ArtLayer, LayerSet]] = None
) -> None:
    """
    Align the currently active layer horizontally with respect to the current selection.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    align(Alignment.CenterHorizontal, layer, reference)


"""
POSITIONING
"""


def position_between_layers(
    layer: Union[ArtLayer, LayerSet],
    top_layer: Union[ArtLayer, LayerSet],
    bottom_layer: Union[ArtLayer, LayerSet]
) -> None:
    """
    Align layer vertically between two reference layers.
    @param layer: Layer to align vertically
    @param top_layer: Reference layer above the layer to be aligned.
    @param bottom_layer: Reference layer below the layer to be aligned.
    """
    app.activeDocument.selection.select([
        [0, top_layer.bounds[3]],
        [app.activeDocument.width, top_layer.bounds[3]],
        [app.activeDocument.width, bottom_layer.bounds[1]],
        [0, bottom_layer.bounds[1]]
    ])
    align_vertical(layer)
    app.activeDocument.selection.deselect()


def spread_layers_over_reference(
    layers: list[ArtLayer],
    ref: ArtLayer,
    gap: Optional[Union[int, float]] = None,
    inside_gap: Union[int, float, None] = None,
    outside_matching: bool = True
) -> None:
    """
    Spread layers apart across a reference layer.
    @param layers: List of ArtLayers or LayerSets.
    @param ref: Reference used as the maximum height boundary for all layers given.
    @param gap: Gap between the top of the reference and the first layer, or between all layers if not provided.
    @param inside_gap: Gap between each layer, calculated using leftover space if not provided.
    @param outside_matching: If enabled, will enforce top and bottom gap to match.
    """
    # Calculate outside gap if not provided
    outside_gap = gap
    if not gap:
        total_space = get_layer_dimensions(ref)['height'] - sum(
            [get_text_layer_dimensions(layer)['height'] for layer in layers]
        )
        outside_gap = total_space / (len(layers) + 1)

    # Position the top layer relative to the reference
    delta = (ref.bounds[1] + outside_gap) - layers[0].bounds[1]
    layers[0].translate(0, delta)

    # Calculate inside gap if not provided
    if gap and not inside_gap:
        # Calculate the inside gap
        ignored = 2 if outside_matching else 1
        spaces = len(layers) - 1 if outside_matching else len(layers)
        total_space = get_layer_dimensions(ref)['height'] - sum(
            [get_text_layer_dimensions(layer)['height'] for layer in layers]
        )
        inside_gap = (total_space - (ignored * gap)) / spaces
    elif not gap:
        # Use the outside gap uniformly
        inside_gap = outside_gap

    # Position the bottom layers relative to the top
    space_layers_apart(layers, inside_gap)


def space_layers_apart(layers: list[Union[ArtLayer, LayerSet]], gap: Union[int, float]) -> None:
    """
    Position list of layers apart using a given gap.
    @param layers: List of ArtLayers or LayerSets.
    @param gap: Gap in pixels.
    """
    # Position each layer relative to the one above it
    for i in range((len(layers) - 1)):
        delta = (layers[i].bounds[3] + gap) - layers[i + 1].bounds[1]
        layers[i + 1].translate(0, delta)


def frame_layer(
    layer: ArtLayer,
    reference: ArtLayer,
    smallest: bool = False,
    anchor: AnchorPosition = AnchorPosition.TopLeft,
    alignments: Optional[list[Alignment]] = None
) -> None:
    """
    Scale a layer equally to the bounds of a reference layer, then center the layer vertically and horizontally
    within those bounds.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = get_layer_dimensions(reference)

    # Scale the layer to fit either the largest, or the smallest dimension
    action = min if smallest else max
    scale = 100 * action((ref_dim['width'] / layer_dim['width']), (ref_dim['height'] / layer_dim['height']))
    layer.resize(scale, scale, anchor)

    # Make any alignments
    select_layer_bounds(reference)
    app.activeDocument.activeLayer = layer
    if alignments is None:
        # Default alignments are center horizontal and vertical
        alignments = [Alignment.CenterHorizontal, Alignment.CenterVertical]
    for a in alignments:
        align(a)
    app.activeDocument.selection.deselect()
