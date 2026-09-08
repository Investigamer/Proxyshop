"""
* PLANESWALKER TEMPLATES
"""

from collections.abc import Callable, Sequence
from functools import cached_property
from logging import getLogger

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import ColorBlendMode, ElementPlacement

import src.helpers as psd
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.helpers import scale_text_layers_to_height
from src.helpers.text import clear_reference_vertical_multi
from src.layouts import NormalLayout, PlaneswalkerAbility, PlaneswalkerLayout
from src.templates._core import StarterTemplate
from src.templates._cosmetic import BorderlessMod, FullartMod
from src.templates.mdfc import MDFCMod
from src.templates.transform import TransformMod
from src.utils.adobe import ReferenceLayer

_logger = getLogger(__name__)

"""
* Template Classes
"""


class PlaneswalkerMod(FullartMod, StarterTemplate):
    """A modifier class which adds methods required for Planeswalker type cards introduced in Lorwyn block.

    Adds:
        * Planeswalker text layers.
        * Planeswalker text layer positioning.
        * Planeswalker ability mask generation.
    """

    frame_suffix = "Normal"

    def __init__(self, layout: NormalLayout):
        super().__init__(layout)

        # Settable Properties
        self._ability_layers: list[ArtLayer] = []
        self._icons: list[ArtLayer | LayerSet | None] = []
        self._colons: list[ArtLayer | LayerSet | None] = []

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add and position Planeswalker text layers, add ability mask."""
        return [*super().text_layer_methods, self.pw_text_layers]

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Add Planeswalker layer positioning and ability mask step."""
        return [
            *super().post_text_methods,
            self.pw_layer_positioning,
            self.pw_ability_mask,
        ]

    """
    * Frame Details
    """

    @cached_property
    def art_frame_vertical(self) -> str:
        """Use special Borderless frame for 'Colorless' cards."""
        if self.is_colorless:
            return LAYERS.BORDERLESS_FRAME
        return LAYERS.FULL_ART_FRAME

    @cached_property
    def ability_text_spacing(self) -> float | int:
        return 64

    @cached_property
    def ability_text_scaling_step_sizes(self) -> Sequence[float] | None:
        return None

    """
    * Planeswalker Details
    """

    @cached_property
    def abilities(self) -> list[PlaneswalkerAbility]:
        """List of Planeswalker abilities data."""
        if isinstance(self.layout, PlaneswalkerLayout):
            return self.layout.pw_abilities
        return []

    @cached_property
    def fill_color(self):
        """Ragged lines mask fill color."""
        return self.RGB_BLACK

    """
    * Planeswalker Layers
    """

    @property
    def ability_layers(self) -> list[ArtLayer]:
        return self._ability_layers

    @ability_layers.setter
    def ability_layers(self, value: list[ArtLayer]):
        self._ability_layers = value

    @property
    def colons(self) -> list[ArtLayer | LayerSet | None]:
        return self._colons

    @colons.setter
    def colons(self, value: list[ArtLayer | LayerSet | None]):
        self._colons = value

    @property
    def icons(self) -> list[ArtLayer | LayerSet | None]:
        return self._icons

    @icons.setter
    def icons(self, value: list[ArtLayer | LayerSet | None]):
        self._icons = value

    """
    * Groups
    """

    @cached_property
    def planeswalker_group(self) -> LayerSet | None:
        """The main Planeswalker layer group, sized according to number of abilities."""
        if isinstance(self.layout, PlaneswalkerLayout) and (
            group := psd.getLayerSet(f"pw-{self.layout.pw_size!s}")
        ):
            group.visible = True
            return group

    @cached_property
    def loyalty_group(self) -> LayerSet | None:
        """Group containing Planeswalker loyalty graphics."""
        return psd.getLayerSet(LAYERS.LOYALTY_GRAPHICS)

    @cached_property
    def border_group(self) -> LayerSet | None:
        """Border group, nested in the appropriate Planeswalker group."""
        return psd.getLayerSet(LAYERS.BORDER, self.planeswalker_group)

    @cached_property
    def mask_group(self) -> LayerSet | None:
        """Group containing the vector shapes used to create the ragged lines divider mask."""
        return psd.getLayerSet(LAYERS.MASKS)

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        """Group to populate with ragged lines divider mask."""
        return psd.getLayerSet(
            "Ragged Lines",
            [self.planeswalker_group, LAYERS.TEXTBOX, "Ability Dividers"],
        )

    @cached_property
    def text_group(self) -> LayerSet | None:
        """Text Layer group, nexted in the appropriate Planeswalker group."""
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, self.planeswalker_group)

    """
    * Frame Layers
    """

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
        return psd.getLayer(
            self.twins, psd.getLayerSet(LAYERS.TWINS, self.planeswalker_group)
        )

    @cached_property
    def pinlines_layer(self) -> ArtLayer | None:
        return psd.getLayer(
            self.pinlines, psd.getLayerSet(LAYERS.PINLINES, self.planeswalker_group)
        )

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        return psd.getLayer(
            self.background, psd.getLayerSet(LAYERS.BACKGROUND, self.planeswalker_group)
        )

    @cached_property
    def color_indicator_layer(self) -> ArtLayer | None:
        return psd.getLayer(
            self.pinlines, [self.planeswalker_group, LAYERS.COLOR_INDICATOR]
        )

    """
    * Text Layers
    """

    @cached_property
    def text_layer_loyalty(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.TEXT, [self.loyalty_group, LAYERS.STARTING_LOYALTY])

    @cached_property
    def text_layer_ability(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.ABILITY_TEXT, self.loyalty_group)

    @cached_property
    def text_layer_static(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.STATIC_TEXT, self.loyalty_group)

    @cached_property
    def text_layer_colon(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.COLON, self.loyalty_group)

    """
    * References
    """

    @cached_property
    def loyalty_reference(self) -> ReferenceLayer | None:
        """ArtLayer: Reference used to check ability layer collision with the loyalty box."""
        return psd.get_reference_layer(LAYERS.LOYALTY_REFERENCE, self.loyalty_group)

    @cached_property
    def textbox_overflow_reference(self) -> ReferenceLayer | None:
        """Rules text is not allowed to go below the top edge of this reference."""
        return None

    """
    * Methods
    """

    def enable_frame_layers(self):
        # Twins
        if self.twins_layer:
            self.twins_layer.visible = True

        # Pinlines
        if self.pinlines_layer:
            self.pinlines_layer.visible = True

        # Background
        if self.background_layer:
            self.background_layer.visible = True

        # Color Indicator
        if self.is_type_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

    """
    * Planeswalker Methods
    """

    def pw_text_layers(self) -> None:
        """Add and modify text layers required by Planeswalker cards."""

        # Iterate through abilities to add text layers
        for ability in self.abilities:
            self.pw_add_ability(ability)

        # Starting loyalty
        if (
            isinstance(self.layout, PlaneswalkerLayout)
            and self.layout.loyalty
            and self.text_layer_loyalty
        ):
            self.text_layer_loyalty.textItem.contents = self.layout.loyalty
        elif self.text_layer_loyalty and isinstance(
            (parent := self.text_layer_loyalty.parent), LayerSet
        ):
            parent.visible = False

    def pw_layer_positioning(self) -> None:
        """Position Planeswalker ability layers and icons."""
        if isinstance(self.layout, PlaneswalkerLayout) and self.textbox_reference:
            # Auto-position the ability text, colons, and shields.
            spacing = self.app.scale_by_dpi(self.ability_text_spacing)
            spaces = len(self.ability_layers) + 1
            total_height = self.textbox_reference.dims["height"] - (spacing * spaces)

            # Resize text items till they fit in the available space
            font_size = scale_text_layers_to_height(
                text_layers=self.ability_layers,
                ref_height=total_height,
                step_sizes=self.ability_text_scaling_step_sizes,
            )

            # Space abilities evenly apart
            uniform_gap = len(self.ability_layers) < 3 or not self.layout.loyalty
            psd.spread_layers_over_reference(
                layers=self.ability_layers,
                ref=self.textbox_reference,
                gap=spacing if not uniform_gap else 0,
            )

            # Adjust text to avoid loyalty badge
            if self.layout.loyalty and self.loyalty_reference:
                clear_reference_vertical_multi(
                    text_layers=self.ability_layers,
                    ref=self.textbox_reference,
                    loyalty_ref=self.loyalty_reference,
                    space=spacing,
                    uniform_gap=uniform_gap,
                    font_size=font_size,
                    docsel=self.doc_selection,
                    bottom_ref=self.textbox_overflow_reference,
                )

            # Align colons and shields to respective text layers
            for i, ref_layer in enumerate(self.ability_layers):
                # Break if we encounter a length mismatch
                if len(self.icons) < (i + 1) or len(self.colons) < (i + 1):
                    _logger.warning(
                        f"Planeswalker ability, icon and colon layers don't match. There's {
                            len(self.ability_layers)
                        } ability layers, {len(self.icons)} icon layers and {
                            len(self.colons)
                        } colon layers."
                    )
                    break
                # Skip if this is a static ability
                if (icon := self.icons[i]) and (colon := self.colons[i]):
                    before = colon.bounds[1]
                    psd.align_vertical(colon, ref_layer)
                    difference = colon.bounds[1] - before
                    icon.translate(0, difference)

    def pw_ability_mask(self) -> None:
        """Position the ragged edge ability mask."""

        # Ragged line layers
        line_top = psd.getLayer(LAYERS.TOP, self.mask_group)
        line_bottom = psd.getLayer(LAYERS.BOTTOM, self.mask_group)

        lines: list[list[ArtLayer]] = []
        if line_top and line_bottom:
            # Create our line mask pairs
            for _i in range(len(self.ability_layers) - 1):
                if lines and len(lines[-1]) == 1:
                    lines[-1].append(
                        line_bottom.duplicate(
                            self.textbox_group, ElementPlacement.PlaceInside
                        )
                    )
                else:
                    lines.append(
                        [
                            line_top.duplicate(
                                self.textbox_group, ElementPlacement.PlaceInside
                            )
                        ]
                    )

        # Position and fill each pair
        n = 0
        for group in lines:
            # Position the top line, bottom if provided, then fill the area between
            self.position_divider(
                [self.ability_layers[n], self.ability_layers[n + 1]], group[0]
            )
            if len(group) == 2:
                self.position_divider(
                    [self.ability_layers[n + 1], self.ability_layers[n + 2]], group[1]
                )
            self.fill_between_dividers(group)
            # Skip every other ability
            n += 2

    """
    * Utility Methods
    """

    def pw_add_ability(self, ability: PlaneswalkerAbility) -> None:
        """Add a Planeswalker ability.

        Args:
            ability: Planeswalker ability data.
        """
        # Create an icon and colon if this isn't a static ability
        static = not (ability.get("icon") and ability.get("cost"))
        icon = (
            None
            if static
            else psd.getLayerSet(ability.get("icon", "0"), self.loyalty_group)
        )
        colon = (
            None
            if static
            else self.text_layer_colon.duplicate()
            if self.text_layer_colon
            else None
        )

        # Update ability cost if needed
        if not static:
            if layer := psd.getLayer(LAYERS.COST, icon):
                layer.textItem.contents = ability.get("cost", "0")
            if icon:
                icon = (
                    icon.duplicate(self.icons[-1], ElementPlacement.PlaceBefore)
                    if (self.icons and self.icons[-1])
                    else icon.duplicate()
                )

        # Add ability, icons, and colons
        self.icons.append(icon)
        self.colons.append(colon)
        if static:
            if self.text_layer_static:
                self.ability_layers.append(self.text_layer_static.duplicate())
        elif self.text_layer_ability:
            self.ability_layers.append(self.text_layer_ability.duplicate())
        self.text.append(
            text_classes.FormattedTextField(
                layer=self.ability_layers[-1], contents=ability.get("text", "")
            )
        )

    def fill_between_dividers(self, group: list[ArtLayer]) -> None:
        """Fill area between two ragged lines, or a top line and the bottom of the document.

        Args:
            group: List containing 1 or 2 ragged lines to fill between.
        """
        # If no second line is provided use the bottom of the document
        bottom_bound = (
            group[1].bounds[1] if len(group) == 2 else self.docref.height
        ) + 1
        top_bound = group[0].bounds

        # Create a new layer to fill the selection
        self.active_layer = self.docref.artLayers.add()
        self.active_layer.move(group[0], ElementPlacement.PlaceAfter)

        # Select between the two points and fill
        self.doc_selection.select(
            (
                (top_bound[0] - 200, top_bound[3] - 1),
                (top_bound[2] + 200, top_bound[3] - 1),
                (top_bound[2] + 200, bottom_bound),
                (top_bound[0] - 200, bottom_bound),
            )
        )
        self.doc_selection.fill(self.fill_color, ColorBlendMode.NormalBlendColor, 100)
        self.doc_selection.deselect()

    @staticmethod
    def position_divider(layers: list[ArtLayer], line: ArtLayer) -> None:
        """Positions a ragged divider line for an ability text mask.

        Args:
            layers: Two layers to position the line between.
            line: Line layer to be positioned.
        """
        delta = (layers[1].bounds[1] - layers[0].bounds[3]) / 2
        reference_position = (line.bounds[3] + line.bounds[1]) / 2
        target_position = delta + layers[0].bounds[3]
        line.translate(0, (target_position - reference_position))


"""
* Template Classes
"""


class PlaneswalkerTemplate(PlaneswalkerMod, StarterTemplate):
    """Core Planeswalker 'Normal' M15-style template."""


class PlaneswalkerBorderlessTemplate(BorderlessMod, PlaneswalkerTemplate):
    """A Borderless version of PlaneswalkerTemplate."""

    """
    * Details
    """

    @cached_property
    def art_frame_vertical(self) -> str:
        """No separation for 'Colorless' cards."""
        return LAYERS.FULL_ART_FRAME


"""
* MDFC Planeswalker Classes, introduced in Kaldheim.
"""


class PlaneswalkerMDFCTemplate(MDFCMod, PlaneswalkerTemplate):
    """Adds MDFC functionality to the existing PlaneswalkerTemplate."""

    """
    * Groups
    """

    @cached_property
    def dfc_group(self) -> LayerSet | None:
        """LayerSet: DFC group at top level."""
        face = LAYERS.FRONT if self.is_front else LAYERS.BACK
        return psd.getLayerSet(f"{LAYERS.MDFC} {face}")

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        """ArtLayer: Name is always shifted."""
        return psd.getLayer(LAYERS.NAME, self.text_group)


class PlaneswalkerMDFCBorderlessTemplate(MDFCMod, PlaneswalkerBorderlessTemplate):
    """Adds MDFC functionality to the existing PlaneswalkerExtendedTemplate."""

    """
    * Groups
    """

    @cached_property
    def dfc_group(self) -> LayerSet | None:
        """LayerSet: DFC group at top level."""
        face = LAYERS.FRONT if self.is_front else LAYERS.BACK
        return psd.getLayerSet(f"{LAYERS.MDFC} {face}")

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        """ArtLayer: Name is always shifted."""
        return psd.getLayer(LAYERS.NAME, self.text_group)


"""
* Transform Planeswalker Classes, introduced in Innistrad.
"""


class PlaneswalkerTFTemplate(TransformMod, PlaneswalkerTemplate):
    """Adds Transform functionality to the existing PlaneswalkerTemplate."""

    """
    * Groups
    """

    @cached_property
    def dfc_group(self) -> LayerSet | None:
        """LayerSet: DFC group at top level."""
        return psd.getLayerSet(
            LAYERS.FRONT if self.is_front else LAYERS.BACK, LAYERS.TRANSFORM
        )

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        """ArtLayer: Name is always shifted."""
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_type(self) -> ArtLayer | None:
        """ArtLayer: Typeline is always shifted."""
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    """
    * Transform Methods
    """

    def text_layers_transform(self):
        """No text changes needed."""


class PlaneswalkerTFBorderlessTemplate(TransformMod, PlaneswalkerBorderlessTemplate):
    """Adds Transform functionality to the existing PlaneswalkerBorderlessTemplate."""

    """
    * Groups
    """

    @cached_property
    def dfc_group(self) -> LayerSet | None:
        """LayerSet: DFC group at top level."""
        return psd.getLayerSet(
            LAYERS.FRONT if self.is_front else LAYERS.BACK, LAYERS.TRANSFORM
        )

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        """ArtLayer: Name is always shifted."""
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_type(self) -> ArtLayer | None:
        """ArtLayer: Typeline is always shifted."""
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    """
    * Transform Methods
    """

    def text_layers_transform(self):
        """No text changes needed."""
