# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import DialogModes, AnchorPosition
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.constants import con
from src.helpers.bounds import get_layer_dimensions, get_text_layer_dimensions, get_dimensions_from_bounds
from src.enums.photoshop import Dimensions

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

# Positioning
positions_horizontal = [Dimensions.Left, Dimensions.Right, Dimensions.CenterX]
positions_vertical = [Dimensions.Top, Dimensions.Bottom, Dimensions.CenterY]


"""
ALIGNMENT
"""


def align(
    axis: Union[str, list[str], None] = None,
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """
    Align the currently active layer to current selection, vertically or horizontal.
    @param axis: Which axis use when aligning the layer, can be provided as a single axis or list.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    # Default axis is both
    axis = axis or [Dimensions.CenterX, Dimensions.CenterY]

    # Get the dimensions of the reference and layer if not provided
    area = get_dimensions_from_bounds(app.activeDocument.selection.bounds) if not reference else (
        reference if isinstance(reference, dict) else get_layer_dimensions(reference))
    layer = layer or app.activeDocument.activeLayer
    item = get_layer_dimensions(layer)

    # Single axis provided
    if isinstance(axis, str):
        x = area[axis] - item[axis] if axis in positions_horizontal else 0
        y = area[axis] - item[axis] if axis in positions_vertical else 0
    else:
        x = area[axis[0]] - item[axis[0]]
        y = area[axis[1]] - item[axis[1]]

    # Shift location using the position difference
    layer.translate(x, y)


def align_all(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing CenterX and CenterY to align function."""
    align([Dimensions.CenterX, Dimensions.CenterY], layer, reference)


def align_vertical(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing CenterY to align function."""
    align(Dimensions.CenterY, layer, reference)


def align_horizontal(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing CenterX to align function."""
    align(Dimensions.CenterX, layer, reference)


def align_left(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing Left to align function."""
    align(Dimensions.Left, layer, reference)


def align_right(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing Right to align function."""
    align(Dimensions.Right, layer, reference)


def align_top(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing Top to align function."""
    align(Dimensions.Top, layer, reference)


def align_bottom(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, dict, None] = None
) -> None:
    """Utility definition for passing Bottom to align function."""
    align(Dimensions.Bottom, layer, reference)


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
    docref = app.activeDocument
    bounds = [0, top_layer.bounds[3], docref.width, bottom_layer.bounds[1]]
    align_vertical(layer, reference=get_dimensions_from_bounds(bounds))


def position_dividers(
    dividers: list[Union[ArtLayer, LayerSet]],
    layers: list[Union[ArtLayer, LayerSet]]
) -> None:
    """
    Positions a list of dividers between a list of layers.
    @param dividers: Divider layers to position, should contain 1 fewer objects than layers param.
    @param layers: Layers to position the dividers between.
    """
    for i in range(len(layers) - 1):
        position_between_layers(dividers[i], layers[i], layers[i + 1])


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


def frame_panorama(
    layer: Union[ArtLayer, LayerSet],
    reference: Union[ArtLayer, LayerSet, dict],
    panorama_element: int,
    panorama_size: [int, int],
    anchor: AnchorPosition = AnchorPosition.TopLeft
):
    """
    Scale and position a layer within the bounds of a reference layer to make a borderless panorama.
    @param layer: Layer to scale and position.
    @param reference: Reference frame to position within.
    @param anchor: Anchor position for scaling the layer.
    """
    # Get layer and full reference dimensions
    art_dim = get_layer_dimensions(layer)
    ref_dim = reference if isinstance(reference, dict) else get_layer_dimensions(reference)
    ref_dim['width'] = ref_dim['width'] * panorama_size[0]
    ref_dim['height'] = ref_dim['height'] * panorama_size[1]

    # Scale the layer to fit either the largest dimension
    scale = 100 * max((ref_dim['width'] / art_dim['width']), (ref_dim['height'] / art_dim['height']))
    layer.resize(scale, scale, anchor)

    # Align the original layer on the left
    alignments = [Dimensions.Left, Dimensions.CenterY]
    align(alignments, layer, ref_dim)
    layer.translate(0, ref_dim['height'] / panorama_size[1])

    # Move the layer according to the given index
    ref_dim = reference if isinstance(reference, dict) else get_layer_dimensions(reference)
    pano_x = panorama_element % panorama_size[0]
    pano_y = panorama_element // panorama_size[0]
    layer.translate(-ref_dim['width'] * pano_x, 0)
    layer.translate(0, -ref_dim['height'] * pano_y)
    
def frame_layer(
    layer: Union[ArtLayer, LayerSet],
    reference: Union[ArtLayer, LayerSet, dict],
    smallest: bool = False,
    anchor: AnchorPosition = AnchorPosition.TopLeft,
    alignments: Union[Dimensions, list[Dimensions], None] = None
):
    """
    Scale and position a layer within the bounds of a reference layer.
    @param layer: Layer to scale and position.
    @param reference: Reference frame to position within.
    @param smallest: Whether to scale to smallest or largest edge.
    @param anchor: Anchor position for scaling the layer.
    @param alignments: Alignments used to position the layer.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = reference if isinstance(reference, dict) else get_layer_dimensions(reference)

    # Scale the layer to fit either the largest, or the smallest dimension
    action = min if smallest else max
    scale = 100 * action((ref_dim['width'] / layer_dim['width']), (ref_dim['height'] / layer_dim['height']))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)
