"""
* PLANESWALKER TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional, Callable

# Third Party Imports
from photoshop.api import ElementPlacement, ColorBlendMode
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._core import StarterTemplate
from src.templates._mods import MDFCMod, TransformMod
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import PlaneswalkerLayouts
import src.format_text as ft
import src.helpers as psd


class PlaneswalkerTemplate (StarterTemplate):
    """
    * The main Planeswalker template to extend to for essential Planeswalker support.
    * Does not support MDFC or Transform Planeswalker cards.
    """

    def __init__(self, layout: PlaneswalkerLayouts, **kwargs):
        super().__init__(layout, **kwargs)

        # Settable Properties
        self._ability_layers = []
        self._icons = []
        self._colons = []

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Add Planeswalker text layers."""
        return [*super().text_layer_methods, self.pw_text_layers]

    @cached_property
    def general_methods(self) -> list[Callable]:
        """Add Planeswalker layer positioning and ability mask step."""
        return [
            *super().general_methods,
            self.pw_layer_positioning,
            self.pw_ability_mask
        ]

    """
    DETAILS
    """

    @cached_property
    def abilities(self) -> list[dict]:
        """List of Planeswalker abilities data."""
        return self.layout.pw_abilities

    @cached_property
    def art_frame_vertical(self):
        """Use special Borderless frame for Colorless cards."""
        if self.is_colorless:
            return LAYERS.BORDERLESS_FRAME
        return LAYERS.FULL_ART_FRAME

    @cached_property
    def fill_color(self):
        """Ragged lines mask fill color."""
        return self.RGB_BLACK

    """
    TOGGLE
    """

    @cached_property
    def is_fullart(self) -> bool:
        """Always prefer vertical art."""
        return True

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        """Always content aware fill non-vertical art."""
        return True if not self.is_art_vertical else False

    """
    PLANESWALKER LAYERS
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
    def icons(self) -> list:
        return self._icons

    @icons.setter
    def icons(self, value):
        self._icons = value

    """
    GROUPS
    """

    @cached_property
    def group(self) -> LayerSet:
        """The main Planeswalker layer group, sized according to number of abilities."""
        if group := psd.getLayerSet(f"pw-{str(self.layout.pw_size)}"):
            group.visible = True
            return group

    @cached_property
    def loyalty_group(self) -> LayerSet:
        """Group containing Planeswalker loyalty graphics."""
        return psd.getLayerSet(LAYERS.LOYALTY_GRAPHICS)

    @cached_property
    def border_group(self) -> Optional[LayerSet]:
        """Border group, nested in the appropriate Planeswalker group."""
        return psd.getLayerSet(LAYERS.BORDER, self.group)

    @cached_property
    def mask_group(self) -> Optional[LayerSet]:
        """Group containing the vector shapes used to create the ragged lines divider mask."""
        return psd.getLayerSet(LAYERS.MASKS)

    @cached_property
    def textbox_group(self) -> Optional[LayerSet]:
        """Group to populate with ragged lines divider mask."""
        return psd.getLayerSet("Ragged Lines", [self.group, LAYERS.TEXTBOX, "Ability Dividers"])

    @cached_property
    def text_group(self) -> LayerSet:
        """Text Layer group, nexted in the appropriate Planeswalker group."""
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, self.group)

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
    TEXT LAYERS
    """

    @cached_property
    def text_layer_loyalty(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TEXT, [self.loyalty_group, LAYERS.STARTING_LOYALTY])

    @cached_property
    def text_layer_ability(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ABILITY_TEXT, self.loyalty_group)

    @cached_property
    def text_layer_static(self) -> ArtLayer:
        return psd.getLayer(LAYERS.STATIC_TEXT, self.loyalty_group)

    @cached_property
    def text_layer_colon(self) -> ArtLayer:
        return psd.getLayer(LAYERS.COLON, self.loyalty_group)

    """
    REFERENCES
    """

    @cached_property
    def top_ref(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PW_TOP_REFERENCE, self.text_group)

    @cached_property
    def adj_ref(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PW_ADJUSTMENT_REFERENCE, self.text_group)

    """
    METHODS
    """

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

    """
    PLANESWALKER METHODS
    """

    def pw_text_layers(self) -> None:
        """Add and modify text layers required by Planeswalker cards."""

        # Iterate through abilities to add text layers
        for ability in self.abilities:
            self.pw_add_ability(ability)

        # Starting loyalty
        if self.layout.loyalty:
            self.text_layer_loyalty.textItem.contents = self.layout.loyalty
        else:
            self.text_layer_loyalty.parent.visible = False

    def pw_layer_positioning(self) -> None:
        """Position Planeswalker ability layers and icons."""

        # Auto-position the ability text, colons, and shields.
        spacing = self.app.scale_by_dpi(64)
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
            if len(self.icons) < (i + 1) or len(self.colons) < (i + 1):
                self.raise_warning("Encountered bizarre Planeswalker data!")
                break
            # Skip if this is a static ability
            if self.icons[i] and self.colons[i]:
                before = self.colons[i].bounds[1]
                psd.align_vertical(self.colons[i], ref_layer)
                difference = self.colons[i].bounds[1] - before
                self.icons[i].translate(0, difference)

    def pw_ability_mask(self) -> None:
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

    """
    PLANESWALKER UTILITY METHODS
    """

    def pw_add_ability(self, ability: dict) -> None:
        """
        Add a Planeswalker ability.
        @param ability: Planeswalker ability data.
        """
        # Create an icon and colon if this isn't a static ability
        static = False if ability.get('icon') and ability.get('cost') else True
        icon = None if static else psd.getLayerSet(ability.get('icon', '0'), self.loyalty_group)
        colon = None if static else self.text_layer_colon.duplicate()

        # Update ability cost if needed
        if not static:
            psd.getLayer(LAYERS.COST, icon).textItem.contents = ability.get('cost', '0')
            icon = icon.duplicate(*[self.icons[-1], ElementPlacement.PlaceBefore]) if (
                self.icons and self.icons[-1]
            ) else icon.duplicate()

        # Add ability, icons, and colons
        self.icons.append(icon)
        self.colons.append(colon)
        self.ability_layers.append(
            self.text_layer_static.duplicate() if static
            else self.text_layer_ability.duplicate())
        self.text.append(
            text_classes.FormattedTextField(
                layer=self.ability_layers[-1],
                contents=ability.get('text', '')
            ))

    def fill_between_dividers(self, group: list[ArtLayer]) -> None:
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

    @staticmethod
    def position_divider(layers: list[ArtLayer], line: ArtLayer) -> None:
        """
        Positions a ragged divider line correctly.
        @param layers: Two layers to position the line between.
        @param line: Line layer to be positioned.
        """
        delta = (layers[1].bounds[1] - layers[0].bounds[3]) / 2
        reference_position = (line.bounds[3] + line.bounds[1]) / 2
        target_position = delta + layers[0].bounds[3]
        line.translate(0, (target_position - reference_position))


class PlaneswalkerExtendedTemplate (PlaneswalkerTemplate):
    """
    * An extended version of PlaneswalkerTemplate.
    * Functionally identical except for the lack of background textures.
    """
    template_suffix = "Extended"

    """
    DETAILS
    """

    @property
    def art_frame_vertical(self) -> str:
        return LAYERS.FULL_ART_FRAME

    """
    PROPERTIES
    """

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


"""
* MDFC PLANESWALKERS, introduced in Kaldheim.
"""


class PlaneswalkerMDFCTemplate (MDFCMod, PlaneswalkerTemplate):
    """Adds support for MDFC functionality to the existing PlaneswalkerTemplate."""

    """
    GROUPS
    """

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        # Both DFC groups at top level
        return psd.getLayerSet(self.face_type, LAYERS.MDFC)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.NAME, self.text_group)


class PlaneswalkerMDFCExtendedTemplate (MDFCMod, PlaneswalkerExtendedTemplate):
    """Adds support for MDFC functionality to the existing PlaneswalkerExtendedTemplate."""
    template_suffix = "Extended"

    """
    GROUPS
    """

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        # Both DFC groups at top level
        return psd.getLayerSet(self.face_type, LAYERS.MDFC)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.NAME, self.text_group)


"""
* TRANSFORM PLANESWALKERS, introduced in Innistrad block.
"""


class PlaneswalkerTransformTemplate (TransformMod, PlaneswalkerTemplate):
    """Adds support for Transform functionality to the existing PlaneswalkerTemplate."""

    """
    GROUPS
    """

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        # Transform group at top level
        return psd.getLayerSet(self.face_type, LAYERS.TRANSFORM)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name always shifted
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # Typeline always shifted
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    """
    METHODS
    """

    def text_layers_transform(self):
        # No text changes needed
        pass


class PlaneswalkerTransformExtendedTemplate (TransformMod, PlaneswalkerExtendedTemplate):
    """Adds support for Transform functionality to the existing PlaneswalkerExtendedTemplate."""
    template_suffix = "Extended"

    """
    GROUPS
    """

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        # Transform group at top level
        return psd.getLayerSet(self.face_type, LAYERS.TRANSFORM)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name always shifted
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # Typeline always shifted
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    """
    METHODS
    """

    def text_layers_transform(self):
        # No text changes needed
        pass
