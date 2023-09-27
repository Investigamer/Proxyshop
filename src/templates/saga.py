"""
* SAGA TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional, Union, Callable

# Third Party Imports
from photoshop.api import SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.mtg import saga_banner_color_map, saga_stripe_color_map, pinline_color_map
from src.templates._core import NormalTemplate
from src.templates._vector import VectorTemplate
from src.templates.transform import VectorTransformMod
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import SagaLayout
import src.format_text as ft
import src.helpers as psd


class SagaMod (NormalTemplate):
    """
    * A template modifier for Saga cards introduced in Dominaria.
    * Utilizes some of the same automated positioning techniques as Planeswalker templates.

    Adds:
        * Ability icons, layers, and dividers.
        * A reminder text layer at the top which describes how the Saga functions.
        * Also has some layer support for double faced sagas.
    """

    def __init__(self, layout: SagaLayout, **kwargs):
        self._abilities: list[ArtLayer] = []
        self._icons: list[list[ArtLayer]] = []
        super().__init__(layout, **kwargs)

    """
    DETAILS
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Add Saga text layers."""
        funcs = [self.text_layers_saga] if isinstance(self.layout, SagaLayout) else []
        return [*super().text_layer_methods, *funcs]

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        """Add Saga text layers."""
        funcs = [self.frame_layers_saga] if isinstance(self.layout, SagaLayout) else []
        return [*super().frame_layer_methods, *funcs]

    @cached_property
    def general_methods(self) -> list[Callable]:
        """Position Saga abilities, dividers, and icons."""
        funcs = [self.layer_positioning_saga] if isinstance(self.layout, SagaLayout) else []
        return [*super().general_methods, *funcs]

    """
    GROUPS
    """

    @cached_property
    def saga_group(self):
        return psd.getLayerSet(LAYERS.SAGA)

    """
    SAGA LAYERS
    """

    @property
    def ability_layers(self) -> list[ArtLayer]:
        return self._abilities

    @ability_layers.setter
    def ability_layers(self, value):
        self._abilities = value

    @property
    def icon_layers(self) -> list[list[ArtLayer]]:
        return self._icons

    @icon_layers.setter
    def icon_layers(self, value):
        self._icons = value

    @cached_property
    def ability_divider_layer(self) -> ArtLayer:
        return psd.getLayer(LAYERS.DIVIDER, self.saga_group)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_ability(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TEXT, self.saga_group)

    @cached_property
    def text_layer_reminder(self) -> ArtLayer:
        return psd.getLayer("Reminder Text", self.saga_group)

    """
    REFERENCES
    """

    @cached_property
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME)

    @cached_property
    def reminder_reference(self) -> ArtLayer:
        return psd.getLayer("Description Reference", self.saga_group)

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:
        """Skip this step for Class cards."""
        pass

    """
    SAGA METHODS
    """

    def frame_layers_saga(self):
        """Enable frame layers required by Saga cards."""

        # Saga stripe
        psd.getLayer(self.pinlines, LAYERS.PINLINES_AND_SAGA_STRIPE).visible = True

    def text_layers_saga(self):
        """Add and modify text layers required by Saga cards."""

        # Add description text with reminder
        self.text.append(
            text_classes.FormattedTextArea(
                layer=self.text_layer_reminder,
                contents=self.layout.saga_description,
                reference=self.reminder_reference))

        # Iterate through each saga stage and add line to text layers
        for i, line in enumerate(self.layout.saga_lines):

            # Add icon layers for this ability
            self.icon_layers.append([psd.getLayer(n, self.saga_group).duplicate() for n in line['icons']])

            # Add ability text for this ability
            layer = self.text_layer_ability if i == 0 else self.text_layer_ability.duplicate()
            self.ability_layers.append(layer)
            self.text.append(
                text_classes.FormattedTextField(
                    layer=layer, contents=line['text']))

    def layer_positioning_saga(self) -> None:
        """Position Saga ability, icon, and divider layers."""

        # Core vars
        spacing = self.app.scale_by_dpi(80)
        spaces = len(self.ability_layers) - 1
        spacing_total = (spaces * 1.5) + 2
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        total_height = ref_height - (((spacing * 1.5) * spaces) + (spacing * 2))

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.ability_layers])
        gap = (ref_height - layer_heights) * (1 / spacing_total)
        inside_gap = (ref_height - layer_heights) * (1.5 / spacing_total)

        # Space Saga lines evenly apart
        psd.spread_layers_over_reference(self.ability_layers, self.textbox_reference, gap, inside_gap)

        # Align icons to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):
            # Skip if no icons present, space apart and merge if more than 1
            if not (icons := self.icon_layers[i]):
                continue
            if len(icons) > 1:
                psd.space_layers_apart(icons, spacing / 3)
            psd.align_vertical(psd.merge_layers(icons), ref_layer)

        # Position divider lines
        dividers = [self.ability_divider_layer.duplicate() for _ in range(len(self.ability_layers) - 1)]
        psd.position_dividers(dividers, self.ability_layers)


class VectorSagaMod(SagaMod, VectorTemplate):
    """Saga mod for vector based templates."""

    """
    COLOR MAPS
    """

    @cached_property
    def saga_banner_color_map(self) -> dict:
        """Maps color values for the Saga Banner."""
        return saga_banner_color_map

    @cached_property
    def saga_stripe_color_map(self) -> dict:
        """Maps color values for the Saga Stripe."""
        return saga_stripe_color_map

    """
    COLORS
    """

    @cached_property
    def saga_banner_colors(self) -> list[SolidColor]:
        """Must be returned as list of SolidColor objects."""
        if len(self.pinlines) == 2:
            return [psd.get_rgb(*self.saga_banner_color_map.get(c, psd.rgb_black())) for c in self.pinlines]
        return [psd.get_rgb(*self.saga_banner_color_map.get(self.pinlines, psd.rgb_black()))]

    @cached_property
    def saga_stripe_color(self) -> SolidColor:
        """Must be returned as SolidColor object."""
        if len(self.pinlines) == 2:
            return psd.get_rgb(*self.saga_stripe_color_map.get('Dual', psd.rgb_black()))
        return psd.get_rgb(*self.saga_stripe_color_map.get(self.pinlines, psd.rgb_black()))

    """
    BLENDING MASKS
    """

    @cached_property
    def saga_banner_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.BANNER])]

    """
    GROUPS
    """

    @cached_property
    def saga_banner_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.BANNER, self.saga_group)

    @cached_property
    def saga_stripe_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STRIPE, self.saga_group)

    """
    SHAPES
    """

    @cached_property
    def saga_stripe_shape(self) -> ArtLayer:
        """The stripe shape in the middle of the Saga banner."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.saga_stripe_group, LAYERS.SHAPE])

    @cached_property
    def saga_banner_shape(self) -> ArtLayer:
        """The overall Saga banner shape."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.saga_banner_group, LAYERS.SHAPE])

    @cached_property
    def saga_trim_shape(self) -> ArtLayer:
        """The gold trim on the Saga Banner."""
        return psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
                self.saga_group)

    """
    SAGA METHODS
    """

    def frame_layers_saga(self):
        """Enable layers required by Saga cards."""

        # Enable Saga group
        self.saga_group.visible = True

        # Add colors
        self.create_blended_solid_color(
            group=self.saga_banner_group,
            colors=self.saga_banner_colors,
            masks=self.saga_banner_masks)
        psd.create_color_layer(
            color=self.saga_stripe_color,
            layer=self.saga_stripe_group
        )


"""
* VECTOR TEMPLATES
* Saga templates that use vectorized layer structure.
"""


class SagaVectorTemplate(VectorSagaMod, VectorTransformMod, VectorTemplate):
    """Saga template using vector shape layers and automatic pinlines / multicolor generation."""

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
    def background_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.NYX if self.is_nyx else LAYERS.BACKGROUND)

    @cached_property
    def crown_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.SHAPE, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def textbox_group(self) -> LayerSet:
        """Must enable textbox group."""
        if group := psd.getLayerSet(LAYERS.TEXTBOX):
            group.visible = True
            return group

    """
    LAYERS
    """

    @cached_property
    def border_layer(self) -> Optional[ArtLayer]:
        # Check for Legendary and/or front face Transform
        name = LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL
        if self.is_transform and self.is_front:
            name += f" {LAYERS.TRANSFORM_FRONT}"
        return psd.getLayer(name, LAYERS.BORDER)

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        # Use Back face versions for back side Transform
        return psd.getLayer(
            f"{self.twins} {LAYERS.BACK}" if self.is_transform and not self.is_front else self.twins,
            self.twins_group)

    """
    REFERENCES
    """

    @cached_property
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME + " Right")

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        if self.is_front and self.is_flipside_creature:
            return psd.getLayer(f"{LAYERS.TEXTBOX_REFERENCE} {LAYERS.TRANSFORM_FRONT}", self.saga_group)
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE, self.saga_group)

    """
    BLENDING MASKS
    """

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
    def pinlines_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Add Legendary shape to pinlines shapes."""
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
    def textbox_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Optional Textbox cutout shapes."""
        if self.is_transform and self.is_front:
            return [psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.textbox_group, LAYERS.SHAPE])]
        return []

    @cached_property
    def twins_shape(self) -> ArtLayer:
        """Allow for both front and back Transform twins."""
        if self.is_transform:
            return psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK,
                [self.twins_group, LAYERS.SHAPE])
        # Normal twins
        return psd.getLayer(LAYERS.NORMAL, [self.twins_group, LAYERS.SHAPE])

    @cached_property
    def outline_shape(self) -> ArtLayer:
        """Outline for textbox and art area."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            LAYERS.OUTLINE)

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Add support for outline shape, multiple pinlines shapes, and saga shapes."""
        return [
            *self.pinlines_shapes,
            *self.textbox_shapes,
            self.saga_banner_shape,
            self.saga_stripe_shape,
            self.saga_trim_shape,
            self.outline_shape,
            self.border_shape,
            self.twins_shape
        ]

    """
    BLENDING MASKS
    """

    @cached_property
    def pinlines_mask(self) -> list[ArtLayer]:
        """Mask hiding pinlines effects inside textbox and art frame."""
        return [
            psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
                [self.mask_group, LAYERS.PINLINES]),
            self.pinlines_group
        ]

    @cached_property
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Support a pinlines mask."""
        return [self.pinlines_mask]

    """
    METHODS
    """

    def enable_crown(self) -> None:

        # Legendary Crown -> A solid color or gradient layer
        self.crown_group.visible = True
        self.pinlines_action(self.crown_colors, layer=self.crown_group)

        # Enable Hollow Crown
        self.enable_hollow_crown(
            masks=[self.crown_group],
            vector_masks=[self.pinlines_group]
        )

    """
    TRANSFORM METHODS
    """

    def enable_transform_layers(self):

        # Must enable Transform Icon group
        self.transform_icon_layer.parent.visible = True
        if self.transform_icon_layer:
            self.transform_icon_layer.visible = True

    def text_layers_transform_back(self):

        # Change back face name and typeline to white
        self.text_layer_name.textItem.color = psd.rgb_white()
        self.text_layer_type.textItem.color = psd.rgb_white()


class UniversesBeyondSagaTemplate(SagaVectorTemplate):
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

    @cached_property
    def twins_colors(self) -> Optional[str]:
        return f"{self.twins} Beyond"

    """
    GROUPS
    """

    @cached_property
    def background_group(self) -> LayerSet:
        return psd.getLayerSet(f'{LAYERS.BACKGROUND} Beyond')

    @cached_property
    def textbox_group(self) -> LayerSet:
        """Must enable group."""
        if group := psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond"):
            group.visible = True
            return group

    """
    TRANSFORM METHODS
    """

    def enable_transform_layers(self):
        super().enable_transform_layers()

        # Switch to darker colors for back side
        if not self.is_front:
            psd.getLayer(LAYERS.BACK, self.textbox_group).visible = True
            psd.getLayer(LAYERS.BACK, self.twins_group).visible = True
