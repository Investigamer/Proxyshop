"""
Utility functions to format text
"""
import re
import photoshop.api as ps
import proxyshop.helpers as psd
from proxyshop.constants import con
from proxyshop.gui import console_handler as console

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
        self.rgb_c = psd.get_rgb(con.rgb_c['r'], con.rgb_c['g'], con.rgb_c['b'])
        self.rgb_w = psd.get_rgb(con.rgb_w['r'], con.rgb_w['g'], con.rgb_w['b'])
        self.rgb_u = psd.get_rgb(con.rgb_u['r'], con.rgb_u['g'], con.rgb_u['b'])
        self.rgb_b = psd.get_rgb(con.rgb_b['r'], con.rgb_b['g'], con.rgb_b['b'])
        self.rgb_bh = psd.get_rgb(con.rgb_bh['r'], con.rgb_bh['g'], con.rgb_bh['b'])
        self.rgb_r = psd.get_rgb(con.rgb_r['r'], con.rgb_r['g'], con.rgb_r['b'])
        self.rgb_g = psd.get_rgb(con.rgb_g['r'], con.rgb_g['g'], con.rgb_g['b'])

        # Symbol colors inner
        self.rgbi_c = psd.get_rgb(con.rgbi_c['r'], con.rgbi_c['g'], con.rgbi_c['b'])
        self.rgbi_w = psd.get_rgb(con.rgbi_w['r'], con.rgbi_w['g'], con.rgbi_w['b'])
        self.rgbi_u = psd.get_rgb(con.rgbi_u['r'], con.rgbi_u['g'], con.rgbi_u['b'])
        self.rgbi_b = psd.get_rgb(con.rgbi_b['r'], con.rgbi_b['g'], con.rgbi_b['b'])
        self.rgbi_bh = psd.get_rgb(con.rgbi_bh['r'], con.rgbi_bh['g'], con.rgbi_bh['b'])
        self.rgbi_r = psd.get_rgb(con.rgbi_r['r'], con.rgbi_r['g'], con.rgbi_r['b'])
        self.rgbi_g = psd.get_rgb(con.rgbi_g['r'], con.rgbi_g['g'], con.rgbi_g['b'])

        # Primary inner color (black default)
        self.rgb_primary = psd.get_rgb(
            con.rgb_primary['r'],
            con.rgb_primary['g'],
            con.rgb_primary['b']
        )

        # Secondary inner color (white default)
        self.rgb_secondary = psd.get_rgb(
            con.rgb_secondary['r'],
            con.rgb_secondary['g'],
            con.rgb_secondary['b']
        )

        # Symbol map for regular mana symbols
        self.color_map = {
            "W": self.rgb_w,
            "U": self.rgb_u,
            "B": self.rgb_b,
            "R": self.rgb_r,
            "G": self.rgb_g,
            "2": self.rgb_c
        }
        self.color_map_inner = {
            "W": self.rgbi_w,
            "U": self.rgbi_u,
            "B": self.rgbi_b,
            "R": self.rgbi_r,
            "G": self.rgbi_g,
            "2": self.rgbi_c,
        }

        # For hybrid symbols with generic mana, use the black symbol color rather than colorless for B
        self.hybrid_color_map = self.color_map.copy()
        self.hybrid_color_map['B'] = self.rgb_bh
        self.hybrid_color_map_inner = self.color_map_inner.copy()
        self.hybrid_color_map_inner['B'] = self.rgbi_bh

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
        if italics.find("}") >= 0:
            for key, symbol in con.symbols.items():
                try: italics = italics.replace(key, symbol)
                except Exception as e: console.log_exception(e)

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
        return [sym.rgb_primary]
    elif symbol == "{S}":
        # Snow symbol
        return [sym.rgb_c, sym.rgb_primary, sym.rgb_secondary]
    elif symbol == "{Q}":
        # Untap symbol
        return [sym.rgb_primary, sym.rgb_secondary]

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
        color_map = sym.color_map
        if hybrid_match[1] == "2":
            # Use the darker color for black's symbols for 2/B hybrid symbols
            color_map = sym.hybrid_color_map
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
    if symbol_length == 2: return [sym.rgb_c, sym.rgb_primary]

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
        desc3 = ps.ActionDescriptor()
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
        desc3.putDouble(
            cID("Rd  "),
            color.rgb.red)  # rgb value.red
        desc3.putDouble(
            cID("Grn "),
            color.rgb.green)  # rgb value.green
        desc3.putDouble(
            cID("Bl  "),
            color.rgb.blue)  # rgb value.blue
        desc2.putObject(
            cID("Clr "),
            cID("RGBC"),
            desc3)
        desc1.putObject(idTxtS, idTxtS, desc2)
        current_ref = desc1
    return current_ref


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
    desc27 = ps.ActionDescriptor()
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
    idClr = cID("Clr ")
    idRd = cID("Rd  ")
    idGrn = cID("Grn ")
    idBl = cID("Bl  ")
    idRGBC = cID("RGBC")
    idLdng = cID("Ldng")
    idTxtt = cID("Txtt")
    idFrom = cID("From")
    ref101.putEnumerated(
        idTxLr,
        cID("Ordn"),
        cID("Trgt"))
    desc119.putReference(cID("null"), ref101)
    primary_action_descriptor.putString(cID("Txt "), input_string)
    desc25.putInteger(idFrom, 0)
    desc25.putInteger(idT, len(input_string))
    desc26.putString(idfontPostScriptName, con.font_rules_text)  # MPlantin default
    desc26.putString(idFntN, con.font_rules_text)  # MPlantin default
    desc26.putUnitDouble(idSz, idPnt, layer_font_size)
    desc27.putDouble(idRd, layer_text_color.rgb.red)  # text color.red
    desc27.putDouble(idGrn, layer_text_color.rgb.green)  # text color.green
    desc27.putDouble(idBl, layer_text_color.rgb.blue)  # text color.blue
    desc26.putObject(idClr, idRGBC, desc27)
    desc26.putBoolean(idautoLeading, False)
    desc26.putUnitDouble(idLdng, idPnt, layer_font_size)
    desc25.putObject(idTxtS, idTxtS, desc26)
    current_layer_ref = desc25

    for italics_index in italics_indices:
        # Italics text
        primary_action_list.putObject(idTxtt, current_layer_ref)
        desc125 = ps.ActionDescriptor()
        desc125.putInteger(idFrom, italics_index['start_index'])  # italics start index
        desc125.putInteger(idT, italics_index['end_index'])  # italics end index
        desc126 = ps.ActionDescriptor()
        desc126.putString(idfontPostScriptName, con.font_rules_text_italic)  # MPlantin italic default
        desc126.putString(idFntN, con.font_rules_text_italic)  # MPlantin italic default
        desc126.putUnitDouble(idSz, idPnt, layer_font_size)
        desc126.putBoolean(idautoLeading, False)
        desc126.putUnitDouble(idLdng, idPnt, layer_font_size)
        # Added
        descTemp = ps.ActionDescriptor()
        # Default text box
        descTemp.putDouble(idRd, layer_text_color.rgb.red)  # text color.red
        descTemp.putDouble(idGrn, layer_text_color.rgb.green)  # text color.green
        descTemp.putDouble(idBl, layer_text_color.rgb.blue)  # text color.blue
        desc126.putObject(idClr, idRGBC, descTemp)
        # End
        desc125.putObject(idTxtS, idTxtS, desc126)
        current_layer_ref = desc125

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

    # paragraph formatting
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
            desc146 = ps.ActionDescriptor()
            desc144.PutInteger(sID("from"), flavor_index)
            desc144.PutInteger(sID("to"), len(input_string))
            desc145.putString(idfontPostScriptName, con.font_rules_text_italic)  # MPlantin italic default
            desc145.putString(idFntN, con.font_rules_text_italic)  # MPlantin italic default
            desc145.putUnitDouble(idSz, idPnt, layer_font_size)
            desc145.putBoolean(idautoLeading, False)
            desc145.putUnitDouble(idLdng, idPnt, layer_font_size)
            desc146.PutDouble(idRd, con.flavor_text_color['r'])
            desc146.PutDouble(idGrn, con.flavor_text_color['g'])
            desc146.PutDouble(idBl, con.flavor_text_color['b'])
            desc145.PutObject(sID("color"), sID("RGBColor"), desc146)
            desc144.PutObject(sID("textStyle"), sID("textStyle"), desc145)
            list15.PutObject(sID("textStyleRange"), desc144)
            primary_action_descriptor.putList(sID("textStyleRange"), list15)

    if quote_index >= 0:
        # Adjust line break spacing if there's a line break in the flavor text
        list14 = ps.ActionList()
        desc141 = ps.ActionDescriptor()
        desc141.putInteger(idFrom, quote_index + 3)
        desc141.putInteger(idT, len(input_string))
        desc142.putUnitDouble(idspaceBefore, idPnt, 0)
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        list13.putObject(idparagraphStyleRange, desc141)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        primary_action_descriptor.putList(idkerningRange, list14)

    # Optional, align last line to right
    if input_string.find('"\r—') >= 0 and con.align_classic_quote:

        # Get start and ending index of quotation credit
        index_start = input_string.find('"\r—') + 2
        index_end = len(input_string) - 1

        # Align this part, disable justification reset
        primary_action_descriptor = classic_align_right(primary_action_descriptor, index_start, index_end)
        disable_justify = True

    else: disable_justify = False

    # Push changes to document
    desc119.putObject(idT, idTxLr, primary_action_descriptor)
    app.executeAction(idsetd, desc119, NO_DIALOG)

    # Reset layer's justification if needed and disable hyphenation
    if not disable_justify:
        app.activeDocument.activeLayer.textItem.justification = layer_justification
    app.activeDocument.activeLayer.textItem.hyphenation = False


def generate_italics(card_text):
    """
     * Generates italics text array from card text to italicise all text within (parentheses) and all ability words.
    """
    italic_text = []
    end_index = 0
    while True:
        start_index = card_text.find("(", end_index)
        if start_index >= 0:
            end_index = card_text.find(")", start_index + 1)
            end_index += 1
            italic_text.extend([card_text[start_index:end_index]])
        else: break

    # Attach all ability words to the italics array
    for ability_word in con.ability_words:
        italic_text.extend([ability_word + " \u2014"])  # Include em dash

    return italic_text


def format_text_wrapper():
    """
     Wrapper for format_text which runs the function with the active layer's current text contents
     and auto-generated italics array. Flavor text index and centered text not supported.
     Super useful to add as a script action in Photoshop for making cards manually!
    """
    card_text = app.activeDocument.activeLayer.textItem.contents
    italic_text = generate_italics(card_text)
    italic_text.color = psd.rgb_grey()
    format_text(card_text, italic_text, -1, False)


def strip_reminder_text(oracle_text):
    """
    Strip out any reminder text that a card's oracle text has (reminder text in parentheses).
    If this would empty the string, instead return the original string.
    """
    oracle_text_stripped = re.sub(r"\([^()]*\)", "", oracle_text)

    # ensure we didn't add any double whitespace by doing that
    oracle_text_stripped = re.sub(r"  +", "", oracle_text_stripped)
    if oracle_text_stripped != "":
        return oracle_text_stripped
    return oracle_text


def classic_align_right(primedesc, start, end):
    """
    Align the quote credit of --Name to the right like on some classic cards.
    @param primedesc: Existing ActionDescriptor object
    @param start: Starting index of the quote string
    @param end: Ending index of the quote string
    @return: Returns the existing ActionDescriptor with changes applied
    """
    desc145 = ps.ActionDescriptor()
    list15 = ps.ActionList()
    desc145.putInteger(cID("From"), start)
    desc145.putInteger(cID("T   "), end)
    desc1265 = ps.ActionDescriptor()
    idstyleSheetHasParent = sID("styleSheetHasParent")
    desc1265.putBoolean(idstyleSheetHasParent, True)
    desc1265.putEnumerated(cID("Algn"), cID("Alg "), cID("Rght"))
    idparagraphStyle = sID("paragraphStyle")
    desc145.putObject(idparagraphStyle, idparagraphStyle, desc1265)
    idparagraphStyleRange = sID("paragraphStyleRange")
    list15.putObject(idparagraphStyleRange, desc145)
    primedesc.putList(idparagraphStyleRange, list15)
    return primedesc


def scale_text_right_overlap(
        layer: ps.LayerKind.TextLayer,
        reference: ps.LayerKind.TextLayer
) -> None:
    """
    Scales a text layer down (in 0.2 pt increments) until its right bound
    has a 24 px clearance from a reference layer's left bound.
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
    step_size = 0.2
    reference_left_bound = reference.bounds[0]
    layer_left_bound = layer.bounds[0]
    layer_right_bound = layer.bounds[2]
    old_size = float(layer.textItem.size)

    # Obtain proper spacing for this document size
    spacing = int((app.activeDocument.width / 3264) * 24)

    # Guard against the reference's left bound being left of the layer's left bound
    if reference_left_bound >= layer_left_bound:
        # Step down the font till it clears the reference
        while layer_right_bound > (reference_left_bound - spacing):  # minimum 24 px gap
            layer.textItem.size -= step_size
            layer_right_bound = layer.bounds[2]

    # Shift baseline up to keep text centered vertically
    if old_size > layer.textItem.size:
        layer.textItem.baselineShift = (old_size * 0.3) - (layer.textItem.size * 0.3)

    # Fix corrected reference layer
    if contents: reference.textItem.contents = contents


def scale_text_to_fit_reference(layer, reference_layer):
    """
    Resize a given text layer's contents (in 0.25 pt increments) until it fits inside a specified reference layer.
    The resulting text layer will have equal font and lead sizes.
    """
    # Establish base variables, ensure a level of spacing at the margins
    if reference_layer is None: return
    spacing = int((app.activeDocument.width / 3264) * 64)
    ref_height = psd.get_layer_dimensions(reference_layer)['height'] - spacing
    font_size = layer.textItem.size
    step_size = 0.25

    # step down font and lead sizes by the step size, and update those sizes in the layer
    while ref_height < psd.get_text_layer_dimensions(layer)['height']:
        font_size -= step_size
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


sym = SymbolMapper()
