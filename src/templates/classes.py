"""
* CLASS TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Union, Optional, Callable

# Third Party Imports
from photoshop.api import SolidColor
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._core import NormalTemplate
from src.templates._vector import VectorTemplate
from src.enums.mtg import pinline_color_map
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import ClassLayout
import src.format_text as ft
import src.helpers as psd


class ClassTemplate (NormalTemplate):
    """
    * A template for Class cards introduced in Adventures in the Forgotten Realms.
    * Utilizes some of the same automated positioning techniques as Planeswalker templates.

    Adds:
        * Level stage groups which contain a cost and level text layer, as well as the divider bar.
        * Level line groups which contain the ability text for each level.
    """

    def __init__(self, layout: ClassLayout, **kwargs):
        self._line_layers: list[ArtLayer] = []
        self._stage_layers: list[LayerSet] = []
        super().__init__(layout, **kwargs)

    """
    LAYERS
    """

    @cached_property
    def class_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.CLASS, LAYERS.TEXT_AND_ICONS)

    @cached_property
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STAGE, self.class_group)

    @property
    def line_layers(self) -> list[ArtLayer]:
        return self._line_layers

    @line_layers.setter
    def line_layers(self, value):
        self._line_layers = value

    @property
    def stage_layers(self) -> list[LayerSet]:
        return self._stage_layers

    @stage_layers.setter
    def stage_layers(self, value):
        self._stage_layers = value

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:
        self.class_text_layers()

    def post_text_layers(self) -> None:
        self.class_layer_positioning()

    """
    CLASS CARD METHODS
    """

    def class_text_layers(self) -> None:
        """Add and modify text layers relating to Class type cards."""

        # Add first static line
        level_1 = psd.getLayer(LAYERS.TEXT, self.class_group)
        self.line_layers.append(level_1)
        self.text.append(
            text_classes.FormattedTextField(
                layer=level_1,
                contents=self.layout.class_lines[0]['text']
            )
        )

        # Add text fields for each line and class stage
        for i, line in enumerate(self.layout.class_lines[1:]):
            line_layer = level_1.duplicate()
            self.active_layer = self.stage_group
            stage = psd.duplicate_group(f"{self.stage_group.name} {i + 1}")
            self.line_layers.append(line_layer)
            self.stage_layers.append(stage)
            self.text.extend([
                text_classes.FormattedTextField(
                    layer=line_layer,
                    contents=line['text']
                ),
                text_classes.FormattedTextField(
                    layer=psd.getLayer("Cost", stage),
                    contents=f"{line['cost']}:"
                ),
                text_classes.TextField(
                    layer=psd.getLayer("Level", stage),
                    contents=f"Level {line['level']}"
                )
            ])
        self.stage_group.visible = False

    def class_layer_positioning(self) -> None:
        """Positions and sizes class ability layers and divider lines."""

        # Core vars
        spacing = self.app.scale_by_dpi(80)
        spaces = len(self.line_layers) - 1
        divider_height = psd.get_layer_dimensions(self.stage_layers[0])['height']
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.line_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * ((spacing + divider_height) / spacing_total)

        # Space Class lines evenly apart
        psd.spread_layers_over_reference(self.line_layers, self.textbox_reference, gap, inside_gap)

        # Position a class stage between each ability line
        psd.position_dividers(self.stage_layers, self.line_layers)


"""
* VECTOR TEMPLATES
* Class templates that use vectorized layer structure.
"""


class ClassVectorTemplate (VectorTemplate):
    """Class template using vector shape layers and automatic pinlines / multicolor generation."""

    def __init__(self, layout: ClassLayout, **kwargs):
        self._line_layers: list[ArtLayer] = []
        self._stage_layers: list[LayerSet] = []
        super().__init__(layout, **kwargs)

    """
    DETAILS
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        return [*super().text_layer_methods, self.class_text_layers]

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        return [*super().frame_layer_methods, self.enable_class_layers]

    @cached_property
    def general_methods(self) -> list[Callable]:
        return [*super().general_methods, self.class_layer_positioning]

    """
    BOOL
    """

    @cached_property
    def is_name_shifted(self) -> bool:
        # Back face TF symbol is on right side
        return bool(self.is_transform and self.is_front)

    """
    COLORS
    """

    @cached_property
    def textbox_colors(self) -> list[str]:
        # Transform back side textures
        if self.is_transform and not self.is_front:
            # Dual color textures
            if 1 < len(self.identity) < self.color_limit:
                return [f"{n} {LAYERS.BACK}" for n in self.identity]
            # Single color textures
            return [f"{self.pinlines} {LAYERS.BACK}"]
        # Dual color front textures
        if 1 < len(self.identity) < self.color_limit:
            return [n for n in self.identity]
        # Single color front textures
        return [self.pinlines]

    @cached_property
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        # Return SolidColor or Gradient dict notation for colored adjustment layers
        return psd.get_pinline_gradient(self.pinlines, self.crown_color_map)

    """
    GROUPS
    """

    @cached_property
    def mode_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.CLASS)

    @cached_property
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STAGE, self.mode_group)

    @cached_property
    def background_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.NYX if self.is_nyx else LAYERS.BACKGROUND)

    @cached_property
    def crown_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.SHAPE, LAYERS.LEGENDARY_CROWN)

    """
    LAYERS
    """

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        # Use Back face versions for back side Transform
        return psd.getLayer(
            f"{self.twins} {LAYERS.BACK}" if self.is_transform and not self.is_front else self.twins,
            self.twins_group)

    @property
    def line_layers(self) -> list[ArtLayer]:
        return self._line_layers

    @line_layers.setter
    def line_layers(self, value):
        self._line_layers = value

    @property
    def stage_layers(self) -> list[LayerSet]:
        return self._stage_layers

    @stage_layers.setter
    def stage_layers(self, value):
        self._stage_layers = value

    """
    REFERENCES
    """

    @cached_property
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME + " Left")

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        if self.is_front and self.is_flipside_creature:
            return psd.getLayer(f"{LAYERS.TEXTBOX_REFERENCE} {LAYERS.TRANSFORM_FRONT}", self.mode_group)
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE, self.mode_group)

    @cached_property
    def textbox_position_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.ART_FRAME + " Right")

    """
    MASKS
    """

    @cached_property
    def pinlines_mask(self) -> ArtLayer:
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.mask_group, LAYERS.PINLINES])

    @cached_property
    def textbox_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.TEXTBOX])]

    @cached_property
    def background_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.BACKGROUND])]

    """
    SHAPES
    """

    @cached_property
    def border_shape(self) -> Optional[ArtLayer]:
        # Front face transform border
        if self.is_transform and self.is_front:
            return psd.getLayer(
                f"{LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL} {LAYERS.TRANSFORM_FRONT}",
                self.border_group)
        return super().border_shape

    @cached_property
    def pinlines_shapes(self) -> list[LayerSet]:
        """Support an additional Legendary pinline shape."""
        shapes = [psd.getLayerSet(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])] if self.is_legendary else []
        return [
            # Normal or Transform pinline
            psd.getLayerSet(
                (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
                if self.is_transform else LAYERS.NORMAL,
                [self.pinlines_group, LAYERS.SHAPE]
            ), *shapes
        ]

    @cached_property
    def twins_shape(self) -> ArtLayer:
        """Support both front and back face Transform shapes."""
        return psd.getLayer(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform else LAYERS.NORMAL,
            [self.twins_group, LAYERS.SHAPE])

    @cached_property
    def outline_shape(self):
        """Outline for the textbox and art."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            LAYERS.OUTLINE)

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Add support for outline shape and multiple pinlines shapes."""
        return [
            *self.pinlines_shapes,
            self.outline_shape,
            self.border_shape,
            self.twins_shape
        ]

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:

        # Enable vector shapes
        self.enable_shape_layers()

        # Color Indicator -> Blend solid colors using layer masks
        if self.is_type_shifted and self.indicator_group:
            self.create_blended_solid_color(
                group=self.indicator_group,
                colors=self.indicator_colors,
                masks=self.indicator_masks)

        # Pinlines -> Solid color or gradient layer
        if self.pinlines_group:
            self.pinlines_group.visible = True
            self.pinlines_action(self.pinlines_colors, layer=self.pinlines_group)
            psd.copy_layer_mask(self.pinlines_mask, self.pinlines_group)

        # Twins -> A static layer
        if self.twins_layer:
            self.twins_layer.visible = True

        # Textbox -> Blended texture layers
        if self.textbox_group:
            self.textbox_group.visible = True
            self.create_blended_layer(
                group=self.textbox_group,
                colors=self.textbox_colors,
                masks=self.textbox_masks)
            psd.merge_group(self.textbox_group)
            psd.align_horizontal(self.active_layer, self.textbox_position_reference)

        # Background -> Blended texture layers
        if self.background_group:
            self.create_blended_layer(
                group=self.background_group,
                colors=self.background_colors,
                masks=self.background_masks)

        # Legendary crown
        if self.is_legendary:
            self.enable_crown()

    def enable_crown(self) -> None:

        # Legendary Crown -> A solid color or gradient layer
        self.crown_group.visible = True
        self.pinlines_action(self.crown_colors, layer=self.crown_group)

        # Enable Hollow Crown
        self.enable_hollow_crown(
            masks=[self.crown_group],
            vector_masks=[self.pinlines_group]
        )

    def rules_text_and_pt_layers(self) -> None:

        # Skip this step
        pass

    """
    CLASS CARD METHODS
    """

    def enable_class_layers(self):
        """Enable layers relating to Class type cards."""

        # Enable class mode group, disable saga banner
        self.mode_group.visible = True
        psd.getLayerSet("Banner Top").visible = False

    def class_text_layers(self) -> None:
        """Add and modify text layers relating to Class type cards."""

        # Add first static line
        level_1 = psd.getLayer(LAYERS.TEXT, self.mode_group)
        self.line_layers.append(level_1)
        self.text.append(
            text_classes.FormattedTextField(
                layer=level_1,
                contents=self.layout.class_lines[0]['text']
            )
        )

        # Add text fields for each line and class stage
        for i, line in enumerate(self.layout.class_lines[1:]):
            line_layer = level_1.duplicate()
            self.active_layer = self.stage_group
            stage = psd.duplicate_group(f"{self.stage_group.name} {i + 1}")
            self.line_layers.append(line_layer)
            self.stage_layers.append(stage)
            self.text.extend([
                text_classes.FormattedTextField(
                    layer=line_layer,
                    contents=line['text']
                ),
                text_classes.FormattedTextField(
                    layer=psd.getLayer("Cost", stage),
                    contents=f"{line['cost']}:"
                ),
                text_classes.TextField(
                    layer=psd.getLayer("Level", stage),
                    contents=f"Level {line['level']}"
                )
            ])
        self.stage_group.visible = False

    def class_layer_positioning(self) -> None:
        """Positions and sizes class ability layers and divider lines."""

        # Core vars
        spacing = self.app.scale_by_dpi(80)
        spaces = len(self.line_layers) - 1
        divider_height = psd.get_layer_dimensions(self.stage_layers[0])['height']
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.line_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * ((spacing + divider_height) / spacing_total)

        # Space Class lines evenly apart
        psd.spread_layers_over_reference(self.line_layers, self.textbox_reference, gap, inside_gap)

        # Position a class stage between each ability line
        psd.position_dividers(self.stage_layers, self.line_layers)


class UniversesBeyondClassTemplate(ClassVectorTemplate):
    """Saga Vector template with Universes Beyond frame treatment."""
    template_suffix = "Universes Beyond"

    """
    COLORS
    """

    @cached_property
    def pinline_color_map(self) -> dict:
        colors = pinline_color_map.copy()
        colors.update({
            'W': [246, 247, 241],
            'U': [0, 131, 193],
            'B': [44, 40, 33],
            'R': [237, 66, 31],
            'G': [5, 129, 64],
            'Gold': [239, 209, 107],
            'Land': [165, 150, 132],
            'Artifact': [227, 228, 230],
            'Colorless': [227, 228, 230]
        })
        return colors

    @cached_property
    def textbox_colors(self) -> list[str]:
        # Dual color front textures
        if 1 < len(self.identity) < self.color_limit:
            return [n for n in self.identity]
        # Single color front textures
        return [self.pinlines]

    """
    LAYERS
    """

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        # Use Back face versions for back side Transform
        return psd.getLayer(f"{self.twins} Beyond", self.twins_group)

    """
    GROUPS
    """

    @cached_property
    def background_group(self) -> LayerSet:
        return psd.getLayerSet(f'{LAYERS.BACKGROUND} Beyond')

    @cached_property
    def textbox_group(self) -> LayerSet:
        return psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond")
