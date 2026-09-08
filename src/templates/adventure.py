"""
* Adventure Templates
"""

from collections.abc import Callable
from functools import cached_property

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import AdventureLayout
from src.schema.colors import ColorObject, GradientConfig
from src.templates._core import NormalTemplate
from src.templates._vector import VectorTemplate

"""
* Modifier Classes
"""


class AdventureMod(NormalTemplate):
    """A modifier class which adds functionality required by Adventure cards, introduced in Throne of Eldraine.

    Adds:
        * Adventure side text layers (Mana cost, name, typeline, and oracle text) and textbox reference.
    """

    """
    * Mixin Methods
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Adventure text layers step."""
        funcs = (
            [self.text_layers_adventure]
            if isinstance(self.layout, AdventureLayout)
            else []
        )
        return [*super().text_layer_methods, *funcs]

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name_adventure(self) -> ArtLayer | None:
        """Name for the adventure side."""
        return psd.getLayer(LAYERS.NAME_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_mana_adventure(self) -> ArtLayer | None:
        """Mana cost for the adventure side."""
        return psd.getLayer(LAYERS.MANA_COST_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_type_adventure(self) -> ArtLayer | None:
        """Type line for the adventure side."""
        return psd.getLayer(LAYERS.TYPE_LINE_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_rules_adventure(self) -> ArtLayer | None:
        """Rules text for the adventure side."""
        return psd.getLayer(LAYERS.RULES_TEXT_ADVENTURE, self.text_group)

    @cached_property
    def divider_layer_adventure(self) -> ArtLayer | None:
        """Flavor divider for the adventure side."""
        return psd.getLayer(LAYERS.DIVIDER_ADVENTURE, self.text_group)

    """
    * References
    """

    @cached_property
    def textbox_reference_adventure(self) -> ArtLayer | None:
        return psd.get_reference_layer(
            LAYERS.TEXTBOX_REFERENCE_ADVENTURE, self.text_group
        )

    """
    * Adventure Methods
    """

    def text_layers_adventure(self):
        if isinstance(self.layout, AdventureLayout):
            # Add adventure text layers

            if self.text_layer_mana_adventure:
                self.text.append(
                    text_classes.FormattedTextField(
                        layer=self.text_layer_mana_adventure,
                        contents=self.layout.mana_adventure,
                    )
                )
            if self.text_layer_name_adventure:
                self.text.append(
                    text_classes.ScaledTextField(
                        layer=self.text_layer_name_adventure,
                        contents=self.layout.name_adventure,
                        reference=self.text_layer_mana_adventure,
                    )
                )
            if self.text_layer_rules_adventure:
                self.text.append(
                    text_classes.FormattedTextArea(
                        layer=self.text_layer_rules_adventure,
                        contents=self.layout.oracle_text_adventure,
                        reference=self.textbox_reference_adventure,
                        flavor=self.layout.flavor_text_adventure,
                        centered=False,
                    )
                )
            if self.text_layer_type_adventure:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_type_adventure,
                        contents=self.layout.type_line_adventure,
                    )
                )


class AdventureVectorMod(AdventureMod, VectorTemplate):
    """
    * A vector template modifier for adding steps required for Adventure type cards introduced in Throne of Eldraine.

    Adds:
        * AdventureMod features.
        * Adventure textbox, pinline, wings, and titles.
    """

    # Color Maps
    @cached_property
    def adventure_name_color_map(self) -> dict[str, tuple[float, float, float]]:
        """Maps color values to adventure name box."""
        return {
            "W": (179, 172, 156),
            "U": (43, 126, 167),
            "B": (104, 103, 102),
            "R": (159, 83, 59),
            "G": (68, 96, 63),
            # There are no colorless adventure cards as of now
            "Colorless": (-1, -1, -1),
            "Gold": (166, 145, 80),
            "Land": (177, 166, 169),
        }

    @cached_property
    def adventure_typeline_color_map(self) -> dict[str, tuple[float, float, float]]:
        """Maps color values to adventure typeline box."""
        return {
            "W": (129, 120, 103),
            "U": (3, 94, 127),
            "B": (44, 41, 40),
            "R": (124, 51, 33),
            "G": (11, 53, 30),
            "Colorless": (-1, -1, -1),
            "Gold": (117, 90, 40),
            "Land": (154, 137, 130),
        }

    @cached_property
    def adventure_typeline_accent_color_map(
        self,
    ) -> dict[str, tuple[float, float, float]]:
        """Maps color values to adventure typeline accent box."""
        return {
            "W": (90, 82, 71),
            "U": (2, 67, 96),
            "B": (20, 17, 19),
            "R": (81, 34, 22),
            "G": (2, 34, 16),
            "Colorless": (-1, -1, -1),
            "Gold": (75, 62, 37),
            "Land": (115, 98, 89),
        }

    @cached_property
    def adventure_wings_color_map(self) -> dict[str, tuple[float, float, float]]:
        """Maps color values to adventure wings."""
        return {
            "W": (213, 203, 181),
            "U": (181, 198, 213),
            "B": (162, 155, 152),
            "R": (192, 142, 115),
            "G": (174, 174, 155),
            "Colorless": (-1, -1, -1),
            "Gold": (196, 172, 131),
            "Land": (194, 178, 177),
        }

    """
    * Mixin Methods
    """

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        """Add Adventure frame layers step."""
        funcs = (
            [self.enable_adventure_layers]
            if isinstance(self.layout, AdventureLayout)
            else []
        )
        return [*super().frame_layer_methods, *funcs]

    """
    * Groups
    """

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        """LayerSet: Use right page of storybook as main textbox group."""
        return psd.getLayerSet(LAYERS.RIGHT, self.adventure_group)

    """
    * Adventure Groups
    """

    @cached_property
    def adventure_group(self) -> LayerSet | None:
        """Adventure storybook group."""
        return psd.getLayerSet(LAYERS.STORYBOOK)

    @cached_property
    def adventure_pinlines_group(self) -> LayerSet | None:
        """Pinline at the bottom of adventure storybook."""
        return psd.getLayerSet(LAYERS.PINLINES, self.adventure_group)

    @cached_property
    def adventure_textbox_group(self) -> LayerSet | None:
        """Left side storybook page, contains adventure text."""
        return psd.getLayerSet(LAYERS.LEFT, self.adventure_group)

    @cached_property
    def adventure_name_group(self) -> LayerSet | None:
        """Plate to color for adventure name."""
        return psd.getLayerSet(LAYERS.ADVENTURE_NAME, self.adventure_group)

    @cached_property
    def adventure_typeline_group(self) -> LayerSet | None:
        """Plate to color for adventure typeline."""
        return psd.getLayerSet(LAYERS.ADVENTURE_TYPELINE, self.adventure_group)

    @cached_property
    def adventure_typeline_accent_group(self) -> LayerSet | None:
        """Plate to color for adventure typeline accent."""
        return psd.getLayerSet(LAYERS.ADVENTURE_TYPELINE_ACCENT, self.adventure_group)

    @cached_property
    def adventure_wings_group(self) -> LayerSet | None:
        """Group containing wings on each side of adventure storybook."""
        return psd.getLayerSet(LAYERS.WINGS, self.adventure_group)

    """
    * Adventure Colors
    """

    @cached_property
    def adventure_textbox_colors(self) -> str:
        """Colors to use for adventure textbox textures."""
        if isinstance(self.layout, AdventureLayout):
            return self.layout.adventure_colors
        return ""

    @cached_property
    def adventure_name_colors(self) -> tuple[float, float, float]:
        """Colors to use for adventure name box."""
        if isinstance(self.layout, AdventureLayout):
            return self.adventure_name_color_map.get(
                self.layout.adventure_colors, (0, 0, 0)
            )
        return (0, 0, 0)

    @cached_property
    def adventure_typeline_colors(self) -> tuple[float, float, float]:
        """Colors to use for adventure typeline box."""
        if isinstance(self.layout, AdventureLayout):
            return self.adventure_typeline_color_map.get(
                self.layout.adventure_colors, (0, 0, 0)
            )
        return (0, 0, 0)

    @cached_property
    def adventure_typeline_accent_colors(self) -> tuple[float, float, float]:
        """Colors to use for adventure typeline accent box."""
        if isinstance(self.layout, AdventureLayout):
            return self.adventure_typeline_accent_color_map.get(
                self.layout.adventure_colors, (0, 0, 0)
            )
        return (0, 0, 0)

    @cached_property
    def adventure_wings_colors(self) -> ColorObject | list[GradientConfig]:
        """Colors to use for adventure wings."""
        return psd.get_pinline_gradient(
            self.identity
            if 1 < len(self.identity) < self.color_limit
            else self.pinlines,
            color_map=self.adventure_wings_color_map,
        )

    """
    * Adventure Blending Masks
    """

    @cached_property
    def adventure_textbox_masks(self) -> list[ArtLayer]:
        """Masks to use for adventure textbox texture blending."""
        return []

    @cached_property
    def textbox_masks(self) -> list[ArtLayer]:
        if layer := psd.getLayer(LAYERS.HALF, [LAYERS.MASKS, LAYERS.RIGHT]):
            return [layer]
        return []

    """
    * Adventure Frame Methods
    """

    def enable_adventure_layers(self) -> None:
        """Add and modify layers required for Adventure cards."""

        if self.adventure_pinlines_group:
            # Pinlines
            self.generate_layer(
                group=self.adventure_pinlines_group, colors=self.pinlines_colors
            )

        if self.adventure_wings_group:
            # Wings
            self.generate_layer(
                group=self.adventure_wings_group, colors=self.adventure_wings_colors
            )

        if self.adventure_textbox_group:
            # textbox
            self.generate_layer(
                group=self.adventure_textbox_group,
                colors=self.adventure_textbox_colors,
                masks=self.adventure_textbox_masks,
            )

        if self.adventure_name_group:
            # Adventure Name
            self.generate_layer(
                group=self.adventure_name_group, colors=self.adventure_name_colors
            )

        if self.adventure_typeline_group:
            # Adventure Typeline
            self.generate_layer(
                group=self.adventure_typeline_group,
                colors=self.adventure_typeline_colors,
            )

        if self.adventure_typeline_accent_group:
            # Adventure Accent
            self.generate_layer(
                group=self.adventure_typeline_accent_group,
                colors=self.adventure_typeline_accent_colors,
            )


"""
* Template Classes
"""


class AdventureTemplate(AdventureMod, NormalTemplate):
    """Raster template for Adventure cards introduced in Throne of Eldraine."""


class AdventureVectorTemplate(AdventureVectorMod, VectorTemplate):
    """Vector template for Adventure cards introduced in Throne of Eldraine."""

    """
    * Groups
    """

    @cached_property
    def crown_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def pinlines_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.PINLINES, LAYERS.PINLINES)

    """
    * Shapes
    """

    @cached_property
    def pinlines_legendary_shape(self) -> ArtLayer | None:
        if self.is_legendary:
            return psd.getLayer(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])
        return

    @cached_property
    def pt_shape(self) -> ArtLayer | None:
        if self.is_creature:
            return psd.getLayer(LAYERS.SHAPE, LAYERS.PT_BOX)
        return

    @cached_property
    def enabled_shapes(self) -> list[ArtLayer | LayerSet | None]:
        return [self.border_shape, self.pinlines_legendary_shape, self.pt_shape]

    """
    METHODS
    """

    def enable_crown(self) -> None:
        if self.crown_group and isinstance(
            (parent := self.crown_group.parent), LayerSet
        ):
            parent.visible = True
        super().enable_crown()
