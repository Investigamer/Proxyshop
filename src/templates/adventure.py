"""
* ADVENTURE TEMPLATES
"""
# Standard Library
from functools import cached_property
from typing import Callable, Optional, Union

# Third Party Imports
from photoshop.api import SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.layouts import AdventureLayout
from src.helpers import create_color_layer
from src.templates._vector import VectorTemplate
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
import src.helpers as psd


"""
* ADVENTURE MODIFIER CLASSES
"""


class AdventureMod (NormalTemplate):
    """
    * A modifier for adding steps required for Adventure type cards introduced in Throne of Eldraine.

    Adds:
        * Adventure side text layers (Mana cost, name, typeline, and oracle text) and textbox reference.
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Add Adventure text layers."""
        funcs = [self.text_layers_adventure] if isinstance(self.layout, AdventureLayout) else []
        return [*super().text_layer_methods, *funcs]

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name_adventure(self) -> Optional[ArtLayer]:
        """Name for the adventure side."""
        return psd.getLayer(LAYERS.NAME_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_mana_adventure(self) -> Optional[ArtLayer]:
        """Mana cost for the adventure side."""
        return psd.getLayer(LAYERS.MANA_COST_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_type_adventure(self) -> Optional[ArtLayer]:
        """Type line for the adventure side."""
        return psd.getLayer(LAYERS.TYPE_LINE_ADVENTURE, self.text_group)

    @cached_property
    def text_layer_rules_adventure(self) -> Optional[ArtLayer]:
        """Rules text for the adventure side."""
        return psd.getLayer(LAYERS.RULES_TEXT_ADVENTURE, self.text_group)

    @cached_property
    def divider_layer_adventure(self) -> Optional[ArtLayer]:
        """Flavor divider for the adventure side."""
        return psd.getLayer(LAYERS.DIVIDER_ADVENTURE, self.text_group)

    """
    REFERENCES
    """

    @cached_property
    def textbox_reference_adventure(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE_ADVENTURE, self.text_group)

    """
    ADVENTURE METHODS
    """

    def text_layers_adventure(self):

        # Add adventure text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_mana_adventure,
                contents = self.layout.mana_adventure
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_name_adventure,
                contents = self.layout.name_adventure,
                reference = self.text_layer_mana_adventure,
            ),
            text_classes.FormattedTextArea(
                layer = self.text_layer_rules_adventure,
                contents = self.layout.oracle_text_adventure,
                reference = self.textbox_reference_adventure,
                flavor = "", centered = False
            ),
            text_classes.TextField(
                layer = self.text_layer_type_adventure,
                contents = self.layout.type_line_adventure
            )
        ])


class AdventureVectorMod(AdventureMod, VectorTemplate):
    """
    * A vector template modifier for adding steps required for Adventure type cards introduced in Throne of Eldraine.

    Adds:
        * AdventureMod features.
        * Adventure textbox, pinline, wings, and titles.
    """

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        # Add Adventure frame layers step
        funcs = [self.enable_adventure_layers] if isinstance(self.layout, AdventureLayout) else []
        return [*super().frame_layer_methods, *funcs]

    """
    GROUPS
    """

    @cached_property
    def textbox_group(self) -> LayerSet:
        """Use right page of storybook as main textbox group."""
        return psd.getLayerSet(LAYERS.RIGHT, self.adventure_group)

    """
    ADVENTURE GROUPS
    """

    @cached_property
    def adventure_group(self) -> LayerSet:
        """Adventure storybook group."""
        return psd.getLayerSet(LAYERS.STORYBOOK)

    @cached_property
    def adventure_pinlines_group(self) -> LayerSet:
        """Pinline at the bottom of adventure storybook."""
        return psd.getLayerSet(LAYERS.PINLINES, self.adventure_group)

    @cached_property
    def adventure_textbox_group(self) -> LayerSet:
        """Left side storybook page, contains adventure text."""
        return psd.getLayerSet(LAYERS.LEFT, self.adventure_group)

    @cached_property
    def adventure_name_group(self) -> LayerSet:
        """Plate to color for adventure name."""
        return psd.getLayerSet(LAYERS.ADVENTURE_NAME, self.adventure_group)

    @cached_property
    def adventure_typeline_group(self) -> LayerSet:
        """Plate to color for adventure typeline."""
        return psd.getLayerSet(LAYERS.ADVENTURE_TYPELINE, self.adventure_group)

    @cached_property
    def adventure_typeline_accent_group(self) -> LayerSet:
        """Plate to color for adventure typeline accent."""
        return psd.getLayerSet(LAYERS.ADVENTURE_TYPELINE_ACCENT, self.adventure_group)

    @cached_property
    def adventure_wings_group(self) -> LayerSet:
        """Group containing wings on each side of adventure storybook."""
        return psd.getLayerSet(LAYERS.WINGS, self.adventure_group)

    """
    ADVENTURE COLOR MAPS
    """

    @cached_property
    def adventure_name_color_map(self) -> dict:
        """Maps color values to adventure name box."""
        return {
            'W': [179, 172, 156],
            'U': [43, 126, 167],
            'B': [104, 103, 102],
            'R': [159, 83, 59],
            'G': [68, 96, 63],
            'Colorless': [],
            'Gold': [166, 145, 80],
            'Land': [177, 166, 169]
        }

    @cached_property
    def adventure_typeline_color_map(self) -> dict:
        """Maps color values to adventure typeline box."""
        return {
            'W': [129, 120, 103],
            'U': [3, 94, 127],
            'B': [44, 41, 40],
            'R': [124, 51, 33],
            'G': [11, 53, 30],
            'Colorless': [],
            'Gold': [117, 90, 40],
            'Land': [154, 137, 130]
        }

    @cached_property
    def adventure_typeline_accent_color_map(self) -> dict:
        """Maps color values to adventure typeline accent box."""
        return {
            'W': [90, 82, 71],
            'U': [2, 67, 96],
            'B': [20, 17, 19],
            'R': [81, 34, 22],
            'G': [2, 34, 16],
            'Colorless': [],
            'Gold': [75, 62, 37],
            'Land': [115, 98, 89]
        }

    @cached_property
    def adventure_wings_color_map(self) -> dict:
        """Maps color values to adventure wings."""
        return {
            'W': [213, 203, 181],
            'U': [181, 198, 213],
            'B': [162, 155, 152],
            'R': [192, 142, 115],
            'G': [174, 174, 155],
            'Colorless': [],
            'Gold': [196, 172, 131],
            'Land': [194, 178, 177]
        }

    """
    ADVENTURE COLORS
    """

    @cached_property
    def adventure_textbox_colors(self) -> str:
        """Colors to use for adventure textbox textures."""
        return self.layout.adventure_colors

    @cached_property
    def adventure_name_colors(self) -> SolidColor:
        """Colors to use for adventure name box."""
        return psd.get_color(self.adventure_name_color_map.get(self.layout.adventure_colors))

    @cached_property
    def adventure_typeline_colors(self) -> SolidColor:
        """Colors to use for adventure typeline box."""
        return psd.get_color(self.adventure_typeline_color_map.get(self.layout.adventure_colors))

    @cached_property
    def adventure_typeline_accent_colors(self) -> SolidColor:
        """Colors to use for adventure typeline accent box."""
        return psd.get_color(self.adventure_typeline_accent_color_map.get(self.layout.adventure_colors))

    @cached_property
    def adventure_wings_colors(self) -> Callable:
        """Colors to use for adventure wings."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.adventure_wings_color_map
        )

    """
    ADVENTURE BLENDING MASKS
    """

    @cached_property
    def adventure_textbox_masks(self) -> list[ArtLayer]:
        """Masks to use for adventure textbox texture blending."""
        return []

    @cached_property
    def textbox_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [LAYERS.MASKS, LAYERS.RIGHT])]

    """
    ADVENTURE METHODS
    """

    def enable_adventure_layers(self) -> None:
        """Add and modify layers required for Adventure cards."""

        # Add pinlines and wings
        self.pinlines_action(self.pinlines_colors, self.adventure_pinlines_group)
        self.pinlines_action(self.adventure_wings_colors, self.adventure_wings_group)

        # Add textbox
        self.create_blended_layer(
            group=self.adventure_textbox_group,
            colors=self.adventure_textbox_colors,
            masks=self.adventure_textbox_masks)

        # Add twins
        create_color_layer(self.adventure_name_colors, self.adventure_name_group)
        create_color_layer(self.adventure_typeline_colors, self.adventure_typeline_group)
        create_color_layer(self.adventure_typeline_accent_colors, self.adventure_typeline_accent_group)


"""
* ADVENTURE TEMPLATE CLASSES
"""


class AdventureTemplate(AdventureMod, NormalTemplate):
    """Raster template for Adventure cards introduced in Throne of Eldraine."""


class AdventureVectorTemplate(AdventureVectorMod, VectorTemplate):
    """Vector template for Adventure cards introduced in Throne of Eldraine."""

    """
    GROUPS
    """

    @cached_property
    def crown_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def pinlines_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.PINLINES, LAYERS.PINLINES)

    """
    SHAPES
    """

    @cached_property
    def pinlines_legendary_shape(self) -> Optional[ArtLayer]:
        if self.is_legendary:
            return psd.getLayer(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])
        return

    @cached_property
    def pt_shape(self) -> Optional[ArtLayer]:
        if self.is_creature:
            return psd.getLayer(LAYERS.SHAPE, LAYERS.PT_BOX)
        return

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        return [self.border_shape, self.pinlines_legendary_shape, self.pt_shape]

    """
    METHODS
    """

    def enable_crown(self) -> None:
        self.crown_group.parent.visible = True
        super().enable_crown()
