# Standard Library Imports
from functools import cached_property
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    ElementPlacement,
    SolidColor
)
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.frame_logic import contains_frame_colors
from src.enums.mtg import (
    crown_color_map,
    indicator_color_map,
    pinline_color_map
)
import src.helpers as psd
from src.enums.layers import LAYERS
from src.templates import NormalTemplate
from src.types.adobe import LayerObject


class VectorTemplate (NormalTemplate):
    """Next generation template using vector shape layers, automatic pinlines, and blended multicolor textures."""

    """
    DETAILS
    """

    @cached_property
    def color_limit(self) -> int:
        """The maximum allowed colors that should be blended plus 1."""
        return 3

    @cached_property
    def pinlines_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        """Function to call to generate pinline colors. Usually to generate a solid color or gradient layer."""
        return psd.create_color_layer if isinstance(self.pinlines_colors, SolidColor) else psd.create_gradient_layer

    """
    COLOR MAPS
    """

    @cached_property
    def pinline_color_map(self) -> dict:
        """Maps color values for the Pinlines."""
        return pinline_color_map.copy()

    @cached_property
    def crown_color_map(self) -> dict:
        """Maps color values for the Legendary Crown."""
        return crown_color_map.copy()

    @cached_property
    def indicator_color_map(self) -> dict:
        """Maps color values for the Color Indicator."""
        return indicator_color_map.copy()

    """
    COLORS
    """

    @cached_property
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.pinline_color_map
        )

    @cached_property
    def indicator_colors(self) -> list[SolidColor]:
        """Must be returned as list of SolidColor objects."""
        return [
            psd.get_rgb(*self.indicator_color_map.get(c, [0, 0, 0]))
            for c in self.layout.color_indicator[::-1]
        ] if self.is_type_shifted else []

    @cached_property
    def textbox_colors(self) -> Optional[str]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines

    @cached_property
    def crown_colors(self) -> Optional[str]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines

    @cached_property
    def twins_colors(self) -> Optional[str]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.twins

    @cached_property
    def background_colors(self) -> Optional[str]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.background

    """
    GROUPS
    """

    @cached_property
    def pinlines_group(self) -> Optional[LayerSet]:
        """Group containing pinlines colors, textures, or other groups."""
        return psd.getLayerSet(LAYERS.PINLINES)

    @cached_property
    def pinlines_groups(self) -> list[LayerSet]:
        """Groups where pinline colors will be generated."""
        return [self.pinlines_group]

    @cached_property
    def twins_group(self) -> Optional[LayerSet]:
        """Group containing twins texture layers."""
        return psd.getLayerSet(LAYERS.TWINS)

    @cached_property
    def textbox_group(self) -> Optional[LayerSet]:
        """Group containing textbox texture layers."""
        return psd.getLayerSet(LAYERS.TEXTBOX)

    @cached_property
    def background_group(self) -> Optional[LayerSet]:
        """Group containing background texture layers."""
        return psd.getLayerSet(LAYERS.BACKGROUND)

    @cached_property
    def crown_group(self) -> Optional[LayerSet]:
        """Group containing Legendary Crown texture layers."""
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN)

    @cached_property
    def pt_group(self) -> Optional[LayerSet]:
        """Group containing PT Box texture layers."""
        return psd.getLayerSet(LAYERS.PT_BOX)

    @cached_property
    def indicator_group(self) -> Optional[LayerSet]:
        """Group where Color Indicator colors will be generated."""
        if group := psd.getLayerSet(LAYERS.SHAPE, LAYERS.COLOR_INDICATOR):
            group.parent.visible = True
        return group

    @cached_property
    def mask_group(self) -> Optional[LayerSet]:
        """Group containing masks used to blend and adjust various layers."""
        return psd.getLayerSet(LAYERS.MASKS)

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        # MDFC Text Group
        if self.is_mdfc:
            return psd.getLayerSet(
                LAYERS.MODAL_FRONT if self.is_front else LAYERS.MODAL_BACK,
                self.text_group
            )
        return psd.getLayerSet(
            LAYERS.TF_FRONT if self.is_front else LAYERS.TF_BACK,
            self.text_group
        )

    """
    VECTOR SHAPES
    """

    @cached_property
    def border_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card border."""
        if self.is_legendary:
            return psd.getLayer(LAYERS.LEGENDARY, self.border_group)
        return psd.getLayer(LAYERS.NORMAL, self.border_group)

    @cached_property
    def pinlines_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card pinlines."""
        return psd.getLayer(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform else LAYERS.NORMAL,
            [self.pinlines_group, LAYERS.SHAPE])

    @cached_property
    def textbox_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card textbox."""
        name = LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL
        return psd.getLayer(name, [self.textbox_group, LAYERS.SHAPE])

    @cached_property
    def twins_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card name and title boxes."""
        name = LAYERS.TRANSFORM if self.is_transform else LAYERS.NORMAL
        return psd.getLayer(name, [self.twins_group, LAYERS.SHAPE])

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Vector shapes that should be enabled during the enable_shape_layers step."""
        return [
            self.border_shape,
            self.twins_shape,
            self.pinlines_shape,
            self.textbox_shape
        ]

    """
    BLENDING MASKS
    """

    @cached_property
    def mask_layers(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend multicolored layers."""
        return [psd.getLayer(LAYERS.HALF, self.mask_group)]

    @cached_property
    def indicator_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to build the Color Indicator."""
        if len(self.layout.color_indicator) == 2:
            # 2 colors -> Enable 2 outline
            psd.getLayer('2', self.indicator_group.parent).visible = True
            return [psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.COLOR_INDICATOR])]
        if len(self.layout.color_indicator) == 3:
            # 3 colors -> Enable 3 outline
            psd.getLayer('3', self.indicator_group.parent).visible = True
            return [
                psd.getLayer(LAYERS.THIRD, [self.mask_group, LAYERS.COLOR_INDICATOR]),
                psd.getLayer(LAYERS.TWO_THIRDS, [self.mask_group, LAYERS.COLOR_INDICATOR])
            ]
        return []

    @cached_property
    def crown_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend legendary crown layers. Defaults to mask_layers."""
        return self.mask_layers

    @cached_property
    def textbox_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend textbox layers. Defaults to mask_layers."""
        return self.mask_layers

    @cached_property
    def background_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend background layers. Defaults to mask_layers."""
        return self.mask_layers

    @cached_property
    def twins_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend background layers. Defaults to mask_layers."""
        return self.mask_layers

    """
    MASKS
    """

    @cached_property
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """
        Masks that should be copied or enabled during the `enable_layer_masks` step. Not utilized by default.

        @return:
            - dict: Advanced mask notation, contains "from" and "to" layers and other optional parameters.
            - list: Contains layer to copy from, layer to copy to.
            - ArtLayer | LayerSet: Layer object to enable a mask on.
            - None: Skip this mask.
        """
        return []

    """
    UTILITY METHODS
    """

    def create_blended_layer(
        self,
        group: LayerSet,
        colors: Union[None, str, list[str]] = None,
        masks: Optional[list[Union[ArtLayer, LayerSet]]] = None
    ):
        """
        Either enable a single frame layer or create a multicolor layer using a gradient mask.
        @param group: Group to look for the color layers within.
        @param colors: Color layers to look for.
        @param masks: Masks to use for blending the layers.
        """
        # Establish our masks
        if not masks:
            masks = self.mask_layers

        # Establish our colors
        colors = colors or self.identity or self.pinlines
        if isinstance(colors, str) and not contains_frame_colors(colors):
            # Received a color string that isn't a frame color combination
            colors = [colors]
        elif len(colors) >= self.color_limit:
            # Received too big a color combination, revert to pinlines
            colors = [self.pinlines]

        # Enable each layer color
        layers: list[ArtLayer] = []
        for i, color in enumerate(colors):
            layer = psd.getLayer(color, group)
            layer.visible = True

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers and len(masks) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(masks[i - 1], layers[i - 1])

            # Add to the layer list
            layers.append(layer)

    def create_blended_solid_color(
        self,
        group: LayerSet,
        colors: list[SolidColor],
        masks: Optional[list[Union[ArtLayer, LayerSet]]] = None
    ):
        """
        Either enable a single frame layer or create a multicolor layer using a gradient mask.
        @param group: Group to look for the color layers within.
        @param colors: Color layers to look for.
        @param masks: Masks to use for blending the layers.
        """
        # Establish our masks
        if masks is None:
            masks = self.mask_layers

        # Enable each layer color
        layers: list[ArtLayer] = []
        for i, color in enumerate(colors):
            layer = psd.smart_layer(psd.create_color_layer(color, group))

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers and len(masks) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(masks[i - 1], layers[i - 1])

            # Add to the layer list
            layers.append(layer)

    """
    RENDER CHAIN
    """

    def enable_frame_layers(self) -> None:
        """Build the card frame by enabling and/or creating various layer."""

        # Enable vector shapes
        self.enable_shape_layers()

        # Enable layer masks
        self.enable_layer_masks()

        # PT Box -> Single static layer
        if self.is_creature and self.pt_layer:
            self.pt_layer.visible = True

        # Color Indicator -> Blended solid color layers
        if self.is_type_shifted and self.indicator_group:
            self.create_blended_solid_color(
                group=self.indicator_group,
                colors=self.indicator_colors,
                masks=self.indicator_masks)

        # Pinlines -> Solid color or gradient layers
        for group in [g for g in self.pinlines_groups if g]:
            group.visible = True
            self.pinlines_action(self.pinlines_colors, layer=group)

        # Twins -> Blended texture layers
        if self.twins_group:
            self.create_blended_layer(
                group=self.twins_group,
                colors=self.twins_colors,
                masks=self.twins_masks)

        # Textbox -> Blended texture layers
        if self.textbox_group:
            self.create_blended_layer(
                group=self.textbox_group,
                colors=self.textbox_colors,
                masks=self.textbox_masks)

        # Background layer -> Blended texture layers
        if self.background_group:
            self.create_blended_layer(
                group=self.background_group,
                colors=self.background_colors,
                masks=self.background_masks)

        # Legendary crown
        if self.is_legendary and self.crown_group:
            self.enable_crown()

    def enable_shape_layers(self) -> None:
        """Enable required vector shape layers."""

        # Enable each shape
        for shape in self.enabled_shapes:
            if shape:
                shape.visible = True

    def enable_layer_masks(self) -> None:
        """Enable or copy required layer masks."""

        # For each mask enabled, apply it based on given notation
        for mask in [m for m in self.enabled_masks if m]:
            # Dict notation, complex mask behavior
            if isinstance(mask, dict):
                # Copy to a layer?
                if layer := mask.get('layer'):
                    # Copy normal or vector mask to layer
                    func = psd.copy_vector_mask if mask.get('vector') else psd.copy_layer_mask
                    func(mask.get('mask'), layer)
                else:
                    # Enable normal or vector mask
                    layer = mask.get('mask')
                    func = psd.enable_vector_mask if mask.get('vector') else psd.enable_mask
                    func(layer)

                # Apply extra functions
                [f(layer) for f in mask.get('funcs', [])]
            # List notation, copy from one layer to another
            elif isinstance(mask, list):
                psd.copy_layer_mask(*mask)
            # Single layer to enable mask on
            elif isinstance(mask, LayerObject):
                psd.enable_mask(mask)

    def enable_crown(self) -> None:
        """Enable the Legendary crown, only called if card is Legendary."""

        # Enable Legendary Crown group and layers
        self.crown_group.visible = True
        self.create_blended_layer(
            group=self.crown_group,
            colors=self.crown_colors,
            masks=self.crown_masks)

        # Enable Hollow Crown
        if self.is_nyx or self.is_companion:
            self.enable_hollow_crown(
                masks=[self.crown_group],
                vector_masks=[self.pinlines_group]
            )

    def enable_hollow_crown(self, **kwargs) -> None:
        """
        Enable the Hollow Crown within the Legendary Crown, only called if card is Legendary Nyx or Companion.
        @keyword masks (list[ArtLayer, LayerSet]): List of layers containing masks to enable.
        @keyword vector_masks (list[ArtLayer, LayerSet]): List of layers containing vector masks to enable.
        """

        # Layer masks to enable
        if kwargs.get('masks'):
            for m in kwargs.get('masks'):
                psd.enable_mask(m)

        # Vector masks to enable
        if kwargs.get('vector_masks'):
            for m in kwargs.get('vector_masks'):
                psd.enable_vector_mask(m)

        # Enable shadow
        if self.crown_shadow_layer:
            self.crown_shadow_layer.visible = True
