"""
TEXT LAYER MODULE
"""
from functools import cached_property
from typing import Optional, Union

import photoshop.api as ps
from photoshop.api._artlayer import ArtLayer

import proxyshop.helpers as psd
from proxyshop.constants import con
from proxyshop.settings import cfg
from proxyshop import format_text as ft

# QOL Definitions
app = ps.Application()
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = ps.DialogModes.DisplayNoDialogs


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
        self.contents = contents.replace("\n", "\r")

        # Change to English formatting if needed
        if self.layer.kind == ps.LayerKind.TextLayer and cfg.force_english_formatting:
            self.layer.textItem.language = ps.Language.EnglishUSA

    """
    PROPERTIES
    """

    @cached_property
    def reference(self) -> Optional[ArtLayer]:
        if 'reference' in self.kwargs:
            return self.kwargs['reference']
        # Bug reporting
        print(f"I'm not getting a scale reference for TextField: {self.layer.name}")
        return

    @cached_property
    def color(self) -> ps.SolidColor:
        if 'color' in self.kwargs:
            return self.kwargs['color']
        return psd.get_text_layer_color(self.layer)

    """
    METHODS
    """

    def execute(self):
        """
        Executes all text actions.
        """
        self.layer.visible = True
        self.layer.textItem.contents = self.contents
        self.layer.textItem.color = self.color


class ScaledTextField (TextField):
    """
    A TextField which automatically scales down its font size (in 0.25 pt increments) until
    its right bound no longer overlaps with a reference layer's left bound.
    """
    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        if self.reference:
            ft.scale_text_right_overlap(self.layer, self.reference)


class FormattedTextField (TextField):
    """
    A utility class for packing in the required infrastructure to format text with action descriptors.
    """

    """
    PROPERTIES
    """

    @property
    def divider(self) -> Optional[ArtLayer]:
        # Default to None unless overwritten
        return

    @cached_property
    def input(self) -> str:
        if hasattr(self, 'flavor_text') and self.flavor_text != "":
            return self.contents + "\r" + self.flavor_text
        return self.contents

    @property
    def flavor_text(self) -> str:
        if 'flavor' in self.kwargs:
            if "\n" in self.kwargs['flavor']:
                return self.kwargs['flavor'].replace("\n", "\r")
            return self.kwargs['flavor']
        return ""

    @flavor_text.setter
    def flavor_text(self, value):
        self.kwargs['flavor'] = value

    @cached_property
    def contents_centered(self) -> bool:
        if 'centered' in self.kwargs and self.kwargs['centered']:
            return True
        return False

    @cached_property
    def flavor_centered(self) -> bool:
        if 'flavor_centered' in self.kwargs and self.kwargs['flavor_centered']:
            return True
        return False

    @cached_property
    def line_break_lead(self) -> Union[int, float]:
        if 'line_break_lead' in self.kwargs:
            return self.kwargs['line_break_lead']
        if self.contents_centered:
            return 0
        return con.line_break_lead

    @cached_property
    def flavor_text_lead(self) -> Union[int, float]:
        # Lead with divider
        if self.divider:
            if 'flavor_text_lead_divider' in self.kwargs:
                return self.kwargs['flavor_text_lead_divider']
            return con.flavor_text_lead_divider
        # Lead without divider
        if 'flavor_text_lead' in self.kwargs:
            return self.kwargs['flavor_text_lead']
        return con.flavor_text_lead

    @cached_property
    def flavor_index(self) -> int:
        return len(self.contents) if len(self.flavor_text) > 0 else -1

    @cached_property
    def quote_index(self) -> int:
        return self.input.find("\r", self.flavor_index + 3) if self.flavor_index >= 0 else -1

    @cached_property
    def italics_strings(self) -> list:
        # Generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = ft.generate_italics(self.contents)

        # Add flavor text to italics array
        if self.flavor_text.count("*") >= 2:
            # Don't italicize text between asterisk
            flavor_text_split = self.flavor_text.split("*")
            italic_text.extend([v for i, v in enumerate(flavor_text_split) if not i % 2 and not v == ""])

            # Reassemble flavor text without asterisks
            self.flavor_text = "".join(flavor_text_split)
        elif len(self.flavor_text) > 0:
            italic_text.append(self.flavor_text)
        return italic_text

    @cached_property
    def bold_rules_text(self) -> bool:
        if 'bold_rules_text' in self.kwargs:
            return self.kwargs['bold_rules_text']
        return False

    @cached_property
    def right_align_quote(self) -> bool:
        if 'right_align_quote' in self.kwargs:
            return self.kwargs['right_align_quote']
        return False

    @cached_property
    def flavor_color(self) -> Optional[ps.SolidColor]:
        if 'flavor_color' in self.kwargs:
            return self.kwargs['flavor_color']
        return

    @cached_property
    def font_size(self) -> float:
        if 'font_size' in self.kwargs:
            return self.kwargs['font_size'] * psd.get_text_scale_factor(self.layer)
        return self.layer.textItem.size * psd.get_text_scale_factor(self.layer)

    """
    METHODS
    """

    def format_text(self):
        """
        Inserts the given string into the active layer and formats it according to defined parameters with symbols
        from the NDPMTG font.
        """
        # Record the layer's justification before modifying the layer in case it's reset along the way
        layer_justification = app.activeDocument.activeLayer.textItem.justification

        # Locate symbols and update the input string
        ret = ft.locate_symbols(self.input)
        input_string = ret['input_string']
        symbol_indices = ret['symbol_indices']

        # Locate italics text indices
        italics_indices = ft.locate_italics(input_string, self.italics_strings)

        # Prepare action descriptor and reference variables
        primary_action_descriptor = ps.ActionDescriptor()
        primary_action_list = ps.ActionList()
        desc119 = ps.ActionDescriptor()
        desc26 = ps.ActionDescriptor()
        desc25 = ps.ActionDescriptor()
        ref101 = ps.ActionReference()
        desc141 = ps.ActionDescriptor()
        desc142 = ps.ActionDescriptor()
        desc143 = ps.ActionDescriptor()
        desc144 = ps.ActionDescriptor()
        desc145 = ps.ActionDescriptor()
        list13 = ps.ActionList()
        list14 = ps.ActionList()
        list15 = ps.ActionList()
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
        idsetd = sID("set")
        idTxLr = sID("textLayer")
        idT = sID("to")
        idFntN = sID("fontName")
        idSz = sID("size")
        idPnt = sID("pointsUnit")
        idLdng = sID("leading")
        idTxtt = sID("textStyleRange")
        idFrom = sID("from")

        # Spin up the text insertion action
        ref101.putEnumerated(idTxLr, sID("ordinal"), sID("targetEnum"))
        desc119.putReference(cID("null"), ref101)
        primary_action_descriptor.putString(sID("textKey"), input_string)
        desc25.putInteger(idFrom, 0)
        desc25.putInteger(idT, len(input_string))
        desc26.putString(idfontPostScriptName, con.font_rules_text)  # MPlantin default
        desc26.putString(idFntN, con.font_rules_text)  # MPlantin default
        desc26.putUnitDouble(idSz, idPnt, self.font_size)
        psd.apply_color(desc26, self.color)
        desc26.putBoolean(idautoLeading, False)
        desc26.putUnitDouble(idLdng, idPnt, self.font_size)
        desc25.putObject(idTxtS, idTxtS, desc26)
        current_layer_ref = desc25

        # Bold the contents if necessary
        if self.bold_rules_text and self.flavor_index != 0:
            bold_action1 = ps.ActionDescriptor()
            bold_action2 = ps.ActionDescriptor()
            contents_index = len(input_string) - 1 if self.flavor_index < 0 else self.flavor_index - 1
            primary_action_list.putObject(idTxtt, current_layer_ref)
            bold_action1.putInteger(idFrom, 0)  # italics start index
            bold_action1.putInteger(idT, contents_index)  # italics end index
            bold_action2.putString(idfontPostScriptName, con.font_rules_text_bold)  # MPlantin italic default
            bold_action2.putString(idFntN, con.font_rules_text_bold)  # MPlantin italic default
            bold_action2.putUnitDouble(idSz, idPnt, self.font_size)
            psd.apply_color(bold_action2, self.color)
            bold_action2.putBoolean(idautoLeading, False)
            bold_action2.putUnitDouble(idLdng, idPnt, self.font_size)
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
            italics_action2.putUnitDouble(idSz, idPnt, self.font_size)
            psd.apply_color(italics_action2, self.color)
            italics_action2.putBoolean(idautoLeading, False)
            italics_action2.putUnitDouble(idLdng, idPnt, self.font_size)
            italics_action1.putObject(idTxtS, idTxtS, italics_action2)
            current_layer_ref = italics_action1

        # Format each symbol correctly
        for symbol_index in symbol_indices:
            current_layer_ref = ft.format_symbol(
                primary_action_list=primary_action_list,
                starting_layer_ref=current_layer_ref,
                symbol_index=symbol_index['index'],
                symbol_colors=symbol_index['colors'],
                layer_font_size=self.font_size,
            )

        # Insert actions for bold, italics, and symbol formatting
        primary_action_list.putObject(idTxtt, current_layer_ref)
        primary_action_descriptor.putList(idTxtt, primary_action_list)

        # Paragraph formatting
        desc141.putInteger(idFrom, 0)
        desc141.putInteger(idT, len(input_string))  # input string length
        desc142.putUnitDouble(idfirstLineIndent, idPnt, 0)
        desc142.putUnitDouble(idstartIndent, idPnt, 0)
        desc142.putUnitDouble(idendIndent, idPnt, 0)
        desc142.putUnitDouble(idspaceBefore, idPnt, self.line_break_lead)
        desc142.putUnitDouble(idspaceAfter, idPnt, 0)
        desc142.putInteger(sID("dropCapMultiplier"), 1)
        desc142.putEnumerated(idleadingType, idleadingType, sID("leadingBelow"))
        desc143.putString(idfontPostScriptName, con.font_mana)  # NDPMTG default
        desc143.putString(idFntN, con.font_rules_text)  # MPlantin default
        desc143.putBoolean(idautoLeading, False)
        primary_action_descriptor.putList(idparagraphStyleRange, list13)
        primary_action_descriptor.putList(idkerningRange, list14)

        # Adjust formatting for modal card with bullet points
        if "\u2022" in input_string:
            startIndexBullet = input_string.find("\u2022")
            endIndexBullet = input_string.rindex("\u2022")
            desc141.putInteger(idFrom, startIndexBullet)
            desc141.putInteger(idT, endIndexBullet + 1)
            desc142.putUnitDouble(idfirstLineIndent, idPnt, -con.modal_indent)  # negative modal indent
            desc142.putUnitDouble(idstartIndent, idPnt, con.modal_indent)  # modal indent
            desc142.putUnitDouble(idspaceBefore, idPnt, 1)
            desc142.putUnitDouble(idspaceAfter, idPnt, 0)
            desc143.putString(idfontPostScriptName, con.font_mana)  # NDPMTG default
            desc143.putString(idFntN, con.font_rules_text)  # MPlantin default
            desc143.putUnitDouble(idSz, idPnt, 12)
            desc143.putBoolean(idautoLeading, False)
            desc142.putObject(sID("defaultStyle"), idTxtS, desc143)
            desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
            list13.putObject(idparagraphStyleRange, desc141)
            primary_action_descriptor.putList(idparagraphStyleRange, list13)
            primary_action_descriptor.putList(idkerningRange, list14)

        # Flavor text actions
        if self.flavor_index >= 0:
            # Add linebreak spacing between rules and flavor text
            desc141.putInteger(idFrom, self.flavor_index + 3)
            desc141.putInteger(idT, self.flavor_index + 4)
            desc142.putUnitDouble(idfirstLineIndent, idPnt, 0)
            idimpliedFirstLineIndent = sID("impliedFirstLineIndent")
            desc142.putUnitDouble(idimpliedFirstLineIndent, idPnt, 0)
            desc142.putUnitDouble(idstartIndent, idPnt, 0)
            desc142.putUnitDouble(sID("impliedStartIndent"), idPnt, 0)
            desc142.putUnitDouble(idspaceBefore, idPnt, self.flavor_text_lead)  # Space between rules and flavor text
            desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
            list13.putObject(idparagraphStyleRange, desc141)
            primary_action_descriptor.putList(idparagraphStyleRange, list13)
            primary_action_descriptor.putList(idkerningRange, list14)

            # Adjust flavor text color
            if self.flavor_color:
                desc144.PutInteger(sID("from"), self.flavor_index)
                desc144.PutInteger(sID("to"), len(input_string))
                desc145.putString(idfontPostScriptName, con.font_rules_text_italic)  # MPlantin italic default
                desc145.putString(idFntN, con.font_rules_text_italic)  # MPlantin italic default
                desc145.putUnitDouble(idSz, idPnt, self.font_size)
                desc145.putBoolean(idautoLeading, False)
                desc145.putUnitDouble(idLdng, idPnt, self.font_size)
                psd.apply_color(desc145, self.flavor_color)
                desc144.PutObject(sID("textStyle"), sID("textStyle"), desc145)
                list15.PutObject(sID("textStyleRange"), desc144)
                primary_action_descriptor.putList(sID("textStyleRange"), list15)

        # Quote actions flavor text
        disable_justify = False
        if self.quote_index >= 0:
            # Adjust line break spacing if there's a line break in the flavor text
            desc141.putInteger(idFrom, self.quote_index + 3)
            desc141.putInteger(idT, len(input_string))
            desc142.putUnitDouble(idspaceBefore, idPnt, 0)
            desc141.putObject(idparagraphStyle, idparagraphStyle, desc142)
            list13.putObject(idparagraphStyleRange, desc141)

            # Optional, align quote credit to right
            if self.right_align_quote and input_string.find('"\r—') >= 0:
                # Get start and ending index of quotation credit
                index_start = input_string.find('"\r—') + 2
                index_end = len(input_string) - 1

                # Align this part, disable justification reset
                list13 = ft.classic_align_right(list13, index_start, index_end)
                disable_justify = True

            # Add quote actions to primary action
            primary_action_descriptor.putList(idparagraphStyleRange, list13)
            primary_action_descriptor.putList(idkerningRange, list14)

        # Push changes to text layer
        desc119.putObject(idT, idTxLr, primary_action_descriptor)
        app.executeAction(idsetd, desc119, NO_DIALOG)

        # Reset layer's justification if needed and disable hyphenation
        if not disable_justify:
            app.activeDocument.activeLayer.textItem.justification = layer_justification
        app.activeDocument.activeLayer.textItem.hyphenation = False

    def execute(self):
        super().execute()

        # Format text
        app.activeDocument.activeLayer = self.layer
        self.format_text()
        if self.contents_centered:
            self.layer.textItem.justification = ps.Justification.Center


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
    def divider(self) -> Optional[ArtLayer]:
        if 'divider' in self.kwargs and cfg.flavor_divider and len(self.flavor_text) > 0 and len(self.contents) > 0:
            return self.kwargs['divider']
        return

    @cached_property
    def fix_length(self) -> bool:
        # Check if text needs the long text entry fix
        if len(self.contents + self.flavor_text) > 280:
            return True
        return False

    """
    METHODS
    """

    def insert_divider(self):
        """
        Inserts and correctly positions flavor text divider.
        """
        if len(self.flavor_text) > 0:

            # Create a flavor-text-only layer to reference
            flavor_test = self.layer.duplicate()
            app.activeDocument.activeLayer = flavor_test
            ft.basic_format_text(self.flavor_text)
            flavor_replace = flavor_test.textItem.contents
            flavor_test.remove()

            # Established two separate layers: contents and flavor, each rasterized
            self.layer.visible = False
            layer_text_contents = self.layer.duplicate()
            psd.replace_text(layer_text_contents, flavor_replace, "")
            layer_text_contents.rasterize(ps.RasterizeType.EntireLayer)
            layer_flavor_text = self.layer.duplicate()
            layer_flavor_text.rasterize(ps.RasterizeType.EntireLayer)
            psd.select_layer_bounds(layer_text_contents)
            app.activeDocument.activeLayer = layer_flavor_text
            app.activeDocument.selection.expand(1)
            app.activeDocument.selection.clear()
            app.activeDocument.selection.deselect()
            self.layer.visible = True

            # Get contents southern bound, move flavor text to bottom, get its northern bound
            text_contents_bottom = layer_text_contents.bounds[3]
            layer_flavor_text.translate(0, psd.get_text_layer_bounds(self.layer)[3] - layer_flavor_text.bounds[3])
            flavor_text_top = layer_flavor_text.bounds[1]

            # Take our final midpoint measurement and remove duplicates
            divider_y_midpoint = (text_contents_bottom + flavor_text_top) / 2
            layer_text_contents.remove()
            layer_flavor_text.remove()

            # Enable the divider and move it
            self.divider.visible = True
            app.activeDocument.activeLayer = self.divider
            app.activeDocument.selection.select([
                [0, divider_y_midpoint - 1],
                [1, divider_y_midpoint - 1],
                [1, divider_y_midpoint + 1],
                [0, divider_y_midpoint + 1]
            ])
            psd.align_vertical()
            psd.clear_selection()

    def execute(self):

        # Fix length procedure before super called
        if self.fix_length:
            self.layer.textItem.contents = self.contents + "\r" + self.flavor_text
            ft.scale_text_to_fit_height(self.layer, int(psd.get_layer_dimensions(self.reference)['height']*1.01))

        super().execute()
        if self.contents != "" or self.flavor_text != "":
            # Resize the text until it fits into the reference layer
            ft.scale_text_to_fit_reference(self.layer, self.reference)

            # Ensure the layer is centered vertically
            ft.vertically_align_text(self.layer, self.reference)

            # Ensure the layer is centered horizontally if needed
            if self.contents_centered:
                psd.select_layer_bounds(self.reference)
                app.activeDocument.activeLayer = self.layer
                psd.align_horizontal()
                psd.clear_selection()

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
        if 'pt_reference' in self.kwargs:
            return self.kwargs['pt_reference']
        return None

    @cached_property
    def pt_top_reference(self) -> Optional[ArtLayer]:
        if 'pt_top_reference' in self.kwargs:
            return self.kwargs['pt_top_reference']
        return None

    """
    METHODS
    """

    def execute(self):
        super().execute()

        # Shift vertically if the text overlaps the PT box
        if self.pt_reference and self.pt_top_reference:
            delta = ft.vertically_nudge_creature_text(self.layer, self.pt_reference, self.pt_top_reference)
            # Shift the divider as well
            if delta and self.divider:
                if delta < 0:
                    self.divider.translate(0, delta)
