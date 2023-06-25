"""
* PLANESWALKER TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api import ElementPlacement, ColorBlendMode
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._core import StarterTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import CardLayout
from src.utils.regex import Reg
import src.format_text as ft
import src.helpers as psd


class PlaneswalkerTemplate (StarterTemplate):
    """
    * The main Planeswalker template to extend to for essential Planeswalker support.
    * Does not support MDFC or Transform Planeswalker cards.
    """

    def __init__(self, layout: CardLayout):
        # Settable Properties
        self._ability_layers = []
        self._shields = []
        self._colons = []
        super().__init__(layout)

    """
    PROPERTIES
    """

    @cached_property
    def abilities(self) -> list:
        # Fix abilities that include a newline
        return Reg.PLANESWALKER.findall(self.layout.oracle_text)

    @property
    def art_frame(self):
        # Name of art reference layer
        if self.is_colorless:
            return LAYERS.FULL_ART_FRAME
        return LAYERS.PLANESWALKER_ART_FRAME

    """
    GROUPS
    """

    @cached_property
    def group(self) -> LayerSet:
        # Get the main layer group based on ability box size
        if self.layout.name in ("Gideon Blackblade", "Comet, Stellar Pup"):
            group = psd.getLayerSet("pw-4")
        elif len(self.abilities) <= 3:
            group = psd.getLayerSet("pw-3")
        else:
            group = psd.getLayerSet("pw-4")
        group.visible = True
        return group

    @cached_property
    def loyalty_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.LOYALTY_GRAPHICS)

    @cached_property
    def border_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.BORDER, self.group)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, self.group)

    @cached_property
    def top_ref(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PW_TOP_REFERENCE, self.text_group)

    @cached_property
    def adj_ref(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PW_ADJUSTMENT_REFERENCE, self.text_group)

    @cached_property
    def loyalty_text(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TEXT, [self.loyalty_group, LAYERS.STARTING_LOYALTY])

    """
    SETTABLE LAYERS
    """

    @property
    def ability_layers(self) -> list[ArtLayer]:
        return self._ability_layers

    @ability_layers.setter
    def ability_layers(self, value):
        self._ability_layers = value

    @property
    def colons(self) -> list:
        return self._colons

    @colons.setter
    def colons(self, value):
        self._colons = value

    @property
    def shields(self) -> list:
        return self._shields

    @shields.setter
    def shields(self, value):
        self._shields = value

    """
    FRAME LAYERS
    """

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.twins, psd.getLayerSet(LAYERS.TWINS, self.group))

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, psd.getLayerSet(LAYERS.PINLINES, self.group))

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.background, psd.getLayerSet(LAYERS.BACKGROUND, self.group))

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, [self.group, LAYERS.COLOR_INDICATOR])

    @cached_property
    def crown_layer(self) -> Optional[ArtLayer]:
        # Crown never included
        return

    """
    METHODS
    """

    def basic_text_layers(self):

        # Iterate through abilities to add text layers
        for i, ability in enumerate(self.abilities):

            # Get the colon index, determine if this is static or activated ability
            colon_index = ability.find(": ")
            if 5 > colon_index > 0:

                # Determine which loyalty group to enable, and set the loyalty symbol's text
                loyalty_graphic = psd.getLayerSet(ability[0], self.loyalty_group)
                psd.getLayer(LAYERS.COST, loyalty_graphic).textItem.contents = ability[0:int(colon_index)]
                ability_layer = psd.getLayer(LAYERS.ABILITY_TEXT, self.loyalty_group).duplicate()

                # Add text layer, shields, and colons to list
                self.ability_layers.append(ability_layer)
                self.shields.append(loyalty_graphic.duplicate())
                self.colons.append(psd.getLayer(LAYERS.COLON, self.loyalty_group).duplicate())
                ability = ability[colon_index + 2:]

            else:

                # Hide default ability, switch to static
                ability_layer = psd.getLayer(LAYERS.STATIC_TEXT, self.loyalty_group).duplicate()
                self.ability_layers.append(ability_layer)
                self.shields.append(None)
                self.colons.append(None)

                # Is this a double line ability?
                if "\n" in ability:
                    self.active_layer = ability_layer
                    ft.space_after_paragraph(2)

            # Add ability text
            self.text.append(
                text_classes.FormattedTextField(
                    layer=ability_layer,
                    contents=ability
                )
            )

        # Starting loyalty
        if self.layout.loyalty:
            self.loyalty_text.textItem.contents = self.layout.loyalty
        else:
            self.loyalty_text.parent.visible = False

        # Call to super for name, type, etc
        super().basic_text_layers()

    def enable_frame_layers(self):

        # Enable twins, pinlines, background, color indicator
        if self.twins_layer:
            self.twins_layer.visible = True
        if self.pinlines_layer:
            self.pinlines_layer.visible = True
        if self.background_layer:
            self.background_layer.visible = True
        if self.is_type_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

    def post_text_layers(self):
        """
        Auto-position the ability text, colons, and shields.
        """
        # Core vars
        spacing = self.app.scale_by_height(64)
        spaces = len(self.ability_layers) + 1
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        total_height = ref_height - (spacing * spaces)

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Space abilities evenly apart
        uniform_gap = True if len(self.ability_layers) < 3 or not self.layout.loyalty else False
        psd.spread_layers_over_reference(
            self.ability_layers,
            self.textbox_reference,
            spacing if not uniform_gap else None
        )

        # Adjust text to avoid loyalty badge
        if self.layout.loyalty:
            ft.vertically_nudge_pw_text(
                self.ability_layers,
                self.textbox_reference,
                self.adj_ref,
                self.top_ref,
                spacing,
                uniform_gap=uniform_gap
            )

        # Align colons and shields to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):
            # Break if we encounter a length mismatch
            if len(self.shields) < (i + 1) or len(self.colons) < (i + 1):
                self.raise_warning("Encountered bizarre Planeswalker data!")
                break
            # Skip if this is a passive ability
            if self.shields[i] and self.colons[i]:
                before = self.colons[i].bounds[1]
                psd.align_vertical(self.colons[i], reference=ref_layer)
                self.docref.selection.deselect()
                difference = self.colons[i].bounds[1] - before
                self.shields[i].translate(0, difference)

        # Add the ability layer mask
        self.pw_ability_mask()

    def pw_ability_mask(self):
        """
        Position the ragged edge ability mask.
        """

        # Ragged line layers
        lines = psd.getLayerSet("Ragged Lines", [self.group, LAYERS.TEXTBOX, "Ability Dividers"])
        line1_top = psd.getLayer("Line 1 Top", lines)
        line1_bottom = psd.getLayer("Line 1 Bottom", lines)
        line1_top_ref = psd.getLayer("Line 1 Top Reference", lines)
        line1_bottom_ref = psd.getLayer("Line 1 Bottom Reference", lines)
        line1_top.visible = True
        line1_bottom.visible = True

        # Additional for 4 Abilities
        if len(self.ability_layers) == 4:
            line2_top = psd.getLayer("Line 2 Top", lines)
            line2_bottom = psd.getLayer("Line 2 Bottom", lines)
            line2_ref = psd.getLayer("Line 2 Reference", lines)
            line2_top.visible = True
            line2_bottom.visible = True
        else:
            line2_top, line2_bottom, line2_ref = None, None, None

        # Position needed ragged lines
        if len(self.ability_layers) > 2:
            # 3+ Ability Planeswalker
            self.position_divider_line([self.ability_layers[0], self.ability_layers[1]], line1_top, line1_top_ref)
            self.position_divider_line([self.ability_layers[1], self.ability_layers[2]], line1_bottom, line1_bottom_ref)
        else:
            # 2 Ability Planeswalker
            self.position_divider_line([self.ability_layers[0], self.ability_layers[1]], line1_top, line1_top_ref)
        if line2_top and line2_ref:
            # 4 Ability Planeswalker
            self.position_divider_line([self.ability_layers[2], self.ability_layers[3]], line2_top, line2_ref)

        # Fill between the ragged lines
        if len(self.ability_layers) > 2:
            # 3+ Ability Planeswalker
            self.fill_between_dividers(line1_top, line1_bottom)
        else:
            # 2 Ability Planeswalker
            line1_bottom.translate(0, 1000)
            self.fill_between_dividers(line1_top, line1_bottom)
        if line2_top and line2_bottom:
            # 4 Ability Planeswalker
            self.fill_between_dividers(line2_top, line2_bottom)

    @staticmethod
    def position_divider_line(layers: list[ArtLayer], line: ArtLayer, line_ref: ArtLayer):
        """
        Positions a ragged divider line correctly.
        @param layers: Two layers to position the line between.
        @param line: Line layer to be positioned.
        @param line_ref: Reference line layer to help position the ragged line.
        """
        dif = (layers[1].bounds[1] - layers[0].bounds[3]) / 2
        ref_pos = (line_ref.bounds[3] + line_ref.bounds[1]) / 2
        targ_pos = dif + layers[0].bounds[3]
        line.translate(0, (targ_pos - ref_pos))

    def fill_between_dividers(self, line1: ArtLayer, line2: ArtLayer):
        """
        Fill area between two ragged lines.
        @param line1: The top ragged line layer.
        @param line2: The bottom ragged line layer.
        """
        self.active_layer = self.docref.artLayers.add()
        self.active_layer.move(line1, ElementPlacement.PlaceAfter)
        self.docref.selection.select([
            [line1.bounds[0] - 200, line1.bounds[3]],
            [line1.bounds[2] + 200, line1.bounds[3]],
            [line1.bounds[2] + 200, line2.bounds[1]],
            [line1.bounds[0] - 200, line2.bounds[1]]
        ])
        fill_color = psd.rgb_black()
        self.docref.selection.expand(1)
        self.docref.selection.fill(
            fill_color, ColorBlendMode.NormalBlendColor, 100, False
        )
        self.docref.selection.deselect()


class PlaneswalkerExtendedTemplate (PlaneswalkerTemplate):
    """
    * An extended version of PlaneswalkerTemplate.
    * Functionally identical except for the lack of background textures.
    """
    template_suffix = "Extended"

    """
    PROPERTIES
    """

    @property
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PLANESWALKER_ART_FRAME)

    @cached_property
    def is_content_aware_enabled(self):
        return True

    """
    LAYERS
    """

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return


class PlaneswalkerMDFCTemplate (PlaneswalkerTemplate):
    """
    * Adds support for MDFC functionality to the existing PlaneswalkerTemplate.
    """

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.LEFT, self.dfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RIGHT, self.dfc_group)

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.NAME, self.text_group)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add mdfc text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer=self.text_layer_mdfc_right,
                contents=self.layout.other_face_right
            ),
            text_classes.ScaledTextField(
                layer=self.text_layer_mdfc_left,
                contents=self.layout.other_face_left,
                reference=self.text_layer_mdfc_right,
            )
        ])

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add special MDFC layers
        psd.getLayer(
            self.twins,
            psd.getLayerSet(LAYERS.TOP, self.dfc_group)
        ).visible = True
        psd.getLayer(
            self.layout.other_face_twins,
            psd.getLayerSet(LAYERS.BOTTOM, self.dfc_group)
        ).visible = True


class PlaneswalkerMDFCExtendedTemplate (PlaneswalkerMDFCTemplate):
    """
    * Extended version of the Planeswalker MDFC template.
    """
    template_suffix = "Extended"

    @property
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PLANESWALKER_ART_FRAME)

    @cached_property
    def is_content_aware_enabled(self):
        return True

    """
    LAYERS
    """

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return


class PlaneswalkerTransformTemplate (PlaneswalkerTemplate):
    """
    * Adds support for Transform functionality to the existing PlaneswalkerTemplate.
    """
    template_file_name = "pw-tf-back"

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    @cached_property
    def transform_icon_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.transform_icon, self.dfc_group)

    def enable_frame_layers(self):
        # Add the transform icon
        super().enable_frame_layers()
        self.transform_icon_layer.visible = True


class PlaneswalkerTransformExtendedTemplate (PlaneswalkerTransformTemplate):
    """
    * Extended version of Planeswalker MDFC Back template.
    """
    template_suffix = "Extended"

    @property
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PLANESWALKER_ART_FRAME)

    @cached_property
    def is_content_aware_enabled(self):
        return True

    """
    LAYERS
    """

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return
