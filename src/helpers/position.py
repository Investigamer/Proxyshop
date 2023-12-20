"""
* Helpers: Positioning
"""
# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import DialogModes, AnchorPosition
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.enums.adobe import Dimensions
from src.helpers.bounds import (
    get_layer_dimensions,
    get_text_layer_dimensions,
    get_dimensions_from_bounds,
    LayerDimensions)

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

# Positioning
positions_horizontal = [Dimensions.Left, Dimensions.Right, Dimensions.CenterX]
positions_vertical = [Dimensions.Top, Dimensions.Bottom, Dimensions.CenterY]

"""
* Alignment Funcs
"""


def align(
    axis: Union[Dimensions, list[Dimensions], None] = None,
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Align the currently active layer to current selection, vertically or horizontal.

    Args:
        axis: Which axis to use when aligning the layer, can be provided as a single axis or list.
        layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
        reference: Reference to align the layer within. Uses current selection if not provided.
    """
    # Default axis is both
    axis = axis or [Dimensions.CenterX, Dimensions.CenterY]
    axis = [axis] if isinstance(axis, str) else axis
    x, y = 0, 0

    # Get the dimensions of layer and reference if not provided
    layer = layer or APP.activeDocument.activeLayer
    item: type[LayerDimensions] = get_layer_dimensions(layer)
    area: type[LayerDimensions] = get_dimensions_from_bounds(
        # Get dimensions from selection
        APP.activeDocument.selection.bounds
    ) if not reference else (
        # Dimensions provided or get dimensions from reference
        reference if (
            isinstance(reference, dict)
        ) else get_layer_dimensions(reference))

    # Single axis provided
    for n in axis:
        if n in positions_horizontal:
            x = area[n] - item[n]
        if n in positions_vertical:
            y = area[n] - item[n]

    # Shift location using the position difference
    layer.translate(x, y)


def align_all(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing CenterX and CenterY to align function."""
    align([Dimensions.CenterX, Dimensions.CenterY], layer, reference)


def align_vertical(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing CenterY to align function."""
    align(Dimensions.CenterY, layer, reference)


def align_horizontal(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing CenterX to align function."""
    align(Dimensions.CenterX, layer, reference)


def align_left(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Left to align function."""
    align(Dimensions.Left, layer, reference)


def align_right(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Right to align function."""
    align(Dimensions.Right, layer, reference)


def align_top(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Top to align function."""
    align(Dimensions.Top, layer, reference)


def align_bottom(
    layer: Union[ArtLayer, LayerSet, None] = None,
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Bottom to align function."""
    align(Dimensions.Bottom, layer, reference)


"""
* Positioning Funcs
"""


def position_between_layers(
    layer: Union[ArtLayer, LayerSet],
    top_layer: Union[ArtLayer, LayerSet],
    bottom_layer: Union[ArtLayer, LayerSet]
) -> None:
    """Align layer vertically between two reference layers.

    Args:
        layer: Layer to align vertically
        top_layer: Reference layer above the layer to be aligned.
        bottom_layer: Reference layer below the layer to be aligned.
    """
    docref = APP.activeDocument
    bounds = [0, top_layer.bounds[3], docref.width, bottom_layer.bounds[1]]
    align_vertical(layer, get_dimensions_from_bounds(bounds))


def position_dividers(
    dividers: list[Union[ArtLayer, LayerSet]],
    layers: list[Union[ArtLayer, LayerSet]]
) -> None:
    """Positions a list of dividers between a list of layers.

    Args:
        dividers: Divider layers to position, should contain 1 fewer objects than layers param.
        layers: Layers to position the dividers between.
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
    """Spread layers apart across a reference layer.

    Args:
        layers: List of ArtLayers or LayerSets.
        ref: Reference used as the maximum height boundary for all layers given.
        gap: Gap between the top of the reference and the first layer, or between all layers if not provided.
        inside_gap: Gap between each layer, calculated using leftover space if not provided.
        outside_matching: If enabled, will enforce top and bottom gap to match.
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
    """Position list of layers apart using a given gap.

    Args:
        layers: List of ArtLayers or LayerSets.
        gap: Gap in pixels.
    """
    # Position each layer relative to the one above it
    for i in range((len(layers) - 1)):
        delta = (layers[i].bounds[3] + gap) - layers[i + 1].bounds[1]
        layers[i + 1].translate(0, delta)


"""
* Framing Funcs
"""


def frame_layer(
    layer: Union[ArtLayer, LayerSet],
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions]],
    smallest: bool = False,
    anchor: AnchorPosition = AnchorPosition.TopLeft,
    alignments: Union[Dimensions, list[Dimensions], None] = None
) -> None:
    """Scale and position a layer within the bounds of a reference.

    Args:
        layer: Layer to scale and position.
        reference: Reference frame to position within.
        smallest: Whether to scale to smallest or largest edge.
        anchor: Anchor position for scaling the layer.
        alignments: Alignments used to position the layer.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = reference if isinstance(
        reference, dict
    ) else get_layer_dimensions(reference)

    # Scale the layer to fit either the largest, or the smallest dimension
    action = min if smallest else max
    scale = 100 * action((ref_dim['width'] / layer_dim['width']), (ref_dim['height'] / layer_dim['height']))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)


def frame_layer_by_height(
    layer: Union[ArtLayer, LayerSet],
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions]],
    anchor: AnchorPosition = AnchorPosition.TopLeft,
    alignments: Union[Dimensions, list[Dimensions], None] = None
) -> None:
    """Scale and position a layer based on the height of a reference layer.

    Args:
        layer: Layer to scale and position.
        reference: Reference frame to position within.
        anchor: Anchor position for scaling the layer.
        alignments: Alignments used to position the layer.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = reference if isinstance(
        reference, dict
    ) else get_layer_dimensions(reference)

    # Scale the layer to fit the height of the reference
    scale = 100 * (ref_dim['height'] / layer_dim['height'])
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)


def frame_layer_by_width(
    layer: Union[ArtLayer, LayerSet],
    reference: Union[ArtLayer, LayerSet, type[LayerDimensions]],
    anchor: AnchorPosition = AnchorPosition.TopLeft,
    alignments: Union[Dimensions, list[Dimensions], None] = None
) -> None:
    """Scale and position a layer based on the width of a reference layer.

    Args:
        layer: Layer to scale and position.
        reference: Reference frame to position within.
        anchor: Anchor position for scaling the layer.
        alignments: Alignments used to position the layer.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = reference if isinstance(
        reference, dict
    ) else get_layer_dimensions(reference)

    # Scale the layer to fit the height of the reference
    scale = 100 * (ref_dim['width'] / layer_dim['width'])
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)
