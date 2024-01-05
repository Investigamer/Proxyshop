"""
* Helpers: Positioning
"""
# Standard Library Imports
from typing import Optional, Union, Iterable

# Third Party Imports
from photoshop.api import DialogModes, AnchorPosition
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.enums.adobe import Dimensions
from src.helpers.bounds import (
    get_layer_dimensions,
    get_dimensions_from_bounds,
    LayerDimensions, get_layer_width, get_layer_height)
from src.helpers.selection import (
    select_overlapping,
    check_selection_bounds,
    select_bounds)
from src.utils.adobe import ReferenceLayer

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
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Align the currently active layer to current selection, vertically or horizontal.

    Args:
        axis: Which axis to use when aligning the layer, can be provided as a single axis or list.
        layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
        ref: Reference to align the layer within. Uses current selection if not provided.
    """
    # Default axis is both
    axis = axis or [Dimensions.CenterX, Dimensions.CenterY]
    axis = [axis] if isinstance(axis, str) else axis
    x, y = 0, 0

    # Get the dimensions of layer and reference if not provided
    layer = layer or APP.activeDocument.activeLayer
    item: type[LayerDimensions] = get_layer_dimensions(layer)
    area: type[LayerDimensions] = ref if isinstance(ref, dict) else (
        get_dimensions_from_bounds(APP.activeDocument.selection.bounds)
        if not ref else get_layer_dimensions(ref))

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
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing CenterX and CenterY to align function."""
    align([Dimensions.CenterX, Dimensions.CenterY], layer, ref)


def align_vertical(
    layer: Union[ArtLayer, LayerSet, None] = None,
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing CenterY to align function."""
    align(Dimensions.CenterY, layer, ref)


def align_horizontal(
    layer: Union[ArtLayer, LayerSet, None] = None,
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing CenterX to align function."""
    align(Dimensions.CenterX, layer, ref)


def align_left(
    layer: Union[ArtLayer, LayerSet, None] = None,
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Left to align function."""
    align(Dimensions.Left, layer, ref)


def align_right(
    layer: Union[ArtLayer, LayerSet, None] = None,
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Right to align function."""
    align(Dimensions.Right, layer, ref)


def align_top(
    layer: Union[ArtLayer, LayerSet, None] = None,
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Top to align function."""
    align(Dimensions.Top, layer, ref)


def align_bottom(
    layer: Union[ArtLayer, LayerSet, None] = None,
    ref: Union[ArtLayer, LayerSet, ReferenceLayer, type[LayerDimensions], None] = None
) -> None:
    """Utility definition for passing Bottom to align function."""
    align(Dimensions.Bottom, layer, ref)


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
    bounds = [0, top_layer.bounds[3], APP.activeDocument.width, bottom_layer.bounds[1]]
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
    ref: ReferenceLayer,
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
    # Get reference dimensions if not provided
    height = ref.dims['height']

    # Calculate outside gap if not provided
    outside_gap = gap
    if not gap:
        total_space = height - sum(
            [get_layer_dimensions(layer)['height'] for layer in layers])
        outside_gap = total_space / (len(layers) + 1)

    # Position the top layer relative to the reference
    delta = (ref.bounds[1] + outside_gap) - layers[0].bounds[1]
    layers[0].translate(0, delta)

    # Calculate inside gap if not provided
    if gap and not inside_gap:
        # Calculate the inside gap
        ignored = 2 if outside_matching else 1
        spaces = len(layers) - 1 if outside_matching else len(layers)
        total_space = height - sum(
            [get_layer_dimensions(layer)['height'] for layer in layers])
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
    ref: Union[ArtLayer, LayerSet, type[LayerDimensions]],
    smallest: bool = False,
    anchor: AnchorPosition = AnchorPosition.MiddleCenter,
    alignments: Union[Dimensions, list[Dimensions], None] = None,
    scale: int = 100,
) -> None:
    """Scale and position a layer within the bounds of a reference.

    Args:
        layer: Layer to scale and position.
        ref: Reference frame to position within.
        smallest: Whether to scale to smallest or largest edge.
        anchor: Anchor position for scaling the layer.
        alignments: Alignments used to position the layer.
        scale: Percentage of the reference size to scale to, defaults to 100.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = ref if isinstance(ref, dict) else get_layer_dimensions(ref)

    # Scale the layer to fit either the largest, or the smallest dimension
    action = min if smallest else max
    scale = scale * action(
        (ref_dim['width'] / layer_dim['width']),
        (ref_dim['height'] / layer_dim['height']))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)


def frame_layer_by_height(
    layer: Union[ArtLayer, LayerSet],
    ref: Union[ArtLayer, LayerSet, type[LayerDimensions]],
    anchor: AnchorPosition = AnchorPosition.MiddleCenter,
    alignments: Union[Dimensions, list[Dimensions], None] = None,
    scale: int = 100,
) -> None:
    """Scale and position a layer based on the height of a reference layer.

    Args:
        layer: Layer to scale and position.
        ref: Reference frame to position within.
        anchor: Anchor position for scaling the layer.
        alignments: Alignments used to position the layer.
        scale: Percentage of the reference size to scale to, defaults to 100.
    """
    # Get reference dimensions
    ref_dim = ref if isinstance(ref, dict) else get_layer_dimensions(ref)

    # Scale the layer to fit the height of the reference
    scale = scale * (ref_dim['height'] / get_layer_height(layer))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)


def frame_layer_by_width(
    layer: Union[ArtLayer, LayerSet],
    ref: Union[ArtLayer, LayerSet, type[LayerDimensions]],
    anchor: AnchorPosition = AnchorPosition.MiddleCenter,
    alignments: Union[Dimensions, list[Dimensions], None] = None,
    scale: int = 100,
) -> None:
    """Scale and position a layer based on the width of a reference layer.

    Args:
        layer: Layer to scale and position.
        ref: Reference frame to position within.
        anchor: Anchor position for scaling the layer.
        alignments: Alignments used to position the layer.
        scale: Percentage of the reference size to scale to, defaults to 100.
    """
    # Get reference dimensions
    ref_dim = ref if isinstance(ref, dict) else get_layer_dimensions(ref)

    # Scale the layer to fit the height of the reference
    scale = scale * (ref_dim['width'] / get_layer_width(layer))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or [Dimensions.CenterX, Dimensions.CenterY], layer, ref_dim)


"""
* Positioning by Reference
"""


def clear_reference_vertical(
        layer: Optional[ArtLayer] = None,
        reference: Union[ArtLayer, list[Union[int, float]], None] = None
) -> Union[int, float]:
    """Nudges a layer clear vertically of a given reference layer or area.

    Args:
        layer: Layer to nudge, so it avoids the reference area.
        reference: Layer or bounds area to nudge clear of.

    Returns:
        The number of pixels layer was translated by (negative or positive indicating direction).
    """
    # Use active layer if not provided
    docref = APP.activeDocument
    docsel = docref.selection
    layer = layer or docref.activeLayer

    # Use reference bounds if layer provided, or bounds provided, or active selection fallback
    ref_bounds = reference.bounds if isinstance(reference, ArtLayer) else (
        reference if isinstance(reference, Iterable) else docsel.bounds)

    # Select reference bounds, then select overlapping pixels on our layer
    select_bounds(ref_bounds)
    select_overlapping(layer)

    # Check if selection is empty, if not translate our layer to clear the reference
    if selected_bounds := check_selection_bounds(docsel):
        delta = ref_bounds[1] - selected_bounds[3]
        docsel.deselect()
        layer.translate(0, delta)
        return delta
    return 0
