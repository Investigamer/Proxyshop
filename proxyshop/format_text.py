# BASIC
import os
import re

# MY MODULES
import proxyshop.constants as con
import proxyshop.settings as cfg
import proxyshop.helpers as psd
import photoshop.api as ps
app = ps.Application()

"""
Locating symbols and italics in the input string
"""
def locate_symbols(input_string):
    """
     * Locate symbols in the input string, replace them with the characters we use to represent them in NDPMTG, and determine
     * the colors those characters need to be. Returns an object with the modified input string and a list of symbol indices.
    """
    symbol_re = r"(\{.*?\})"
    symbol_indices = []
    #try:
    while(True):
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
    #except: print(f"Encountered a formatted character in braces that doesn't map to characters: {symbol}")
    return {
        'input_string': input_string,
        'symbol_indices': symbol_indices
    }

def locate_italics(input_string, italics_strings):
    """
     * Locate all instances of italic strings in the input string and record their start and end indices.
     * Returns a list of italic string indices (start and end).
    """
    italics_indices = []

    for italics in italics_strings:
        start_index = 0
        end_index = 0

        # replace symbols with their character representations in the italic string
        if italics.find("}") >= 0:
            for symbol in con.symbols:
                try: 
                    italics = italics.replace(symbol, con.symbols[symbol])
                except: pass

        # Locate Italicized text
        while (True):
            start_index = input_string.find(italics, end_index)
            end_index = start_index + len(italics)
            if start_index < 0: break

            italics_indices.extend([{
                'start_index': start_index,
                'end_index': end_index,
            }])

    return italics_indices

# Formatting for different symbol types
def determine_symbol_colors(symbol, symbol_length):
    """
     * Determines the colors of a symbol (represented as Scryfall string) and returns an array of SolidColor objects.
    """

    symbol_color_map = {
        "W": con.rgb_w,
        "U": con.rgb_u,
        "B": con.rgb_c,
        "R": con.rgb_r,
        "G": con.rgb_g,
        "2": con.rgb_c,
    }

    # for hybrid symbols with generic mana, use the black symbol color rather than colorless for B
    hybrid_symbol_color_map = {
        "W": con.rgb_w,
        "U": con.rgb_u,
        "B": con.rgb_b,
        "R": con.rgb_r,
        "G": con.rgb_g,
        "2": con.rgb_c,
    }

    # SPECIAL SYMBOLS
    if symbol == "{E}" or symbol == "{CHAOS}":
        # energy or chaos symbols
        return [psd.rgb_black()]
    elif symbol == "{S}":
        # snow symbol
        return [con.rgb_c, psd.rgb_black(), psd.rgb_white()]
    elif symbol == "{Q}":
        # untap symbol
        return [psd.rgb_black(), psd.rgb_white()]

    # Phyrexian
    phyrexian_regex = r"\{([W,U,B,R,G])\/P\}"
    phyrexian_match = re.match(phyrexian_regex, symbol)
    if phyrexian_match: return [hybrid_symbol_color_map[phyrexian_match[1]], psd.rgb_black()]

    # Phyrexian hybrid
    phyrexian_hybrid_regex = r"\{([W,U,B,R,G])\/([W,U,B,R,G])\/P\}"
    phyrexian_hybrid_match = re.match(phyrexian_hybrid_regex, symbol)
    if phyrexian_hybrid_match:
        return [
            symbol_color_map[phyrexian_hybrid_match[2]],
            symbol_color_map[phyrexian_hybrid_match[1]],
            psd.rgb_black()
        ]

    # Hybrid
    hybrid_regex = r"\{([2,W,U,B,R,G])\/([W,U,B,R,G])\}"
    hybrid_match = re.match(hybrid_regex, symbol)
    if hybrid_match:
        color_map = symbol_color_map
        if hybrid_match[1] == "2":
            # Use the darker color for black's symbols for 2/B hybrid symbols
            color_map = hybrid_symbol_color_map
        return [
            color_map[hybrid_match[2]],
            color_map[hybrid_match[1]],
            psd.rgb_black(),
            psd.rgb_black()
        ]

    normal_symbol_regex = r"\{([W,U,B,R,G])\}"
    normal_symbol_match = re.match(normal_symbol_regex, symbol)
    if normal_symbol_match: return [symbol_color_map[normal_symbol_match[1]], psd.rgb_black()]

    if symbol_length == 2: return [con.rgb_c, psd.rgb_black()]
    else: print(f"Encountered a symbol that I don't know how to color: {symbol}")

def format_symbol(primary_action_list, starting_layer_ref, symbol_index, symbol_colors, layer_font_size):
    """
     * Formats an n-character symbol at the specified index (symbol length determined from symbol_colors).
    """
    current_ref = starting_layer_ref
    for i in range(len(symbol_colors)):
        idTxtt = app.charIDToTypeID("Txtt")
        primary_action_list.putObject(idTxtt, current_ref)
        desc1 = ps.ActionDescriptor()
        idFrom = app.charIDToTypeID("From")
        desc1.putInteger(idFrom, symbol_index + i)
        idT = app.charIDToTypeID("T   ")
        desc1.putInteger(idT, symbol_index + i + 1)
        idTxtS = app.charIDToTypeID("TxtS")
        desc2 = ps.ActionDescriptor()
        idfontPostScriptName = app.stringIDToTypeID("fontPostScriptName")
        desc2.putString(idfontPostScriptName, con.font_name_ndpmtg) # NDPMTG font name
        idFntN = app.charIDToTypeID("FntN")
        desc2.putString(idFntN, con.font_name_ndpmtg) # NDPMTG font name
        idSz = app.charIDToTypeID("Sz  ")
        idPnt = app.charIDToTypeID("#Pnt")
        desc2.putUnitDouble(idSz, idPnt, layer_font_size)
        idautoLeading = app.stringIDToTypeID("autoLeading")
        desc2.putBoolean(idautoLeading, False)
        idLdng = app.charIDToTypeID("Ldng")
        idPnt = app.charIDToTypeID("#Pnt")
        desc2.putUnitDouble(idLdng, idPnt, layer_font_size)
        idClr = app.charIDToTypeID("Clr ")
        desc3 = ps.ActionDescriptor()
        """
        idRd = app.charIDToTypeID("Rd  ")
        desc3.putDouble(idRd, symbol_colors[i].rgb.red) # rgb value.red
        idGrn = app.charIDToTypeID("Grn ")
        desc3.putDouble(idGrn, symbol_colors[i].rgb.green) # rgb value.green
        idBl = app.charIDToTypeID("Bl  ")
        desc3.putDouble(idBl, symbol_colors[i].rgb.blue) # rgb value.blue
        """
        idRd = app.charIDToTypeID("Rd  ")
        desc3.putDouble(idRd, symbol_colors[i].rgb.red) # rgb value.red
        idGrn = app.charIDToTypeID("Grn ")
        desc3.putDouble(idGrn, symbol_colors[i].rgb.green) # rgb value.green
        idBl = app.charIDToTypeID("Bl  ")
        desc3.putDouble(idBl, symbol_colors[i].rgb.blue) # rgb value.blue
        
        
        idRGBC = app.charIDToTypeID("RGBC")
        desc2.putObject(idClr, idRGBC, desc3)
        idTxtS = app.charIDToTypeID("TxtS")
        desc1.putObject(idTxtS, idTxtS, desc2)
        current_ref = desc1
    return current_ref

def format_text(input_string, italics_strings, flavor_index, is_centered):
    """
     * Inserts the given string into the active layer and formats it according to def parameters with symbols 
     * from the NDPMTG font.
     * @param {str} input_string The string to insert into the active layer
     * @param {Array[str]} italic_strings An array containing strings that are present in the main input string and should be italicised
     * @param {int} flavor_index The index at which linebreak spacing should be increased and any subsequent chars should be italicised (where the card's flavor text begins)
     * @param {boolean} is_centered Whether or not the input text should be centre-justified
    """

    # record the layer's justification before modifying the layer in case it's reset along the way
    layer_justification = app.activeDocument.activeLayer.textItem.justification

    # TODO: check that the active layer is a text layer, and raise an issue if not
    if flavor_index > 0: quote_index = input_string.find("\r", flavor_index + 3)
    else: quote_index = 0 

    # Locate symbols and update the input string
    ret = locate_symbols(input_string)
    input_string = ret['input_string']
    symbol_indices = ret['symbol_indices']

    # Locate italics text indices
    italics_indices = locate_italics(input_string, italics_strings)

    # Prepare action descriptor and reference variables
    layer_font_size = app.activeDocument.activeLayer.textItem.size
    layer_text_color = app.activeDocument.activeLayer.textItem.color
    # layer_text_color = rgb_grey()
    desc119 = ps.ActionDescriptor()
    idnull = app.charIDToTypeID("null")
    ref101 = ps.ActionReference()
    idTxLr = app.charIDToTypeID("TxLr")
    idOrdn = app.charIDToTypeID("Ordn")
    idTrgt = app.charIDToTypeID("Trgt")
    ref101.putEnumerated(idTxLr, idOrdn, idTrgt)
    desc119.putReference(idnull, ref101)
    primary_action_descriptor = ps.ActionDescriptor()
    idTxt = app.charIDToTypeID("Txt ")
    primary_action_descriptor.putString(idTxt, input_string)
    primary_action_list = ps.ActionList()
    desc25 = ps.ActionDescriptor()
    idFrom = app.charIDToTypeID("From")
    desc25.putInteger(idFrom, 0)
    idT = app.charIDToTypeID("T   ")
    desc25.putInteger(idT, len(input_string))
    desc26 = ps.ActionDescriptor()
    idfontPostScriptName = app.stringIDToTypeID("fontPostScriptName")
    desc26.putString(idfontPostScriptName, con.font_name_mplantin)  # MPlantin font name
    idFntN = app.charIDToTypeID("FntN")
    desc26.putString(idFntN, con.font_name_mplantin)  # MPlantin font name
    idSz = app.charIDToTypeID("Sz  ")
    idPnt = app.charIDToTypeID("#Pnt")
    desc26.putUnitDouble(idSz, idPnt, layer_font_size)
    idClr = app.charIDToTypeID("Clr ")
    desc27 = ps.ActionDescriptor()
    idRd = app.charIDToTypeID("Rd  ")
    desc27.putDouble(idRd, layer_text_color.rgb.red)  # text color.red
    idGrn = app.charIDToTypeID("Grn ")
    desc27.putDouble(idGrn, layer_text_color.rgb.green)  # text color.green
    idBl = app.charIDToTypeID("Bl  ")
    desc27.putDouble(idBl, layer_text_color.rgb.blue)  # text color.blue
    idRGBC = app.charIDToTypeID("RGBC")
    desc26.putObject(idClr, idRGBC, desc27)
    idHrzS = app.charIDToTypeID("HrzS")
    idautoLeading = app.stringIDToTypeID("autoLeading")
    desc26.putBoolean(idautoLeading, False)
    idLdng = app.charIDToTypeID("Ldng")
    idPnt = app.charIDToTypeID("#Pnt")
    desc26.putUnitDouble(idLdng, idPnt, layer_font_size)
    idTxtS = app.charIDToTypeID("TxtS")
    desc25.putObject(idTxtS, idTxtS, desc26)
    current_layer_ref = desc25

    for i in range(len(italics_indices)):
        # Italics text
        idTxtt = app.charIDToTypeID("Txtt")
        primary_action_list.putObject(idTxtt, current_layer_ref)
        desc125 = ps.ActionDescriptor()
        idFrom = app.charIDToTypeID("From")
        desc125.putInteger(idFrom, italics_indices[i]['start_index'])  # italics start index
        idT = app.charIDToTypeID("T   ")
        desc125.putInteger(idT, italics_indices[i]['end_index'])  # italics end index
        idTxtS = app.charIDToTypeID("TxtS")
        desc126 = ps.ActionDescriptor()
        idfontPostScriptName = app.stringIDToTypeID("fontPostScriptName")
        desc126.putString(idfontPostScriptName, con.font_name_mplantin_italic)  # MPlantin italic font name
        idFntN = app.charIDToTypeID("FntN")
        desc126.putString(idFntN, con.font_name_mplantin_italic)  # MPlantin italic font name
        idFntS = app.charIDToTypeID("FntS")
        idSz = app.charIDToTypeID("Sz  ")
        idPnt = app.charIDToTypeID("#Pnt")
        desc126.putUnitDouble(idSz, idPnt, layer_font_size)
        idautoLeading = app.stringIDToTypeID("autoLeading")
        desc126.putBoolean(idautoLeading, False)
        idLdng = app.charIDToTypeID("Ldng")
        idPnt = app.charIDToTypeID("#Pnt")
        desc126.putUnitDouble(idLdng, idPnt, layer_font_size)
        idTxtS = app.charIDToTypeID("TxtS")
        # Added
        idClr = app.charIDToTypeID("Clr ")
        descTemp = ps.ActionDescriptor()
        idRd = app.charIDToTypeID("Rd  ")
        """
        // GREY
        descTemp.putDouble(idRd, 170)  // text color.red
        idGrn = app.charIDToTypeID("Grn ")
        descTemp.putDouble(idGrn, 170)  // text color.green
        idBl = app.charIDToTypeID("Bl  ")
        descTemp.putDouble(idBl, 170)  // text color.blue
        """
        # Default text box
        descTemp.putDouble(idRd, layer_text_color.rgb.red)  # text color.red
        idGrn = app.charIDToTypeID("Grn ")
        descTemp.putDouble(idGrn, layer_text_color.rgb.green)  # text color.green
        idBl = app.charIDToTypeID("Bl  ")
        descTemp.putDouble(idBl, layer_text_color.rgb.blue)  # text color.blue

        idRGBC = app.charIDToTypeID("RGBC")
        desc126.putObject( idClr, idRGBC, descTemp )
        # End
        desc125.putObject(idTxtS, idTxtS, desc126)
        current_layer_ref = desc125

    # Format each symbol correctly
    for i in range(len(symbol_indices)):
        current_layer_ref = format_symbol(
            primary_action_list = primary_action_list,
            starting_layer_ref = current_layer_ref,
            symbol_index = symbol_indices[i]['index'],
            symbol_colors = symbol_indices[i]['colors'],
            layer_font_size = layer_font_size,
        )

    idTxtt = app.charIDToTypeID("Txtt")
    primary_action_list.putObject(idTxtt, current_layer_ref)
    primary_action_descriptor.putList(idTxtt, primary_action_list)

    # paragraph formatting
    idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
    list13 = ps.ActionList()
    desc141 = ps.ActionDescriptor()
    idFrom = app.charIDToTypeID("From")
    desc141.putInteger(idFrom, 0)
    idT = app.charIDToTypeID("T   ")
    desc141.putInteger(idT, len(input_string))  # input string length
    idparagraphStyle = app.stringIDToTypeID("paragraphStyle")
    desc142 = ps.ActionDescriptor()
    idfirstLineIndent = app.stringIDToTypeID("firstLineIndent")
    idPnt = app.charIDToTypeID("#Pnt")
    desc142.putUnitDouble(idfirstLineIndent, idPnt, 0.000000)
    idstartIndent = app.stringIDToTypeID("startIndent")
    idPnt = app.charIDToTypeID("#Pnt")
    desc142.putUnitDouble(idstartIndent, idPnt, 0.000000)
    idendIndent = app.stringIDToTypeID("endIndent")
    idPnt = app.charIDToTypeID("#Pnt")
    desc142.putUnitDouble(idendIndent, idPnt, 0.000000)
    idspaceBefore = app.stringIDToTypeID("spaceBefore")
    idPnt = app.charIDToTypeID("#Pnt")
    if is_centered:  # line break lead
        desc142.putUnitDouble(idspaceBefore, idPnt, 0)
    else:
        desc142.putUnitDouble(idspaceBefore, idPnt, con.line_break_lead)
    idspaceAfter = app.stringIDToTypeID("spaceAfter")
    idPnt = app.charIDToTypeID("#Pnt")
    desc142.putUnitDouble(idspaceAfter, idPnt, 0.000000)
    iddropCapMultiplier = app.stringIDToTypeID("dropCapMultiplier")
    desc142.putInteger(iddropCapMultiplier, 1)
    idleadingType = app.stringIDToTypeID("leadingType")
    idleadingType = app.stringIDToTypeID("leadingType")
    idleadingBelow = app.stringIDToTypeID("leadingBelow")
    desc142.putEnumerated(idleadingType, idleadingType, idleadingBelow)
    desc143 = ps.ActionDescriptor()
    idfontPostScriptName = app.stringIDToTypeID("fontPostScriptName")
    desc143.putString(idfontPostScriptName, con.font_name_ndpmtg)  # NDPMTG font name
    idFntN = app.charIDToTypeID("FntN")
    desc143.putString(idFntN, con.font_name_mplantin)  # MPlantin font name
    idautoLeading = app.stringIDToTypeID("autoLeading")
    desc143.putBoolean(idautoLeading, False)
    primary_action_descriptor.putList(idparagraphStyleRange, list13)
    idkerningRange = app.stringIDToTypeID("kerningRange")
    list14 = ps.ActionList()
    primary_action_descriptor.putList(idkerningRange, list14)
    list13 = ps.ActionList()

    if input_string.find("\u2022") >= 0:
        # Modal card with bullet points - adjust the formatting slightly
        startIndexBullet = input_string.find("\u2022")
        endIndexBullet = input_string.rindex("\u2022")
        idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
        list13 = ps.ActionList()
        desc141 = ps.ActionDescriptor()
        idFrom = app.charIDToTypeID("From")
        desc141.putInteger(idFrom, startIndexBullet)
        idT = app.charIDToTypeID("T   ")
        desc141.putInteger(idT, endIndexBullet + 1)
        idparagraphStyle = app.stringIDToTypeID("paragraphStyle")
        idfirstLineIndent = app.stringIDToTypeID("firstLineIndent")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idfirstLineIndent, idPnt, -con.modal_indent) # negative modal indent
        idstartIndent = app.stringIDToTypeID("startIndent")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idstartIndent, idPnt, con.modal_indent) # modal indent
        idspaceBefore = app.stringIDToTypeID("spaceBefore")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idspaceBefore, idPnt, 1.0)
        idspaceAfter = app.stringIDToTypeID("spaceAfter")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idspaceAfter, idPnt, 0.000000)
        iddefaultStyle = app.stringIDToTypeID("defaultStyle")
        desc143 = ps.ActionDescriptor()
        idfontPostScriptName = app.stringIDToTypeID("fontPostScriptName")
        desc143.putString(idfontPostScriptName, con.font_name_ndpmtg)  # NDPMTG font name
        idFntN = app.charIDToTypeID("FntN")
        desc143.putString(idFntN, con.font_name_mplantin)
        idSz = app.charIDToTypeID("Sz  ")
        idPnt = app.charIDToTypeID("#Pnt")
        desc143.putUnitDouble(idSz, idPnt, 11.998500)  # TODO: what's this?
        idautoLeading = app.stringIDToTypeID("autoLeading")
        desc143.putBoolean(idautoLeading, False)
        idTxtS = app.charIDToTypeID("TxtS")
        desc142.putObject(iddefaultStyle, idTxtS, desc143)
        idparagraphStyle = app.stringIDToTypeID("paragraphStyle")
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
        list13.putObject(idparagraphStyleRange, desc141)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        idkerningRange = app.stringIDToTypeID("kerningRange")
        list14 = ps.ActionList()
        primary_action_descriptor.putList(idkerningRange, list14)

    if flavor_index > 0:
        # Adjust line break spacing if there's a line break in the flavor text
        idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
        desc141 = ps.ActionDescriptor()
        idFrom = app.charIDToTypeID("From")
        desc141.putInteger(idFrom, flavor_index + 3)
        idT = app.charIDToTypeID("T   ")
        desc141.putInteger(idT, flavor_index + 4)
        idfirstLineIndent = app.stringIDToTypeID("firstLineIndent")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idfirstLineIndent, idPnt, 0)
        idimpliedFirstLineIndent = app.stringIDToTypeID("impliedFirstLineIndent")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idimpliedFirstLineIndent, idPnt, 0)
        idstartIndent = app.stringIDToTypeID("startIndent")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idstartIndent, idPnt, 0)
        idimpliedStartIndent = app.stringIDToTypeID("impliedStartIndent")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idimpliedStartIndent, idPnt, 0)
        idspaceBefore = app.stringIDToTypeID("spaceBefore")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idspaceBefore, idPnt, con.flavor_text_lead)  # lead size between rules text and flavor text
        idparagraphStyle = app.stringIDToTypeID("paragraphStyle")
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
        list13.putObject(idparagraphStyleRange, desc141)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        idkerningRange = app.stringIDToTypeID("kerningRange")
        list14 = ps.ActionList()
        primary_action_descriptor.putList(idkerningRange, list14)

    if quote_index > 0:
        # Adjust line break spacing if there's a line break in the flavor text
        idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
        desc141 = ps.ActionDescriptor()
        idFrom = app.charIDToTypeID("From")
        desc141.putInteger(idFrom, quote_index + 3)
        idT = app.charIDToTypeID("T   ")
        desc141.putInteger(idT, len(input_string))
        idspaceBefore = app.stringIDToTypeID("spaceBefore")
        idPnt = app.charIDToTypeID("#Pnt")
        desc142.putUnitDouble(idspaceBefore, idPnt, 0)
        idparagraphStyle = app.stringIDToTypeID("paragraphStyle")
        desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
        idparagraphStyleRange = app.stringIDToTypeID("paragraphStyleRange")
        list13.putObject(idparagraphStyleRange, desc141)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        idkerningRange = app.stringIDToTypeID("kerningRange")
        list14 = ps.ActionList()
        primary_action_descriptor.putList(idkerningRange, list14)

    # Push changes to document
    idsetd = app.charIDToTypeID("setd")
    idTxLr = app.charIDToTypeID("TxLr")
    desc119.putObject(idT, idTxLr, primary_action_descriptor)
    app.executeAction(idsetd, desc119, ps.DialogModes.DisplayNoDialogs)

    # Reset layer's justification and disable hypenation
    app.activeDocument.activeLayer.textItem.justification = layer_justification
    app.activeDocument.activeLayer.textItem.hyphenation = False

def generate_italics(card_text):
    """
     * Generates italics text array from card text to italicise all text within (parentheses) and all ability words.
    """
    reminder_text = True
    italic_text = []
    end_index = 0
    while (reminder_text):
        start_index = card_text.find("(", end_index)
        if start_index >= 0:
            end_index = card_text.find(")", start_index + 1)
            end_index+=1
            italic_text.extend([card_text[start_index:end_index]])
        else: reminder_text = False

    # Attach all ability words to the italics array
    for ability_word in con.ability_words:
        italic_text.extend([ability_word + " \u2014"])  # Include em dash

    # italic_text.color = rgb_grey()
    return italic_text

def format_text_wrapper():
    """
     * Wrapper for format_text which runs the def with the active layer's current text contents and auto-generated italics array.
     * flavor text index and centered text not supported.
     * Super useful to add as a script action in Photoshop for making cards manually!
    """
    card_text = app.activeDocument.activeLayer.textItem.contents
    italic_text = generate_italics(card_text)
    italic_text.color = rgb_grey()
    format_text(card_text, italic_text, -1, False)

def strip_reminder_text(oracle_text):
    """
     * Strip out any reminder text that a card's oracle text has (reminder text in parentheses).
     * If this would empty the string, instead return the original string.
    """
    oracle_text_stripped = re.sub(r"\([^()]*\)", "", oracle_text)

    # ensure we didn't add any double whitespace by doing that
    oracle_text_stripped = re.sub(r"  +", "", oracle_text_stripped)
    if oracle_text_stripped != "":
        return oracle_text_stripped
    return oracle_text