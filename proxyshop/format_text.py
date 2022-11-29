"""
Utility functions to format text
"""
import math
import re
import photoshop.api as ps
import proxyshop.helpers as psd
from proxyshop.constants import con
if not con.headless:
    from proxyshop.gui import console
else:
    from proxyshop.core import console

# QOL Definitions
app = ps.Application()
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = ps.DialogModes.DisplayNoDialogs


class SymbolMapper:
    def __init__(self):
        self.load_values()

    def load_values(self):

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
        self.load_values()


def locate_symbols(input_string):
    """
    Locate symbols in the input string, replace them with the characters we use to represent them in NDPMTG,
    and determine the colors those characters need to be. Returns an object with the modified input string and
    a list of symbol indices.
    """
    symbol = ""
    symbol_re = r"(\{.*?\})"
    symbol_indices = []
    try:
        while True:
            match = re.search(symbol_re, input_string)
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


def locate_italics(input_string, italics_strings):
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


def determine_symbol_colors(symbol, symbol_length):
    """
    Determines the colors of a symbol (represented as Scryfall string) and returns an array of SolidColor objects.
    """
    # Ensure symbol mappings are up-to-date
    sym.reload()

    # SPECIAL SYMBOLS
    if symbol in ("{E}", "{CHAOS}"):
        # Energy or chaos symbols
        return [sym.clr_primary]
    elif symbol == "{S}":
        # Snow symbol
        return [sym.clr_c, sym.clr_primary, sym.clr_secondary]
    elif symbol == "{Q}":
        # Untap symbol
        return [sym.clr_primary, sym.clr_secondary]

    # Phyrexian
    phyrexian_regex = r"\{([W,U,B,R,G])\/P\}"
    phyrexian_match = re.match(phyrexian_regex, symbol)
    if phyrexian_match:
        return [
            sym.hybrid_color_map[phyrexian_match[1]],
            sym.hybrid_color_map_inner[phyrexian_match[1]]
        ]

    # Phyrexian hybrid
    phyrexian_hybrid_regex = r"\{([W,U,B,R,G])\/([W,U,B,R,G])\/P\}"
    phyrexian_hybrid_match = re.match(phyrexian_hybrid_regex, symbol)
    if phyrexian_hybrid_match:
        return [
            sym.color_map[phyrexian_hybrid_match[2]],
            sym.color_map[phyrexian_hybrid_match[1]],
            sym.color_map_inner[phyrexian_hybrid_match[1]],
            sym.color_map_inner[phyrexian_hybrid_match[2]]
        ]

    # Hybrid
    hybrid_regex = r"\{([2,W,U,B,R,G])\/([W,U,B,R,G])\}"
    hybrid_match = re.match(hybrid_regex, symbol)
    if hybrid_match:
        if hybrid_match[1] == "2":
            # Use the darker color for black's symbols for 2/B hybrid symbols
            color_map = sym.hybrid_color_map
        else: color_map = sym.color_map
        return [
            color_map[hybrid_match[2]],
            color_map[hybrid_match[1]],
            sym.color_map_inner[hybrid_match[1]],
            sym.color_map_inner[hybrid_match[2]]
        ]

    # Normal mana symbol
    normal_symbol_regex = r"\{([W,U,B,R,G])\}"
    normal_symbol_match = re.match(normal_symbol_regex, symbol)
    if normal_symbol_match:
        return [
            sym.color_map[normal_symbol_match[1]],
            sym.color_map_inner[normal_symbol_match[1]]
        ]

    # Weird situation?
    if symbol_length == 2: return [sym.clr_c, sym.clr_primary]

    # Nothing matching found!
    console.update(f"Encountered a symbol that I don't know how to color: {symbol}")
    return None


def format_symbol(primary_action_list, starting_layer_ref, symbol_index, symbol_colors, layer_font_size):
    """
     * Formats an n-character symbol at the specified index (symbol length determined from symbol_colors).
    """
    current_ref = starting_layer_ref
    for i, color in enumerate(symbol_colors):
        desc1 = ps.ActionDescriptor()
        desc2 = ps.ActionDescriptor()
        idTxtS = cID("TxtS")
        primary_action_list.putObject(cID("Txtt"), current_ref)
        desc1.putInteger(cID("From"), symbol_index + i)
        desc1.putInteger(cID("T   "), symbol_index + i + 1)
        desc2.putString(
            sID("fontPostScriptName"),
            con.font_mana)  # NDPMTG default
        desc2.putString(
            cID("FntN"),
            con.font_mana)  # NDPMTG default
        desc2.putUnitDouble(
            cID("Sz  "),
            cID("#Pnt"),
            layer_font_size)
        desc2.putBoolean(sID("autoLeading"), False)
        desc2.putUnitDouble(
            cID("Ldng"),
            cID("#Pnt"),
            layer_font_size)

        psd.apply_color(desc2, color)

        desc1.putObject(idTxtS, idTxtS, desc2)
        current_ref = desc1
    return current_ref


def basic_format_text(input_string):
    """
    Inserts the given string into the active layer and formats it without any of the more advanced features like
    italics strings, centering, etc.
    @param input_string: The string to insert into the active layer
    """
    # Is the active layer a text layer?
    if app.activeDocument.activeLayer.kind is not ps.LayerKind.TextLayer: return

    # Locate symbols and update the input string
    ret = locate_symbols(input_string)
    input_string = ret['input_string']
    symbol_indices = ret['symbol_indices']

    # Prepare action descriptor and reference variables
    layer_font_size = app.activeDocument.activeLayer.textItem.size
    layer_text_color = app.activeDocument.activeLayer.textItem.color
    primary_action_descriptor = ps.ActionDescriptor()
    primary_action_list = ps.ActionList()
    desc119 = ps.ActionDescriptor()
    desc26 = ps.ActionDescriptor()
    desc25 = ps.ActionDescriptor()
    ref101 = ps.ActionReference()
    desc141 = ps.ActionDescriptor()
    desc142 = ps.ActionDescriptor()
    desc143 = ps.ActionDescriptor()
    list13 = ps.ActionList()
    list14 = ps.ActionList()
    idkerningRange = sID("kerningRange")
    idparagraphStyleRange = sID("paragraphStyleRange")
    idfontPostScriptName = sID("fontPostScriptName")
    idfirstLineIndent = sID("firstLineIndent")
    idparagraphStyle = sID("paragraphStyle")
    idautoLeading = sID("autoLeading")
    idstartIndent = sID("startIndent")
    idspaceBefore = sID("spaceBefore")
    idleadingType = sID("leadingType")
    idspaceAfter = sID("spaceAfter")
    idendIndent = sID("endIndent")
    idTxtS = sID("textStyle")
    idsetd = cID("setd")
    idTxLr = cID("TxLr")
    idT = cID("T   ")
    idFntN = cID("FntN")
    idSz = cID("Sz  ")
    idPnt = cID("#Pnt")
    idLdng = cID("Ldng")
    idTxtt = cID("Txtt")
    idFrom = cID("From")
    ref101.putEnumerated(
        idTxLr,
        cID("Ordn"),
        cID("Trgt"))

    # Spin up the text insertion action
    desc119.putReference(cID("null"), ref101)
    primary_action_descriptor.putString(cID("Txt "), input_string)
    desc25.putInteger(idFrom, 0)
    desc25.putInteger(idT, len(input_string))
    desc26.putString(idfontPostScriptName, con.font_rules_text)  # MPlantin default
    desc26.putString(idFntN, con.font_rules_text)  # MPlantin default
    desc26.putUnitDouble(idSz, idPnt, layer_font_size)
    psd.apply_color(desc26, layer_text_color)
    desc26.putBoolean(idautoLeading, False)
    desc26.putUnitDouble(idLdng, idPnt, layer_font_size)
    desc25.putObject(idTxtS, idTxtS, desc26)
    current_layer_ref = desc25

    # Format each symbol correctly
    for symbol_index in symbol_indices:
        current_layer_ref = format_symbol(
            primary_action_list = primary_action_list,
            starting_layer_ref = current_layer_ref,
            symbol_index = symbol_index['index'],
            symbol_colors = symbol_index['colors'],
            layer_font_size = layer_font_size,
        )

    primary_action_list.putObject(idTxtt, current_layer_ref)
    primary_action_descriptor.putList(idTxtt, primary_action_list)

    # Paragraph formatting
    desc141.putInteger(idFrom, 0)
    desc141.putInteger(idT, len(input_string))  # input string length
    desc142.putUnitDouble(idfirstLineIndent, idPnt, 0)
    desc142.putUnitDouble(idstartIndent, idPnt, 0)
    desc142.putUnitDouble(idendIndent, idPnt, 0)
    desc142.putUnitDouble(idspaceBefore, idPnt, con.line_break_lead)
    desc142.putUnitDouble(idspaceAfter, idPnt, 0)
    desc142.putInteger(sID("dropCapMultiplier"), 1)
    desc142.putEnumerated(idleadingType, idleadingType, sID("leadingBelow"))
    desc143.putString(idfontPostScriptName, con.font_mana)  # NDPMTG default
    desc143.putString(idFntN, con.font_rules_text)  # MPlantin default
    desc143.putBoolean(idautoLeading, False)
    primary_action_descriptor.putList(idparagraphStyleRange, list13)
    primary_action_descriptor.putList(idkerningRange, list14)
    list13 = ps.ActionList()

    # Push changes to document
    desc119.putObject(idT, idTxLr, primary_action_descriptor)
    app.executeAction(idsetd, desc119, NO_DIALOG)

    # Reset layer's justification if needed and disable hyphenation
    app.activeDocument.activeLayer.textItem.hyphenation = False


def format_text(input_string, italics_strings, flavor_index, is_centered):
    """
    Inserts the given string into the active layer and formats it according to defined parameters with symbols
    from the NDPMTG font.
    @param input_string: The string to insert into the active layer
    @param italics_strings: An array containing strings that should be italicized within the input_string.
    @param flavor_index: The index at which linebreak spacing should be increased and any subsequent
    chars should be italicized (where the card's flavor text begins)
    @param is_centered: Should the input text should be center-justified
    """
    # Is the active layer a text layer?
    if app.activeDocument.activeLayer.kind is not ps.LayerKind.TextLayer: return

    # Record the layer's justification before modifying the layer in case it's reset along the way
    layer_justification = app.activeDocument.activeLayer.textItem.justification

    # Check if the flavor text contains a quote
    if flavor_index >= 0: quote_index = input_string.find("\r", flavor_index + 3)
    else: quote_index = -1

    # Locate symbols and update the input string
    ret = locate_symbols(input_string)
    input_string = ret['input_string']
    symbol_indices = ret['symbol_indices']

    # Locate italics text indices
    italics_indices = locate_italics(input_string, italics_strings)

    # Prepare action descriptor and reference variables
    layer_font_size = app.activeDocument.activeLayer.textItem.size
    layer_text_color = app.activeDocument.activeLayer.textItem.color
    primary_action_descriptor = ps.ActionDescriptor()
    primary_action_list = ps.ActionList()
    desc119 = ps.ActionDescriptor()
    desc26 = ps.ActionDescriptor()
    desc25 = ps.ActionDescriptor()
    ref101 = ps.ActionReference()
    desc141 = ps.ActionDescriptor()
    desc142 = ps.ActionDescriptor()
    desc143 = ps.ActionDescriptor()
    list13 = ps.ActionList()
    list14 = ps.ActionList()
    idkerningRange = sID("kerningRange")
    idparagraphStyleRange = sID("paragraphStyleRange")
    idfontPostScriptName = sID("fontPostScriptName")
    idfirstLineIndent = sID("firstLineIndent")
    idparagraphStyle = sID("paragraphStyle")
    idautoLeading = sID("autoLeading")
    idstartIndent = sID("startIndent")
    idspaceBefore = sID("spaceBefore")
    idleadingType = sID("leadingType")
    idspaceAfter = sID("spaceAfter")
    idendIndent = sID("endIndent")
    idTxtS = sID("textStyle")
    idsetd = cID("setd")
    idTxLr = cID("TxLr")
    idT = cID("T   ")
    idFntN = cID("FntN")
    idSz = cID("Sz  ")
    idPnt = cID("#Pnt")
    idLdng = cID("Ldng")
    idTxtt = cID("Txtt")
    idFrom = cID("From")
    ref101.putEnumerated(
        idTxLr,
        cID("Ordn"),
        cID("Trgt"))

    # Spin up the text insertion action
    desc119.putReference(cID("null"), ref101)
    primary_action_descriptor.putString(cID("Txt "), input_string)
    desc25.putInteger(idFrom, 0)
    desc25.putInteger(idT, len(input_string))
    desc26.putString(idfontPostScriptName, con.font_rules_text)  # MPlantin default
    desc26.putString(idFntN, con.font_rules_text)  # MPlantin default
    desc26.putUnitDouble(idSz, idPnt, layer_font_size)
    psd.apply_color(desc26, layer_text_color)
    desc26.putBoolean(idautoLeading, False)
    desc26.putUnitDouble(idLdng, idPnt, layer_font_size)
    desc25.putObject(idTxtS, idTxtS, desc26)
    current_layer_ref = desc25

    # Bold the contents if necessary
    if con.bold_rules_text and flavor_index != 0:
        bold_action1 = ps.ActionDescriptor()
        bold_action2 = ps.ActionDescriptor()
        contents_index = len(input_string) - 1 if flavor_index < 0 else flavor_index - 1
        primary_action_list.putObject(idTxtt, current_layer_ref)
        bold_action1.putInteger(idFrom, 0)  # italics start index
        bold_action1.putInteger(idT, contents_index)  # italics end index
        bold_action2.putString(idfontPostScriptName, con.font_rules_text_bold)  # MPlantin italic default
        bold_action2.putString(idFntN, con.font_rules_text_bold)  # MPlantin italic default
        bold_action2.putUnitDouble(idSz, idPnt, layer_font_size)
        bold_action2.putBoolean(idautoLeading, False)
        bold_action2.putUnitDouble(idLdng, idPnt, layer_font_size)
        bold_action1.putObject(idTxtS, idTxtS, bold_action2)
        current_layer_ref = bold_action1

    # Italicize text from our italics indices
    for italics_index in italics_indices:
        italics_action1 = ps.ActionDescriptor()
        italics_action2 = ps.ActionDescriptor()
        primary_action_list.putObject(idTxtt, current_layer_ref)
        italics_action1.putInteger(idFrom, italics_index['start_index'])  # italics start index
        italics_action1.putInteger(idT, italics_index['end_index'])  # italics end index
        italics_action2.putString(idfontPostScriptName, con.font_rules_text_italic)  # MPlantin italic default
        italics_action2.putString(idFntN, con.font_rules_text_italic)  # MPlantin italic default
        italics_action2.putUnitDouble(idSz, idPnt, layer_font_size)
        italics_action2.putBoolean(idautoLeading, False)
        italics_action2.putUnitDouble(idLdng, idPnt, layer_font_size)
        # Default text box

        psd.apply_color(italics_action2, layer_text_color)

        # End
        italics_action1.putObject(idTxtS, idTxtS, italics_action2)
        current_layer_ref = italics_action1

    # Format each symbol correctly
    for symbol_index in symbol_indices:
        current_layer_ref = format_symbol(
            primary_action_list = primary_action_list,
            starting_layer_ref = current_layer_ref,
            symbol_index = symbol_index['index'],
            symbol_colors = symbol_index['colors'],
            layer_font_size = layer_font_size,
        )

    primary_action_list.putObject(idTxtt, current_layer_ref)
    primary_action_descriptor.putList(idTxtt, primary_action_list)

    # Paragraph formatting
    desc141.putInteger(idFrom, 0)
    desc141.putInteger(idT, len(input_string))  # input string length
    desc142.putUnitDouble(idfirstLineIndent, idPnt, 0)
    desc142.putUnitDouble(idstartIndent, idPnt, 0)
    desc142.putUnitDouble(idendIndent, idPnt, 0)
    if is_centered:  # line break lead
        desc142.putUnitDouble(idspaceBefore, idPnt, 0)
    else:
        desc142.putUnitDouble(idspaceBefore, idPnt, con.line_break_lead)
    desc142.putUnitDouble(idspaceAfter, idPnt, 0)
    desc142.putInteger(sID("dropCapMultiplier"), 1)
    desc142.putEnumerated(idleadingType, idleadingType, sID("leadingBelow"))
    desc143.putString(idfontPostScriptName, con.font_mana)  # NDPMTG default
    desc143.putString(idFntN, con.font_rules_text)  # MPlantin default
    desc143.putBoolean(idautoLeading, False)
    primary_action_descriptor.putList(idparagraphStyleRange, list13)
    primary_action_descriptor.putList(idkerningRange, list14)
    list13 = ps.ActionList()

    if input_string.find("\u2022") >= 0:
        # Modal card with bullet points - adjust the formatting slightly
        startIndexBullet = input_string.find("\u2022")
        endIndexBullet = input_string.rindex("\u2022")
        list13 = ps.ActionList()
        list14 = ps.ActionList()
        desc141 = ps.ActionDescriptor()
        desc141.putInteger(idFrom, startIndexBullet)
        desc141.putInteger(idT, endIndexBullet + 1)
        desc142.putUnitDouble(idfirstLineIndent, idPnt, -con.modal_indent)  # negative modal indent
        desc142.putUnitDouble(idstartIndent, idPnt, con.modal_indent)  # modal indent
        desc142.putUnitDouble(idspaceBefore, idPnt, 1)
        desc142.putUnitDouble(idspaceAfter, idPnt, 0)
        desc143 = ps.ActionDescriptor()
        desc143.putString(idfontPostScriptName, con.font_mana)  # NDPMTG default
        desc143.putString(idFntN, con.font_rules_text)  # MPlantin default
        desc143.putUnitDouble(idSz, idPnt, 12)
        desc143.putBoolean(idautoLeading, False)
        desc142.putObject(sID("defaultStyle"), idTxtS, desc143)
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        list13.putObject(idparagraphStyleRange, desc141)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        primary_action_descriptor.putList(idkerningRange, list14)

    if flavor_index >= 0:
        # Adjust line break spacing if there's a line break in the flavor text
        list14 = ps.ActionList()
        desc141 = ps.ActionDescriptor()
        desc141.putInteger(idFrom, flavor_index + 3)
        desc141.putInteger(idT, flavor_index + 4)
        desc142.putUnitDouble(idfirstLineIndent, idPnt, 0)
        idimpliedFirstLineIndent = sID("impliedFirstLineIndent")
        desc142.putUnitDouble(idimpliedFirstLineIndent, idPnt, 0)
        desc142.putUnitDouble(idstartIndent, idPnt, 0)
        desc142.putUnitDouble(sID("impliedStartIndent"), idPnt, 0)
        desc142.putUnitDouble(idspaceBefore, idPnt, con.flavor_text_lead)  # Lead size between rules and flavor text
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        list13.putObject(idparagraphStyleRange, desc141)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        primary_action_descriptor.putList(idkerningRange, list14)

        # Adjust flavor text color
        if con.flavor_text_color:
            list15 = ps.ActionList()
            desc144 = ps.ActionDescriptor()
            desc145 = ps.ActionDescriptor()
            desc144.PutInteger(sID("from"), flavor_index)
            desc144.PutInteger(sID("to"), len(input_string))
            desc145.putString(idfontPostScriptName, con.font_rules_text_italic)  # MPlantin italic default
            desc145.putString(idFntN, con.font_rules_text_italic)  # MPlantin italic default
            desc145.putUnitDouble(idSz, idPnt, layer_font_size)
            desc145.putBoolean(idautoLeading, False)
            desc145.putUnitDouble(idLdng, idPnt, layer_font_size)

            psd.apply_color(desc145, con.flavor_text_color)

            desc144.PutObject(sID("textStyle"), sID("textStyle"), desc145)
            list15.PutObject(sID("textStyleRange"), desc144)
            primary_action_descriptor.putList(sID("textStyleRange"), list15)

    disable_justify = False
    if quote_index >= 0:
        # Adjust line break spacing if there's a line break in the flavor text
        list14 = ps.ActionList()
        desc141 = ps.ActionDescriptor()
        desc141.putInteger(idFrom, quote_index + 3)
        desc141.putInteger(idT, len(input_string))
        desc142.putUnitDouble(idspaceBefore, idPnt, 0)
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        list13.putObject(idparagraphStyleRange, desc141)

        # Optional, align quote credit to right
        if input_string.find('"\r—') >= 0 and con.align_classic_quote:
            # Get start and ending index of quotation credit
            index_start = input_string.find('"\r—') + 2
            index_end = len(input_string) - 1

            # Align this part, disable justification reset
            list13 = classic_align_right(list13, index_start, index_end)
            disable_justify = True

        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        primary_action_descriptor.putList(idkerningRange, list14)

    # Push changes to document
    desc119.putObject(idT, idTxLr, primary_action_descriptor)
    app.executeAction(idsetd, desc119, NO_DIALOG)

    # Reset layer's justification if needed and disable hyphenation
    if not disable_justify:
        app.activeDocument.activeLayer.textItem.justification = layer_justification
    app.activeDocument.activeLayer.textItem.hyphenation = False


def generate_italics(card_text):
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
    for match in re.findall(r"(?:\A|\r+|• +)([A-Za-z0-9 ]+) — ", card_text):
        # Cover boast cards and cards like Mirrodin Besieged
        if (f"• {match}" in card_text and card_text[0:12] != "Choose one —") or "Boast" in match:
            continue
        italic_text.append(match)

    return italic_text


def format_text_wrapper():
    """
    Wrapper for format_text which runs the function with the active layer's current text contents
    and auto-generated italics array. Flavor text index and centered text not supported.
    Super useful to add as a script action in Photoshop for making cards manually!
    """
    card_text = app.activeDocument.activeLayer.textItem.contents
    italic_text = generate_italics(card_text)
    format_text(card_text, italic_text, -1, False)


def strip_reminder_text(oracle_text):
    """
    Strip out any reminder text that a card's oracle text has (reminder text in parentheses).
    If this empties the string, instead return the original string.
    """
    oracle_text_stripped = re.sub(r"\([^()]*\)", "", oracle_text)

    # ensure we didn't add any double whitespace by doing that
    oracle_text_stripped = re.sub(r"  +", "", oracle_text_stripped)
    if oracle_text_stripped != "":
        return oracle_text_stripped
    return oracle_text


def classic_align_right(action_list, start, end):
    """
    Align the quote credit of --Name to the right like on some classic cards.
    @param action_list: Action list to add this action to
    @param start: Starting index of the quote string
    @param end: Ending index of the quote string
    @return: Returns the existing ActionDescriptor with changes applied
    """
    desc1 = ps.ActionDescriptor()
    desc1.putInteger(cID("From"), start)
    desc1.putInteger(cID("T   "), end)
    desc2 = ps.ActionDescriptor()
    idstyleSheetHasParent = sID("styleSheetHasParent")
    desc2.putBoolean(idstyleSheetHasParent, True)
    desc2.putEnumerated(cID("Algn"), cID("Alg "), cID("Rght"))
    idparagraphStyle = sID("paragraphStyle")
    desc1.putObject(idparagraphStyle, idparagraphStyle, desc2)
    idparagraphStyleRange = sID("paragraphStyleRange")
    action_list.putObject(idparagraphStyleRange, desc1)
    return action_list


def scale_text_right_overlap(layer, reference) -> None:
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

        font_size += half_step
        layer.textItem.size = font_size
        layer_right_bound = layer.bounds[2]
        if layer_right_bound > (reference_left_bound - spacing):
            font_size -= half_step
            layer.textItem.size = font_size

    # Shift baseline up to keep text centered vertically
    if old_size > layer.textItem.size:
        layer.textItem.baselineShift = (old_size * 0.3) - (layer.textItem.size * 0.3)

    # Fix corrected reference layer
    if contents: reference.textItem.contents = contents


def scale_text_to_fit_reference(layer, ref, spacing: int = None):
    """
    Resize a given text layer's contents (in 0.25 pt increments) until it fits inside a specified reference layer.
    The resulting text layer will have equal font and lead sizes.
    @param layer: Text layer to scale.
    @param ref: Reference layer the text should fit inside.
    @param spacing: [Optional] Amount of mandatory spacing at the bottom of text layer.
    """
    # Establish base variables, ensure a level of spacing at the margins
    factor = 1
    if not ref: return
    if not spacing:  # If no spacing provided, use default
        spacing = int((app.activeDocument.width / 3264) * 64)
    if app.activeDocument.width != 3264:
        factor = psd.get_text_scale_factor(layer)
    ref_height = psd.get_layer_dimensions(ref)['height'] - spacing
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


def scale_text_to_fit_height(layer, height: int):
    """
    Resize a given text layer's contents (in 0.25 pt increments) until it fits inside a specified reference layer.
    The resulting text layer will have equal font and lead sizes.
    @param layer: Text layer to scale.
    @param height: Reference height to fit.
    """
    # Establish base variables, ensure a level of spacing at the margins
    factor = 1
    if app.activeDocument.width != 3264:
        factor = psd.get_text_scale_factor(layer)
    font_size = layer.textItem.size * factor
    step, half_step = 0.4, 0.2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    if height > psd.get_text_layer_dimensions(layer)['height']: return
    while height < psd.get_text_layer_dimensions(layer)['height']:
        font_size -= step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size

    # Take a half step back up, check if still in bounds and adjust back if needed
    font_size += half_step
    layer.textItem.size = font_size
    layer.textItem.leading = font_size
    if height < psd.get_text_layer_dimensions(layer)['height']:
        font_size -= half_step
        layer.textItem.size = font_size
        layer.textItem.leading = font_size


def vertically_align_text(layer, reference_layer):
    """
    Centers a given text layer vertically with respect to the bounding box of a reference layer.
    """
    ref_height = psd.get_layer_dimensions(reference_layer)['height']
    lay_height = psd.get_text_layer_dimensions(layer)['height']
    bound_delta = reference_layer.bounds[1] - layer.bounds[1]
    height_delta = ref_height - lay_height
    layer.translate(0, bound_delta + height_delta / 2)


def vertically_nudge_creature_text(layer, reference_layer, top_reference_layer):
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


def vertically_nudge_pw_text(text_layers, space, layer_gap, ref_height, adj_reference, top_reference):
    """
    Shift or resize planeswalker text to prevent overlap with the loyalty shield.
    """
    # Layer to check for overlap
    lyrs = text_layers.copy()
    bottom = lyrs[-1]
    movable = len(lyrs)-1
    leftover = (layer_gap - space) * movable

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
        if dif > 0: return

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
        elif dif < 0:
            # Layer gap would be too small, need to resize text then shift upward
            total_h = 0
            for lyr in text_layers:
                lyr.textItem.size -= .2000000000000
                lyr.textItem.leading -= .2000000000000
                total_h += psd.get_text_layer_dimensions(lyr)["height"]

            # Get the exact spacing left over
            new_gap = (ref_height - total_h) / movable

            # Position the bottom layers relative to the top
            for n in range(movable):
                delta = new_gap - (text_layers[n + 1].bounds[1] - text_layers[n].bounds[3])
                text_layers[n + 1].translate(0, delta)

            # Check for another iteration
            vertically_nudge_pw_text(text_layers, space, new_gap, ref_height, adj_reference, top_reference)


"""
PARAGRAPH FORMATTING
"""


def space_after_paragraph(space):
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
