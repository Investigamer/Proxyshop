"""
* Vector Parent Classes
* Vector templates use more advanced automation techniques including:
    - Automatically blended multicolor textures
    - Automatically blended SolidColor and gradient layers
    - Automatically generated color indicators
    - Architecture for mask and shape enabling based on card archetype
* Vector templates can be challenging for beginners, but have huge benefits.
"""

from collections.abc import Callable, Sequence
from functools import cached_property
from typing import NotRequired, TypedDict

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
from src.enums.layers import LAYERS
from src.schema.colors import (
    ColorObject,
    GradientConfig,
    crown_color_map,
    indicator_color_map,
    pinlines_color_map,
)
from src.templates import NormalTemplate


class MaskAction(TypedDict):
    layer: NotRequired[ArtLayer | LayerSet]
    mask: ArtLayer | LayerSet
    vector: NotRequired[bool]
    funcs: NotRequired[Sequence[Callable[[ArtLayer | LayerSet], None]]]
    """The layer is passed to the callback functions."""


"""
* Template Classes
"""


class VectorTemplate(NormalTemplate):
    """Next generation template using vector shape layers, automatic pinlines, and blended multicolor textures."""

    """
    * Frame Details
    """

    @cached_property
    def color_limit(self) -> int:
        """int: The maximum allowed colors that should be blended plus 1."""
        return 3

    """
    * Logical Tests
    """

    @cached_property
    def is_within_color_limit(self) -> bool:
        """bool: Whether the color identity of this card is within the bounds of `self.color_limit`."""
        return bool(1 < len(self.identity) < self.color_limit)

    """
    * Layer Groups
    """

    @cached_property
    def pinlines_group(self) -> LayerSet | None:
        """Group containing pinlines colors, textures, or other groups."""
        return psd.getLayerSet(LAYERS.PINLINES, self.docref)

    @cached_property
    def pinlines_groups(self) -> list[LayerSet]:
        """Groups where pinline colors will be generated."""
        if self.pinlines_group:
            return [self.pinlines_group]
        return []

    @cached_property
    def twins_group(self) -> LayerSet | None:
        """Group containing twins texture layers."""
        return psd.getLayerSet(LAYERS.TWINS, self.docref)

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        """Group containing textbox texture layers."""
        return psd.getLayerSet(LAYERS.TEXTBOX, self.docref)

    @cached_property
    def background_group(self) -> LayerSet | None:
        """Optional[LayerSet]: Group containing background texture layers."""
        return psd.getLayerSet(LAYERS.BACKGROUND, self.docref)

    @cached_property
    def crown_group(self) -> LayerSet | None:
        """Group containing Legendary Crown texture layers."""
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, self.docref)

    @cached_property
    def pt_group(self) -> LayerSet | None:
        """Group containing PT Box texture layers."""
        return psd.getLayerSet(LAYERS.PT_BOX, self.docref)

    @cached_property
    def indicator_group(self) -> LayerSet | None:
        """Group where Color Indicator colors will be generated."""
        if (
            group := psd.getLayerSet(
                LAYERS.SHAPE, [self.docref, LAYERS.COLOR_INDICATOR]
            )
        ) and isinstance((parent := group.parent), LayerSet):
            parent.visible = True
        return group

    """
    * Color Maps
    """

    @cached_property
    def pinlines_color_map(self) -> dict[str, ColorObject]:
        """Maps color values for the Pinlines."""
        return {**pinlines_color_map}

    @cached_property
    def crown_color_map(self) -> dict[str, ColorObject]:
        """Maps color values for the Legendary Crown."""
        return {**crown_color_map}

    @cached_property
    def indicator_color_map(
        self,
    ) -> dict[str, tuple[float, float, float] | tuple[float, float, float, float]]:
        """Maps color values for the Color Indicator."""
        return {**indicator_color_map}

    """
    * Colors
    """

    @cached_property
    def pinlines_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity
            if 1 < len(self.identity) < self.color_limit
            else self.pinlines,
            color_map=self.pinlines_color_map,
        )

    @cached_property
    def indicator_colors(
        self,
    ) -> list[tuple[float, float, float] | tuple[float, float, float, float]]:
        """Must be returned as list of RGB/CMYK color notations."""
        return (
            [
                self.indicator_color_map.get(c, (0, 0, 0))
                for c in self.layout.color_indicator[::-1]
            ]
            if self.layout.color_indicator
            else []
        )

    @cached_property
    def textbox_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return (
            self.identity
            if 1 < len(self.identity) < self.color_limit
            else self.pinlines
        )

    @cached_property
    def crown_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return (
            self.identity
            if 1 < len(self.identity) < self.color_limit
            else self.pinlines
        )

    @cached_property
    def twins_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.twins

    @cached_property
    def background_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.background

    @cached_property
    def pt_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as a color combination or layer name, e.g. WU or Artifact."""
        if self.is_vehicle and self.background == LAYERS.VEHICLE and self.text_layer_pt:
            # Typically use white text for Vehicle PT
            self.text_layer_pt.textItem.color = self.RGB_WHITE
            return LAYERS.VEHICLE
        return self.twins

    """
    * Vector Shapes
    
    Notes:
        Shape properties can be a single layer/layer group OR a list of layers and/or layer groups.
        Returning None or an empty list will cause that shape to be skipped.
    """

    @cached_property
    def border_shape(self) -> ArtLayer | None:
        """Vector shape representing the card border."""
        if isinstance(self.border_group, LayerSet):
            if self.is_legendary:
                return psd.getLayer(LAYERS.LEGENDARY, self.border_group)
            return psd.getLayer(LAYERS.NORMAL, self.border_group)

    @cached_property
    def crown_shape(self) -> ArtLayer | None:
        """Vector shape representing the legendary crown. This isn't typically used, so by default
        it just returns empty."""
        return None

    @cached_property
    def pinlines_shape(self) -> ArtLayer | None:
        """Vector shape representing the card pinlines."""
        return psd.getLayer(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform
            else LAYERS.NORMAL,
            [self.pinlines_group, LAYERS.SHAPE],
        )

    @cached_property
    def textbox_shape(self) -> ArtLayer | None:
        """Vector shape representing the card textbox."""
        name = (
            LAYERS.TRANSFORM_FRONT
            if self.is_transform and self.is_front
            else LAYERS.NORMAL
        )
        return psd.getLayer(name, [self.textbox_group, LAYERS.SHAPE])

    @cached_property
    def twins_shape(self) -> ArtLayer | None:
        """Vector shape representing the card name and title boxes."""
        name = LAYERS.TRANSFORM if self.is_transform or self.is_mdfc else LAYERS.NORMAL
        return psd.getLayer(name, [self.twins_group, LAYERS.SHAPE])

    @cached_property
    def enabled_shapes(self) -> list[ArtLayer | LayerSet | None]:
        """Vector shapes that should be enabled during the enable_shape_layers step. Should be
        a list of layer, layer group, or None objects."""
        return [
            self.border_shape,
            self.crown_shape,
            self.pinlines_shape,
            self.twins_shape,
            self.textbox_shape,
        ]

    """
    * Blending Masks
    """

    @cached_property
    def indicator_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to build the Color Indicator."""
        if len(self.layout.color_indicator) == 2 and self.indicator_group:
            # 2 colors -> Enable 2 outline
            if layer := psd.getLayer("2", self.indicator_group.parent):
                layer.visible = True
            if layer := psd.getLayer(
                LAYERS.HALF, [self.mask_group, LAYERS.COLOR_INDICATOR]
            ):
                return [layer]
            return []
        if len(self.layout.color_indicator) == 3 and self.indicator_group:
            # 3 colors -> Enable 3 outline
            if layer := psd.getLayer("3", self.indicator_group.parent):
                layer.visible = True
            return [
                layer
                for layer in (
                    psd.getLayer(
                        LAYERS.THIRD, [self.mask_group, LAYERS.COLOR_INDICATOR]
                    ),
                    psd.getLayer(
                        LAYERS.TWO_THIRDS, [self.mask_group, LAYERS.COLOR_INDICATOR]
                    ),
                )
                if layer
            ]
        return []

    @cached_property
    def pinlines_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend Pinlines layers. Default: `mask_layers`."""
        return self.mask_layers

    @cached_property
    def crown_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend legendary crown layers. Default: `mask_layers`."""
        return self.mask_layers

    @cached_property
    def textbox_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend textbox layers. Default: `mask_layers`."""
        return self.mask_layers

    @cached_property
    def background_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend background layers. Default: `mask_layers`."""
        return self.mask_layers

    @cached_property
    def twins_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend background layers. Default: `mask_layers`."""
        return self.mask_layers

    @cached_property
    def pt_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend PT box layers. Default: `mask_layers`."""
        return self.mask_layers

    """
    * Masks to Enable
    """

    @cached_property
    def enabled_masks(
        self,
    ) -> list[
        MaskAction
        | tuple[ArtLayer | LayerSet, ArtLayer | LayerSet]
        | ArtLayer
        | LayerSet
        | None
    ]:
        """
        Masks that should be copied or enabled during the `enable_layer_masks` step. Not utilized by default.

        Returns:
            - dict: Advanced mask notation, contains "from" and "to" layers and other optional parameters.
            - tuple: Contains layer to copy from, layer to copy to.
            - ArtLayer | LayerSet: Layer object to enable a mask on.
            - None: Skip this mask.
        """
        return []

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self) -> None:
        """Build the card frame by enabling and/or generating various layer."""

        # Enable vector shapes
        self.enable_shape_layers()

        # Enable layer masks
        self.enable_layer_masks()

        # PT Box -> Single static layer
        if self.is_creature and self.pt_group:
            self.pt_group.visible = True
            self.generate_layer(
                group=self.pt_group, colors=self.pt_colors, masks=self.pt_masks
            )

        # Color Indicator -> Blended solid color layers
        if self.is_type_shifted and self.indicator_group:
            self.generate_layer(
                group=self.indicator_group,
                colors=self.indicator_colors,
                masks=self.indicator_masks,
            )

        # Pinlines -> Solid color or gradient layers
        for group in [g for g in self.pinlines_groups if g]:
            group.visible = True
            self.generate_layer(
                group=group, colors=self.pinlines_colors, masks=self.pinlines_masks
            )

        # Twins -> Blended texture layers
        if self.twins_group:
            self.generate_layer(
                group=self.twins_group, colors=self.twins_colors, masks=self.twins_masks
            )

        # Textbox -> Blended texture layers
        if self.textbox_group:
            self.generate_layer(
                group=self.textbox_group,
                colors=self.textbox_colors,
                masks=self.textbox_masks,
            )

        # Background layer -> Blended texture layers
        if self.background_group:
            self.generate_layer(
                group=self.background_group,
                colors=self.background_colors,
                masks=self.background_masks,
            )

        # Legendary crown
        if self.is_legendary:
            self.enable_crown()

    def enable_shape_layers(self) -> None:
        """Enable required vector shape layers provided by `enabled_shapes`."""

        def _enable_shape(
            shapes: list[ArtLayer | LayerSet | None],
        ) -> None:
            for x in shapes:
                if not x:
                    continue
                else:
                    x.visible = True

        _enable_shape(self.enabled_shapes)

    def enable_layer_masks(self) -> None:
        """Enable or copy required layer masks provided by `enabled_masks`."""

        # For each mask enabled, apply it based on given notation
        for mask in [m for m in self.enabled_masks if m]:
            # Dict notation, complex mask behavior
            if isinstance(mask, dict):
                # Copy to a layer?
                if layer := mask.get("layer"):
                    # Copy normal or vector mask to layer
                    func = (
                        psd.copy_vector_mask
                        if mask.get("vector")
                        else psd.copy_layer_mask
                    )
                    func(mask.get("mask"), layer)
                else:
                    # Enable normal or vector mask
                    layer = mask.get("mask")
                    func = (
                        psd.enable_vector_mask
                        if mask.get("vector")
                        else psd.enable_mask
                    )
                    func(layer)

                # Apply extra functions
                [f(layer) for f in mask.get("funcs", [])]

            # Tuple notation, copy from one layer to another
            elif isinstance(mask, tuple):
                psd.copy_layer_mask(*mask)

            # Single layer to enable mask on
            else:
                psd.enable_mask(mask)

    def enable_crown(self) -> None:
        """Enable the Legendary crown, only called if card is Legendary."""

        # Enable Legendary Crown group and layers
        if self.crown_group:
            self.crown_group.visible = True
            self.generate_layer(
                group=self.crown_group, colors=self.crown_colors, masks=self.crown_masks
            )

            # Enable Hollow Crown
            if self.is_hollow_crown:
                self.enable_hollow_crown()

    def enable_hollow_crown(self) -> None:
        """Enable the Hollow Crown within the Legendary Crown, only called if card is Legendary Nyx or Companion.

        Keyword Args:
            masks (list[ArtLayer | LayerSet]): List of layers containing masks to enable.
            vector_masks (list[ArtLayer | LayerSet]): List of layers containing vector masks to enable.
        """

        # Layer masks to enable
        if self.crown_group:
            psd.enable_mask(self.crown_group)

        # Vector masks to enable
        if self.pinlines_group:
            psd.enable_vector_mask(self.pinlines_group)

        # Enable shadow
        if self.crown_shadow_layer:
            self.crown_shadow_layer.visible = True
