"""
Utility functions to format text
"""
# Standard Library Imports
import math
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    DialogModes,
    LayerKind,
    RasterizeType
)
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api.text_item import TextItem

# Local Imports
from src import APP, CONSOLE
from src.enums.mtg import non_italics_abilities, SymbolColor
from src.helpers.bounds import (
    get_width_no_effects,
    get_textbox_width,
    get_layer_height,
    get_layer_width)
from src.helpers.position import spread_layers_over_reference
from src.helpers.selection import select_layer_bounds
from src.helpers.text import set_text_size, get_font_size, set_text_size_and_leading
from src.utils.adobe import ReferenceLayer
from src.utils.regex import Reg

# QOL Definitions
sID = APP.stringIDToTypeID
cID = APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Types
"""

# (Start index, end index)
CardItalicString = tuple[int, int]

# (Start index, list of colors for each character)
CardSymbolString = tuple[int, list[SymbolColor]]

"""
* Classes
"""


def locate_symbols(
    text: str,
    symbol_map: dict[str, tuple[str, list[SymbolColor]]]
) -> tuple[str, list[CardSymbolString]]:
    """Locate symbols in the input string, replace them with the proper characters from the NDPMTG font,
    and determine the colors those characters need to be.

    Args:
        text: String to analyze for symbols.
        symbol_map: Maps a characters and colors to a scryfall symbol string.

    Returns:
        Tuple containing the modified string, and a list of dictionaries containing the location and color
            of each symbol to format.
    """
    # Is there a symbol in this text?
    if '{' not in text:
        return text, []

    # Starting values
    symbol_indices: list[CardSymbolString] = []
    start, end = text.find('{'), text.find('}')

    # Look for symbols in the text
    while 0 <= start <= end:
        symbol = text[start:end + 1]
        try:
            # Replace the symbol, add its location and color
            symbol_string, symbol_color = symbol_map[symbol]
            text = text.replace(symbol, symbol_string, 1)
            symbol_indices.append((start, symbol_color))
        except (KeyError, IndexError):
            CONSOLE.update(f"Symbol not recognized: {symbol}")
            text = text.replace(symbol, symbol.strip('{}'))
        # Move to the next symbols
        start, end = text.find('{'), text.find('}')
    return text, symbol_indices


def locate_italics(
    st: str,
    italics_strings: list,
    symbol_map: dict[str, tuple[str, list[SymbolColor]]]
) -> list[CardItalicString]:
    """Locate all instances of italic strings in the input string and record their start and end indices.

    Args:
        st: String to search for italics strings.
        italics_strings: List of italics strings to look for.
        symbol_map: Maps a characters and colors to a scryfall symbol string.

    Returns:
        List of italic string indices (start and end).
    """
    indexes = []
    for italic in italics_strings:

        # Look for symbols present in italicized text
        if '{' in italic:
            start = italic.find('{')
            end = italic.find('}')
            while 0 <= start < end:
                # Replace the symbol
                symbol = italic[start:end + 1]
                try:
                    italic = italic.replace(symbol, symbol_map[symbol][0])
                except (KeyError, IndexError):
                    CONSOLE.update(f"Symbol not recognized: {symbol}")
                    st = st.replace(symbol, symbol.strip('{}'))
                # Move to the next symbol
                start, end = italic.find('{'), italic.find('}')

        # Locate Italicized text
        end_index = 0
        while True:
            start_index = st.find(italic, end_index)
            if start_index < 0:
                break
            end_index = start_index + len(italic)
            indexes.append((start_index, end_index))

    # Return list of italics indexes
    return indexes


def generate_italics(card_text: str) -> list[str]:
    """Generates italics text array from card text to italicise all text within (parentheses) and all ability words.

    Args:
        card_text: Text to search for strings that need to be italicised.

    Returns:
        List of italics strings.
    """
    italic_text = []

    # Find and add reminder text
    end_index = 0
    while True:
        start_index = card_text.find("(", end_index)
        if start_index < 0:
            break
        end_index = card_text.find(")", start_index + 1) + 1
        italic_text.append(card_text[start_index:end_index])

    # Determine whether to look for ability words
    if ' — ' not in card_text:
        return italic_text

    # Find and add ability words
    for match in Reg.TEXT_ABILITY.findall(card_text):
        # Cover "Davros, Dalek Creator" case
        if match.count(' ') > 6:
            continue
        # Cover "Mirrodin Besieged" case
        if f"• {match}" in card_text and "choose one" not in card_text.lower():
            continue
        # Non-Italicized Abilities
        if match in non_italics_abilities:
            continue
        # "Celebr-8000" case, number digit only
        if match.isnumeric() and len(match) < 3:
            continue
        italic_text.append(match)
    return italic_text


def strip_reminder_text(text: str) -> str:
    """Strip out any reminder text from a given oracle text. Reminder text appears in parentheses.

    Args:
        text: Text that may contain reminder text.

    Returns:
        Oracle text with no reminder text.
    """
    # Skip if there's no reminder text present
    if '(' not in text:
        return text

    # Remove reminder text
    text_stripped = Reg.TEXT_REMINDER.sub("", text)

    # Remove any extra whitespace
    text_stripped = Reg.EXTRA_SPACE.sub('', text_stripped).strip()

    # Return the stripped text if it isn't empty
    if text_stripped:
        return text_stripped
    return text


def ensure_visible_reference(reference: ArtLayer) -> Optional[TextItem]:
    """Ensures that a layer used for reference has bounds if it is a text layer.

    Args:
        reference: Reference layer that might be a TextLayer.

    Returns:
        TextItem if reference is an empty text layer, otherwise None.
    """
    if isinstance(reference, LayerSet):
        return None
    if reference.kind is LayerKind.TextLayer:
        if reference.bounds == (0, 0, 0, 0):
            TI = reference.textItem
            TI.contents = "."
            return TI
    return None


def scale_text_right_overlap(layer: ArtLayer, reference: ArtLayer, gap: int = 30) -> None:
    """Scales a text layer down (in 0.2 pt increments) until its right bound
    has a 30 px~ (based on DPI) clearance from a reference layer's left bound.

    Args:
        layer: The text item layer to scale.
        reference: Reference layer we need to avoid.
        gap: Minimum gap to ensure between the layer and reference (DPI adjusted).
    """
    # Ensure a valid and visible reference layer
    if not reference:
        return
    ref_TI = ensure_visible_reference(reference)

    # Set starting variables
    font_size = old_size = get_font_size(layer)
    ref_left_bound = reference.bounds[0] - APP.scale_by_dpi(gap)
    step, half_step = 0.4, 0.2

    # Guard against reference being left of the layer
    if ref_left_bound < layer.bounds[0]:
        # Reset reference
        if ref_TI:
            ref_TI.contents = ''
        return

    # Make our first check if scaling is necessary
    if continue_scaling := bool(layer.bounds[2] > ref_left_bound):

        # Step down the font till it clears the reference
        while continue_scaling:
            font_size -= step
            set_text_size(layer, font_size)
            continue_scaling = bool(layer.bounds[2] > ref_left_bound)

        # Go up a half step
        font_size += half_step
        set_text_size(layer, font_size)

        # If out of bounds, revert half step
        if layer.bounds[2] > ref_left_bound:
            font_size -= half_step
            set_text_size(layer, font_size)

        # Shift baseline up to keep text centered vertically
        layer.textItem.baselineShift = (old_size * 0.3) - (font_size * 0.3)

    # Fix corrected reference layer
    if ref_TI:
        # Reset reference
        ref_TI.contents = ''


def scale_text_left_overlap(layer: ArtLayer, reference: ArtLayer, gap: int = 30) -> None:
    """Scales a text layer down (in 0.2 pt increments) until its left bound
    has a 30 px~ (based on DPI) clearance from a reference layer's right bound.

    Args:
        layer: The text item layer to scale.
        reference: Reference layer we need to avoid.
        gap: Minimum gap to ensure between the layer and reference (DPI adjusted).
    """
    # Ensure a valid and visible reference layer
    if not reference or reference.bounds == [0, 0, 0, 0]:
        return
    ref_TI = ensure_visible_reference(reference)

    # Set starting variables
    font_size = old_size = get_font_size(layer)
    ref_right_bound = reference.bounds[2] + APP.scale_by_dpi(gap)
    step, half_step = 0.4, 0.2

    # Guard against reference being right of the layer
    if layer.bounds[0] < reference.bounds[0]:
        # Reset reference
        if ref_TI:
            ref_TI.contents = ''
        return

    # Make our first check if scaling is necessary
    if continue_scaling := bool(ref_right_bound > layer.bounds[0]):

        # Step down the font till it clears the reference
        while continue_scaling:
            font_size -= step
            set_text_size(layer, font_size)
            continue_scaling = bool(ref_right_bound > layer.bounds[0])

        # Go up a half step
        font_size += half_step
        set_text_size(layer, font_size)

        # If text not in bounds, revert half step
        if ref_right_bound > layer.bounds[0]:
            font_size -= half_step
            set_text_size(layer, font_size)

        # Shift baseline up to keep text centered vertically
        layer.textItem.baselineShift = (old_size * 0.3) - (font_size * 0.3)

    # Fix corrected reference layer
    if ref_TI:
        ref_TI.contents = ''


def scale_text_to_width(
    layer: ArtLayer,
    width: int,
    spacing: int = 64,
    step: float = 0.4,
    font_size: Optional[float] = None
) -> Optional[float]:
    """Resize a given text layer's font size/leading until it fits inside a reference width.

    Args:
        layer: Text layer to scale.
        width: Width the text layer must fit (after spacing added).
        spacing: Amount of DPI adjusted spacing to pad the width.
        step: Amount to step font size down by in each check.
        font_size: The starting font size if pre-calculated.

    Returns:
        Font size if font size is calculated during operation, otherwise None.
    """
    # Cancel if we're already within expected bounds
    width = width - APP.scale_by_dpi(spacing)
    continue_scaling = bool(width < get_layer_width(layer))
    if not continue_scaling:
        return

    # Establish starting size and half step
    if font_size is None:
        font_size = get_font_size(layer)
    half_step = step / 2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    while continue_scaling:
        font_size -= step
        set_text_size_and_leading(layer, font_size, font_size)
        continue_scaling = bool(width < get_layer_width(layer))

    # Increase by a half step
    font_size += half_step
    set_text_size_and_leading(layer, font_size, font_size)

    # Revert if half step still exceeds reference
    if width < get_layer_width(layer):
        font_size -= half_step
        set_text_size_and_leading(layer, font_size, font_size)
    return font_size


def scale_text_to_height(
    layer: ArtLayer,
    height: int,
    spacing: int = 64,
    step: float = 0.4,
    font_size: Optional[float] = None
) -> Optional[float]:
    """Resize a given text layer's font size/leading until it fits inside a reference width.

    Args:
        layer: Text layer to scale.
        height: Width the text layer must fit (after spacing added).
        spacing: Amount of DPI adjusted spacing to pad the height.
        step: Amount to step font size down by in each check.
        font_size: The starting font size if pre-calculated.

    Returns:
        Font size if font size is calculated during operation, otherwise None.
    """
    # Cancel if we're already within expected bounds
    height = height - APP.scale_by_dpi(spacing)
    continue_scaling = bool(height < get_layer_height(layer))
    if not continue_scaling:
        return

    # Establish starting size and half step
    if font_size is None:
        font_size = get_font_size(layer)
    half_step = step / 2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    while continue_scaling:
        font_size -= step
        set_text_size_and_leading(layer, font_size, font_size)
        continue_scaling = bool(height < get_layer_height(layer))

    # Increase by a half step
    font_size += half_step
    set_text_size_and_leading(layer, font_size, font_size)

    # Revert if half step still exceeds reference
    if height < get_layer_height(layer):
        font_size -= half_step
        set_text_size_and_leading(layer, font_size, font_size)
    return font_size


def scale_text_to_width_textbox(
    layer: ArtLayer,
    font_size: Optional[float] = None,
    step: float = 0.1
) -> None:
    """Check if the text in a TextLayer exceeds its bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.
        font_size: Starting font size, calculated if not provided (slower execution time).
        step: Amount of points to step down each iteration.
    """
    # Get the starting font size
    if font_size is None:
        font_size = get_font_size(layer)
    ref = get_textbox_width(layer) + 1

    # Continue to reduce the size until within the bounding box
    while get_width_no_effects(layer) > ref:
        font_size -= step
        set_text_size_and_leading(layer, font_size, font_size)


def scale_text_layers_to_fit(
    text_layers: list[ArtLayer],
    ref_height: Union[int, float],
    font_size: Optional[float] = None,
    step: float = 0.4
) -> None:
    """Scale multiple text layers until they all can fit within the same given height dimension.

    Args:
        text_layers: List of TextLayers to check.
        ref_height: Height to fit inside.
        font_size: Starting font size of the text layers, calculated if not provided.
        step: Points to step down the text layers to fit.
    """
    # Heights
    half_step = step / 2
    if font_size is None:
        font_size = get_font_size(text_layers[0])
    total_layer_height = sum([get_layer_height(layer) for layer in text_layers])

    # Skip if the size is already fine
    if total_layer_height <= ref_height:
        return

    # Compare height of all 3 elements vs total reference height
    while total_layer_height > ref_height:
        total_layer_height = 0
        font_size -= step
        for i, layer in enumerate(text_layers):
            set_text_size_and_leading(layer, font_size, font_size)
            total_layer_height += get_layer_height(layer)

    # Increase by a half step
    font_size += half_step
    total_layer_height = 0
    for i, layer in enumerate(text_layers):
        set_text_size_and_leading(layer, font_size, font_size)
        total_layer_height += get_layer_height(layer)

    # If out of bounds, revert half step
    if total_layer_height > ref_height:
        font_size -= half_step
        for i, layer in enumerate(text_layers):
            set_text_size_and_leading(layer, font_size, font_size)


def check_for_text_overlap(
    text_layer: ArtLayer,
    adj_reference: ArtLayer,
    top_reference: ArtLayer
) -> Union[int, float]:
    """Check if text layer overlaps another layer.

    Args:
        text_layer: Text layer to check.
        adj_reference: Box marking where the text is overlapping.
        top_reference: Box marking where the text is cleared.

    Returns:
        How much the layer must be moved to compensate.
    """
    docref = APP.activeDocument
    docsel = docref.selection
    layer_copy = text_layer.duplicate()
    layer_copy.rasterize(RasterizeType.TextContents)
    docref.activeLayer = layer_copy
    select_layer_bounds(adj_reference, docsel)
    docsel.invert()
    docsel.clear()
    docsel.deselect()

    # Determine how much the rules text overlaps loyalty box
    dif = top_reference.bounds[3] - layer_copy.bounds[3]
    layer_copy.delete()
    return dif


def vertically_nudge_creature_text(
    layer: ArtLayer,
    adj_reference: ArtLayer,
    top_reference: ArtLayer
) -> int:
    """Vertically nudge a creature's text layer if it overlaps with the power/toughness box,
    determined by the given reference layers.

    Args:
        layer: Layer to vertically nudge.
        adj_reference: Box marking where the text is overlapping.
        top_reference: Box marking where the text is cleared.

    Returns:
        How much the layer must be moved to compensate.
    """
    # Is the layer even close?
    if layer.bounds[2] >= adj_reference.bounds[0]:
        # does the layer overlap?
        delta = check_for_text_overlap(layer, adj_reference, top_reference)
        if delta < 0:
            layer.translate(0, delta)

        # Clear selection, remove copy, return
        return delta
    return 0


def vertically_nudge_pw_text(
    text_layers: list[ArtLayer],
    ref: ReferenceLayer,
    adj_ref: Optional[ArtLayer],
    top_ref: Optional[ArtLayer],
    space: Union[int, float],
    uniform_gap: bool = False,
    font_size: Optional[float] = None,
    step: float = 0.2
) -> None:
    """Shift or resize planeswalker text to prevent overlap with the loyalty shield.

    Args:
        text_layers: Ability text layers to nudge or resize.
        ref: Reference area ability text layers must fit inside.
        adj_ref: Box marking where the text is overlapping.
        top_ref: Box marking where the text is cleared.
        space: Minimum space between planeswalker abilities.
        uniform_gap: Whether the gap between abilities should be the same between each ability.
        font_size: The current font size of the text layers, if known. Otherwise, calculate automatically.
        step: The amount of font size and leading to step down each iteration.
    """
    # Return if adjustments weren't provided
    if not adj_ref or not top_ref:
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
    delta = check_for_text_overlap(layers[-1], adj_ref, top_ref)
    if delta > 0:
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
    font_size = font_size - step
    for lyr in text_layers:
        set_text_size_and_leading(lyr, font_size, font_size)

    # Space apart planeswalker text evenly
    spread_layers_over_reference(
        layers=text_layers,
        ref=ref,
        gap=space if not uniform_gap else None,
        outside_matching=False)

    # Check for another iteration
    vertically_nudge_pw_text(
        text_layers=text_layers,
        ref=ref,
        adj_ref=adj_ref,
        top_ref=top_ref,
        space=space,
        uniform_gap=uniform_gap,
        font_size=font_size)
