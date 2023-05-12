"""
Utility functions to format text
"""
# Standard Library Imports
import math
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    ActionList,
    ActionReference,
    ActionDescriptor,
    SolidColor,
    DialogModes,
    LayerKind,
    RasterizeType
)
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.constants import con
import src.helpers as psd
from src.utils.types_cards import CardTextSymbols, CardTextSymbolIndex
from src.utils.regex import Reg

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


class SymbolMapper:
    """
    Maps symbols to their corresponding colors.
    """
    def load(self):
        """
        Load SolidColor objects using data from the constants object.
        """
        # Symbol colors outer
        self.clr_c = psd.get_color(con.clr_c)
        self.clr_w = psd.get_color(con.clr_w)
        self.clr_u = psd.get_color(con.clr_u)
        self.clr_b = psd.get_color(con.clr_b)
        self.clr_bh = psd.get_color(con.clr_bh)
        self.clr_r = psd.get_color(con.clr_r)
        self.clr_g = psd.get_color(con.clr_g)

        # Symbol colors inner
        self.clri_c = psd.get_color(con.clri_c)
        self.clri_w = psd.get_color(con.clri_w)
        self.clri_u = psd.get_color(con.clri_u)
        self.clri_b = psd.get_color(con.clri_b)
        self.clri_bh = psd.get_color(con.clri_bh)
        self.clri_r = psd.get_color(con.clri_r)
        self.clri_g = psd.get_color(con.clri_g)

        # Primary inner color (black default)
        self.clr_primary = psd.get_color(con.clr_primary)

        # Secondary inner color (white default)
        self.clr_secondary = psd.get_color(con.clr_secondary)

        # Symbol map for regular mana symbols
        self.color_map = {
            "W": self.clr_w,
            "U": self.clr_u,
            "B": self.clr_b,
            "R": self.clr_r,
            "G": self.clr_g,
            "2": self.clr_c
        }
        self.color_map_inner = {
            "W": self.clri_w,
            "U": self.clri_u,
            "B": self.clri_b,
            "R": self.clri_r,
            "G": self.clri_g,
            "2": self.clri_c,
        }

        # For hybrid symbols with generic mana, use the black symbol color rather than colorless for B
        self.hybrid_color_map = self.color_map.copy()
        self.hybrid_color_map['B'] = self.clr_bh
        self.hybrid_color_map_inner = self.color_map_inner.copy()
        self.hybrid_color_map_inner['B'] = self.clri_bh


def locate_symbols(input_string: str) -> CardTextSymbols:
    """
    Locate symbols in the input string, replace them with the proper characters from the NDPMTG font,
    and determine the colors those characters need to be.
    @param input_string: String to analyze for symbols.
    @return: Dict containing the modified string, and a list of dictionaries containing the location and color
             of each symbol to format.
    """
    # Is there a symbol in this text?
    if '{' not in input_string:
        return {
            'input_string': input_string,
            'symbol_indices': []
        }

    # Starting values
    symbol_indices: list[CardTextSymbolIndex] = []
    start = input_string.find('{')
    end = input_string.find('}')
    symbol = ""
    try:
        while 0 <= start <= end:
            # Replace the symbol and add its index
            symbol = input_string[start:end+1]
            input_string = input_string.replace(symbol, con.symbols[symbol], 1)
            symbol_indices.append({
                'index': start,
                'colors': determine_symbol_colors(symbol)
            })
            start = input_string.find('{')
            end = input_string.find('}')
    except (KeyError, IndexError):
        raise Exception(f"Encountered a symbol I don't recognize: {symbol}")
    return {
        'input_string': input_string,
        'symbol_indices': symbol_indices
    }


def locate_italics(input_string: str, italics_strings: list) -> list[dict[str: int]]:
    """
    Locate all instances of italic strings in the input string and record their start and end indices.
    @param input_string: String to search for italics strings.
    @param italics_strings: List of italics strings to look for.
    @return: List of italic string indices (start and end).
    """
    italics_indices = []
    for italics in italics_strings:
        # Replace symbols with their font characters
        if '{' in italics:
            start = italics.find('{')
            end = italics.find('}')
            while 0 <= start < end:
                symbol = italics[start:end + 1]
                italics = italics.replace(symbol, con.symbols[symbol])
                start = italics.find('{')
                end = italics.find('}')

        # Locate Italicized text
        end_index = 0
        while True:
            start_index = input_string.find(italics, end_index)
            if start_index < 0:
                break
            end_index = start_index + len(italics)
            italics_indices.append({
                'start_index': start_index,
                'end_index': end_index,
            })
    return italics_indices


def determine_symbol_colors(symbol: str) -> list[SolidColor]:
    """
    Determines the colors of a symbol (represented as Scryfall string) and returns an array of SolidColor objects.
    @param symbol: Symbol to determine the colors of.
    @return: List of SolidColor objects to color the symbol's characters.
    """
    # Special Symbols
    if symbol in ("{E}", "{CHAOS}"):
        # Energy or chaos symbols
        return [symbol_map.clr_primary]
    elif symbol == "{S}":
        # Snow symbol
        return [symbol_map.clr_c, symbol_map.clr_primary, symbol_map.clr_secondary]
    elif symbol == "{Q}":
        # Untap symbol
        return [symbol_map.clr_primary, symbol_map.clr_secondary]

    # Normal mana symbol
    normal_symbol_match = Reg.MANA_NORMAL.match(symbol)
    if normal_symbol_match:
        return [
            symbol_map.color_map[normal_symbol_match[1]],
            symbol_map.color_map_inner[normal_symbol_match[1]]
        ]

    # Hybrid
    hybrid_match = Reg.MANA_HYBRID.match(symbol)
    if hybrid_match:
        # Use the darker color for black's symbols for 2/B hybrid symbols
        color_map = symbol_map.hybrid_color_map if hybrid_match[1] == "2" else symbol_map.color_map
        return [
            color_map[hybrid_match[2]],
            color_map[hybrid_match[1]],
            symbol_map.color_map_inner[hybrid_match[1]],
            symbol_map.color_map_inner[hybrid_match[2]]
        ]

    # Phyrexian
    phyrexian_match = Reg.MANA_PHYREXIAN.match(symbol)
    if phyrexian_match:
        return [
            symbol_map.hybrid_color_map[phyrexian_match[1]],
            symbol_map.hybrid_color_map_inner[phyrexian_match[1]]
        ]

    # Phyrexian hybrid
    phyrexian_hybrid_match = Reg.MANA_PHYREXIAN_HYBRID.match(symbol)
    if phyrexian_hybrid_match:
        return [
            symbol_map.color_map[phyrexian_hybrid_match[2]],
            symbol_map.color_map[phyrexian_hybrid_match[1]],
            symbol_map.color_map_inner[phyrexian_hybrid_match[1]],
            symbol_map.color_map_inner[phyrexian_hybrid_match[2]]
        ]

    # Weird situation?
    if len(con.symbols[symbol]) == 2:
        return [symbol_map.clr_c, symbol_map.clr_primary]

    # Nothing matching found!
    raise Exception(f"Encountered a symbol that I don't know how to color: {symbol}")


def format_symbol(
    action_list: ActionList,
    starting_ref: ActionDescriptor,
    symbol_index: int,
    symbol_colors: list[SolidColor],
    font_size: Union[int, float]
) -> ActionDescriptor:
    """
    Formats an n-character symbol at the specified index (symbol length determined from symbol_colors).
    @param action_list: Action list to append these actions to.
    @param starting_ref: Action reference to use at the beginning of appending actions to the action list.
    @param symbol_index: Index where the symbol begins in the text layer.
    @param symbol_colors: List of SolidColors to color this symbol's characters.
    @param font_size: Font size to apply to this symbol's characters.
    @return: Action descriptor with all actions applied.
    """
    current_ref = starting_ref
    for i, color in enumerate(symbol_colors):
        desc1 = ActionDescriptor()
        desc2 = ActionDescriptor()
        idTxtS = cID("TxtS")
        action_list.putObject(cID("Txtt"), current_ref)
        desc1.putInteger(cID("From"), symbol_index + i)
        desc1.putInteger(cID("T   "), symbol_index + i + 1)
        desc2.putString(sID("fontPostScriptName"), con.font_mana)
        desc2.putString(cID("FntN"), con.font_mana)
        desc2.putUnitDouble(cID("Sz  "), cID("#Pnt"), font_size)
        desc2.putBoolean(sID("autoLeading"), False)
        desc2.putUnitDouble(cID("Ldng"), cID("#Pnt"), font_size)
        psd.apply_color(desc2, color)
        desc1.putObject(idTxtS, idTxtS, desc2)
        current_ref = desc1
    return current_ref


def format_flavor_text(input_string: str) -> None:
    """
    Inserts the given string into the active layer and formats it without any of the more advanced features like
    italics strings, centering, etc.
    @param input_string: The string to insert into the active layer
    """
    # Is the active layer a text layer?
    if app.activeDocument.activeLayer.kind is not LayerKind.TextLayer:
        return

    # Prepare action descriptor and reference variables
    layer_font_size = app.activeDocument.activeLayer.textItem.size
    primary_action_descriptor = ActionDescriptor()
    primary_action_list = ActionList()
    desc119 = ActionDescriptor()
    desc26 = ActionDescriptor()
    desc25 = ActionDescriptor()
    ref101 = ActionReference()
    idTxtS = sID("textStyle")
    idTxLr = cID("TxLr")
    idTo = sID("to")
    idPnt = cID("#Pnt")
    idTxtt = cID("Txtt")

    # Spin up the text insertion action
    ref101.putEnumerated(idTxLr, cID("Ordn"), cID("Trgt"))
    desc119.putReference(cID("null"), ref101)
    primary_action_descriptor.putString(cID("Txt "), input_string)
    desc25.putInteger(cID("From"), 0)
    desc25.putInteger(idTo, len(input_string))
    desc26.putString(sID("fontPostScriptName"), con.font_rules_text)
    desc26.putString(sID("fontName"), con.font_rules_text)
    desc26.putUnitDouble(sID("size"), idPnt, layer_font_size)
    desc26.putBoolean(sID("autoLeading"), False)
    desc26.putUnitDouble(sID("leading"), idPnt, layer_font_size)
    desc25.putObject(idTxtS, idTxtS, desc26)
    primary_action_list.putObject(idTxtt, desc25)
    primary_action_descriptor.putList(idTxtt, primary_action_list)

    # Push changes to the layer, disable hyphenation
    desc119.putObject(idTo, idTxLr, primary_action_descriptor)
    app.executeAction(sID("set"), desc119, NO_DIALOG)
    app.activeDocument.activeLayer.textItem.hyphenation = False


def generate_italics(card_text: str) -> list[str]:
    """
    Generates italics text array from card text to italicise all text within (parentheses) and all ability words.
    @param card_text: Text to search for strings that need to be italicised.
    @return: List of italics strings.
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
        # Cover boast cards and cards like Mirrodin Besieged
        if (f"• {match}" in card_text and card_text[0:12] != "Choose one —") or "Boast" in match:
            continue
        italic_text.append(match)
    return italic_text


def strip_reminder_text(text: str) -> str:
    """
    Strip out any reminder text from a given oracle text. Reminder text appears in parentheses.
    @param text: Text that may contain reminder text.
    @return: Oracle text with no reminder text.
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


def align_formatted_text(
    action_list: ActionList,
    start: int,
    end: int,
    alignment: str = "right"
):
    """
    Align the quote credit of --Name to the right like on some classic cards.
    @param action_list: Action list to add this action to
    @param start: Starting index of the quote string
    @param end: Ending index of the quote string
    @param alignment: left, right, or center
    @return: Returns the existing ActionDescriptor with changes applied
    """
    desc1 = ActionDescriptor()
    desc1.putInteger(cID("From"), start)
    desc1.putInteger(cID("T   "), end)
    desc2 = ActionDescriptor()
    idstyleSheetHasParent = sID("styleSheetHasParent")
    desc2.putBoolean(idstyleSheetHasParent, True)
    desc2.putEnumerated(cID("Algn"), cID("Alg "), sID(alignment))
    idparagraphStyle = sID("paragraphStyle")
    desc1.putObject(idparagraphStyle, idparagraphStyle, desc2)
    idparagraphStyleRange = sID("paragraphStyleRange")
    action_list.putObject(idparagraphStyleRange, desc1)
    return action_list


def align_formatted_text_right(action_list: ActionList, start: int, end: int) -> None:
    """
    Quality of life shorthand to call align_formatted_text with correct alignment.
    @param action_list: Action list to apply the following action to.
    @param start: Starting index of the string to apply this action to.
    @param end: Ending index of the string to apply this action to.
    """
    align_formatted_text(action_list, start, end, "right")


def align_formatted_text_left(action_list: ActionList, start: int, end: int) -> None:
    """
    Quality of life shorthand to call align_formatted_text with correct alignment.
    @param action_list: Action list to apply the following action to.
    @param start: Starting index of the string to apply this action to.
    @param end: Ending index of the string to apply this action to.
    """
    align_formatted_text(action_list, start, end, "left")


def align_formatted_text_center(action_list: ActionList, start: int, end: int) -> None:
    """
    Quality of life shorthand to call align_formatted_text with correct alignment.
    @param action_list: Action list to apply the following action to.
    @param start: Starting index of the string to apply this action to.
    @param end: Ending index of the string to apply this action to.
    """
    align_formatted_text(action_list, start, end, "center")


def ensure_visible_reference(reference: ArtLayer) -> bool:
    """
    Ensures that a layer used for reference has bounds if it is a text layer.
    @param reference: Reference layer that might be a TextLayer.
    @return: True if it was empty previously, False if it was always visible.
    """
    if reference.kind is LayerKind.TextLayer:
        if reference.textItem.contents in ("", " "):
            reference.textItem.contents = "."
            return True
    return False


def scale_text_right_overlap(layer: ArtLayer, reference: ArtLayer) -> None:
    """
    Scales a text layer down (in 0.2 pt increments) until its right bound
    has a 36 px clearance from a reference layer's left bound.
    @param layer: The text item layer to scale.
    @param reference: Reference layer we need to avoid.
    """
    # Ensure a valid and visible reference layer
    if not reference or reference.bounds == [0, 0, 0, 0]:
        return
    ref_empty = ensure_visible_reference(reference)

    # Obtain the correct font scale factor
    factor = 1
    if app.activeDocument.width != 3264:
        factor = psd.get_text_scale_factor(layer)
    # On the largest document size, ensure 30 pixel gap
    spacing = int((app.activeDocument.width / 3264) * 30)

    # Can't find UnitValue object in python api
    font_size = old_size = float(layer.textItem.size) * factor
    ref_left_bound = reference.bounds[0]
    layer_right_bound = layer.bounds[2]
    step, half_step = 0.4, 0.2

    # Guard against reference being left of the layer
    if ref_left_bound < layer.bounds[0]:
        if ref_empty:
            # Reset reference
            reference.textItem.contents = ''
        return

    # Make our first check if scaling is necessary
    continue_scaling = bool(layer_right_bound > (ref_left_bound - spacing))
    if continue_scaling:

        # Step down the font till it clears the reference
        while continue_scaling:
            font_size -= step
            layer.textItem.size = font_size
            continue_scaling = bool(layer.bounds[2] > (ref_left_bound - spacing))

        # Go up a half step and check if still in bounds
        font_size += half_step
        layer.textItem.size = font_size
        if layer.bounds[2] > (ref_left_bound - spacing):
            font_size -= half_step
            layer.textItem.size = font_size

        # Shift baseline up to keep text centered vertically
        layer.textItem.baselineShift = (old_size * 0.3) - (float(layer.textItem.size) * factor * 0.3)

    # Fix corrected reference layer
    if ref_empty:
        # Reset reference
        reference.textItem.contents = ''


def scale_text_left_overlap(layer: ArtLayer, reference: ArtLayer) -> None:
    """
    Scales a text layer down (in 0.2 pt increments) until its right bound
    has a 36 px clearance from a reference layer's left bound.
    @param layer: The text item layer to scale.
    @param reference: Reference layer we need to avoid.
    """
    # Ensure a valid and visible reference layer
    if not reference or reference.bounds == [0, 0, 0, 0]:
        return
    ref_empty = ensure_visible_reference(reference)

    # Obtain the correct scale factor and spacing
    factor = 1
    if app.activeDocument.width != 3264:
        factor = psd.get_text_scale_factor(layer)
    spacing = int((app.activeDocument.width / 3264) * 36)

    # Set starting variables
    font_size = old_size = layer.textItem.size * factor
    ref_left_bound = reference.bounds[0]
    ref_right_bound = reference.bounds[2]
    layer_left_bound = layer.bounds[0]
    step, half_step = 0.4, 0.2

    # Guard against reference being right of the layer
    if layer.bounds[0] < ref_left_bound:
        if ref_empty:
            # Reset reference
            reference.textItem.contents = ''
        return

    # Make our first check if scaling is necessary
    continue_scaling = bool(ref_right_bound > (layer_left_bound - spacing))
    if continue_scaling:

        # Step down the font till it clears the reference
        while continue_scaling:  # minimum 24 px gap
            font_size -= step
            layer.textItem.size = font_size
            continue_scaling = bool(ref_right_bound > (layer.bounds[0] - spacing))

        # Go up a half step and check if still in bounds
        font_size += half_step
        layer.textItem.size = font_size
        if ref_right_bound > (layer.bounds[0] - spacing):
            font_size -= half_step
            layer.textItem.size = font_size

        # Shift baseline up to keep text centered vertically
        layer.textItem.baselineShift = (old_size * 0.3) - (float(layer.textItem.size) * factor * 0.3)

    # Fix corrected reference layer
    if ref_empty:
        reference.textItem.contents = ''


def scale_text_to_fit_textbox(layer: ArtLayer) -> None:
    """
    Check if the text in a TextLayer exceeds its bounding box.
    @param layer: ArtLayer with "kind" of TextLayer.
    """
    if layer.kind != LayerKind.TextLayer:
        return

    # Get the starting font size
    font_size = layer.textItem.size * psd.get_text_scale_factor(layer)
    step = 0.1

    # Continue to reduce the size until within the bounding box
    while psd.get_dimensions_no_effects(layer)['width'] > (psd.get_textbox_dimensions(layer)['width'] + 1):
        font_size -= step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size


def scale_text_to_fit_reference(
    layer: ArtLayer,
    ref: Union[ArtLayer, int, float],
    spacing: Optional[int] = None,
    height: bool = True,
    step: float = 0.4
) -> None:
    """
    Resize a given text layer's contents (in 0.2 pt increments) until it fits inside a specified reference layer.
    The resulting text layer will have equal font and lead sizes.
    @param layer: Text layer to scale.
    @param ref: Reference layer the text should fit inside.
    @param spacing: [Optional] Amount of mandatory spacing at the bottom of text layer.
    @param height: Fit according to height if true, otherwise fit according to width.
    @param step: Amount to step font size down by in each check.
    """
    # Establish the dimension to use
    dim = 'height' if height else 'width'

    # Establish base variables, ensure a level of spacing at the margins
    if not ref:
        return
    if isinstance(ref, int) or isinstance(ref, float):
        # Only checking against fixed number
        ref_dim = ref
    elif isinstance(ref, ArtLayer):
        # Use a reference layer
        if not spacing:  # If no spacing provided, use default
            spacing = int((app.activeDocument.width / 3264) * 64)
        ref_dim = psd.get_layer_dimensions(ref)[dim] - spacing
    else:
        return
    factor = psd.get_text_scale_factor(layer) or 1
    font_size = layer.textItem.size * factor
    half_step = step / 2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    if ref_dim > psd.get_text_layer_dimensions(layer)[dim]:
        return
    while ref_dim < psd.get_text_layer_dimensions(layer)[dim]:
        font_size -= step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size

    # Take a half step back up, check if still in bounds and adjust back if needed
    font_size += half_step
    layer.textItem.size = font_size
    layer.textItem.leading = font_size
    if ref_dim < psd.get_text_layer_dimensions(layer)[dim]:
        font_size -= half_step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size


def scale_text_layers_to_fit(text_layers: list[ArtLayer], ref_height: Union[int, float]) -> None:
    """
    Scale multiple text layers until they all can fit within the same given height dimension.
    @param text_layers: List of TextLayers to check.
    @param ref_height: Height to fit inside.
    """
    # Heights
    font_size = text_layers[0].textItem.size * psd.get_text_scale_factor(text_layers[0])
    step = 0.40
    half_step = 0.20
    total_layer_height = sum([psd.get_text_layer_dimensions(layer)["height"] for layer in text_layers])

    # Skip if the size is already fine
    if total_layer_height <= ref_height:
        return

    # Compare height of all 3 elements vs total reference height
    while total_layer_height > ref_height:
        total_layer_height = 0
        font_size -= step
        for i, layer in enumerate(text_layers):
            layer.textItem.size = font_size
            layer.textItem.leading = font_size
            total_layer_height += psd.get_text_layer_dimensions(layer)["height"]

    # Check half_step
    font_size += half_step
    total_layer_height = 0
    for i, layer in enumerate(text_layers):
        layer.textItem.size = font_size
        layer.textItem.leading = font_size
        total_layer_height += psd.get_text_layer_dimensions(layer)["height"]

    # Compare height of all 3 elements vs total reference height
    if total_layer_height > ref_height:
        font_size -= half_step
        for i, layer in enumerate(text_layers):
            layer.textItem.size = font_size
            layer.textItem.leading = font_size


def vertically_align_text(layer: ArtLayer, reference_layer: ArtLayer) -> None:
    """
    Centers a given text layer vertically with respect to the bounding box of a reference layer.
    @param layer: TextLayer to vertically center.
    @param reference_layer: Reference layer to center within.
    """
    ref_height = psd.get_layer_dimensions(reference_layer)['height']
    lay_height = psd.get_text_layer_dimensions(layer)['height']
    bound_delta = reference_layer.bounds[1] - layer.bounds[1]
    height_delta = ref_height - lay_height
    layer.translate(0, bound_delta + height_delta / 2)


def check_for_text_overlap(
    text_layer: ArtLayer,
    adj_reference: ArtLayer,
    top_reference: ArtLayer
) -> Union[int, float]:
    """
    Check if text layer overlaps another layer.
    @param text_layer: Text layer to check.
    @param adj_reference: Box marking where the text is overlapping.
    @param top_reference: Box marking where the text is cleared.
    @return: How much the layer must be moved to compensate.
    """
    layer_copy = text_layer.duplicate()
    layer_copy.rasterize(RasterizeType.TextContents)
    app.activeDocument.activeLayer = layer_copy
    psd.select_layer_pixels(adj_reference)
    app.activeDocument.selection.invert()
    app.activeDocument.selection.clear()
    app.activeDocument.selection.deselect()

    # Determine how much the rules text overlaps loyalty box
    dif = top_reference.bounds[3] - layer_copy.bounds[3]
    layer_copy.delete()
    psd.clear_selection()
    return dif


def vertically_nudge_creature_text(
    layer: ArtLayer,
    reference_layer: ArtLayer,
    top_reference_layer: ArtLayer
) -> Optional[int]:
    """
    Vertically nudge a creature's text layer if it overlaps with the power/toughness box,
    determined by the given reference layers.
    """
    # Is the layer even close?
    if layer.bounds[2] >= reference_layer.bounds[0]:
        # does the layer overlap?
        delta = check_for_text_overlap(layer, reference_layer, top_reference_layer)
        if delta < 0:
            layer.translate(0, delta)

        # Clear selection, remove copy, return
        return delta


def vertically_nudge_pw_text(
    text_layers: list[ArtLayer],
    ref: ArtLayer,
    adj_reference: Optional[ArtLayer],
    top_reference: Optional[ArtLayer],
    space: Union[int, float],
    uniform_gap: bool = False
) -> None:
    """
    Shift or resize planeswalker text to prevent overlap with the loyalty shield.
    """
    # Return if adjustments weren't provided
    if not adj_reference or not top_reference:
        return

    # Layer references
    layers = text_layers.copy()
    bottom = layers[-1]
    movable = len(layers)-1

    # Additional references
    ref_height = psd.get_layer_dimensions(ref)['height']
    font_size = text_layers[0].textItem.size * psd.get_text_scale_factor(text_layers[0])

    # Calculate inside gap
    total_space = ref_height - sum(
        [psd.get_text_layer_dimensions(layer)['height'] for layer in text_layers]
    )
    if not uniform_gap:
        inside_gap = ((total_space - space) - (ref.bounds[3] - layers[-1].bounds[1])) / movable
    else:
        inside_gap = total_space / (len(layers) + 1)
    leftover = (inside_gap - space) * movable

    # Does the layer overlap with the loyalty box?
    delta = check_for_text_overlap(bottom, adj_reference, top_reference)
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
    for lyr in text_layers:
        lyr.textItem.size = font_size - 0.2
        lyr.textItem.leading = font_size - 0.2

    # Space apart planeswalker text evenly
    psd.spread_layers_over_reference(text_layers, ref, space if not uniform_gap else None, outside_matching=False)

    # Check for another iteration
    vertically_nudge_pw_text(text_layers, ref, adj_reference, top_reference, space, uniform_gap)


"""
PARAGRAPH FORMATTING
"""


def space_after_paragraph(space: Union[int, float]) -> None:
    """
    Set the space after paragraph value.
    @param space: Space after paragraph
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    deesc2 = ActionDescriptor()
    ref1.PutProperty(sID("property"), sID("paragraphStyle"))
    ref1.PutEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc1.PutReference(sID("target"),  ref1)
    deesc2.PutInteger(sID("textOverrideFeatureName"),  808464438)
    deesc2.PutUnitDouble(sID("spaceAfter"), sID("pointsUnit"),  space)
    desc1.PutObject(sID("to"), sID("paragraphStyle"),  deesc2)
    app.ExecuteAction(sID("set"), desc1, NO_DIALOG)


symbol_map = SymbolMapper()
