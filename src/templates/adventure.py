"""
* Adventure Templates
"""
# Standard Library
from typing import Callable, Optional, Union

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.layers import LAYERS
import src.helpers as psd
from src.layouts import AdventureLayout
from src.templates._vector import VectorTemplate
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.utils.properties import auto_prop_cached

"""
* Modifier Classes
"""


class AdventureMod(NormalTemplate):
    """A modifier class which adds functionality required by Adventure cards, introduced in Throne of Eldraine.

    Adds:
        * Adventure side text layers (Mana cost, name, typeline, and oracle text) and textbox reference.
    """

    def __init__(self, layout: AdventureLayout, **kwargs):
        super().__init__(layout, **kwargs)

    """
    * Mixin Methods
    """

    @auto_prop_cached
    def text_layer_methods(self) -> list[Callable]:
        """Add Adventure text layers step."""
        funcs = [self.text_layers_adventure] if isinstance(self.layout, AdventureLayout) else []
        return [*super().text_layer_methods, *funcs]

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_name_adventure(self) -> Optional[ArtLayer]:
        """Name for the adventure side."""
        return psd.getLayer(LAYERS.NAME_ADVENTURE, self.text_group)

    @auto_prop_cached
    def text_layer_mana_adventure(self) -> Optional[ArtLayer]:
        """Mana cost for the adventure side."""
        return psd.getLayer(LAYERS.MANA_COST_ADVENTURE, self.text_group)

    @auto_prop_cached
    def text_layer_type_adventure(self) -> Optional[ArtLayer]:
        """Type line for the adventure side."""
        return psd.getLayer(LAYERS.TYPE_LINE_ADVENTURE, self.text_group)

    @auto_prop_cached
    def text_layer_rules_adventure(self) -> Optional[ArtLayer]:
        """Rules text for the adventure side."""
        return psd.getLayer(LAYERS.RULES_TEXT_ADVENTURE, self.text_group)

    @auto_prop_cached
    def divider_layer_adventure(self) -> Optional[ArtLayer]:
        """Flavor divider for the adventure side."""
        return psd.getLayer(LAYERS.DIVIDER_ADVENTURE, self.text_group)

    """
    * References
    """

    @auto_prop_cached
    def textbox_reference_adventure(self) -> Optional[ArtLayer]:
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE_ADVENTURE, self.text_group)

    """
    * Adventure Methods
    """

    def text_layers_adventure(self):
        # Add adventure text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer=self.text_layer_mana_adventure,
                contents=self.layout.mana_adventure
            ),
            text_classes.ScaledTextField(
                layer=self.text_layer_name_adventure,
                contents=self.layout.name_adventure,
                reference=self.text_layer_mana_adventure,
            ),
            text_classes.FormattedTextArea(
                layer=self.text_layer_rules_adventure,
                contents=self.layout.oracle_text_adventure,
                reference=self.textbox_reference_adventure,
                flavor=self.layout.flavor_text_adventure,
                centered=False
            ),
            text_classes.TextField(
                layer=self.text_layer_type_adventure,
                contents=self.layout.type_line_adventure
            )
        ])


class AdventureVectorMod(AdventureMod, VectorTemplate):
    """
    * A vector template modifier for adding steps required for Adventure type cards introduced in Throne of Eldraine.

    Adds:
        * AdventureMod features.
        * Adventure textbox, pinline, wings, and titles.
    """

    # Color Maps
    """Maps color values to adventure name box."""
    adventure_name_color_map = {
        'W': [179, 172, 156],
        'U': [43, 126, 167],
        'B': [104, 103, 102],
        'R': [159, 83, 59],
        'G': [68, 96, 63],
        'Colorless': [],
        'Gold': [166, 145, 80],
        'Land': [177, 166, 169]
    }
    """Maps color values to adventure typeline box."""
    adventure_typeline_color_map = {
        'W': [129, 120, 103],
        'U': [3, 94, 127],
        'B': [44, 41, 40],
        'R': [124, 51, 33],
        'G': [11, 53, 30],
        'Colorless': [],
        'Gold': [117, 90, 40],
        'Land': [154, 137, 130]
    }
    """Maps color values to adventure typeline accent box."""
    adventure_typeline_accent_color_map = {
        'W': [90, 82, 71],
        'U': [2, 67, 96],
        'B': [20, 17, 19],
        'R': [81, 34, 22],
        'G': [2, 34, 16],
        'Colorless': [],
        'Gold': [75, 62, 37],
        'Land': [115, 98, 89]
    }
    """Maps color values to adventure wings."""
    adventure_wings_color_map = {
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
    * Mixin Methods
    """

    @auto_prop_cached
    def frame_layer_methods(self) -> list[Callable]:
        """Add Adventure frame layers step."""
        funcs = [self.enable_adventure_layers] if isinstance(self.layout, AdventureLayout) else []
        return [*super().frame_layer_methods, *funcs]

    """
    * Groups
    """

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """LayerSet: Use right page of storybook as main textbox group."""
        return psd.getLayerSet(LAYERS.RIGHT, self.adventure_group)

    """
    * Adventure Groups
    """

    @auto_prop_cached
    def adventure_group(self) -> LayerSet:
        """Adventure storybook group."""
        return psd.getLayerSet(LAYERS.STORYBOOK)

    @auto_prop_cached
    def adventure_pinlines_group(self) -> LayerSet:
        """Pinline at the bottom of adventure storybook."""
        return psd.getLayerSet(LAYERS.PINLINES, self.adventure_group)

    @auto_prop_cached
    def adventure_textbox_group(self) -> LayerSet:
        """Left side storybook page, contains adventure text."""
        return psd.getLayerSet(LAYERS.LEFT, self.adventure_group)

    @auto_prop_cached
    def adventure_name_group(self) -> LayerSet:
        """Plate to color for adventure name."""
        return psd.getLayerSet(LAYERS.ADVENTURE_NAME, self.adventure_group)

    @auto_prop_cached
    def adventure_typeline_group(self) -> LayerSet:
        """Plate to color for adventure typeline."""
        return psd.getLayerSet(LAYERS.ADVENTURE_TYPELINE, self.adventure_group)

    @auto_prop_cached
    def adventure_typeline_accent_group(self) -> LayerSet:
        """Plate to color for adventure typeline accent."""
        return psd.getLayerSet(LAYERS.ADVENTURE_TYPELINE_ACCENT, self.adventure_group)

    @auto_prop_cached
    def adventure_wings_group(self) -> LayerSet:
        """Group containing wings on each side of adventure storybook."""
        return psd.getLayerSet(LAYERS.WINGS, self.adventure_group)

    """
    * Adventure Colors
    """

    @auto_prop_cached
    def adventure_textbox_colors(self) -> str:
        """Colors to use for adventure textbox textures."""
        return self.layout.adventure_colors

    @auto_prop_cached
    def adventure_name_colors(self) -> list[int]:
        """Colors to use for adventure name box."""
        return self.adventure_name_color_map.get(self.layout.adventure_colors)

    @auto_prop_cached
    def adventure_typeline_colors(self) -> list[int]:
        """Colors to use for adventure typeline box."""
        return self.adventure_typeline_color_map.get(self.layout.adventure_colors)

    @auto_prop_cached
    def adventure_typeline_accent_colors(self) -> list[int]:
        """Colors to use for adventure typeline accent box."""
        return self.adventure_typeline_accent_color_map.get(self.layout.adventure_colors)

    @auto_prop_cached
    def adventure_wings_colors(self) -> Union[list[int], list[dict]]:
        """Colors to use for adventure wings."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.adventure_wings_color_map)

    """
    * Adventure Blending Masks
    """

    @auto_prop_cached
    def adventure_textbox_masks(self) -> list[ArtLayer]:
        """Masks to use for adventure textbox texture blending."""
        return []

    @auto_prop_cached
    def textbox_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [LAYERS.MASKS, LAYERS.RIGHT])]

    """
    * Adventure Frame Methods
    """

    def enable_adventure_layers(self) -> None:
        """Add and modify layers required for Adventure cards."""

        # Pinlines
        self.generate_layer(
            group=self.adventure_pinlines_group,
            colors=self.pinlines_colors)

        # Wings
        self.generate_layer(
            group=self.adventure_wings_group,
            colors=self.adventure_wings_colors)

        # textbox
        self.generate_layer(
            group=self.adventure_textbox_group,
            colors=self.adventure_textbox_colors,
            masks=self.adventure_textbox_masks)

        # Adventure Name
        self.generate_layer(
            group=self.adventure_name_group,
            colors=self.adventure_name_colors)

        # Adventure Typeline
        self.generate_layer(
            group=self.adventure_typeline_group,
            colors=self.adventure_typeline_colors)

        # Adventure Accent
        self.generate_layer(
            group=self.adventure_typeline_accent_group,
            colors=self.adventure_typeline_accent_colors)


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

    @auto_prop_cached
    def crown_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, LAYERS.LEGENDARY_CROWN)

    @auto_prop_cached
    def pinlines_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.PINLINES, LAYERS.PINLINES)

    """
    * Shapes
    """

    @auto_prop_cached
    def pinlines_legendary_shape(self) -> Optional[ArtLayer]:
        if self.is_legendary:
            return psd.getLayer(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])
        return

    @auto_prop_cached
    def pt_shape(self) -> Optional[ArtLayer]:
        if self.is_creature:
            return psd.getLayer(LAYERS.SHAPE, LAYERS.PT_BOX)
        return

    @auto_prop_cached
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        return [self.border_shape, self.pinlines_legendary_shape, self.pt_shape]

    """
    METHODS
    """

    def enable_crown(self) -> None:
        self.crown_group.parent.visible = True
        super().enable_crown()
