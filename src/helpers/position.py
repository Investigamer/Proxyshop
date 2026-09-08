"""
* Helpers: Positioning
"""

from collections.abc import Sequence
from enum import Enum
from typing import Literal

from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api._selection import Selection
from photoshop.api.enumerations import AnchorPosition

from src import APP
from src.enums.adobe import Dimensions
from src.helpers.bounds import (
    LayerDimensions,
    get_card_dimensions,
    get_dimensions_from_bounds,
    get_layer_dimensions,
    get_layer_height,
    get_layer_width,
)
from src.helpers.selection import (
    check_selection_bounds,
    select_layer_pixels,
    select_overlapping,
)
from src.utils.adobe import ReferenceLayer

# Positioning
positions_horizontal = [Dimensions.Left, Dimensions.Right, Dimensions.CenterX]
positions_vertical = [Dimensions.Top, Dimensions.Bottom, Dimensions.CenterY]

"""
* Alignment Funcs
"""

DimensionNames = Literal[
    "width", "height", "center_x", "center_y", "left", "right", "top", "bottom"
]


def align(
    axis: DimensionNames | Sequence[DimensionNames] | None = None,
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Align the currently active layer to current selection, vertically or horizontal.

    Args:
        axis: Which axis to use when aligning the layer, can be provided as a single axis or list.
        layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
        ref: Reference to align the layer within. Uses current selection if not provided.
    """
    # Default axis is both
    axis = axis or ("center_x", "center_y")
    axis = [axis] if isinstance(axis, str) else axis
    x, y = 0, 0

    # Get the dimensions of layer and reference if not provided
    layer = layer or APP.instance.activeDocument.activeLayer
    item = get_layer_dimensions(layer)
    area = (
        ref
        if isinstance(ref, dict)
        else (
            get_dimensions_from_bounds(APP.instance.activeDocument.selection.bounds)
            if not ref
            else get_layer_dimensions(ref)
        )
    )

    # Single axis provided
    for n in axis:
        if n in positions_horizontal:
            x = area[n] - item[n]
        if n in positions_vertical:
            y = area[n] - item[n]

    # Shift location using the position difference
    layer.translate(x, y)


def align_all(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing CenterX and CenterY to align function."""
    align(["center_x", "center_y"], layer, ref)


def align_vertical(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing CenterY to align function."""
    align("center_y", layer, ref)


def align_horizontal(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing CenterX to align function."""
    align("center_x", layer, ref)


def align_left(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing Left to align function."""
    align("left", layer, ref)


def align_right(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing Right to align function."""
    align("right", layer, ref)


def align_top(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing Top to align function."""
    align("top", layer, ref)


def align_bottom(
    layer: ArtLayer | LayerSet | None = None,
    ref: ArtLayer | LayerSet | ReferenceLayer | LayerDimensions | None = None,
) -> None:
    """Utility definition for passing Bottom to align function."""
    align("bottom", layer, ref)


"""
* Positioning Funcs
"""


def position_between_layers(
    layer: ArtLayer | LayerSet,
    top_layer: ArtLayer | LayerSet,
    bottom_layer: ArtLayer | LayerSet,
    docref: Document | None = None,
) -> None:
    """Align layer vertically between two reference layers.

    Args:
        layer: Layer to align vertically
        top_layer: Reference layer above the layer to be aligned.
        bottom_layer: Reference layer below the layer to be aligned.
        docref: Document reference, use active if not provided.
    """
    docref = docref or APP.instance.activeDocument
    bounds = (0, top_layer.bounds[3], docref.width, bottom_layer.bounds[1])
    align_vertical(layer, get_dimensions_from_bounds(bounds))


def position_dividers(
    dividers: Sequence[ArtLayer | LayerSet],
    layers: Sequence[ArtLayer | LayerSet],
    docref: Document | None = None,
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
            docref=docref,
        )


def spread_layers_over_reference(
    layers: list[ArtLayer],
    ref: ReferenceLayer,
    gap: float = 0,
    inside_gap: float = 0,
    outside_matching: bool = True,
) -> float:
    """Spread layers apart across a reference layer.

    Args:
        layers: List of ArtLayers or LayerSets.
        ref: Reference used as the maximum height boundary for all layers given.
        gap: Gap between the top of the reference and the first layer, or between all layers if not provided.
        inside_gap: Gap between each layer, calculated using leftover space if not provided.
        outside_matching: If enabled, will enforce top and bottom gap to match.

    Returns:
        Calculated or given inside gap
    """
    # Get reference dimensions if not provided
    height = ref.dims["height"]

    # Calculate outside gap if not provided
    outside_gap = gap
    if not gap:
        total_space = height - sum(
            [get_layer_dimensions(layer)["height"] for layer in layers]
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
        total_space = height - sum(
            [get_layer_dimensions(layer)["height"] for layer in layers]
        )
        inside_gap = (total_space - (ignored * gap)) / spaces
    elif not gap:
        # Use the outside gap uniformly
        inside_gap = outside_gap

    # Position the bottom layers relative to the top
    space_layers_apart(layers, inside_gap)

    return inside_gap


def space_layers_apart(layers: Sequence[ArtLayer | LayerSet], gap: float) -> None:
    """Position list of layers apart using a given gap.

    Args:
        layers: List of ArtLayers or LayerSets.
        gap: Gap in pixels.
    """
    # Position each layer relative to the one above it
    for i in range(len(layers) - 1):
        delta = (layers[i].bounds[3] + gap) - layers[i + 1].bounds[1]
        layers[i + 1].translate(0, delta)


"""
* Framing Funcs
"""


def frame_panorama(
    layer: ArtLayer | LayerSet,
    document: Document,
    panorama_position: tuple[int, int],
    panorama_size: tuple[int, int],
    anchor: AnchorPosition = AnchorPosition.TopLeft,
) -> None:
    """
    Scale and position a layer within the bounds of a reference layer to make a borderless panorama.
    @param layer: Layer to scale and position.
    @param reference: Reference frame to position within.
    @param anchor: Anchor position for scaling the layer.
    """
    # Get layer and full reference dimensions
    art_dim: LayerDimensions = get_layer_dimensions(layer)
    ref_dim = get_card_dimensions(document)
    panorama_dim = (
        ref_dim["width"] * panorama_size[0],
        ref_dim["height"] * panorama_size[1],
    )

    # Scale the layer to fit either the largest dimension
    scale = 100 * max(
        (panorama_dim[0] / art_dim["width"]), (panorama_dim[1] / art_dim["height"])
    )
    layer.resize(scale, scale, anchor)

    # Align the original layer on the top-left
    alignments = ("left", "top")
    align(alignments, layer, ref_dim)

    # Move the layer according to the given index
    pano_x = -ref_dim["width"] * panorama_position[0]
    pano_y = -ref_dim["height"] * panorama_position[1]
    layer.translate(pano_x, pano_y)


def frame_layer(
    layer: ArtLayer | LayerSet,
    ref: ArtLayer | LayerSet | LayerDimensions,
    smallest: bool = False,
    anchor: AnchorPosition = AnchorPosition.MiddleCenter,
    alignments: DimensionNames | Sequence[DimensionNames] | None = None,
    scale: float = 100,
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
        (ref_dim["width"] / layer_dim["width"]),
        (ref_dim["height"] / layer_dim["height"]),
    )
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or ("center_x", "center_y"), layer, ref_dim)


def frame_layer_by_height(
    layer: ArtLayer | LayerSet,
    ref: ArtLayer | LayerSet | LayerDimensions,
    anchor: AnchorPosition = AnchorPosition.MiddleCenter,
    alignments: DimensionNames | Sequence[DimensionNames] | None = None,
    scale: float = 100,
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
    scale = scale * (ref_dim["height"] / get_layer_height(layer))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or ("center_x", "center_y"), layer, ref_dim)


def frame_layer_by_width(
    layer: ArtLayer | LayerSet,
    ref: ArtLayer | LayerSet | LayerDimensions,
    anchor: AnchorPosition = AnchorPosition.MiddleCenter,
    alignments: DimensionNames | Sequence[DimensionNames] | None = None,
    scale: float = 100,
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
    scale = scale * (ref_dim["width"] / get_layer_width(layer))
    layer.resize(scale, scale, anchor)

    # Default alignments are center horizontal and vertical
    align(alignments or ("center_x", "center_y"), layer, ref_dim)


"""
* Positioning by Reference
"""


class RefSide(Enum):
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4
    ANY = 5


def check_bounds_overlap(
    bounds: tuple[float, float, float, float],
    ref_bounds: tuple[float, float, float, float],
    ref_side: RefSide,
) -> bool:
    match ref_side:
        case RefSide.LEFT:
            return bounds[2] > ref_bounds[0]
        case RefSide.TOP:
            return bounds[3] > ref_bounds[1]
        case RefSide.RIGHT:
            return bounds[0] < ref_bounds[2]
        case RefSide.BOTTOM:
            return bounds[1] < ref_bounds[3]
        case RefSide.ANY:
            overlap_width = min(bounds[2], ref_bounds[2]) - max(
                bounds[0], ref_bounds[0]
            )
            overlap_height = min(bounds[3], ref_bounds[3]) - max(
                bounds[1], ref_bounds[1]
            )
            return overlap_width > 0 and overlap_height > 0


def check_reference_overlap(
    layer: ArtLayer,
    ref: ArtLayer,
    ref_side: RefSide = RefSide.TOP,
    docsel: Selection | None = None,
) -> float:
    """Checks if a layer is overlapping with given set of bounds.

    Args:
        layer: Layer to check collision for.
        ref_bounds: Bounds to check collision with.
        docsel: Selection object, pull from document if not provided.

    Returns:
        Amount of overlap between `ref_side` and the opposing side of `layer`.
    """
    selection = docsel or APP.instance.activeDocument.selection
    select_layer_pixels(ref)
    select_overlapping(layer)
    if bounds := check_selection_bounds(selection):
        selection.deselect()
        ref_bounds = ref.bounds
        if ref_side == RefSide.LEFT:
            return ref_bounds[0] - bounds[2]
        if ref_side == RefSide.TOP:
            return ref_bounds[1] - bounds[3]
        if ref_side == RefSide.RIGHT:
            return ref_bounds[2] - bounds[0]
        else:
            return ref_bounds[3] - bounds[1]
    return 0


def clear_reference_vertical(
    layer: ArtLayer, ref: ReferenceLayer, docsel: Selection | None = None
) -> int | float:
    """Nudges a layer clear vertically of a given reference layer or area.

    Args:
        layer: Layer to nudge, so it avoids the reference area.
        ref: Layer or bounds area to nudge clear of.
        docsel: Selection object, pull from document if not provided.

    Returns:
        The number of pixels layer was translated by (negative or positive indicating direction).
    """
    # Use active layer if not provided
    docsel = docsel or APP.instance.activeDocument.selection
    delta = check_reference_overlap(layer=layer, ref=ref, docsel=docsel)

    # Check if selection is empty, if not translate our layer to clear the reference
    if delta < 0:
        layer.translate(0, delta)
        return delta
    return 0
