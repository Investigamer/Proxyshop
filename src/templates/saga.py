"""
* Templates: Saga
"""
# Standard Library Imports
from typing import Optional, Union, Callable

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.layers import LAYERS
from src.enums.mtg import (
    saga_banner_color_map,
    saga_stripe_color_map,
    pinlines_color_map)
import src.helpers as psd
from src.layouts import SagaLayout
from src.templates import VectorNyxMod
from src.templates._core import NormalTemplate
from src.templates._vector import VectorTemplate
from src.templates.transform import VectorTransformMod
import src.text_layers as text_classes
from src.utils.adobe import ReferenceLayer
from src.utils.properties import auto_prop_cached

"""
* Modifier Classes
"""


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
    * Layout Checks
    """

    def is_layout_saga(self) -> bool:
        """Checks whether the card matches SagaLayout."""
        return isinstance(self.layout, SagaLayout)

    """
    * Mixin Methods
    """

    @auto_prop_cached
    def text_layer_methods(self) -> list[Callable]:
        """Add Saga text layers."""
        funcs = [self.text_layers_saga] if self.is_layout_saga else []
        return [*super().text_layer_methods, *funcs]

    @auto_prop_cached
    def frame_layer_methods(self) -> list[Callable]:
        """Add Saga text layers."""
        funcs = [self.frame_layers_saga] if self.is_layout_saga else []
        return [*super().frame_layer_methods, *funcs]

    @auto_prop_cached
    def post_text_methods(self) -> list[Callable]:
        """Position Saga abilities, dividers, and icons."""
        funcs = [self.layer_positioning_saga] if self.is_layout_saga else []
        return [*super().post_text_methods, *funcs]

    """
    * Groups
    """

    @auto_prop_cached
    def saga_group(self):
        return psd.getLayerSet(LAYERS.SAGA)

    """
    * Saga Layers
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

    @auto_prop_cached
    def ability_divider_layer(self) -> ArtLayer:
        return psd.getLayer(LAYERS.DIVIDER, self.saga_group)

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_ability(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TEXT, self.saga_group)

    @auto_prop_cached
    def text_layer_reminder(self) -> ArtLayer:
        return psd.getLayer("Reminder Text", self.saga_group)

    """
    * References
    """

    @auto_prop_cached
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME)

    @auto_prop_cached
    def reminder_reference(self) -> ReferenceLayer:
        return psd.get_reference_layer("Description Reference", self.saga_group)

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Skip this step for Saga cards."""
        pass

    """
    * Saga Frame Layer Methods
    """

    def frame_layers_saga(self):
        """Enable frame layers required by Saga cards."""

        # Saga stripe
        psd.getLayer(self.pinlines, LAYERS.PINLINES_AND_SAGA_STRIPE).visible = True

    """
    * Saga Text Layer Methods
    """

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

    """
    * Saga Positioning Methods
    """

    def layer_positioning_saga(self) -> None:
        """Position Saga ability, icon, and divider layers."""

        # Core vars
        spacing = self.app.scale_by_dpi(80)
        spaces = len(self.ability_layers) - 1
        spacing_total = (spaces * 1.5) + 2
        ref_height = self.textbox_reference.dims['height']
        total_height = ref_height - (((spacing * 1.5) * spaces) + (spacing * 2))

        # Resize text items till they fit in the available space
        psd.scale_text_layers_to_height(
            text_layers=self.ability_layers,
            ref_height=total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_layer_height(lyr) for lyr in self.ability_layers])
        gap = (ref_height - layer_heights) * (1 / spacing_total)
        inside_gap = (ref_height - layer_heights) * (1.5 / spacing_total)

        # Space Saga lines evenly apart
        psd.spread_layers_over_reference(
            layers=self.ability_layers,
            ref=self.textbox_reference,
            gap=gap,
            inside_gap=inside_gap)

        # Align icons to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):

            # Skip if no icons present or icons are invalid
            if not (icons := self.icon_layers[i]):
                continue
            if not all(icons):
                continue

            # Space multiple icons apart
            if len(icons) > 1:
                psd.space_layers_apart(
                    layers=icons,
                    gap=spacing / 3)

            # Combine icons and align them
            layer = icons[0] if len(icons) == 1 else psd.merge_layers(icons)
            psd.align_vertical(layer, ref_layer)

        # Position divider lines
        dividers = [self.ability_divider_layer.duplicate() for _ in range(len(self.ability_layers) - 1)]
        psd.position_dividers(
            dividers=dividers,
            layers=self.ability_layers,
            docref=self.docref)


class VectorSagaMod(SagaMod, VectorTemplate):
    """Saga mod for vector based templates."""

    # Color Maps
    saga_banner_color_map = saga_banner_color_map.copy()
    saga_stripe_color_map = saga_stripe_color_map.copy()

    """
    * Colors
    """

    @auto_prop_cached
    def saga_banner_colors(self) -> list[list[int]]:
        """Must be returned as list of RGB/CMYK integer lists."""
        if len(self.pinlines) == 2:
            return [self.saga_banner_color_map.get(c, [0, 0, 0]) for c in self.pinlines]
        return [self.saga_banner_color_map.get(self.pinlines, [0, 0, 0])]

    @auto_prop_cached
    def saga_stripe_colors(self) -> list[int]:
        """Must be returned as an RGB/CMYK integer list."""
        if len(self.pinlines) == 2:
            return self.saga_stripe_color_map.get('Dual', [0, 0, 0])
        return self.saga_stripe_color_map.get(self.pinlines, [0, 0, 0])

    """
    * Blending Masks
    """

    @auto_prop_cached
    def saga_banner_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.BANNER])]

    """
    * Groups
    """

    @auto_prop_cached
    def saga_banner_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.BANNER, self.saga_group)

    @auto_prop_cached
    def saga_stripe_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.STRIPE, self.saga_group)

    """
    * Shape Layers
    """

    @auto_prop_cached
    def saga_stripe_shape(self) -> ArtLayer:
        """The stripe shape in the middle of the Saga banner."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.saga_stripe_group, LAYERS.SHAPE])

    @auto_prop_cached
    def saga_banner_shape(self) -> ArtLayer:
        """The overall Saga banner shape."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.saga_banner_group, LAYERS.SHAPE])

    @auto_prop_cached
    def saga_trim_shape(self) -> ArtLayer:
        """The gold trim on the Saga Banner."""
        return psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
                self.saga_group)

    """
    * Saga Frame Layer Methods
    """

    def frame_layers_saga(self):
        """Enable layers required by Saga cards."""

        # Enable Saga group
        self.saga_group.visible = True

        # Add colors
        self.generate_layer(
            group=self.saga_banner_group,
            colors=self.saga_banner_colors,
            masks=self.saga_banner_masks)
        self.generate_layer(
            group=self.saga_stripe_group,
            colors=self.saga_stripe_colors)


"""
* Template Classes
"""


class SagaVectorTemplate(VectorNyxMod, VectorSagaMod, VectorTransformMod, VectorTemplate):
    """Saga template using vector shape layers and automatic pinlines / multicolor generation."""

    """
    * Bool Properties
    """

    @auto_prop_cached
    def is_name_shifted(self) -> bool:
        """bool: Back face TF icon is on right side."""
        return bool(self.is_transform and self.is_front)

    """
    * Colors
    """

    @auto_prop_cached
    def twins_colors(self) -> list[str]:
        """list[str]: Use Back face versions for back side Transform."""
        return [f'{self.twins} {LAYERS.BACK}'] if self.is_transform and not self.is_front else [self.twins]

    @auto_prop_cached
    def textbox_colors(self) -> list[str]:
        """list[str]: Support back and front side textures."""
        if self.is_transform and not self.is_front:
            # Back -> Dual color
            if 1 < len(self.identity) < self.color_limit:
                return [f"{n} {LAYERS.BACK}" for n in self.identity]
            # Back -> Single color
            return [f"{self.pinlines} {LAYERS.BACK}"]
        # Front -> Dual color
        if 1 < len(self.identity) < self.color_limit:
            return [n for n in self.identity]
        # Front -> Single color
        return [self.pinlines]

    @auto_prop_cached
    def crown_colors(self) -> Union[list[int], list[dict]]:
        """Return RGB/CMYK integer list or Gradient dict notation for color adjustment layers."""
        return psd.get_pinline_gradient(
            colors=self.pinlines,
            color_map=self.crown_color_map)

    """
    * Groups
    """

    @auto_prop_cached
    def crown_group(self) -> LayerSet:
        """Legendary crown group."""
        return psd.getLayerSet(LAYERS.SHAPE, LAYERS.LEGENDARY_CROWN)

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """Must enable textbox group."""
        if group := psd.getLayerSet(LAYERS.TEXTBOX):
            group.visible = True
            return group

    """
    * Layers
    """

    @auto_prop_cached
    def border_layer(self) -> Optional[ArtLayer]:
        """Check for Legendary and/or front face Transform."""
        name = LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL
        if self.is_transform and self.is_front:
            name += f" {LAYERS.TRANSFORM_FRONT}"
        return psd.getLayer(name, LAYERS.BORDER)

    """
    * References
    """

    @auto_prop_cached
    def art_reference(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME + " Right")

    @auto_prop_cached
    def textbox_reference(self) -> Optional[ReferenceLayer]:
        if self.is_front and self.is_flipside_creature:
            return psd.get_reference_layer(f"{LAYERS.TEXTBOX_REFERENCE} {LAYERS.TRANSFORM_FRONT}", self.saga_group)
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.saga_group)

    """
    * Blending Masks
    """

    @auto_prop_cached
    def textbox_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.TEXTBOX])]

    @auto_prop_cached
    def background_masks(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.BACKGROUND])]

    """
    * Shape Layers
    """

    @auto_prop_cached
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

    @auto_prop_cached
    def textbox_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Optional Textbox cutout shapes."""
        if self.is_transform and self.is_front:
            return [psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.textbox_group, LAYERS.SHAPE])]
        return []

    @auto_prop_cached
    def twins_shape(self) -> ArtLayer:
        """Allow for both front and back Transform twins."""
        if self.is_transform:
            return psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK,
                [self.twins_group, LAYERS.SHAPE])
        # Normal twins
        return psd.getLayer(LAYERS.NORMAL, [self.twins_group, LAYERS.SHAPE])

    @auto_prop_cached
    def outline_shape(self) -> ArtLayer:
        """Outline for textbox and art area."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            LAYERS.OUTLINE)

    @auto_prop_cached
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
    * Blending Masks
    """

    @auto_prop_cached
    def pinlines_mask(self) -> list[ArtLayer]:
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
    * Transform Frame Layer Methods
    """

    def enable_transform_layers(self):

        # Must enable Transform Icon group
        if self.transform_icon_layer:
            self.transform_icon_layer.parent.visible = True
            self.transform_icon_layer.visible = True

    """
    * Transform Text Layer Methods
    """

    def text_layers_transform_back(self):

        # Change back face name and typeline to white
        self.text_layer_name.textItem.color = psd.rgb_white()
        self.text_layer_type.textItem.color = psd.rgb_white()


class UniversesBeyondSagaTemplate(SagaVectorTemplate):
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
        """Not separated by front/back face."""
        if 1 < len(self.identity) < self.color_limit:
            return [n for n in self.identity]
        return [self.pinlines]

    @auto_prop_cached
    def twins_colors(self) -> Optional[str]:
        """Look for 'Beyond' variant texture."""
        return f'{self.twins} Beyond'

    """
    * Groups
    """

    @auto_prop_cached
    def background_group(self) -> LayerSet:
        """Look for 'Beyond' variant group."""
        return psd.getLayerSet(f'{LAYERS.BACKGROUND} Beyond')

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """Look for 'Beyond' variant group. Must be enabled."""
        if group := psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond"):
            group.visible = True
            return group

    """
    * Transform Frame Layers
    """

    def enable_transform_layers(self):
        super().enable_transform_layers()

        # Switch to darker colors for back side
        if not self.is_front:
            psd.getLayer(LAYERS.BACK, self.textbox_group).visible = True
            psd.getLayer(LAYERS.BACK, self.twins_group).visible = True
