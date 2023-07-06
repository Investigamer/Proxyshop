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

    @cached_property
    def art_frame_vertical(self):
        # Name of art reference layer
        if self.is_colorless:
            return LAYERS.BORDERLESS_FRAME
        return LAYERS.FULL_ART_FRAME

    @cached_property
    def fill_color(self):
        # Textbox mask fill color
        return psd.rgb_black()

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

    @cached_property
    def mask_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.MASKS)

    @cached_property
    def textbox_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet("Ragged Lines", [self.group, LAYERS.TEXTBOX, "Ability Dividers"])

    @cached_property
    def text_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, self.group)

    """
    TEXT LAYERS
    """

    @cached_property
    def top_ref(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PW_TOP_REFERENCE, self.text_group)

    @cached_property
    def adj_ref(self) -> Optional[ArtLayer]:
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

    """
    METHODS
    """

    def basic_text_layers(self):

        # Iterate through abilities to add text layers
        for i, ability in enumerate(self.abilities):

            # Static or activated?
            index = ability.find(": ")
            self.pw_add_ability(ability, index) if 5 > index > 0 else self.pw_add_ability_static(ability)

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

        # Auto-position the ability text, colons, and shields.
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
                psd.align_vertical(self.colons[i], ref_layer)
                difference = self.colons[i].bounds[1] - before
                self.shields[i].translate(0, difference)

        # Add the ability layer mask
        self.pw_ability_mask()

    def pw_add_ability(self, text: str, index: int):
        """
        Add a Planeswalker ability.
        @param text: Ability text to fill in.
        @param index: Location of the ability colon.
        """
        # Determine which loyalty group to enable, and set the loyalty symbol's text
        shield = psd.getLayerSet(text[0], self.loyalty_group)
        psd.getLayer(LAYERS.COST, shield).textItem.contents = text[0:int(index)]
        layer = psd.getLayer(LAYERS.ABILITY_TEXT, self.loyalty_group).duplicate()

        # Add text layer, shields, and colons to list
        self.ability_layers.append(layer)
        if len(self.shields) > 0 and self.shields[-1]:
            # Place each new shield above the last
            self.shields.append(shield.duplicate(self.shields[-1], ElementPlacement.PlaceBefore))
        else:
            self.shields.append(shield.duplicate())
        self.colons.append(psd.getLayer(LAYERS.COLON, self.loyalty_group).duplicate())

        # Add ability text
        self.text.append(
            text_classes.FormattedTextField(
                layer=layer,
                contents=text[index + 2:]
            )
        )

    def pw_add_ability_static(self, text: str):
        """
        Add a Planeswalker static ability.
        @param text: Ability text to fill in.
        """
        # Hide default ability, switch to static
        layer = psd.getLayer(LAYERS.STATIC_TEXT, self.loyalty_group).duplicate()
        self.ability_layers.append(layer)
        self.shields.append(None)
        self.colons.append(None)

        # Is this a double line ability?
        if "\n" in text:
            self.active_layer = layer
            ft.space_after_paragraph(2)

        # Add ability text
        self.text.append(
            text_classes.FormattedTextField(
                layer=layer,
                contents=text
            )
        )

    def pw_ability_mask(self):
        """Position the ragged edge ability mask."""

        # Ragged line layers
        line_top = psd.getLayer(LAYERS.TOP, self.mask_group)
        line_bottom = psd.getLayer(LAYERS.BOTTOM, self.mask_group)

        # Create our line mask pairs
        lines: list[list[ArtLayer]] = []
        for i in range(len(self.ability_layers)-1):
            if lines and len(lines[-1]) == 1:
                lines[-1].append(line_bottom.duplicate(self.textbox_group, ElementPlacement.PlaceInside))
            else:
                lines.append([line_top.duplicate(self.textbox_group, ElementPlacement.PlaceInside)])

        # Position and fill each pair
        n = 0
        for i, group in enumerate(lines):
            # Position the top line, bottom if provided, then fill the area between
            self.position_divider([self.ability_layers[n], self.ability_layers[n+1]], group[0])
            if len(group) == 2:
                self.position_divider([self.ability_layers[n+1], self.ability_layers[n+2]], group[1])
            self.fill_between_dividers(group)
            # Skip every other ability
            n += 2

    @staticmethod
    def position_divider(layers: list[ArtLayer], line: ArtLayer):
        """
        Positions a ragged divider line correctly.
        @param layers: Two layers to position the line between.
        @param line: Line layer to be positioned.
        """
        delta = (layers[1].bounds[1] - layers[0].bounds[3]) / 2
        reference_position = (line.bounds[3] + line.bounds[1]) / 2
        target_position = delta + layers[0].bounds[3]
        line.translate(0, (target_position - reference_position))

    def fill_between_dividers(self, group: list[ArtLayer]):
        """
        Fill area between two ragged lines, or a top line and the bottom of the document.
        @param group: List containing 1 or 2 ragged lines to fill between.
        """
        # If no second line is provided use the bottom of the document
        bottom_bound: int = (group[1].bounds[1] if len(group) == 2 else self.docref.height) + 1
        top_bound = group[0].bounds

        # Create a new layer to fill the selection
        self.active_layer = self.docref.artLayers.add()
        self.active_layer.move(group[0], ElementPlacement.PlaceAfter)

        # Select between the two points and fill
        self.docref.selection.select([
            [top_bound[0] - 200, top_bound[3] - 1],
            [top_bound[2] + 200, top_bound[3] - 1],
            [top_bound[2] + 200, bottom_bound],
            [top_bound[0] - 200, bottom_bound]
        ])
        self.docref.selection.fill(self.fill_color, ColorBlendMode.NormalBlendColor, 100)
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
    def art_frame(self) -> str:
        return LAYERS.ART_FRAME

    @property
    def art_frame_vertical(self):
        return LAYERS.FULL_ART_FRAME

    @property
    def is_fullart(self) -> bool:
        return True

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
    def dfc_group(self) -> Optional[LayerSet]:
        if self.face_type and self.text_group:
            return psd.getLayerSet(self.face_type, LAYERS.MDFC)
        return

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
    def art_frame(self) -> str:
        return LAYERS.ART_FRAME

    @property
    def art_frame_vertical(self):
        return LAYERS.FULL_ART_FRAME

    @property
    def is_fullart(self) -> bool:
        return True

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

    """
    GROUPS
    """

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        if self.face_type and self.text_group:
            return psd.getLayerSet(self.face_type, LAYERS.TRANSFORM)
        return

    """
    TEXT LAYERS
    """

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

    """
    METHODS
    """

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
    def art_frame(self) -> str:
        return LAYERS.ART_FRAME

    @property
    def art_frame_vertical(self):
        return LAYERS.FULL_ART_FRAME

    @property
    def is_fullart(self) -> bool:
        return True

    @cached_property
    def is_content_aware_enabled(self):
        return True

    """
    LAYERS
    """

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return
