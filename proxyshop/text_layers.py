"""
TEXT LAYER MODULE
"""
import proxyshop.helpers as psd
from proxyshop.constants import con
from proxyshop.settings import cfg
from proxyshop import format_text as ft
from proxyshop.helpers import ps, app


"""
Text Layer Classes
"""


class TextField:
    """
    A generic TextField, which allows you to set a text layer's contents and text color.
    """
    def __init__(self, layer, contents = "", color = psd.rgb_black()):
        self.contents = contents.replace("\n", "\r")
        if color: self.text_color = color
        else: self.text_color = psd.get_text_layer_color(layer)
        self.layer = layer

    def execute(self):
        """
        Enables, fills, and colors the text item.
        """
        self.layer.visible = True
        self.layer.textItem.contents = self.contents
        self.layer.textItem.color = self.text_color


class ScaledTextField (TextField):
    """
    A TextField which automatically scales down its font size (in 0.25 pt increments) until
    its right bound no longer overlaps with a reference layer's left bound.
    """
    def __init__(self, layer, contents = "", color = None, reference = None):
        super().__init__(layer, contents, color)
        self.reference = reference

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        ft.scale_text_right_overlap(self.layer, self.reference)


class ExpansionSymbolField (TextField):
    """
     A TextField which represents a card's expansion symbol.
     @param layer: Expansion symbol layer
     @param contents: The symbol character
     * `rarity`: The clipping mask to enable (uncommon, rare, mythic)
     * `reference`: Reference layer to scale and center
     * `centered`: Whether to center horizontally, ex: Ixalan
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        rarity = "common",
        reference = None, centered = False
    ):
        super().__init__(layer, contents, color)
        self.centered = centered
        self.rarity = rarity
        self.reference = reference

        # Special mythic rarities
        if rarity in (con.rarity_bonus, con.rarity_special):
            self.rarity = con.rarity_mythic

    def execute (self):
        super().execute()

        # Size to fit reference?
        if cfg.auto_symbol_size:
            if self.centered: psd.frame_expansion_symbol(self.layer, self.reference, True)
            else: psd.frame_expansion_symbol(self.layer, self.reference)
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
    A TextField where the contents contain some number of symbols which should be replaced
    with glyphs from the NDPMTG font. For example, if the text contents for an instance of self
    class is "{2}{R}", formatting self text with NDPMTG would correctly show the mana cost 2R with
    text contents "o2or" with characters being appropriately colored. Doesn't support flavor text
    or centered text. For use with fields like mana costs and planeswalker abilities.
    """
    def execute(self):
        super().execute()

        # Format text
        app.activeDocument.activeLayer = self.layer
        italic_text = ft.generate_italics(self.contents)
        ft.format_text(self.contents, italic_text, -1, False)


class FormattedTextField (TextField):
    """
    A TextField where the contents contain some number of symbols which should be replaced
    with glyphs from the NDPMTG font. For example, if the text contents for an instance of
    self class is "{2}{R}", formatting self text with NDPMTG would correctly show the mana
    cost 2R with text contents "o2or" with characters being appropriately colored. The big
    boy version which supports centered text and flavor text. For use with card rules text.
    """
    def __init__(self, layer, contents = "", color = None, flavor_text = "", centered = False):
        super().__init__(layer, contents, color)
        self.flavor_text = flavor_text.replace("\n", "\r")
        self.centered = centered

    def execute(self):
        super().execute()

        # generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = ft.generate_italics(self.contents)

        # Flavor text included?
        if len(self.flavor_text) > 1:
            # remove things between asterisks from flavor text if necessary
            flavor_text_split = self.flavor_text.split("*")
            if len(flavor_text_split) > 1:
                # asterisks present in flavor text
                for i in flavor_text_split:
                    # add the parts of the flavor text not between asterisks to italic_text
                    if i != "": italic_text.append(i)

                # reassemble flavor text without asterisks
                self.flavor_text = "".join(flavor_text_split)
            else: italic_text.append(self.flavor_text)
            flavor_index = len(self.contents)
        else: flavor_index = -1

        # Format text
        app.activeDocument.activeLayer = self.layer
        ft.format_text(self.contents + "\r" + self.flavor_text, italic_text, flavor_index, self.centered)
        if self.centered: self.layer.textItem.justification = ps.Justification.Center


class FormattedTextArea (FormattedTextField):
    """
    A FormattedTextField where the text is required to fit within a given area.
    An instance of this class will step down the font size until the text fits
    within the reference layer's bounds, then rasterize the text layer, and
    center it vertically with respect to the reference layer's selection area.
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        flavor = "",
        reference = None,
        centered = False,
        fix_length = True
    ):
        super().__init__(layer, contents, color, flavor, centered)
        self.reference = reference

        # Prepare for text being too long
        if fix_length and len(contents) > 300:
            steps = int((len(contents)-200)/100)
            layer.textItem.size = layer.textItem.size - steps
            layer.textItem.leading = layer.textItem.leading - steps

    def execute(self):
        super().execute()
        if self.contents != "" or self.flavor_text != "":
            # Resize the text until it fits into the reference layer
            ft.scale_text_to_fit_reference(self.layer, self.reference)

            # Rasterize and centre vertically
            ft.vertically_align_text(self.layer, self.reference)

            if self.centered:
                # Ensure the layer is centered horizontally as well
                psd.select_layer_pixels(self.reference)
                app.activeDocument.activeLayer = self.layer
                psd.align_horizontal()
                psd.clear_selection()


class CreatureFormattedTextArea (FormattedTextArea):
    """
    FormattedTextArea which also respects the bounds of creature card's power/toughness boxes.
    If the rasterized and centered text layer overlaps with another specified reference layer
    (which should represent the bounds of the power/toughness box), the layer will be shifted
    vertically to ensure that it doesn't overlap.
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        flavor = "",
        reference = None,
        pt_reference = None,
        pt_top_reference = None,
        centered = False,
        fix_length = True
    ):
        super().__init__(layer, contents, color, flavor, reference, centered, fix_length)
        self.pt_reference = pt_reference
        self.pt_top_reference = pt_top_reference

    def execute(self):
        super().execute()

        # shift vertically if the text overlaps the PT box
        ft.vertically_nudge_creature_text(self.layer, self.pt_reference, self.pt_top_reference)
