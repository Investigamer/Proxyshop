"""
* Helpers: Positioning
"""
# Standard Library Imports
import math
from typing import Optional, Union

# Third Party Imports
from photoshop.api import DialogModes, AnchorPosition
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._selection import Selection
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.enums.adobe import Dimensions
from src.helpers.bounds import (
    get_layer_dimensions,
    get_dimensions_from_bounds,
    LayerDimensions,
    get_layer_width,
    get_layer_height)
from src.helpers.selection import (
    select_overlapping,
    check_selection_bounds,
    select_bounds)
from src.helpers.text import get_font_size, set_text_size_and_leading
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
    bottom_layer: Union[ArtLayer, LayerSet],
    docref: Optional[Document] = None
) -> None:
    """Align layer vertically between two reference layers.

    Args:
        layer: Layer to align vertically
        top_layer: Reference layer above the layer to be aligned.
        bottom_layer: Reference layer below the layer to be aligned.
        docref: Document reference, use active if not provided.
    """
    docref = docref or APP.activeDocument
    bounds = (0, top_layer.bounds[3], docref.width, bottom_layer.bounds[1])
    align_vertical(layer, get_dimensions_from_bounds(bounds))


def position_dividers(
    dividers: list[Union[ArtLayer, LayerSet]],
    layers: list[Union[ArtLayer, LayerSet]],
    docref: Optional[Document] = None
) -> None:
    """Positions a list of dividers between a list of layers.

    Args:
        dividers: Divider layers to position, should contain 1 fewer objects than layers param.
        layers: Layers to position the dividers between.
        docref: Document reference, use active if not provided.
    """
    for i in range(len(layers) - 1):
        position_between_layers(
            layer=dividers[i],
            top_layer=layers[i],
            bottom_layer=layers[i + 1],
            docref=docref)


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
    panorama_position: [int, int],
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
    layer.translate(-ref_dim['width'] * panorama_position[0], 0)
    layer.translate(0, -ref_dim['height'] * panorama_position[1])


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


def check_reference_overlap(
    layer: Optional[ArtLayer],
    ref_bounds: tuple[int, int, int, int],
    docsel: Optional[Selection] = None
):
    """Checks if a layer is overlapping with given set of bounds.

    Args:
        layer: Layer to check collision for.
        ref_bounds: Bounds to check collision with.
        docsel: Selection object, pull from document if not provided.

    Returns:
        Bounds if overlap exists, otherwise None.
    """
    select_bounds(ref_bounds, selection=docsel)
    select_overlapping(layer)
    if bounds := check_selection_bounds(docsel):
        docsel.deselect()
        return ref_bounds[1] - bounds[3]
    return 0


def clear_reference_vertical(
    layer: ArtLayer,
    ref: ReferenceLayer,
    docsel: Optional[Selection] = None
) -> Union[int, float]:
    """Nudges a layer clear vertically of a given reference layer or area.

    Args:
        layer: Layer to nudge, so it avoids the reference area.
        ref: Layer or bounds area to nudge clear of.
        docsel: Selection object, pull from document if not provided.

    Returns:
        The number of pixels layer was translated by (negative or positive indicating direction).
    """
    # Use active layer if not provided
    docsel = docsel or APP.activeDocument.selection
    delta = check_reference_overlap(layer=layer, ref_bounds=ref.bounds, docsel=docsel)

    # Check if selection is empty, if not translate our layer to clear the reference
    if delta < 0:
        layer.translate(0, delta)
        return delta
    return 0


def clear_reference_vertical_multi(
    text_layers: list[ArtLayer],
    ref: ReferenceLayer,
    loyalty_ref: ReferenceLayer,
    space: Union[int, float],
    uniform_gap: bool = False,
    font_size: Optional[float] = None,
    step: float = 0.2,
    docref: Optional[Document] = None,
    docsel: Optional[Selection] = None
) -> None:
    """Shift or resize multiple text layers to prevent vertical collision with a reference area.

    Note:
        Used on Planeswalker cards to allow multiple text abilities to clear the loyalty box.

    Args:
        text_layers: Ability text layers to nudge or resize.
        ref: Reference area ability text layers must fit inside.
        loyalty_ref: Reference area that covers the loyalty box.
        space: Minimum space between planeswalker abilities.
        uniform_gap: Whether the gap between abilities should be the same between each ability.
        font_size: The current font size of the text layers, if known. Otherwise, calculate automatically.
        step: The amount of font size and leading to step down each iteration.
        docref: Reference document, use active if not provided (improves performance).
        docsel: Selection object, pull from document if not provided (improves performance).
    """
    # Return if adjustments weren't provided
    if not loyalty_ref:
        return

    # Establish fresh data
    if font_size is None:
        font_size = get_font_size(text_layers[0])
    layers = text_layers.copy()
    movable = len(layers)-1

    # Calculate inside gap
    total_space = ref.dims['height'] - sum([get_layer_height(layer) for layer in text_layers])
    if not uniform_gap:
        inside_gap = ((total_space - space) - (ref.bounds[3] - layers[-1].bounds[1])) / movable
    else:
        inside_gap = total_space / (len(layers) + 1)
    leftover = (inside_gap - space) * movable

    # Does the bottom layer overlap with the loyalty box?
    delta = check_reference_overlap(
        layer=layers[-1],
        ref_bounds=loyalty_ref.bounds,
        docsel=docsel)
    if delta >= 0:
        return

    # Calculate the total distance needing to be covered
    total_move = 0
    layers.pop(0)
    for n, lyr in enumerate(layers):
        total_move += math.fabs(delta) * ((len(layers) - n)/len(layers))

    # Text layers can just be shifted upwards
    if total_move < leftover:
        layers.reverse()
        for n, lyr in enumerate(layers):
            move_y = delta * ((len(layers) - n)/len(layers))
            lyr.translate(0, move_y)
        return

    # Layer gap would be too small, need to resize text then shift upward
    font_size -= step
    for lyr in text_layers:
        set_text_size_and_leading(
            layer=lyr,
            size=font_size,
            leading=font_size)

    # Space apart planeswalker text evenly
    spread_layers_over_reference(
        layers=text_layers,
        ref=ref,
        gap=space if not uniform_gap else None,
        outside_matching=False)

    # Check for another iteration
    clear_reference_vertical_multi(
        text_layers=text_layers,
        ref=ref,
        loyalty_ref=loyalty_ref,
        space=space,
        uniform_gap=uniform_gap,
        font_size=font_size,
        docref=docref,
        docsel=docsel)
