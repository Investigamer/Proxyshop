"""
TEXT LAYER MODULE
"""
# Standard Library Imports
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

# Local Imports
from src.constants import con
from src.helpers.bounds import get_text_layer_bounds, get_layer_dimensions
from src.helpers.colors import get_text_layer_color, apply_color
from src.helpers.layers import select_layer_bounds
from src.helpers.position import position_between_layers, align_horizontal
from src.helpers.text import (
    get_text_scale_factor,
    remove_trailing_text, set_composer_single_line
)
from src.settings import cfg
from src import format_text as ft

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
Text Layer Classes
"""


class TextField:
    """
    A generic TextField, which allows you to set a text layer's contents and text color.
    @param layer: TextItem layer to insert contents.
    @param contents: Text contents to be inserted.
    @param color: Font color to use for this TextItem.
    @param kwargs: Optional keyword parameters.
    """
    def __init__(self, layer: ArtLayer, contents: str = "", **kwargs):
        # Mandatory attributes
        self.kwargs = kwargs
        self.layer = layer
        self.layer.visible = True
        self.contents = contents.replace("\n", "\r")

        # Change to English formatting if needed
        if self.layer.kind == LayerKind.TextLayer and cfg.force_english_formatting:
            self.layer.textItem.language = Language.EnglishUSA

    """
    PROPERTIES
    """

    @property
    def input(self) -> str:
        return self.contents

    @cached_property
    def reference(self) -> Optional[ArtLayer]:
        return self.kwargs.get('reference', None)

    @cached_property
    def color(self) -> SolidColor:
        return self.kwargs.get('color', get_text_layer_color(self.layer))

    @cached_property
    def docref(self) -> Document:
        return app.activeDocument

    """
    METHODS
    """

    def execute(self):
        """
        Executes all text actions.
        """
        self.layer.textItem.contents = self.input
        self.layer.textItem.color = self.color


class ScaledWidthTextField (TextField):
    """
    A TextField which automatically scales down its font size until the width of the
    layer is within the horizontal bound of a reference layer.
    """

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            ft.scale_text_to_fit_reference(self.layer, self.reference, height=False)


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


class FormattedTextField (TextField):
    """
    A utility class for packing in the required infrastructure to format text with action descriptors.
    """

    """
    PROPERTIES
    """

    @cached_property
    def text_details(self) -> dict:

        # Generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = ft.generate_italics(self.contents) if self.contents else []

        # Add flavor text to italics array
        flavor_text = self.flavor_text
        if self.flavor_text.count("*") >= 2:
            # Don't italicize text between asterisk
            flavor_text_split = self.flavor_text.split("*")
            italic_text.extend([v for i, v in enumerate(flavor_text_split) if not i % 2 and not v == ''])
            flavor_text = ''.join(flavor_text_split)
        elif self.flavor_text:
            # Regular flavor text
            italic_text.append(self.flavor_text)

        # Locate symbols and update the input string
        ret = ft.locate_symbols(self.contents)
        input_string = f"{ret['input_string']}\r{flavor_text}" if self.contents else flavor_text

        # Locate italics text indices
        italics_indices = ft.locate_italics(input_string, italic_text)

        return {
            'input_string': input_string,
            'symbol_indices': ret['symbol_indices'],
            'italics_indices': italics_indices,
            'rules_text': ret['input_string'],
            'flavor_text': flavor_text,
        }

    @property
    def italics_indices(self) -> list[dict]:
        return self.text_details['italics_indices']

    @property
    def symbol_indices(self) -> list[dict]:
        return self.text_details['symbol_indices']

    @property
    def input(self) -> str:
        return self.text_details['input_string']

    @property
    def flavor_text_updated(self) -> str:
        return self.text_details['flavor_text']

    @property
    def rules_text_updated(self) -> str:
        return self.text_details['rules_text']

    @cached_property
    def flavor_text(self) -> str:
        return self.kwargs.get('flavor', '').replace('\n', '\r')

    @property
    def divider(self) -> Optional[ArtLayer]:
        # Default to None unless overridden
        return

    @cached_property
    def contents_centered(self) -> bool:
        return self.kwargs.get('centered', False)

    @cached_property
    def flavor_centered(self) -> bool:
        return self.kwargs.get('flavor_centered', self.contents_centered)

    @cached_property
    def line_break_lead(self) -> Union[int, float]:
        return self.kwargs.get(
            'line_break_lead',
            0 if self.contents_centered else con.line_break_lead
        )

    @cached_property
    def flavor_text_lead(self) -> Union[int, float]:
        # Lead with divider
        if self.divider:
            return self.kwargs.get('flavor_text_lead_divider', con.flavor_text_lead_divider)
        # Lead without divider
        return self.kwargs.get('flavor_text_lead', con.flavor_text_lead)

    @cached_property
    def flavor_index(self) -> int:
        return len(self.contents) if len(self.flavor_text) > 0 else -1

    @cached_property
    def quote_index(self) -> int:
        return self.input.find("\r", self.flavor_index + 3) if self.flavor_index >= 0 else -1

    @cached_property
    def bold_rules_text(self) -> bool:
        return self.kwargs.get('bold_rules_text', False)

    @cached_property
    def right_align_quote(self) -> bool:
        return self.kwargs.get('right_align_quote', False)

    @cached_property
    def flavor_color(self) -> Optional[SolidColor]:
        return self.kwargs.get('flavor_color', None)

    @cached_property
    def font_size(self) -> float:
        if font_size := self.kwargs.get('font_size'):
            return font_size * get_text_scale_factor(self.layer)
        return self.layer.textItem.size * get_text_scale_factor(self.layer)

    """
    METHODS
    """

    def format_text(self):
        """
        Inserts the given string into the active layer and formats it according to defined parameters with symbols
        from the NDPMTG font.
        """
        # Set up main descriptors and lists
        main_descriptor = ActionDescriptor()
        style_list = ActionList()
        main_list = ActionList()

        # Descriptor ID's
        idTo = sID("to")
        size = sID("size")
        idFrom = sID("from")
        leading = sID("leading")
        fontName = sID("fontName")
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
        main_style.putString(fontPostScriptName, con.font_rules_text)  # MPlantin default
        main_style.putString(fontName, con.font_rules_text)  # MPlantin default
        main_style.putUnitDouble(size, pointsUnit, self.font_size)
        apply_color(main_style, self.color)
        main_style.putBoolean(autoLeading, False)
        main_style.putUnitDouble(leading, pointsUnit, self.font_size)
        main_range.putObject(textStyle, textStyle, main_style)
        main_list.putObject(styleRange, main_range)

        # Bold the contents if necessary
        if self.bold_rules_text and self.flavor_index != 0:
            bold_range = ActionDescriptor()
            bold_style = ActionDescriptor()
            contents_index = len(self.input) - 1 if self.flavor_index < 0 else self.flavor_index - 1
            bold_range.putInteger(idFrom, 0)  # bold start index
            bold_range.putInteger(idTo, contents_index)  # bold end index
            bold_style.putString(fontPostScriptName, con.font_rules_text_bold)
            bold_style.putString(fontName, con.font_rules_text_bold)
            bold_style.putUnitDouble(size, pointsUnit, self.font_size)
            apply_color(bold_style, self.color)
            bold_style.putBoolean(autoLeading, False)
            bold_style.putUnitDouble(leading, pointsUnit, self.font_size)
            bold_range.putObject(textStyle, textStyle, bold_style)
            main_list.putObject(styleRange, bold_range)

        # Italicize text from our italics indices
        for i in self.italics_indices:
            italic_range = ActionDescriptor()
            italic_style = ActionDescriptor()
            italic_range.putInteger(idFrom, i['start_index'])  # italics start index
            italic_range.putInteger(idTo, i['end_index'])  # italics end index
            italic_style.putString(fontPostScriptName, con.font_rules_text_italic)
            italic_style.putString(fontName, con.font_rules_text_italic)
            italic_style.putUnitDouble(size, pointsUnit, self.font_size)
            apply_color(italic_style, self.color)
            italic_style.putBoolean(autoLeading, False)
            italic_style.putUnitDouble(leading, pointsUnit, self.font_size)
            italic_range.putObject(textStyle, textStyle, italic_style)
            main_list.putObject(styleRange, italic_range)

        # Format each symbol correctly
        for symbol_index in self.symbol_indices:
            ft.format_symbol(
                action_list=main_list,
                symbol_index=symbol_index['index'],
                symbol_colors=symbol_index['colors'],
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
            desc142.putUnitDouble(firstLineIndent, pointsUnit, -con.modal_indent)  # negative modal indent
            desc142.putUnitDouble(startIndent, pointsUnit, con.modal_indent)  # modal indent
            desc142.putUnitDouble(spaceBefore, pointsUnit, 1)
            desc142.putUnitDouble(spaceAfter, pointsUnit, 0)
            desc143.putString(fontPostScriptName, con.font_mana)  # NDPMTG default
            desc143.putString(fontName, con.font_rules_text)  # MPlantin default
            desc143.putUnitDouble(size, pointsUnit, 12)
            desc143.putBoolean(autoLeading, False)
            desc142.putObject(sID("defaultStyle"), textStyle, desc143)
            desc141.putObject(paragraphStyle, paragraphStyle, desc142)
            style_list.putObject(paragraphStyleRange, desc141)
            main_descriptor.putList(paragraphStyleRange, style_list)

        # Flavor text actions
        if self.flavor_index >= 0:
            # Add linebreak spacing between rules and flavor text
            desc141.putInteger(idFrom, self.flavor_index + 3)
            desc141.putInteger(idTo, self.flavor_index + 4)
            desc142.putUnitDouble(firstLineIndent, pointsUnit, 0)
            desc142.putUnitDouble(sID("impliedFirstLineIndent"), pointsUnit, 0)
            desc142.putUnitDouble(startIndent, pointsUnit, 0)
            desc142.putUnitDouble(sID("impliedStartIndent"), pointsUnit, 0)
            desc142.putUnitDouble(spaceBefore, pointsUnit, self.flavor_text_lead)  # Space between rules and flavor text
            desc141.putObject(paragraphStyle, paragraphStyle, desc142)
            style_list.putObject(paragraphStyleRange, desc141)
            main_descriptor.putList(paragraphStyleRange, style_list)

            # Adjust flavor text color
            if self.flavor_color:
                colored_range = ActionList()
                colored_style = ActionDescriptor()
                desc145 = ActionDescriptor()
                colored_style.PutInteger(sID("from"), self.flavor_index)
                colored_style.PutInteger(sID("to"), len(self.input))
                desc145.putString(fontPostScriptName, con.font_rules_text_italic)  # MPlantin italic default
                desc145.putString(fontName, con.font_rules_text_italic)  # MPlantin italic default
                desc145.putUnitDouble(size, pointsUnit, self.font_size)
                desc145.putBoolean(autoLeading, False)
                desc145.putUnitDouble(leading, pointsUnit, self.font_size)
                apply_color(desc145, self.flavor_color)
                colored_style.PutObject(sID("textStyle"), sID("textStyle"), desc145)
                colored_range.PutObject(sID("textStyleRange"), colored_style)
                main_descriptor.putList(sID("textStyleRange"), colored_range)

        # Quote actions flavor text
        if self.quote_index >= 0:
            # Adjust line break spacing if there's a line break in the flavor text
            desc141.putInteger(idFrom, self.quote_index + 3)
            desc141.putInteger(idTo, len(self.input))
            desc142.putUnitDouble(spaceBefore, pointsUnit, 0)
            desc141.putObject(paragraphStyle, paragraphStyle, desc142)
            style_list.putObject(paragraphStyleRange, desc141)

            # Optional, align quote credit to right
            if self.right_align_quote and self.input.find('"\r—') >= 0:
                # Get start and ending index of quotation credit
                index_start = self.input.find('"\r—') + 2
                index_end = len(self.input) - 1

                # Align this part, disable justification reset
                ft.align_formatted_text_right(style_list, index_start, index_end)

            # Add quote actions to primary action
            main_descriptor.putList(paragraphStyleRange, style_list)

        # Push changes to text layer
        textLayer = sID("textLayer")
        ref101 = ActionReference()
        desc119 = ActionDescriptor()
        ref101.putEnumerated(textLayer, sID("ordinal"), sID("targetEnum"))
        desc119.putReference(sID("target"), ref101)
        desc119.putObject(idTo, textLayer, main_descriptor)
        app.executeAction(sID("set"), desc119, NO_DIALOG)

        # Disable hyphenation and set text composer
        self.docref.activeLayer.textItem.hyphenation = False
        set_composer_single_line(self.layer)

    def execute(self):
        super().execute()

        # Format text
        self.docref.activeLayer = self.layer
        self.format_text()
        if self.contents_centered:
            self.layer.textItem.justification = Justification.Center


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
        if (divider := self.kwargs.get('divider')) and all([self.flavor_text, self.contents, cfg.flavor_divider]):
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
        remove_trailing_text(rules, len(self.rules_text_updated) + 1)
        rules.rasterize(RasterizeType.EntireLayer)
        select_layer_bounds(rules)
        self.docref.activeLayer = flavor
        self.docref.selection.expand(2)
        self.docref.selection.clear()

        # Move flavor text to bottom, then position divider
        flavor.translate(0, get_text_layer_bounds(self.layer)[3] - flavor.bounds[3])
        position_between_layers(self.divider, rules, flavor)
        self.docref.selection.deselect()
        flavor.remove()
        rules.remove()

    def execute(self):

        # Skip if both are empty
        if not self.contents and not self.flavor_text:
            self.layer.visible = False
            return

        # Fix height overflow before formatting text
        if self.fix_overflow_height and self.reference:
            contents = self.contents if not self.flavor_text else str(self.contents + "\r" + self.flavor_text)
            self.layer.textItem.contents = contents
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
