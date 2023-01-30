"""
Utility functions to format text
"""
import math
import re
from typing import Optional, Union

import photoshop.api as ps
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import proxyshop.helpers as psd
from proxyshop.constants import con
from proxyshop.__console__ import console

# QOL Definitions
app = ps.Application()
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = ps.DialogModes.DisplayNoDialogs

# Precompiled regex
reg_symbol = re.compile(r"(\{.*?})")
reg_mana_normal = re.compile(r"{([WUBRG])}")
reg_mana_hybrid = re.compile(r"{([2WUBRG])/([WUBRG])}")
reg_mana_phyrexian = re.compile(r"{([WUBRG])/P}")
reg_mana_phyrexian_hybrid = re.compile(r"{([WUBRG])/([WUBRG])/P}")
reg_ability_words = re.compile(r"(?:\A|\r+|• +)([A-Za-z0-9 ]+) — ")
reg_reminder_text = re.compile(r"\([^()]*\)")


class SymbolMapper:
    def __init__(self):
        self.load_values()

    def load_values(self):
        """
        Load SolidColor objects using data from the constants object.
        """
        # Symbol colors outer
        self.clr_c = psd.solidcolor(con.clr_c)
        self.clr_w = psd.solidcolor(con.clr_w)
        self.clr_u = psd.solidcolor(con.clr_u)
        self.clr_b = psd.solidcolor(con.clr_b)
        self.clr_bh = psd.solidcolor(con.clr_bh)
        self.clr_r = psd.solidcolor(con.clr_r)
        self.clr_g = psd.solidcolor(con.clr_g)

        # Symbol colors inner
        self.clri_c = psd.solidcolor(con.clri_c)
        self.clri_w = psd.solidcolor(con.clri_w)
        self.clri_u = psd.solidcolor(con.clri_u)
        self.clri_b = psd.solidcolor(con.clri_b)
        self.clri_bh = psd.solidcolor(con.clri_bh)
        self.clri_r = psd.solidcolor(con.clri_r)
        self.clri_g = psd.solidcolor(con.clri_g)

        # Primary inner color (black default)
        self.clr_primary = psd.solidcolor(con.clr_primary)

        # Secondary inner color (white default)
        self.clr_secondary = psd.solidcolor(con.clr_secondary)

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

    def reload(self):
        """
        Reload default values.
        """
        self.load_values()


def locate_symbols(input_string: str) -> dict[str: Union[str, dict]]:
    """
    Locate symbols in the input string, replace them with the characters we use to represent them in NDPMTG,
    and determine the colors those characters need to be. Returns an object with the modified input string and
    a list of symbol indices.
    """
    # Ensure symbol mappings are up-to-date
    sym.reload()
    symbol = ""
    symbol_indices = []
    try:
        while True:
            match = reg_symbol.search(input_string)
            if match:
                symbol = match[1]
                symbol_index = match.span()[0]
                symbol_char = con.symbols[symbol]
                input_string = input_string.replace(symbol, symbol_char, 1)
                symbol_indices.extend([{
                    'index': symbol_index,
                    'colors': determine_symbol_colors(symbol, len(symbol_char))
                }])
            else: break
    except Exception as e:
        console.update(
            f"Encountered a symbol I don't recognize: {symbol}", e
        )
    return {
        'input_string': input_string,
        'symbol_indices': symbol_indices
    }


def locate_italics(input_string: str, italics_strings: list) -> list[dict[str: int]]:
    """
    Locate all instances of italic strings in the input string and record their start and end indices.
    Returns a list of italic string indices (start and end).
    """
    italics_indices = []
    for italics in italics_strings:

        # replace symbols with their character representations in the italic string
        if "}" in italics:
            for key, symbol in con.symbols.items():
                if key in italics:
                    italics = italics.replace(key, symbol)

        # Locate Italicized text
        end_index = 0
        while True:
            start_index = input_string.find(italics, end_index)
            end_index = start_index + len(italics)
            if start_index < 0: break
            italics_indices.append({
                'start_index': start_index,
                'end_index': end_index,
            })

    return italics_indices


def determine_symbol_colors(
    symbol: str,
    symbol_length: int
) -> Optional[list[ps.SolidColor]]:
    """
    Determines the colors of a symbol (represented as Scryfall string) and returns an array of SolidColor objects.
    """
    # Special Symbols
    if symbol in ("{E}", "{CHAOS}"):
        # Energy or chaos symbols
        return [sym.clr_primary]
    elif symbol == "{S}":
        # Snow symbol
        return [sym.clr_c, sym.clr_primary, sym.clr_secondary]
    elif symbol == "{Q}":
        # Untap symbol
        return [sym.clr_primary, sym.clr_secondary]

    # Normal mana symbol
    normal_symbol_match = reg_mana_normal.match(symbol)
    if normal_symbol_match:
        return [
            sym.color_map[normal_symbol_match[1]],
            sym.color_map_inner[normal_symbol_match[1]]
        ]

    # Hybrid
    hybrid_match = reg_mana_hybrid.match(symbol)
    if hybrid_match:
        # Use the darker color for black's symbols for 2/B hybrid symbols
        color_map = sym.hybrid_color_map if hybrid_match[1] == "2" else sym.color_map
        return [
            color_map[hybrid_match[2]],
            color_map[hybrid_match[1]],
            sym.color_map_inner[hybrid_match[1]],
            sym.color_map_inner[hybrid_match[2]]
        ]

    # Phyrexian
    phyrexian_match = reg_mana_phyrexian.match(symbol)
    if phyrexian_match:
        return [
            sym.hybrid_color_map[phyrexian_match[1]],
            sym.hybrid_color_map_inner[phyrexian_match[1]]
        ]

    # Phyrexian hybrid
    phyrexian_hybrid_match = reg_mana_phyrexian_hybrid.match(symbol)
    if phyrexian_hybrid_match:
        return [
            sym.color_map[phyrexian_hybrid_match[2]],
            sym.color_map[phyrexian_hybrid_match[1]],
            sym.color_map_inner[phyrexian_hybrid_match[1]],
            sym.color_map_inner[phyrexian_hybrid_match[2]]
        ]

    # Weird situation?
    if symbol_length == 2:
        return [sym.clr_c, sym.clr_primary]

    # Nothing matching found!
    console.update(f"Encountered a symbol that I don't know how to color: {symbol}")
    return None


def format_symbol(
    primary_action_list: ps.ActionList,
    starting_layer_ref: ps.ActionDescriptor,
    symbol_index: int,
    symbol_colors: list[ps.SolidColor],
    layer_font_size: Union[int, float]
) -> ps.ActionDescriptor:
    """
    Formats an n-character symbol at the specified index (symbol length determined from symbol_colors).
    """
    current_ref = starting_layer_ref
    for i, color in enumerate(symbol_colors):
        desc1 = ps.ActionDescriptor()
        desc2 = ps.ActionDescriptor()
        idTxtS = cID("TxtS")
        primary_action_list.putObject(cID("Txtt"), current_ref)
        desc1.putInteger(cID("From"), symbol_index + i)
        desc1.putInteger(cID("T   "), symbol_index + i + 1)
        desc2.putString(sID("fontPostScriptName"), con.font_mana)
        desc2.putString(cID("FntN"), con.font_mana)
        desc2.putUnitDouble(cID("Sz  "), cID("#Pnt"), layer_font_size)
        desc2.putBoolean(sID("autoLeading"), False)
        desc2.putUnitDouble(cID("Ldng"), cID("#Pnt"), layer_font_size)
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
    if app.activeDocument.activeLayer.kind is not ps.LayerKind.TextLayer: return

    # Prepare action descriptor and reference variables
    layer_font_size = app.activeDocument.activeLayer.textItem.size
    primary_action_descriptor = ps.ActionDescriptor()
    primary_action_list = ps.ActionList()
    desc119 = ps.ActionDescriptor()
    desc26 = ps.ActionDescriptor()
    desc25 = ps.ActionDescriptor()
    ref101 = ps.ActionReference()
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

    # Push changes to document, disable hyphenation
    desc119.putObject(idTo, idTxLr, primary_action_descriptor)
    app.executeAction(sID("set"), desc119, NO_DIALOG)
    app.activeDocument.activeLayer.textItem.hyphenation = False


def generate_italics(card_text: str) -> list[str]:
    """
    Generates italics text array from card text to italicise all text within (parentheses) and all ability words.
    """
    italic_text = []

    # Find and add reminder text
    end_index = 0
    while True:
        start_index = card_text.find("(", end_index)
        if start_index >= 0:
            end_index = card_text.find(")", start_index + 1)
            end_index += 1
            italic_text.extend([card_text[start_index:end_index]])
        else:
            break

    # Find and add ability words
    for match in reg_ability_words.findall(card_text):
        # Cover boast cards and cards like Mirrodin Besieged
        if (f"• {match}" in card_text and card_text[0:12] != "Choose one —") or "Boast" in match:
            continue
        italic_text.append(match)

    return italic_text


def strip_reminder_text(oracle_text: str) -> str:
    """
    Strip out any reminder text that a card's oracle text has (reminder text in parentheses).
    If this empties the string, instead return the original string.
    """
    oracle_text_stripped = reg_reminder_text.sub("", oracle_text)

    # ensure we didn't add any double whitespace by doing that
    oracle_text_stripped = re.sub(r"  +", "", oracle_text_stripped)
    if oracle_text_stripped != "":
        return oracle_text_stripped
    return oracle_text


def align_formatted_text(
    action_list: ps.ActionList,
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
    desc1 = ps.ActionDescriptor()
    desc1.putInteger(cID("From"), start)
    desc1.putInteger(cID("T   "), end)
    desc2 = ps.ActionDescriptor()
    idstyleSheetHasParent = sID("styleSheetHasParent")
    desc2.putBoolean(idstyleSheetHasParent, True)
    desc2.putEnumerated(cID("Algn"), cID("Alg "), sID(alignment))
    idparagraphStyle = sID("paragraphStyle")
    desc1.putObject(idparagraphStyle, idparagraphStyle, desc2)
    idparagraphStyleRange = sID("paragraphStyleRange")
    action_list.putObject(idparagraphStyleRange, desc1)
    return action_list


def align_formatted_text_right(action_list: ps.ActionList, start: int, end: int):
    """
    Quality of life shorthand to call align_formatted_text with correct alignment.
    """
    align_formatted_text(action_list, start, end, "right")


def align_formatted_text_left(action_list: ps.ActionList, start: int, end: int):
    """
    Quality of life shorthand to call align_formatted_text with correct alignment.
    """
    align_formatted_text(action_list, start, end, "left")


def align_formatted_text_center(action_list: ps.ActionList, start: int, end: int):
    """
    Quality of life shorthand to call align_formatted_text with correct alignment.
    """
    align_formatted_text(action_list, start, end, "center")


def scale_text_right_overlap(layer: ArtLayer, reference: ArtLayer) -> None:
    """
    Scales a text layer down (in 0.2 pt increments) until its right bound
    has a 36 px clearance from a reference layer's left bound.
    @param layer: The text item layer to scale.
    @param reference: Reference layer we need to avoid.
    """
    # Ensure a proper reference layer
    contents = None
    if not reference: return
    if reference.kind is ps.LayerKind.TextLayer:
        if reference.textItem.contents in ("", " "):
            contents = reference.textItem.contents
            reference.textItem.contents = "."
    elif reference.bounds == [0, 0, 0, 0]: return

    # Can't find UnitValue object in python api
    factor = 1
    if app.activeDocument.width != 3264:
        factor = psd.get_text_scale_factor(layer)
    font_size = layer.textItem.size * factor
    reference_left_bound = reference.bounds[0]
    layer_left_bound = layer.bounds[0]
    layer_right_bound = layer.bounds[2]
    old_size = font_size
    step, half_step = 0.4, 0.2

    # Obtain proper spacing for this document size
    spacing = int((app.activeDocument.width / 3264) * 36)

    # Guard against the reference's left bound being left of the layer's left bound
    if reference_left_bound >= layer_left_bound:
        # Step down the font till it clears the reference
        while layer_right_bound > (reference_left_bound - spacing):  # minimum 24 px gap
            font_size -= step
            layer.textItem.size = font_size
            layer_right_bound = layer.bounds[2]

        # Go up a half step and check if still in bounds
        font_size += half_step
        layer.textItem.size = font_size
        layer_right_bound = layer.bounds[2]
        if layer_right_bound > (reference_left_bound - spacing):
            font_size -= half_step
            layer.textItem.size = font_size

        # Shift baseline up to keep text centered vertically
        if old_size > (layer.textItem.size * factor):
            layer.textItem.baselineShift = (old_size * 0.3) - (layer.textItem.size * factor * 0.3)

    # Fix corrected reference layer
    if contents:
        reference.textItem.contents = contents


def scale_text_left_overlap(layer: ArtLayer, reference: ArtLayer) -> None:
    """
    Scales a text layer down (in 0.2 pt increments) until its right bound
    has a 36 px clearance from a reference layer's left bound.
    @param layer: The text item layer to scale.
    @param reference: Reference layer we need to avoid.
    """
    # Ensure a proper reference layer
    contents = None
    if not reference: return
    if reference.kind is ps.LayerKind.TextLayer:
        if reference.textItem.contents in ("", " "):
            contents = reference.textItem.contents
            reference.textItem.contents = "."
    elif reference.bounds == [0, 0, 0, 0]: return

    # Can't find UnitValue object in python api
    factor = 1
    if app.activeDocument.width != 3264:
        factor = psd.get_text_scale_factor(layer)
    font_size = layer.textItem.size * factor
    reference_left_bound = reference.bounds[0]
    reference_right_bound = reference.bounds[2]
    layer_left_bound = layer.bounds[0]
    old_size = font_size
    step, half_step = 0.4, 0.2

    # Obtain proper spacing for this document size
    spacing = int((app.activeDocument.width / 3264) * 36)

    # Guard against the reference's left bound being left of the layer's left bound
    if layer_left_bound >= reference_left_bound:
        # Step down the font till it clears the reference
        while reference_right_bound > (layer_left_bound - spacing):  # minimum 24 px gap
            font_size -= step
            layer.textItem.size = font_size
            layer_left_bound = layer.bounds[0]

        # Go up a half step and check if still in bounds
        font_size += half_step
        layer.textItem.size = font_size
        layer_left_bound = layer.bounds[0]
        if reference_right_bound > (layer_left_bound - spacing):
            font_size -= half_step
            layer.textItem.size = font_size

        # Shift baseline up to keep text centered vertically
        if old_size > (layer.textItem.size * factor):
            layer.textItem.baselineShift = (old_size * 0.3) - (layer.textItem.size * factor * 0.3)

    # Fix corrected reference layer
    if contents:
        reference.textItem.contents = contents


def scale_text_to_fit_reference(
    layer: ArtLayer,
    ref: Union[ArtLayer, int, float],
    spacing: Optional[int] = None
) -> None:
    """
    Resize a given text layer's contents (in 0.25 pt increments) until it fits inside a specified reference layer.
    The resulting text layer will have equal font and lead sizes.
    @param layer: Text layer to scale.
    @param ref: Reference layer the text should fit inside.
    @param spacing: [Optional] Amount of mandatory spacing at the bottom of text layer.
    """
    # Establish base variables, ensure a level of spacing at the margins
    if not ref: return
    if isinstance(ref, int) or isinstance(ref, float):
        # Only checking against fixed height
        ref_height = ref
    elif isinstance(ref, ArtLayer):
        # Use a reference layer
        if not spacing:  # If no spacing provided, use default
            spacing = int((app.activeDocument.width / 3264) * 64)
        ref_height = psd.get_layer_dimensions(ref)['height'] - spacing
    else:
        return
    factor = psd.get_text_scale_factor(layer) or 1
    font_size = layer.textItem.size * factor
    step, half_step = 0.4, 0.2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    if ref_height > psd.get_text_layer_dimensions(layer)['height']: return
    while ref_height < psd.get_text_layer_dimensions(layer)['height']:
        font_size -= step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size

    # Take a half step back up, check if still in bounds and adjust back if needed
    font_size += half_step
    layer.textItem.size = font_size
    layer.textItem.leading = font_size
    if ref_height < psd.get_text_layer_dimensions(layer)['height']:
        font_size -= half_step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size


def scale_text_layers_to_fit(text_layers: list[ArtLayer], ref_height: Union[int, float]) -> None:
    # Heights
    font_size = text_layers[0].textItem.size * psd.get_text_scale_factor(text_layers[0])
    step = 0.40
    half_step = 0.20
    total_layer_height = sum([psd.get_text_layer_dimensions(layer)["height"] for layer in text_layers])

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


def vertically_align_text(layer: ArtLayer, reference_layer: ArtLayer):
    """
    Centers a given text layer vertically with respect to the bounding box of a reference layer.
    """
    ref_height = psd.get_layer_dimensions(reference_layer)['height']
    lay_height = psd.get_text_layer_dimensions(layer)['height']
    bound_delta = reference_layer.bounds[1] - layer.bounds[1]
    height_delta = ref_height - lay_height
    layer.translate(0, bound_delta + height_delta / 2)


def vertically_nudge_creature_text(
    layer: ArtLayer,
    reference_layer: ArtLayer,
    top_reference_layer: ArtLayer
) -> Optional[int]:
    """
    Vertically nudge a creature's text layer if it overlaps with the power/toughness box,
    determined by the given reference layers.
    """
    # Does the layer needs to be nudged?
    if layer.bounds[2] >= reference_layer.bounds[0]:
        layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
        layer_copy.rasterize(ps.RasterizeType.TextContents)
        app.activeDocument.activeLayer = layer_copy
        psd.select_layer_pixels(reference_layer)
        app.activeDocument.selection.invert()
        app.activeDocument.selection.clear()

        # Determine how much the rules text overlaps the power/toughness by
        delta = top_reference_layer.bounds[3] - layer_copy.bounds[3]
        if delta < 0: layer.translate(0, delta)

        # Clear selection, remove copy, return
        psd.clear_selection()
        layer_copy.remove()
        return delta


def vertically_nudge_pw_text(
    text_layers: list[ArtLayer],
    space: Union[int, float],
    layer_gap: Union[int, float],
    ref: ArtLayer,
    adj_reference: Optional[ArtLayer],
    top_reference: Optional[ArtLayer]
) -> None:
    """
    Shift or resize planeswalker text to prevent overlap with the loyalty shield.
    """
    # Return if adjustments weren't provided
    if not adj_reference or not top_reference:
        return

    # Layer to check for overlap
    lyrs = text_layers.copy()
    bottom = lyrs[-1]
    movable = len(lyrs) + 1
    leftover = (layer_gap - space) * movable
    ref_height = psd.get_layer_dimensions(ref)['height']
    font_size = text_layers[0].textItem.size * psd.get_text_scale_factor(text_layers[0])

    # Does the layer overlap with the loyalty box?
    if bottom.bounds[2] >= adj_reference.bounds[0]:
        layer_copy = bottom.duplicate()
        layer_copy.rasterize(ps.RasterizeType.TextContents)
        app.activeDocument.activeLayer = layer_copy
        psd.select_layer_pixels(adj_reference)
        app.activeDocument.selection.invert()
        app.activeDocument.selection.clear()
        app.activeDocument.selection.deselect()

        # Determine how much the rules text overlaps loyalty box
        dif = top_reference.bounds[3] - layer_copy.bounds[3]
        layer_copy.delete()
        if dif > 0:
            return

        # Calculate the total distance needing to be covered
        total_move = 0
        lyrs.pop(0)
        for n, lyr in enumerate(lyrs):
            total_move += math.fabs(dif) * ((len(lyrs) - n)/len(lyrs))

        if total_move < leftover:
            # Text layers can just be shifted upward
            lyrs.reverse()
            for n, lyr in enumerate(lyrs):
                move_y = dif * ((len(lyrs) - n)/len(lyrs))
                lyr.translate(0, move_y)
            return

        # Layer gap would be too small, need to resize text then shift upward
        total_h = 0
        font_size -= 0.2
        for lyr in text_layers:
            lyr.textItem.size = font_size
            lyr.textItem.leading = font_size
            total_h += psd.get_text_layer_dimensions(lyr)["height"]

        # Get the exact spacing left over
        new_gap = (ref_height - total_h) / movable

        # Space apart planeswalker text evenly
        psd.spread_layers_over_reference(text_layers, ref, new_gap)

        # Check for another iteration
        vertically_nudge_pw_text(text_layers, space, new_gap, ref, adj_reference, top_reference)


"""
PARAGRAPH FORMATTING
"""


def space_after_paragraph(space: Union[int, float]) -> None:
    """
    Set the space after paragraph value.
    @param space: Space after paragraph
    @return:
    """
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    deesc2 = ps.ActionDescriptor()
    ref1.PutProperty(sID("property"), sID("paragraphStyle"))
    ref1.PutEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc1.PutReference(sID("target"),  ref1)
    deesc2.PutInteger(sID("textOverrideFeatureName"),  808464438)
    deesc2.PutUnitDouble(sID("spaceAfter"), sID("pointsUnit"),  space)
    desc1.PutObject(sID("to"), sID("paragraphStyle"),  deesc2)
    app.ExecuteAction(sID("set"), desc1, NO_DIALOG)


sym = SymbolMapper()
