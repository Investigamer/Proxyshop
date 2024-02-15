"""
* CLASS TEMPLATES
"""
# Standard Library Imports
from typing import Union, Optional, Callable

# Third Party Imports
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.layers import LAYERS
from src.enums.mtg import pinlines_color_map
import src.helpers as psd
from src.layouts import ClassLayout
from src.templates._core import NormalTemplate
from src.templates._cosmetic import VectorNyxMod
from src.templates._vector import VectorTemplate
from src.text_layers import FormattedTextField, TextField
from src.utils.properties import auto_prop_cached

"""
* Modifier Classes
"""


class ClassMod (NormalTemplate):
    """
    * A template modifier for Class cards introduced in Adventures in the Forgotten Realms.
    * Utilizes similar automated positioning techniques as Planeswalker templates.

    Adds:
        * Level stage groups which contain a cost and level text layer, as well as the divider bar.
        * Level line groups which contain the ability text for each level.
        * A positioning step to evenly space the abilities and stage dividers.
    """

    def __init__(self, layout: ClassLayout, **kwargs):
        self._line_layers: list[ArtLayer] = []
        self._stage_layers: list[LayerSet] = []
        super().__init__(layout, **kwargs)

    """
    * Checks
    """

    @auto_prop_cached
    def is_class_layout(self) -> bool:
        """bool: Checks if this card is a ClassLayout object."""
        return isinstance(self.layout, ClassLayout)

    """
    * Mixin Methods
    """

    @auto_prop_cached
    def text_layer_methods(self) -> list[Callable]:
        """Add Class text layers."""
        funcs = [self.text_layers_classes] if self.is_class_layout else []
        return [*super().text_layer_methods, *funcs]

    @auto_prop_cached
    def frame_layer_methods(self) -> list[Callable]:
        """Add Class text layers."""
        funcs = [self.frame_layers_classes] if self.is_class_layout else []
        return [*super().frame_layer_methods, *funcs]

    @auto_prop_cached
    def post_text_methods(self) -> list[Callable]:
        """Position Class abilities and stage dividers."""
        funcs = [self.layer_positioning_classes] if self.is_class_layout else []
        return [*super().post_text_methods, *funcs]

    """
    * Class Groups
    """

    @auto_prop_cached
    def class_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.CLASS)

    @auto_prop_cached
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STAGE, self.class_group)

    """
    * Class Text Layers
    """

    @auto_prop_cached
    def text_layer_ability(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TEXT, self.class_group)

    """
    * Class Abilities
    """

    @property
    def line_layers(self) -> list[ArtLayer]:
        return self._line_layers

    @line_layers.setter
    def line_layers(self, value):
        self._line_layers = value

    """
    * Class Stage Dividers
    """

    @property
    def stage_layers(self) -> list[LayerSet]:
        return self._stage_layers

    @stage_layers.setter
    def stage_layers(self, value):
        self._stage_layers = value

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Skip this step for Class cards."""
        pass

    """
    * Class Text Layer Methods
    """

    def text_layers_classes(self) -> None:
        """Add and modify text layers relating to Class type cards."""

        # Add first static line
        self.line_layers.append(self.text_layer_ability)
        self.text.append(
            FormattedTextField(
                layer=self.text_layer_ability,
                contents=self.layout.class_lines[0]['text']
            ))

        # Add text fields for each line and class stage
        for i, line in enumerate(self.layout.class_lines[1:]):

            # Create a new ability line
            line_layer = self.text_layer_ability.duplicate()
            self.line_layers.append(line_layer)

            # Use existing stage divider or create new one
            stage = self.stage_group if i == 0 else self.stage_group.duplicate()
            cost, level = [*stage.artLayers][:2]
            self.stage_layers.append(stage)

            # Add text layers to be formatted
            self.text.extend([
                FormattedTextField(layer=line_layer, contents=line['text']),
                FormattedTextField(layer=cost, contents=f"{line['cost']}:"),
                TextField(layer=level, contents=f"Level {line['level']}")
            ])

    """
    * Class Frame Layer Methods
    """

    def frame_layers_classes(self) -> None:
        """Enable frame layers required by Class cards. None by default."""
        pass

    """
    * Class Positioning Methods
    """

    def layer_positioning_classes(self) -> None:
        """Positions and sizes class ability layers and stage dividers."""

        # Core vars
        spacing = self.app.scale_by_dpi(80)
        spaces = len(self.line_layers) - 1
        divider_height = psd.get_layer_height(self.stage_layers[0])
        ref_height = self.textbox_reference.dims['height']
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        psd.scale_text_layers_to_height(
            text_layers=self.line_layers,
            ref_height=total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_layer_height(lyr) for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * ((spacing + divider_height) / spacing_total)

        # Space Class lines evenly apart
        psd.spread_layers_over_reference(
            layers=self.line_layers,
            ref=self.textbox_reference,
            gap=gap,
            inside_gap=inside_gap)

        # Position a class stage between each ability line
        psd.position_dividers(
            dividers=self.stage_layers,
            layers=self.line_layers,
            docref=self.docref)


"""
* Template Classes
"""


class ClassVectorTemplate (VectorNyxMod, ClassMod, VectorTemplate):
    """Class template using vector shape layers and automatic pinlines / multicolor generation."""

    """
    * Bool
    """

    @auto_prop_cached
    def is_name_shifted(self) -> bool:
        """Back face TF symbol is on right side."""
        return bool(self.is_transform and self.is_front)

    """
    * Colors
    """

    @auto_prop_cached
    def textbox_colors(self) -> list[str]:
        """list[str]: Support back side texture names."""
        colors = list(self.identity) if self.is_within_color_limit else [self.pinlines]
        # Is this card a back face transform?
        if self.is_transform and not self.is_front:
            return [f'{n} {LAYERS.BACK}' for n in colors]
        return colors

    @auto_prop_cached
    def crown_colors(self) -> Union[list[int], list[dict]]:
        """Return RGB notation or Gradient dict notation for adjustment layers."""
        return psd.get_pinline_gradient(
            colors=self.pinlines, color_map=self.crown_color_map)

    """
    * Groups
    """

    @auto_prop_cached
    def crown_group(self) -> LayerSet:
        """Use inner shape group for Legendary Crown."""
        return psd.getLayerSet(LAYERS.SHAPE, [self.docref, LAYERS.LEGENDARY_CROWN])

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """Must enable textbox group."""
        if group := psd.getLayerSet(LAYERS.TEXTBOX, self.docref):
            group.visible = True
            return group

    """
    * Layers
    """

    @auto_prop_cached
    def twins_layer(self) -> Optional[ArtLayer]:
        # Use Back face versions for back side Transform
        return psd.getLayer(
            f"{self.twins} {LAYERS.BACK}" if self.is_transform and not self.is_front else self.twins,
            self.twins_group)

    """
    * References
    """

    @auto_prop_cached
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME + " Left")

    @auto_prop_cached
    def textbox_reference(self) -> Optional[ArtLayer]:
        if self.is_front and self.is_flipside_creature:
            return psd.get_reference_layer(
                f'{LAYERS.TEXTBOX_REFERENCE} {LAYERS.TRANSFORM_FRONT}',
                self.class_group)
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.class_group)

    @auto_prop_cached
    def textbox_position_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.ART_FRAME + " Right")

    """
    * Blending Masks
    """

    @auto_prop_cached
    def textbox_masks(self) -> list[ArtLayer]:
        """Blends the textbox colors."""
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.TEXTBOX])]

    @auto_prop_cached
    def background_masks(self) -> list[ArtLayer]:
        """Blends the background colors."""
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.BACKGROUND])]

    """
    * Shapes
    """

    @auto_prop_cached
    def border_shape(self) -> Optional[ArtLayer]:
        """Support a Normal and Legendary border for front-face Transform."""
        if self.is_transform and self.is_front:
            return psd.getLayer(
                f"{LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL} {LAYERS.TRANSFORM_FRONT}",
                self.border_group)
        return super().border_shape

    @auto_prop_cached
    def pinlines_shapes(self) -> list[LayerSet]:
        """Support front and back face Transform pinlines, and optional Legendary pinline shape."""
        shapes = [psd.getLayerSet(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])] if self.is_legendary else []
        return [
            # Normal or Transform pinline
            psd.getLayerSet(
                (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
                if self.is_transform else LAYERS.NORMAL,
                [self.pinlines_group, LAYERS.SHAPE]
            ), *shapes
        ]

    @auto_prop_cached
    def twins_shape(self) -> ArtLayer:
        """Support both front and back face Transform shapes."""
        return psd.getLayer(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform else LAYERS.NORMAL,
            [self.twins_group, LAYERS.SHAPE])

    @auto_prop_cached
    def outline_shape(self):
        """Outline for the textbox and art."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            LAYERS.OUTLINE)

    @auto_prop_cached
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Add support for outline shape and multiple pinlines shapes."""
        return [
            *self.pinlines_shapes,
            self.outline_shape,
            self.border_shape,
            self.twins_shape
        ]

    """
    * Masks to Enable
    """

    @auto_prop_cached
    def pinlines_mask(self) -> list[Union[ArtLayer, LayerSet]]:
        """Mask hiding pinlines effects inside textbox and art frame."""
        return [
            psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
                [self.mask_group, LAYERS.PINLINES]),
            self.pinlines_group
        ]

    @auto_prop_cached
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Support a pinlines mask."""
        return [self.pinlines_mask]

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self) -> None:
        super().enable_frame_layers()

        # Merge the textbox and shift it to right half
        psd.merge_group(self.textbox_group)
        psd.align_horizontal(
            layer=self.active_layer,
            ref=self.textbox_position_reference)

    """
    * Class Frame Layer Methods
    """

    def frame_layers_classes(self):
        """Enable layers relating to Class type cards."""

        # Enable class group, disable saga banner
        self.class_group.visible = True
        psd.getLayerSet("Banner Top").visible = False


class UniversesBeyondClassTemplate(ClassVectorTemplate):
    """Saga Vector template with Universes Beyond frame treatment."""
    template_suffix = 'Universes Beyond'

    # Color Maps
    pinlines_color_map = {
        **pinlines_color_map.copy(),
        'W': [246, 247, 241],
        'U': [0, 131, 193],
        'B': [44, 40, 33],
        'R': [237, 66, 31],
        'G': [5, 129, 64],
        'Gold': [239, 209, 107],
        'Land': [165, 150, 132],
        'Artifact': [227, 228, 230],
        'Colorless': [227, 228, 230]
    }

    """
    * Colors
    """

    @auto_prop_cached
    def textbox_colors(self) -> list[str]:
        """list[str]: Support identity by color limit, fallback to pinline colors."""
        if self.is_within_color_limit:
            return [n for n in self.identity]
        return [self.pinlines]

    @auto_prop_cached
    def twins_colors(self) -> str:
        """str: Universes Beyond variant texture name."""
        return f'{self.twins} Beyond'

    """
    * Groups
    """

    @auto_prop_cached
    def background_group(self) -> LayerSet:
        """LayerSet: Universes Beyond variant group."""
        return psd.getLayerSet(f'{LAYERS.BACKGROUND} Beyond')

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """LayerSet: Universes Beyond variant group. Must be enabled."""
        group = psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond")
        group.visible = True
        return group
