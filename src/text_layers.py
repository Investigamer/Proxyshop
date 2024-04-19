"""
* Text Layer Classes
"""
# Standard Library Imports
from contextlib import suppress
from functools import cached_property
from typing import Optional, Union

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
    RasterizeType)
from photoshop.api._document import Document
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api._selection import Selection
from photoshop.api.text_item import TextItem

# Local Imports
from src import APP, CFG, CON, CONSOLE
from src.cards import generate_italics, locate_symbols, locate_italics, CardItalicString, CardSymbolString
from src.enums.mtg import CardFonts, ColorObject
from src.helpers import select_layer
from src.helpers.bounds import get_layer_dimensions, LayerDimensions, get_layer_width
from src.helpers.colors import apply_color, get_text_item_color
from src.helpers.position import position_between_layers, clear_reference_vertical
from src.helpers.selection import select_layer_bounds
from src.helpers.text import (
    get_text_scale_factor,
    remove_trailing_text,
    scale_text_to_width_textbox,
    scale_text_to_width,
    scale_text_to_height,
    scale_text_left_overlap,
    scale_text_right_overlap)
from src.utils.adobe import ReferenceLayer
from src.utils.properties import auto_prop_cached

# QOL Definitions
sID = APP.stringIDToTypeID
cID = APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Text Layer Classes
"""


class TextField:
    FONT = CardFonts.TITLES
    FONT_ITALIC = CardFonts.RULES_ITALIC
    FONT_BOLD = CardFonts.RULES_BOLD

    def __init__(self, layer: ArtLayer, contents: str = "", **kwargs):
        """A generic TextField, which allows you to set a text layer's contents and text color.

        Args:
            layer: TextItem layer to insert contents.
            contents: Text contents to be inserted.
            color: Font color to use for this TextItem.

        Keyword Args:
            color: Color to apply to the text item.
            font: Font postScriptName to apply to the text item.
            font_mana: Font postScriptName to apply to mana symbol text.
            font_italic: Font postScriptName to apply to italicized text.
            font_bold: Font postScriptName to apply to bold text.
            reference: Reference layer to used for scaling operations.
        """
        self._kwargs = kwargs
        self._layer = layer
        self.contents = contents.replace(
            "\n", "\r")

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

    @cached_property
    def kw_symbol_map(self) -> dict[str, tuple[str, list[ColorObject]]]:
        """Symbol map to use for formatting mana symbols."""
        return self.kwargs.get('symbol_map', CON.symbol_map)

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

    @cached_property
    def doc_selection(self) -> Selection:
        """The Selection object from the active document."""
        return self.docref.selection

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

    @cached_property
    def reference_dims(self) -> Optional[type[LayerDimensions]]:
        """Optional[type[LayerDimensions]]: Dimensions of the scaling reference layer."""
        if isinstance(self.reference, ReferenceLayer):
            return self.reference.dims
        if self.reference:
            return get_layer_dimensions(self.reference)
        return None

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
        if self.layer and self.is_text_layer:
            # Layer is valid, select and show it
            select_layer(self.layer, True)
            return True
        with suppress(Exception):
            # Layer provided doesn't exist or isn't a text layer
            name = self.layer.name if self.layer else '[Non-Layer]'
            print(f'Text Field class: {self.__class__.__name__}\n'
                  f'Invalid layer provided: {name}')
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

        # Change to English formatting if needed
        if CFG.force_english_formatting:
            self.TI.language = Language.EnglishUSA


class ScaledTextField (TextField):
    """A TextField which automatically scales down its font size until the right bound
        no longer overlaps with the `reference` layer's left bound."""

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            scale_text_right_overlap(self.layer, self.reference)


class ScaledTextFieldLeft (TextField):
    """A TextField which automatically scales down its font size until the left bound
        no longer overlaps with the `reference` layer's right bound."""

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            scale_text_left_overlap(self.layer, self.reference)


class ScaledWidthTextField (TextField):
    """A TextField which automatically scales down its font size until the width of the
        layer is within the horizontal bound of a reference layer."""
    FONT = CardFonts.RULES

    @cached_property
    def font(self) -> str:
        """str: Font provided, or fallback on global constant."""
        return self.kw_font or CON.font_rules_text

    @cached_property
    def reference_width(self) -> Union[float, int]:
        """Union[float, int]: Width of the reference layer provided."""
        return get_layer_width(self.reference)

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            scale_text_to_width(self.layer, width=self.reference_width)


class FormattedTextField (TextField):
    """A utility class containing the required infrastructure to format text with action descriptors.

    * Formats any recognized mana symbols contained in the text.
    * Formats any modal/bullet point sections in the text.
    * Formats any italicized or bolded text, as well as line breaks.
    """
    FONT = CardFonts.RULES

    def __init__(self, layer: ArtLayer, contents: str = "", **kwargs):
        super().__init__(layer, contents, **kwargs)

        # Pre-cache text details
        _ = self.text_details

    """
    * Core Text Details
    """

    @cached_property
    def text_details(self) -> dict:

        # Generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = generate_italics(self.contents) if self.contents else []

        # Add flavor text to italics array
        if self.flavor_text.count("*") >= 2:
            # Don't italicize text between asterisk
            flavor_text_split = self.flavor_text.split("*")
            italic_text.extend([v for i, v in enumerate(flavor_text_split) if not i % 2 and not v == ''])
            self.flavor_text = ''.join(flavor_text_split)
        elif self.flavor_text:
            # Regular flavor text
            italic_text.append(self.flavor_text)

        # Locate symbols and update the rules string
        rules, symbols = locate_symbols(
            text=self.contents,
            symbol_map=self.kw_symbol_map,
            logger=CONSOLE)

        # Create the new input string
        input_str = f'{rules}\r{self.flavor_text}' if rules and self.flavor_text else (
            rules if rules else self.flavor_text)

        # Locate italics text indices
        italicized = locate_italics(
            st=input_str,
            italics_strings=italic_text,
            symbol_map=self.kw_symbol_map,
            logger=CONSOLE)

        # Return text details
        return {
            'rules_text': rules,
            'input_string': input_str,
            'symbol_indices': symbols,
            'italics_indices': italicized,
        }

    @cached_property
    def italics_indices(self) -> list[CardItalicString]:
        return self.text_details['italics_indices']

    @cached_property
    def symbol_indices(self) -> list[CardSymbolString]:
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
    def rules_text(self) -> str:
        return self.text_details['rules_text']

    @cached_property
    def rules_range(self) -> Optional[tuple[int, int]]:
        if not self.rules_text:
            return
        return 0, len(self.rules_text)

    @cached_property
    def rules_start(self) -> int:
        if self.rules_range:
            return self.rules_range[0]
        return -1

    @cached_property
    def rules_end(self) -> int:
        if self.rules_range:
            return self.rules_range[1]
        return -1

    """
    * Flavor Text and Indexes
    """

    @auto_prop_cached
    def flavor_text(self) -> str:
        return self.kwargs.get('flavor', '').replace('\n', '\r')

    @cached_property
    def flavor_text_range(self) -> Optional[tuple[int, int]]:
        if not self.flavor_text:
            return
        total = len(self.input)
        return total - len(self.flavor_text), total

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
    * Formatting Checks
    """

    @cached_property
    def is_flavor_text(self) -> bool:
        return bool(self.flavor_start >= 0)

    @cached_property
    def is_quote_text(self) -> bool:
        return bool(self.quote_index >= 0)

    @cached_property
    def is_modal(self) -> bool:
        return bool('\u2022' in self.input)

    """
    * Methods
    """

    def format_text(self):
        """Inserts rules and flavor text and formats it based on the defined mana
        symbols, italics text indices, and other predefined properties."""

        # Descriptors
        para_style = ActionDescriptor()
        para_range = ActionDescriptor()
        main_style = ActionDescriptor()
        main_range = ActionDescriptor()
        main_target = ActionDescriptor()
        main_desc = ActionDescriptor()

        # References
        main_ref = ActionReference()

        # Lists
        style_list = ActionList()
        main_list = ActionList()

        # Descriptor ID's
        idTo = sID('to')
        size = sID('size')
        idFrom = sID('from')
        textLayer = sID('textLayer')
        textStyle = sID('textStyle')
        ptUnit = sID('pointsUnit')
        spaceAfter = sID('spaceAfter')
        autoLeading = sID('autoLeading')
        startIndent = sID('startIndent')
        spaceBefore = sID('spaceBefore')
        leadingType = sID('leadingType')
        styleRange = sID('textStyleRange')
        paragraphStyle = sID('paragraphStyle')
        firstLineIndent = sID('firstLineIndent')
        fontPostScriptName = sID('fontPostScriptName')
        paragraphStyleRange = sID('paragraphStyleRange')

        # Spin up the text insertion action
        main_desc.putString(sID('textKey'), self.input)
        main_range.putInteger(idFrom, 0)
        main_range.putInteger(idTo, len(self.input))
        apply_color(main_style, self.color)
        main_style.putBoolean(autoLeading, False)
        main_style.putUnitDouble(size, ptUnit, self.font_size)
        main_style.putUnitDouble(sID('leading'), ptUnit, self.font_size)
        main_style.putString(fontPostScriptName, self.font)
        main_range.putObject(textStyle, textStyle, main_style)
        main_list.putObject(styleRange, main_range)

        # Bold the contents if necessary
        if self.rules_text and self.bold_rules_text:
            main_range.putInteger(idFrom, self.rules_start)
            main_range.putInteger(idTo, self.rules_end)
            main_style.putString(fontPostScriptName, self.font_bold)
            main_range.putObject(textStyle, textStyle, main_style)
            main_list.putObject(styleRange, main_range)

        # Italicize text from our italics indices
        if self.italics_indices:
            for start, end in self.italics_indices:
                main_range.putInteger(idFrom, start)
                main_range.putInteger(idTo, end)
                main_style.putString(fontPostScriptName, self.font_italic)
                main_range.putObject(textStyle, textStyle, main_style)
                main_list.putObject(styleRange, main_range)

        # Format each mana symbol
        if self.symbol_indices:
            for index, colors in self.symbol_indices:
                for i, color in enumerate(colors):
                    main_range.putInteger(idFrom, index + i)
                    main_range.putInteger(idTo, index + i + 1)
                    apply_color(main_style, color)
                    main_style.putString(fontPostScriptName, self.font_mana)
                    main_range.putObject(textStyle, textStyle, main_style)
                    main_list.putObject(styleRange, main_range)

        # Modal choice formatting
        if self.is_modal or self.is_flavor_text:
            para_range.putInteger(idFrom, 0)
            para_range.putInteger(idTo, len(self.input))
            para_style.putUnitDouble(firstLineIndent, ptUnit, 0)
            para_style.putUnitDouble(startIndent, ptUnit, 0)
            para_style.putUnitDouble(sID("endIndent"), ptUnit, 0)
            para_style.putUnitDouble(spaceBefore, ptUnit, self.line_break_lead)
            para_style.putUnitDouble(spaceAfter, ptUnit, 0)
            para_style.putInteger(sID("dropCapMultiplier"), 1)
            para_style.putEnumerated(leadingType, leadingType, sID("leadingBelow"))

        # Adjust paragraph formatting for modal card with bullet points
        if self.is_modal:
            default_style = ActionDescriptor()
            para_range.putInteger(idFrom, self.input.find("\u2022"))
            para_range.putInteger(idTo, self.input.rindex("\u2022") + 1)
            para_style.putUnitDouble(firstLineIndent, ptUnit, -CON.modal_indent)
            para_style.putUnitDouble(startIndent, ptUnit, CON.modal_indent)
            para_style.putUnitDouble(spaceBefore, ptUnit, 1)
            default_style.putString(fontPostScriptName, self.font_mana)
            default_style.putUnitDouble(size, ptUnit, 12)
            default_style.putBoolean(autoLeading, False)
            para_style.putObject(sID("defaultStyle"), textStyle, default_style)
            para_range.putObject(paragraphStyle, paragraphStyle, para_style)
            style_list.putObject(paragraphStyleRange, para_range)

        # Flavor text actions
        if self.is_flavor_text:

            # Add linebreak spacing between rules and flavor text
            para_range.putInteger(idFrom, self.flavor_start + 3)
            para_range.putInteger(idTo, self.flavor_start + 4)
            para_style.putUnitDouble(startIndent, ptUnit, 0)
            para_style.putUnitDouble(firstLineIndent, ptUnit, 0)
            para_style.putUnitDouble(sID("impliedStartIndent"), ptUnit, 0)
            para_style.putUnitDouble(sID("impliedFirstLineIndent"), ptUnit, 0)
            para_style.putUnitDouble(spaceBefore, ptUnit, self.flavor_text_lead)
            para_range.putObject(paragraphStyle, paragraphStyle, para_style)
            style_list.putObject(paragraphStyleRange, para_range)

            # Adjust flavor text color
            if self.flavor_color:
                main_range.PutInteger(idFrom, self.flavor_start)
                main_range.PutInteger(idTo, self.flavor_end)
                apply_color(main_style, self.flavor_color)
                main_style.putString(fontPostScriptName, self.font_italic)
                main_range.PutObject(textStyle, textStyle, main_style)
                main_list.putObject(styleRange, main_range)

            # Quote actions flavor text
            if self.is_quote_text:

                # Adjust line break spacing if there's a line break in the flavor text
                para_range.putInteger(idFrom, self.quote_index + 3)
                para_range.putInteger(idTo, len(self.input))
                para_style.putUnitDouble(spaceBefore, ptUnit, 0)
                para_range.putObject(paragraphStyle, paragraphStyle, para_style)
                style_list.putObject(paragraphStyleRange, para_range)

                # Optional, align quote credit to right
                if self.right_align_quote and '"\r—' in self.flavor_text:
                    para_range.putInteger(idFrom, self.input.find('"\r—') + 2)
                    para_range.putInteger(idTo, self.flavor_end)
                    para_style.putBoolean(sID('styleSheetHasParent'), True)
                    para_range.putEnumerated(sID('align'), sID('alignmentType'), sID('right'))
                    para_range.putObject(paragraphStyle, paragraphStyle, para_style)
                    style_list.putObject(paragraphStyleRange, para_range)

        # Apply action lists
        main_desc.putList(paragraphStyleRange, style_list)
        main_desc.putList(styleRange, main_list)

        # Push changes to text layer
        main_ref.putEnumerated(textLayer, sID("ordinal"), sID("targetEnum"))
        main_target.putReference(sID("target"), main_ref)
        main_target.putObject(idTo, textLayer, main_desc)
        APP.executeAction(sID("set"), main_target, NO_DIALOG)

    def execute(self):
        super().execute()

        # Format text
        self.format_text()

        # Justify center if required
        if self.contents_centered:
            self.TI.justification = Justification.Center

        # Ensure hyphenation disabled
        self.TI.hyphenation = False


class FormattedTextArea (FormattedTextField):
    """A FormattedTextField where the text is required to fit within a given area.

    * Reduces font size until the text fits within the reference layer's bounds.
    * Properly separates and formats flavor text with respect to an optional divider layer.
    * Centers the formatted text vertically with respect to the reference layer's bounds.
    """

    """
    * Properties
    """

    @cached_property
    def pt_reference(self) -> Optional[ReferenceLayer]:
        return self.kwargs.get('pt_reference', None)

    @cached_property
    def divider(self) -> Optional[Union[ArtLayer, LayerSet]]:
        """Divider layer, if provided and flavor text exists."""
        if (divider := self.kwargs.get('divider')) and all([self.flavor_text, self.contents, CFG.flavor_divider]):
            divider.visible = True
            return divider
        return

    @cached_property
    def scale_height(self) -> bool:
        """Scale text to fit reference height (Default: True)."""
        if scale_height := self.kwargs.get('scale_height'):
            return scale_height
        return True

    @cached_property
    def scale_width(self) -> bool:
        """Scale text to fit reference width (Default: False)."""
        if scale_width := self.kwargs.get('scale_width'):
            return scale_width
        return False

    @cached_property
    def fix_overflow_width(self) -> bool:
        """Scale text to fit bounding box width (Default: False)."""
        if fix_overflow_width := self.kwargs.get('fix_overflow_width'):
            return fix_overflow_width
        return True

    @cached_property
    def fix_overflow_height(self) -> bool:
        """Scale text to fit bounding box height (Default: If it overflows the bounds)."""
        if len(self.contents + self.flavor_text) > 280:
            return True
        if fix_overflow_height := self.kwargs.get('fix_overflow_height'):
            return fix_overflow_height
        return False

    """
    * Methods
    """

    def insert_divider(self):
        """Inserts and correctly positions flavor text divider."""

        # Create a reference layer with no effects
        flavor = self.layer.duplicate()
        rules = flavor.duplicate()
        flavor.rasterize(RasterizeType.EntireLayer)
        remove_trailing_text(rules, self.flavor_start)
        select_layer_bounds(rules, self.doc_selection)
        self.docref.activeLayer = flavor
        self.doc_selection.expand(2)
        self.doc_selection.clear()

        # Move flavor text to bottom, then position divider
        flavor.translate(0, self.layer.bounds[3] - flavor.bounds[3])
        position_between_layers(self.divider, rules, flavor)
        self.doc_selection.deselect()
        flavor.remove()
        rules.remove()

    def pre_scale_to_fit(self) -> Optional[float]:
        """Fix height overflow before formatting text."""
        contents = self.contents if not self.flavor_text else str(
            self.contents + "\r" + self.flavor_text)
        self.TI.contents = contents
        return scale_text_to_height(
            layer=self.layer,
            height=int(self.reference_dims['height']*1.1))

    def scale_to_fit(self, font_size: Optional[float] = None) -> None:
        """Scale font size to fit within any references."""

        # Scale layer to reference
        if self.reference_dims:

            # Resize the text until it fits the reference vertically
            if self.scale_height:
                font_size = scale_text_to_height(
                    layer=self.layer,
                    height=self.reference_dims['height'])

            # Resize the text until it fits the reference horizontally
            if self.scale_width:
                font_size = scale_text_to_width(
                    layer=self.layer,
                    width=self.reference_dims['width'],
                    step=0.2, font_size=font_size)

        # Resize the text until it fits the TextLayer bounding box
        if self.fix_overflow_width:
            scale_text_to_width_textbox(
                layer=self.layer, font_size=font_size)

    def position_within_reference(self):
        """Positions the layer with respect to the reference, if required."""

        # Ensure the layer is centered vertically
        dims = get_layer_dimensions(self.layer)
        self.layer.translate(0, self.reference_dims['center_y'] - dims['center_y'])

        # Ensure the layer is centered horizontally if needed
        if self.contents_centered and self.flavor_centered:
            self.layer.translate(0, self.reference_dims['center_x'] - dims['center_x'])

    def execute(self):

        # Skip if both are empty
        if not self.input:
            return
        font_size = None

        # Pre-scaling to prevent text overflow errors
        if self.fix_overflow_height and self.reference_dims:
            font_size = self.pre_scale_to_fit()

        # Execute text formatting
        super().execute()

        # Scale layer to fit reference
        self.scale_to_fit(font_size)

        # Position the layer properly
        if self.reference_dims:
            self.position_within_reference()

        # Insert flavor divider if needed
        if self.divider:
            self.insert_divider()

        # Shift vertically if the text overlaps the PT box
        if self.pt_reference:

            # Use newer methodology if top reference not provided
            delta = clear_reference_vertical(
                layer=self.layer,
                ref=self.pt_reference,
                docsel=self.doc_selection)

            # Shift the divider if layer was moved
            if delta < 0 and self.divider:
                self.divider.translate(0, delta)


"""
* Text Item Type
"""

FormattedTextLayer = Union[
    TextField,
    ScaledTextField,
    FormattedTextArea,
    FormattedTextField,
    ScaledWidthTextField,
]
