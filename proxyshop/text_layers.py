"""
TEXT LAYER MODULE
"""
import proxyshop.helpers as psd
import proxyshop.constants as con
from proxyshop import format_text
from proxyshop.helpers import ps, app
cfg = con.cfg

def scale_text_right_overlap(layer, reference_layer):
    """
     * Scales a text layer down (in 0.2 pt increments) until its right bound has a 24 px clearance from a reference
     * layer's left bound.
    """
    # Correct for empty reference layer
    try:
        contents = str(reference_layer.textItem.contents)
        if contents in ("", " "):
            reference_layer.textItem.contents = "."
    except: pass

    # Can't find UnitValue object in python api
    step_size = 0.25
    reference_left_bound = reference_layer.bounds[0]
    layer_left_bound = layer.bounds[0]
    layer_right_bound = layer.bounds[2]

    # Obtain proper spacing for this document size
    spacing = int((app.activeDocument.width/3264)*60)

    # Guard against the reference's left bound being left of the layer's left bound or other irregularities
    if reference_left_bound < layer_left_bound: return None

    # Step down the font till it clears the reference
    while layer_right_bound > (reference_left_bound-spacing):  # minimum 24 px gap
        layer.textItem.size = layer.textItem.size - step_size
        layer_right_bound = layer.bounds[2]

    # Fix corrected reference layer
    try:
        if str(reference_layer.textItem.contents) == ".":
            reference_layer.textItem.contents = contents
    except: pass

# TODO: Multiple layers, each with a reference, that scale together until they all fit their references?
def scale_text_to_fit_reference(layer, reference_layer):
    """
    * Resize a given text layer's contents (in 0.25 pt increments) until it fits inside a specified reference layer.
    * The resulting text layer will have equal font and lead sizes.
    """
    if reference_layer is None: return True
    text_item = layer.textItem
    starting_font_size = text_item.size
    font_size = starting_font_size
    step_size = 0.25
    scaled = False

    # Obtain proper spacing for this document size
    spacing = int((app.activeDocument.width/3264)*60)

    # Reduce the reference height by 64 pixels to avoid text landing on the top/bottom bevels
    reference_height = psd.compute_layer_dimensions(reference_layer)['height']-spacing
    layer_height = psd.compute_text_layer_dimensions(layer)['height']

    while reference_height < layer_height:
        scaled = True
        # step down font and lead sizes by the step size, and update those sizes in the layer
        font_size -= step_size
        text_item.size = font_size
        text_item.leading = font_size
        layer_height = psd.compute_text_layer_dimensions(layer)['height']

    return scaled

def vertically_align_text(layer, reference_layer):
    """
     * Rasterises a given text layer and centres it vertically with respect to the bounding box of a reference layer.
    """
    layer.rasterize(ps.RasterizeType.TextContents)
    psd.select_layer_pixels(reference_layer)
    app.activeDocument.activeLayer = layer
    psd.align_vertical()
    psd.clear_selection()

def vertically_nudge_creature_text(layer, reference_layer, top_reference_layer):
    """
     * Vertically nudge a creature's text layer if it overlaps with the power/toughness box, determined by the given reference layers.
    """
    # Does the layer needs to be nudged?
    if layer.bounds[2] >= reference_layer.bounds[0]:
        psd.select_layer_pixels(reference_layer)
        app.activeDocument.activeLayer = layer

        # copy the contents of the active layer within the current selection to a new layer
        app.executeAction(
            app.charIDToTypeID("CpTL"),
            None,
            ps.DialogModes.DisplayNoDialogs)
        desc5 = ps.ActionDescriptor()
        desc6 = ps.ActionDescriptor()
        ref4 = ps.ActionReference()
        idLyr = app.charIDToTypeID("Lyr ")
        ref4.putEnumerated(
            idLyr,
            app.charIDToTypeID("Ordn"),
            app.charIDToTypeID("Trgt"))
        desc5.putReference(app.charIDToTypeID("null"), ref4)
        desc6.putString(app.charIDToTypeID("Nm  "), "Extra Bit")
        desc5.putObject(app.charIDToTypeID("T   "), idLyr, desc6)
        app.executeAction(
            app.charIDToTypeID("setd"),
            desc5,
            ps.DialogModes.DisplayNoDialogs)

        # determine how much the rules text overlaps the power/toughness by
        extra_bit_layer = psd.getLayer("Extra Bit", layer.parent)
        delta = top_reference_layer.bounds[3] - extra_bit_layer.bounds[3]
        extra_bit_layer.visible = False

        if delta < 0: layer.applyOffset(0, delta, ps.OffsetUndefinedAreas.OffsetSetToLayerFill)

        psd.clear_selection()

# Class definitions
class TextField ():
    """
    A generic TextField, which allows you to set a text layer's contents and text color.
    """
    def __init__ (self, layer, text_contents, text_color):
        self.layer = layer
        self.text_contents = ""
        if text_contents: self.text_contents = text_contents.replace("\n", "\r")
        self.text_color = text_color

    def execute (self):
        """
        Enables and fills the text field
        """
        self.layer.visible = True
        self.layer.textItem.contents = self.text_contents
        self.layer.textItem.color = self.text_color

class ScaledTextField (TextField):
    """
     * A TextField which automatically scales down its font size (in 0.2 pt increments) until its
     * right bound no longer overlaps with a specified reference layer's left bound.
    """
    def __init__ (self, layer, text_contents, text_color, reference_layer):
        super().__init__(layer, text_contents, text_color)
        self.reference_layer = reference_layer

    def execute (self):
        super().execute()

        # scale down the text layer until it doesn't overlap with the reference layer (e.g. card name overlapping with mana cost)
        scale_text_right_overlap(self.layer, self.reference_layer)

class ExpansionSymbolField (TextField):
    """
     * A TextField which represents a card's expansion symbol.
     * `layer`: Expansion symbol layer
     * `text_contents`: The symbol character
     * `rarity`: The clipping mask to enable (uncommon, rare, mythic)
     * `reference`: Reference layer to scale and center
     * `centered`: Whether to center horizontally, ex: Ixalan
    """
    def __init__ (self, layer, text_contents, rarity, reference, centered=False):
        super().__init__(layer, text_contents, psd.rgb_black())
        self.centered = centered
        self.rarity = rarity
        self.reference = reference
        if rarity in (con.rarity_bonus, con.rarity_special):
            self.rarity = con.rarity_mythic

    def execute (self):
        super().execute()

        # Size to fit reference?
        if cfg.auto_symbol_size:
            if self.centered: psd.frame_expansion_symbol(self.layer, self.reference, True)
            else: psd.frame_expansion_symbol(self.layer, self.reference, False)
        app.activeDocument.activeLayer = self.layer

        # Rarity above common?
        if self.rarity == con.rarity_common: psd.apply_stroke(cfg.symbol_stroke, psd.rgb_white())
        else:
            mask_layer = psd.getLayer(self.rarity, self.layer.parent)
            mask_layer.visible = True
            psd.apply_stroke(cfg.symbol_stroke, psd.rgb_black())
            psd.select_layer_pixels(self.layer)
            app.activeDocument.activeLayer = mask_layer
            psd.align_horizontal()
            psd.align_vertical()
            psd.clear_selection()

        # Fill in the expansion symbol?
        if cfg.fill_symbol:
            app.activeDocument.activeLayer = self.layer
            if self.rarity == con.rarity_common: psd.fill_expansion_symbol(self.reference, psd.rgb_white())
            else: psd.fill_expansion_symbol(self.reference)


class BasicFormattedTextField (TextField):
    """
     * A TextField where the contents contain some number of symbols which should be replaced with glyphs from the NDPMTG font.
     * For example, if the text contents for an instance of self class is "{2}{R}", formatting self text with NDPMTG would correctly
     * show the mana cost 2R with text contents "o2or" with characters being appropriately colored.
     * Doesn't support flavor text or centered text. For use with fields like mana costs and planeswalker abilities.
    """
    def execute (self):
        super().execute()

        # Format text
        app.activeDocument.activeLayer = self.layer
        italic_text = format_text.generate_italics(self.text_contents)
        format_text.format_text(self.text_contents, italic_text, -1, False)

class FormattedTextField (TextField):
    """
     * A TextField where the contents contain some number of symbols which should be replaced with glyphs from the NDPMTG font.
     * For example, if the text contents for an instance of self class is "{2}{R}", formatting self text with NDPMTG would correctly
     * show the mana cost 2R with text contents "o2or" with characters being appropriately colored.
     * The big boy version which supports centered text and flavor text. For use with card rules text.
    """
    def __init__ (self, layer, text_contents, text_color, flavor_text, is_centered=False):
        super().__init__(layer, text_contents, text_color)
        self.flavor_text = ""
        if flavor_text: self.flavor_text = flavor_text.replace("\n", "\r")
        self.is_centered = is_centered

    def execute (self):
        super().execute()

        # generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = format_text.generate_italics(self.text_contents)

        # Flavor text included?
        if len(self.flavor_text) > 1:
            # remove things between asterisks from flavor text if necessary
            flavor_text_split = self.flavor_text.split("*")
            if len(flavor_text_split) > 1:
                # asterisks present in flavor text
                for i in flavor_text_split:
                    # add the parts of the flavor text not between asterisks to italic_text
                    if i != "": italic_text.append(i)

                # reassemble flavorText without asterisks
                self.flavor_text = "".join(flavor_text_split)
            else: italic_text.append(self.flavor_text)
            flavor_index = len(self.text_contents)
        else: flavor_index = -1

        # Format text
        app.activeDocument.activeLayer = self.layer
        format_text.format_text(self.text_contents + "\r" + self.flavor_text, italic_text, flavor_index, self.is_centered)
        if self.is_centered: self.layer.textItem.justification = ps.Justification.Center

class FormattedTextArea (FormattedTextField):
    """
     * A FormattedTextField where the text is required to fit within a given area. An instance of self class will step down the font size
     * until the text fits within the reference layer's bounds (in 0.25 pt increments), then rasterise the text layer, and centre it vertically
     * with respect to the reference layer's pixels.
    """
    def __init__ (self, layer, text_contents, text_color, flavor_text, reference_layer, is_centered=False, fix_length=True):

        # Prepare for text being too long
        if len(text_contents) > 300 and fix_length:
            layer.textItem.size = (layer.textItem.size-0.5)
            layer.textItem.leading = (layer.textItem.leading-0.5)

        super().__init__(layer, text_contents, text_color, flavor_text, is_centered)
        self.reference_layer = reference_layer

    def execute (self):
        super().execute()
        if self.text_contents or self.flavor_text:
            if self.text_contents != "" or self.flavor_text != "":
                # resize the text until it fits into the reference layer
                scale_text_to_fit_reference(self.layer, self.reference_layer)

                # rasterise and centre vertically
                vertically_align_text(self.layer, self.reference_layer)

                if self.is_centered:
                    # ensure the layer is centered horizontally as well
                    psd.select_layer_pixels(self.reference_layer)
                    app.activeDocument.activeLayer = self.layer
                    psd.align_horizontal()
                    psd.clear_selection()

class CreatureFormattedTextArea (FormattedTextArea):
    """
     * A FormattedTextArea which also respects the bounds of creature card's power/toughness boxes. If the rasterised and centered text layer
     * overlaps with another specified reference layer (which should represent the bounds of the power/toughness box), the layer will be shifted
     * vertically by just enough to ensure that it doesn't overlap.
    """
    def __init__ (self, layer, text_contents, text_color, flavor_text, reference_layer, pt_reference_layer, pt_top_reference_layer, is_centered=False):
        super().__init__(layer, text_contents, text_color, flavor_text, reference_layer, is_centered)
        self.pt_reference_layer = pt_reference_layer
        self.pt_top_reference_layer = pt_top_reference_layer

    def execute (self):
        super().execute()

        # shift vertically if the text overlaps the PT box
        vertically_nudge_creature_text(self.layer, self.pt_reference_layer, self.pt_top_reference_layer)
