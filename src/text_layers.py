"""
* Text Layer Classes
"""
# Standard Library Imports
from contextlib import suppress
from functools import cached_property
from typing import Optional, Union, Callable

# Third Party Imports
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    ActionList,
    DialogModes,
    LayerKind,
    SolidColor,
    Language,
    Justification,
    RasterizeType
)
from photoshop.api._document import Document
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api.text_item import TextItem

# Local Imports
from src import APP, CFG, CON
from src.enums.mtg import CardFonts
from src import format_text as ft
from src.format_text import CardSymbolString, CardItalicString
from src.helpers.bounds import get_layer_dimensions
from src.helpers.colors import apply_color, get_text_item_color
from src.helpers.layers import select_layer_bounds
from src.helpers.position import position_between_layers, align_horizontal
from src.helpers.text import get_text_scale_factor, remove_trailing_text

# QOL Definitions
sID = APP.stringIDToTypeID
cID = APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Text Layer Classes
"""


class TextField:
    """
    A generic TextField, which allows you to set a text layer's contents and text color.
    @param layer: TextItem layer to insert contents.
    @param contents: Text contents to be inserted.
    @param color: Font color to use for this TextItem.
    @param kwargs: Optional keyword parameters.
    """
    FONT = CardFonts.TITLES
    FONT_ITALIC = CardFonts.RULES_ITALIC
    FONT_BOLD = CardFonts.RULES_BOLD

    def __init__(self, layer: ArtLayer, contents: str = "", **kwargs):
        # Mandatory attributes
        self._kwargs = kwargs
        self._layer = layer
        self.layer.visible = True
        self.contents = contents.replace("\n", "\r")

        # Change to English formatting if needed
        if self.is_text_layer and CFG.force_english_formatting:
            self.TI.language = Language.EnglishUSA

    """
    * Keyword Arguments
    """

    @cached_property
    def kwargs(self) -> dict:
        """Contains optional parameters to modify text formatting behavior."""
        return self._kwargs

    @cached_property
    def kw_color(self) -> Optional[SolidColor]:
        """Color to apply to the TextItem."""
        return self.kwargs.get('color')

    @cached_property
    def kw_font(self) -> Optional[str]:
        """Font to apply to the root TextItem."""
        return self.kwargs.get('font')

    @cached_property
    def kw_font_mana(self) -> Optional[str]:
        """Font to apply to any mana symbols in the TextItem."""
        return self.kwargs.get('font_mana')

    @cached_property
    def kw_font_italic(self) -> Optional[str]:
        """Font to apply to any italicized text in the TextItem."""
        return self.kwargs.get('font_italic')

    @cached_property
    def kw_font_bold(self) -> Optional[str]:
        """Font to apply to any bold text in the TextItem."""
        return self.kwargs.get('font_bold')

    """
    * Checks
    """

    @cached_property
    def is_text_layer(self) -> bool:
        """Checks if the layer provided is a TextLayer."""
        return bool(self.layer.kind == LayerKind.TextLayer)

    """
    * Core Objects
    """

    @cached_property
    def docref(self) -> Document:
        """The currently active Photoshop document."""
        return APP.activeDocument

    @property
    def layer(self) -> ArtLayer:
        """ArtLayer containing the TextItem."""
        return self._layer

    @cached_property
    def TI(self) -> TextItem:
        """The TextItem object within the ArtLayer."""
        return self.layer.textItem

    @cached_property
    def reference(self) -> Optional[ArtLayer]:
        """A reference layer, typically used for scaling the TextItem."""
        return self.kwargs.get('reference', None)

    @property
    def input(self) -> str:
        """Raw contents provided to fill the TextItem."""
        return self.contents

    @cached_property
    def color(self) -> SolidColor:
        """A SolidColor object provided, or fallback on current TextItem color."""
        return self.kw_color or get_text_item_color(self.TI)

    @cached_property
    def font(self) -> str:
        """Font provided, or fallback on global constant."""
        return self.kw_font or CON.font_title

    """
    * Methods
    """

    def validate(self):
        """Ensure the Text Layer provided is valid."""
        if self.is_text_layer:
            return True
        with suppress(Exception):
            print(self.__class__.__name__)
            print(f'Invalid layer provided: {self.layer}')
            self.layer.visible = False
        return False

    def execute(self):
        """Executes all text actions."""
        # Update TextItem contents
        self.TI.contents = self.input

        # Update color if it was provided manually
        if self.kw_color:
            self.TI.color = self.color

        # Update font manually if mismatch detected
        if self.font != self.FONT:
            self.TI.font = self.font


class ScaledTextField (TextField):
    """
    A TextField which automatically scales down its font size until the right bound
    no longer overlaps with a reference layer's left bound.
    """
    @cached_property
    def flip_scale(self) -> bool:
        return self.kwargs.get('flip_scale', False)

    @cached_property
    def scale_action(self) -> Callable:
        if self.flip_scale:
            return ft.scale_text_left_overlap
        return ft.scale_text_right_overlap

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            self.scale_action(self.layer, self.reference)


class ScaledWidthTextField (TextField):
    """
    A TextField which automatically scales down its font size until the width of the
    layer is within the horizontal bound of a reference layer.
    """
    FONT = CardFonts.RULES

    @cached_property
    def font(self) -> str:
        """Font provided, or fallback on global constant."""
        return self.kw_font or CON.font_rules_text

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            ft.scale_text_to_fit_reference(self.layer, self.reference, height=False)


class FormattedTextField (TextField):
    """
    A utility class for packing in the required infrastructure to format text with action descriptors.
    """
    FONT = CardFonts.RULES

    """
    * Core Text Details
    """

    @cached_property
    def text_details(self) -> dict:

        # Generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = ft.generate_italics(self.contents) if self.contents else []

        # Add flavor text to italics array
        flavor = self.flavor_text
        if self.flavor_text.count("*") >= 2:
            # Don't italicize text between asterisk
            flavor_text_split = self.flavor_text.split("*")
            italic_text.extend([v for i, v in enumerate(flavor_text_split) if not i % 2 and not v == ''])
            flavor = ''.join(flavor_text_split)
        elif self.flavor_text:
            # Regular flavor text
            italic_text.append(self.flavor_text)

        # Locate symbols and update the rules string
        rules, symbols = ft.locate_symbols(self.contents)

        # Create the new input string
        input_str = f'{rules}\r{flavor}' if rules and flavor else (
            rules if rules else flavor)

        # Locate italics text indices
        italicized = ft.locate_italics(input_str, italic_text)

        return {
            'symbol_indices': symbols, 'italics_indices': italicized,
            'rules_text': rules, 'flavor_text': flavor,
            'input_string': input_str
        }

    @cached_property
    def italics_indices(self) -> CardItalicString:
        return self.text_details['italics_indices']

    @cached_property
    def symbol_indices(self) -> CardSymbolString:
        return self.text_details['symbol_indices']

    @cached_property
    def input(self) -> str:
        return self.text_details['input_string']

    @property
    def divider(self) -> Optional[ArtLayer]:
        # Default to None unless overridden
        return

    """
    * Rules Text and Indexes
    """

    @cached_property
    def rules_text_updated(self) -> str:
        return self.text_details['rules_text']

    @cached_property
    def rules_text_range(self) -> Optional[tuple[int, int]]:
        if not self.rules_text_updated:
            return
        return 0, len(self.rules_text_updated)

    @cached_property
    def rules_start(self) -> int:
        if self.rules_text_range:
            return self.rules_text_range[0]
        return -1

    @cached_property
    def rules_end(self) -> int:
        if self.rules_text_range:
            return self.rules_text_range[1]
        return -1

    """
    * Flavor Text and Indexes
    """

    @cached_property
    def flavor_text(self) -> str:
        return self.kwargs.get('flavor', '').replace('\n', '\r')

    @cached_property
    def flavor_text_updated(self) -> str:
        return self.text_details['flavor_text']

    @cached_property
    def flavor_text_range(self) -> Optional[tuple[int, int]]:
        if not self.flavor_text_updated:
            return
        total = len(self.input)
        return total - len(self.flavor_text_updated), total

    @cached_property
    def flavor_start(self) -> int:
        if self.flavor_text_range:
            return self.flavor_text_range[0]
        return -1

    @cached_property
    def flavor_end(self) -> int:
        if self.flavor_text_range:
            return self.flavor_text_range[1]
        return -1

    @cached_property
    def quote_index(self) -> int:
        if self.flavor_text_range:
            return self.input.find("\r", self.flavor_start + 3)
        return -1

    """
    * Colors
    """

    @cached_property
    def flavor_color(self) -> Optional[SolidColor]:
        """If defined separately, `color` is effectively the `rules_color`."""
        return self.kwargs.get('flavor_color')

    """
    * Fonts
    """

    @cached_property
    def font(self) -> str:
        """Font provided, or fallback on global constant."""
        return self.kw_font or CON.font_rules_text

    @cached_property
    def font_mana(self) -> str:
        """Mana font provided, or fallback on global constant."""
        return self.kw_font_mana or CON.font_mana

    @cached_property
    def font_italic(self) -> str:
        """Italic font provided, or fallback on global constant."""
        return self.kw_font_italic or CON.font_rules_text_italic

    @cached_property
    def font_bold(self) -> str:
        """Bold font provided, or fallback on global constant."""
        return self.kw_font_bold or CON.font_rules_text_bold

    """
    * Text Formatting Properties
    """

    @cached_property
    def line_break_lead(self) -> Union[int, float]:
        """Leading space before linebreaks."""
        return self.kwargs.get(
            'line_break_lead',
            0 if self.contents_centered else CON.line_break_lead
        )

    @cached_property
    def flavor_text_lead(self) -> Union[int, float]:
        """Leading space before linebreak separating rules and flavor text. Increased if divider is present."""
        if self.divider:
            return self.kwargs.get('flavor_text_lead_divider', CON.flavor_text_lead_divider)
        return self.kwargs.get('flavor_text_lead', CON.flavor_text_lead)

    """
    * Optional Properties
    """

    @cached_property
    def contents_centered(self) -> bool:
        return self.kwargs.get('centered', False)

    @cached_property
    def flavor_centered(self) -> bool:
        return self.kwargs.get('flavor_centered', self.contents_centered)

    @cached_property
    def bold_rules_text(self) -> bool:
        return self.kwargs.get('bold_rules_text', False)

    @cached_property
    def right_align_quote(self) -> bool:
        return self.kwargs.get('right_align_quote', False)

    @cached_property
    def font_size(self) -> float:
        if font_size := self.kwargs.get('font_size'):
            return font_size * get_text_scale_factor(self.layer)
        return self.TI.size * get_text_scale_factor(self.layer)

    """
    * Methods
    """

    def format_text(self):
        """Inserts rules and flavor text and formats it based on the defined mana
        symbols, italics text indices, and other predefined properties."""

        # Set up main descriptors and lists
        main_descriptor = ActionDescriptor()
        style_list = ActionList()
        main_list = ActionList()

        # Descriptor ID's
        idTo = sID("to")
        size = sID("size")
        idFrom = sID("from")
        leading = sID("leading")
        textStyle = sID("textStyle")
        pointsUnit = sID("pointsUnit")
        spaceAfter = sID("spaceAfter")
        autoLeading = sID("autoLeading")
        startIndent = sID("startIndent")
        spaceBefore = sID("spaceBefore")
        leadingType = sID("leadingType")
        styleRange = sID("textStyleRange")
        paragraphStyle = sID("paragraphStyle")
        firstLineIndent = sID("firstLineIndent")
        fontPostScriptName = sID("fontPostScriptName")
        paragraphStyleRange = sID("paragraphStyleRange")

        # Spin up the text insertion action
        main_style = ActionDescriptor()
        main_range = ActionDescriptor()
        main_descriptor.putString(sID("textKey"), self.input)
        main_range.putInteger(idFrom, 0)
        main_range.putInteger(idTo, len(self.input))
        main_style.putString(fontPostScriptName, self.font)
        main_style.putUnitDouble(size, pointsUnit, self.font_size)
        apply_color(main_style, self.color)
        main_style.putBoolean(autoLeading, False)
        main_style.putUnitDouble(leading, pointsUnit, self.font_size)
        main_range.putObject(textStyle, textStyle, main_style)
        main_list.putObject(styleRange, main_range)

        # Bold the contents if necessary
        if self.rules_text_updated and self.bold_rules_text:
            bold_range = ActionDescriptor()
            bold_style = ActionDescriptor()
            bold_range.putInteger(idFrom, self.rules_start)  # bold start index
            bold_range.putInteger(idTo, self.rules_end)  # bold end index
            bold_style.putString(fontPostScriptName, self.font_bold)
            bold_style.putUnitDouble(size, pointsUnit, self.font_size)
            apply_color(bold_style, self.color)
            bold_style.putBoolean(autoLeading, False)
            bold_style.putUnitDouble(leading, pointsUnit, self.font_size)
            bold_range.putObject(textStyle, textStyle, bold_style)
            main_list.putObject(styleRange, bold_range)

        # Italicize text from our italics indices
        for start, end in self.italics_indices:
            italic_range = ActionDescriptor()
            italic_style = ActionDescriptor()
            italic_range.putInteger(idFrom, start)  # italics start index
            italic_range.putInteger(idTo, end)  # italics end index
            italic_style.putString(fontPostScriptName, self.font_italic)
            italic_style.putUnitDouble(size, pointsUnit, self.font_size)
            apply_color(italic_style, self.color)
            italic_style.putBoolean(autoLeading, False)
            italic_style.putUnitDouble(leading, pointsUnit, self.font_size)
            italic_range.putObject(textStyle, textStyle, italic_style)
            main_list.putObject(styleRange, italic_range)

        # Format each symbol correctly
        for index, colors in self.symbol_indices:
            ft.format_symbol(
                action_list=main_list,
                symbol_index=index,
                symbol_colors=colors,
                font_size=self.font_size,
            )

        # Insert actions for bold, italics, and symbol formatting
        main_descriptor.putList(styleRange, main_list)

        # Paragraph formatting
        desc141 = ActionDescriptor()
        desc142 = ActionDescriptor()
        desc141.putInteger(idFrom, 0)
        desc141.putInteger(idTo, len(self.input))  # input string length
        desc142.putUnitDouble(firstLineIndent, pointsUnit, 0)
        desc142.putUnitDouble(startIndent, pointsUnit, 0)
        desc142.putUnitDouble(sID("endIndent"), pointsUnit, 0)
        desc142.putUnitDouble(spaceBefore, pointsUnit, self.line_break_lead)
        desc142.putUnitDouble(spaceAfter, pointsUnit, 0)
        desc142.putInteger(sID("dropCapMultiplier"), 1)
        desc142.putEnumerated(leadingType, leadingType, sID("leadingBelow"))

        # Adjust formatting for modal card with bullet points
        if "\u2022" in self.input:
            desc143 = ActionDescriptor()
            startIndexBullet = self.input.find("\u2022")
            endIndexBullet = self.input.rindex("\u2022")
            desc141.putInteger(idFrom, startIndexBullet)
            desc141.putInteger(idTo, endIndexBullet + 1)
            desc142.putUnitDouble(firstLineIndent, pointsUnit, -CON.modal_indent)  # negative modal indent
            desc142.putUnitDouble(startIndent, pointsUnit, CON.modal_indent)  # modal indent
            desc142.putUnitDouble(spaceBefore, pointsUnit, 1)
            desc142.putUnitDouble(spaceAfter, pointsUnit, 0)
            desc143.putString(fontPostScriptName, self.font_mana)  # NDPMTG default
            desc143.putUnitDouble(size, pointsUnit, 12)
            desc143.putBoolean(autoLeading, False)
            desc142.putObject(sID("defaultStyle"), textStyle, desc143)
            desc141.putObject(paragraphStyle, paragraphStyle, desc142)
            style_list.putObject(paragraphStyleRange, desc141)
            main_descriptor.putList(paragraphStyleRange, style_list)

        # Flavor text actions
        if self.flavor_start >= 0:
            # Add linebreak spacing between rules and flavor text
            desc141.putInteger(idFrom, self.flavor_start + 3)
            desc141.putInteger(idTo, self.flavor_start + 4)
            [desc142.putUnitDouble(n, pointsUnit, 0) for n in [
                firstLineIndent, sID("impliedFirstLineIndent"), startIndent, sID("impliedStartIndent")]]
            desc142.putUnitDouble(spaceBefore, pointsUnit, self.flavor_text_lead)
            desc141.putObject(paragraphStyle, paragraphStyle, desc142)
            style_list.putObject(paragraphStyleRange, desc141)
            main_descriptor.putList(paragraphStyleRange, style_list)

            # Adjust flavor text color
            if self.flavor_color:
                colored_range = ActionList()
                colored_style = ActionDescriptor()
                desc145 = ActionDescriptor()
                colored_style.PutInteger(idFrom, self.flavor_start)
                colored_style.PutInteger(idTo, self.flavor_end)
                desc145.putString(fontPostScriptName, self.font_italic)  # MPlantin italic default
                desc145.putUnitDouble(size, pointsUnit, self.font_size)
                desc145.putBoolean(autoLeading, False)
                desc145.putUnitDouble(leading, pointsUnit, self.font_size)
                apply_color(desc145, self.flavor_color)
                colored_style.PutObject(textStyle, textStyle, desc145)
                colored_range.PutObject(styleRange, colored_style)
                main_descriptor.putList(styleRange, colored_range)

        # Quote actions flavor text
        if self.quote_index >= 0:
            # Adjust line break spacing if there's a line break in the flavor text
            desc141.putInteger(idFrom, self.quote_index + 3)
            desc141.putInteger(idTo, len(self.input))
            desc142.putUnitDouble(spaceBefore, pointsUnit, 0)
            desc141.putObject(paragraphStyle, paragraphStyle, desc142)
            style_list.putObject(paragraphStyleRange, desc141)

            # Optional, align quote credit to right
            if self.right_align_quote and '"\r—' in self.flavor_text_updated:
                ft.align_formatted_text_right(
                    action_list=style_list,
                    start=self.input.find('"\r—') + 2,
                    end=self.flavor_end)

            # Add quote actions to primary action
            main_descriptor.putList(paragraphStyleRange, style_list)

        # Push changes to text layer
        textLayer = sID("textLayer")
        ref101 = ActionReference()
        desc119 = ActionDescriptor()
        ref101.putEnumerated(textLayer, sID("ordinal"), sID("targetEnum"))
        desc119.putReference(sID("target"), ref101)
        desc119.putObject(idTo, textLayer, main_descriptor)
        APP.executeAction(sID("set"), desc119, NO_DIALOG)

        # Disable hyphenation and set text composer
        self.docref.activeLayer.textItem.hyphenation = False

    def execute(self):
        super().execute()

        # Format text
        self.docref.activeLayer = self.layer
        self.format_text()
        if self.contents_centered:
            self.TI.justification = Justification.Center


class FormattedTextArea (FormattedTextField):
    """
    A FormattedTextField where the text is required to fit within a given area.
    An instance of this class will step down the font size until the text fits
    within the reference layer's bounds, then rasterize the text layer, and
    center it vertically with respect to the reference layer's selection area.
    """

    """
    PROPERTIES
    """

    @cached_property
    def divider(self) -> Optional[Union[ArtLayer, LayerSet]]:
        if (divider := self.kwargs.get('divider')) and all([self.flavor_text, self.contents, CFG.flavor_divider]):
            divider.visible = True
            return divider
        return

    @cached_property
    def scale_height(self) -> bool:
        # Scale text to fit reference height (Default: True)
        if scale_height := self.kwargs.get('scale_height'):
            return scale_height
        return True

    @cached_property
    def scale_width(self) -> bool:
        # Scale text to fit reference width (Default: False)
        if scale_width := self.kwargs.get('scale_width'):
            return scale_width
        return False

    @cached_property
    def fix_overflow_width(self) -> bool:
        # Scale text to fit bounding box width (Default: False)
        if fix_overflow_width := self.kwargs.get('fix_overflow_width'):
            return fix_overflow_width
        return True

    @cached_property
    def fix_overflow_height(self) -> bool:
        # Scale text to fit bounding box height (Default: If overflow the bounds)
        if len(self.contents + self.flavor_text) > 280:
            return True
        if fix_overflow_height := self.kwargs.get('fix_overflow_height'):
            return fix_overflow_height
        return False

    """
    METHODS
    """

    def insert_divider(self):
        """
        Inserts and correctly positions flavor text divider.
        """
        # Create a reference layer with no effects
        flavor = self.layer.duplicate()
        rules = flavor.duplicate()
        flavor.rasterize(RasterizeType.EntireLayer)
        remove_trailing_text(rules, self.flavor_start)
        select_layer_bounds(rules)
        self.docref.activeLayer = flavor
        self.docref.selection.expand(2)
        self.docref.selection.clear()

        # Move flavor text to bottom, then position divider
        flavor.translate(0, self.layer.bounds[3] - flavor.bounds[3])
        position_between_layers(self.divider, rules, flavor)
        self.docref.selection.deselect()
        flavor.remove()
        rules.remove()

    def execute(self):

        # Skip if both are empty
        if not any([self.contents, self.flavor_text]):
            self.layer.visible = False
            return

        # Fix height overflow before formatting text
        if self.fix_overflow_height and self.reference:
            contents = self.contents if not self.flavor_text else str(
                self.contents + "\r" + self.flavor_text)
            self.TI.contents = contents
            ft.scale_text_to_fit_reference(
                self.layer, int(get_layer_dimensions(self.reference)['height']*1.01)
            )

        # Execute text formatting
        super().execute()

        # Resize the text until it fits the reference vertically
        if self.scale_height:
            ft.scale_text_to_fit_reference(self.layer, self.reference)

        # Resize the text until it fits the reference horizontally
        if self.scale_width:
            ft.scale_text_to_fit_reference(self.layer, self.reference, height=False, step=0.2)

        # Resize the text until it fits the TextLayer bounding box
        if self.fix_overflow_width:
            ft.scale_text_to_fit_textbox(self.layer)

        # Ensure the layer is centered vertically
        ft.vertically_align_text(self.layer, self.reference)

        # Ensure the layer is centered horizontally if needed
        if self.contents_centered and self.flavor_centered:
            align_horizontal(self.layer, self.reference)

        # Insert flavor divider if needed
        if self.divider:
            self.insert_divider()


class CreatureFormattedTextArea (FormattedTextArea):
    """
    FormattedTextArea which also respects the bounds of creature card's power/toughness boxes.
    If the rasterized and centered text layer overlaps with another specified reference layer
    (which should represent the bounds of the power/toughness box), the layer will be shifted
    vertically to ensure that it doesn't overlap.
    """

    """
    PROPERTIES
    """

    @cached_property
    def pt_reference(self) -> Optional[ArtLayer]:
        return self.kwargs.get('pt_reference', None)

    @cached_property
    def pt_top_reference(self) -> Optional[ArtLayer]:
        return self.kwargs.get('pt_top_reference', None)

    """
    METHODS
    """

    def execute(self):
        super().execute()

        # Shift vertically if the text overlaps the PT box
        if self.pt_reference and self.pt_top_reference:
            delta = ft.vertically_nudge_creature_text(self.layer, self.pt_reference, self.pt_top_reference)
            # Shift the divider as well
            if delta < 0 and self.divider:
                self.divider.translate(0, delta)


"""
* Named Utility Child Classes
"""


class CardName(TextItem):
    FONT = CardFonts.TITLES


class CardManaCost(FormattedTextField):
    FONT = CardFonts.MANA


class CardTypeLine(ScaledTextField):
    FONT = CardFonts.TITLES


class CardRules(FormattedTextArea):
    FONT = CardFonts.RULES


class CardRulesCreature(CreatureFormattedTextArea):
    FONT = CardFonts.RULES


class CardPowerToughness(TextField):
    FONT = CardFonts.PT


"""
* Text Item Type
"""

FormattedTextLayer = Union[
    TextField,
    ScaledTextField,
    FormattedTextArea,
    FormattedTextField,
    ScaledWidthTextField,
    CreatureFormattedTextArea
]
