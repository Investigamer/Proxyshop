"""
* Vector Parent Classes
* Vector templates use more advanced automation techniques including:
    - Automatically blended multicolor textures
    - Automatically blended SolidColor and gradient layers
    - Automatically generated color indicators
    - Architecture for mask and shape enabling based on card archetype
* Vector templates can be challenging for beginners, but have huge benefits.
"""
# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    ElementPlacement,
    SolidColor
)
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.adobe import LayerObject
from src.enums.layers import LAYERS
from src.enums.mtg import (
    crown_color_map,
    indicator_color_map,
    pinline_color_map
)
from src.frame_logic import contains_frame_colors
import src.helpers as psd
from src.templates import NormalTemplate
from src.utils.properties import auto_prop_cached

"""
* Template Classes
"""


class VectorTemplate (NormalTemplate):
    """Next generation template using vector shape layers, automatic pinlines, and blended multicolor textures."""

    """
    * Frame Details
    """

    @auto_prop_cached
    def color_limit(self) -> int:
        """int: The maximum allowed colors that should be blended plus 1."""
        return 3

    """
    * Logical Tests
    """

    @auto_prop_cached
    def is_within_color_limit(self) -> bool:
        """bool: Whether the color identity of this card is within the bounds of `self.color_limit`."""
        return bool(1 < len(self.identity) < self.color_limit)

    """
    * Layer Groups
    """

    @auto_prop_cached
    def pinlines_group(self) -> Optional[LayerSet]:
        """Group containing pinlines colors, textures, or other groups."""
        return psd.getLayerSet(LAYERS.PINLINES, self.docref)

    @auto_prop_cached
    def pinlines_groups(self) -> list[LayerSet]:
        """Groups where pinline colors will be generated."""
        return [self.pinlines_group]

    @auto_prop_cached
    def twins_group(self) -> Optional[LayerSet]:
        """Group containing twins texture layers."""
        return psd.getLayerSet(LAYERS.TWINS, self.docref)

    @auto_prop_cached
    def textbox_group(self) -> Optional[LayerSet]:
        """Group containing textbox texture layers."""
        return psd.getLayerSet(LAYERS.TEXTBOX, self.docref)

    @auto_prop_cached
    def background_group(self) -> Optional[LayerSet]:
        """Group containing background texture layers."""
        return psd.getLayerSet(LAYERS.BACKGROUND, self.docref)

    @auto_prop_cached
    def crown_group(self) -> Optional[LayerSet]:
        """Group containing Legendary Crown texture layers."""
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, self.docref)

    @auto_prop_cached
    def pt_group(self) -> Optional[LayerSet]:
        """Group containing PT Box texture layers."""
        return psd.getLayerSet(LAYERS.PT_BOX, self.docref)

    @auto_prop_cached
    def indicator_group(self) -> Optional[LayerSet]:
        """Group where Color Indicator colors will be generated."""
        if group := psd.getLayerSet(LAYERS.SHAPE, [self.docref, LAYERS.COLOR_INDICATOR]):
            group.parent.visible = True
        return group

    @auto_prop_cached
    def mask_group(self) -> Optional[LayerSet]:
        """Group containing masks used to blend and adjust various layers."""
        return psd.getLayerSet(LAYERS.MASKS, self.docref)

    """
    * Color Maps
    """

    @auto_prop_cached
    def pinline_color_map(self) -> dict:
        """Maps color values for the Pinlines."""
        return pinline_color_map.copy()

    @auto_prop_cached
    def crown_color_map(self) -> dict:
        """Maps color values for the Legendary Crown."""
        return crown_color_map.copy()

    @auto_prop_cached
    def indicator_color_map(self) -> dict:
        """Maps color values for the Color Indicator."""
        return indicator_color_map.copy()

    """
    * Colors
    """

    @auto_prop_cached
    def pinlines_colors(self) -> Union[list[int], list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.pinline_color_map
        )

    @auto_prop_cached
    def indicator_colors(self) -> list[list[int]]:
        """Must be returned as list of SolidColor objects."""
        return [
            self.indicator_color_map.get(c, [0, 0, 0])
            for c in self.layout.color_indicator[::-1]
        ] if self.layout.color_indicator else []

    @auto_prop_cached
    def textbox_colors(self) -> str:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines

    @auto_prop_cached
    def crown_colors(self) -> str:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines

    @auto_prop_cached
    def twins_colors(self) -> str:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.twins

    @auto_prop_cached
    def background_colors(self) -> str:
        """Must be returned as color combination or layer name, e.g. WU or Artifact."""
        return self.background

    @auto_prop_cached
    def pt_colors(self) -> str:
        """Optional[str]: returned as a color combination or layer name, e.g. WU or Artifact."""
        if self.is_vehicle and self.background == LAYERS.VEHICLE:
            # Typically use white text for Vehicle PT
            self.text_layer_pt.textItem.color = self.RGB_WHITE
            return LAYERS.VEHICLE
        return self.twins

    """
    * Vector Shapes
    """

    @auto_prop_cached
    def border_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card border."""
        if self.is_legendary:
            return psd.getLayer(LAYERS.LEGENDARY, self.border_group)
        return psd.getLayer(LAYERS.NORMAL, self.border_group)

    @auto_prop_cached
    def pinlines_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card pinlines."""
        return psd.getLayer(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform else LAYERS.NORMAL,
            [self.pinlines_group, LAYERS.SHAPE])

    @auto_prop_cached
    def textbox_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card textbox."""
        name = LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL
        return psd.getLayer(name, [self.textbox_group, LAYERS.SHAPE])

    @auto_prop_cached
    def twins_shape(self) -> Optional[ArtLayer]:
        """Vector shape representing the card name and title boxes."""
        name = LAYERS.TRANSFORM if self.is_transform or self.is_mdfc else LAYERS.NORMAL
        return psd.getLayer(name, [self.twins_group, LAYERS.SHAPE])

    @auto_prop_cached
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Vector shapes that should be enabled during the enable_shape_layers step."""
        return [
            self.border_shape,
            self.twins_shape,
            self.pinlines_shape,
            self.textbox_shape
        ]

    """
    * Blending Masks
    """

    @auto_prop_cached
    def mask_layers(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend multicolored layers."""
        return [psd.getLayer(LAYERS.HALF, self.mask_group)]

    @auto_prop_cached
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

    @auto_prop_cached
    def pinlines_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend Pinlines layers. Default: `mask_layers`."""
        return self.mask_layers

    @auto_prop_cached
    def crown_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend legendary crown layers. Default: `mask_layers`."""
        return self.mask_layers

    @auto_prop_cached
    def textbox_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend textbox layers. Default: `mask_layers`."""
        return self.mask_layers

    @auto_prop_cached
    def background_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend background layers. Default: `mask_layers`."""
        return self.mask_layers

    @auto_prop_cached
    def twins_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend background layers. Default: `mask_layers`."""
        return self.mask_layers

    @auto_prop_cached
    def pt_masks(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend PT box layers. Default: `mask_layers`."""
        return self.mask_layers

    """
    * Masks to Enable
    """

    @auto_prop_cached
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """
        Masks that should be copied or enabled during the `enable_layer_masks` step. Not utilized by default.

        Returns:
            - dict: Advanced mask notation, contains "from" and "to" layers and other optional parameters.
            - list: Contains layer to copy from, layer to copy to.
            - ArtLayer | LayerSet: Layer object to enable a mask on.
            - None: Skip this mask.
        """
        return []

    """
    * Utility Methods
    """

    def create_blended_layer(
        self,
        group: LayerSet,
        colors: Union[None, str, list[str]] = None,
        masks: Optional[list[Union[ArtLayer, LayerSet]]] = None
    ):
        """Either enable a single frame layer or create a multicolor layer using a gradient mask.

        Args:
            group: Group to look for the color layers within.
            colors: Color layers to look for.
            masks: Masks to use for blending the layers.
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
        elif isinstance(colors, str):
            # Convert string of colors to list
            colors = list(colors)

        # Single layer
        if len(colors) == 1:
            layer = psd.getLayer(colors[0], group)
            layer.visible = True
            return

        # Enable each layer color
        layers: list[ArtLayer] = []
        for i, color in enumerate(colors):

            # Make layer visible
            layer = psd.getLayer(color, group)
            layer.visible = True

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers and len(masks) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(masks[i - 1], layers[i - 1])

            # Add to the layer list
            layers.append(layer)

    @staticmethod
    def create_blended_solid_color(
        group: LayerSet,
        colors: list[SolidColor],
        masks: Optional[list[Union[ArtLayer, LayerSet]]] = None
    ) -> None:
        """Either enable a single frame layer or create a multicolor layer using a gradient mask.

        Args:
            group: Group to look for the color layers within.
            colors: Color layers to look for.
            masks: Masks to use for blending the layers.
        """
        # Ensure masks is a list
        masks = masks or []

        # Enable each layer color
        layers: list[ArtLayer] = []
        for i, color in enumerate(colors):
            layer = psd.smart_layer(psd.create_color_layer(color, group))

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers and len(masks) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(masks[i - 1], layers[i - 1])
            layers.append(layer)

    def generate_layer(
        self, group: Union[ArtLayer, LayerSet],
        colors: Union[list[list[int]], list[int], list[dict], list[str], str],
        masks: Optional[list[ArtLayer]] = None
    ) -> Optional[ArtLayer]:
        """Takes information about a frame layer group and routes it to the correct
        generation function which blends rasterized layers, blends solid color layers, or
        generates a solid color/gradient adjustment layer.

        Notes:
            The result for a given 'colors' schema:
            - str: Enable a single texture layer.
            - list[str]: Blend multiple texture layers.
            - list[int]: Create a solid color adjustment layer.
            - list[dict]: Create a gradient adjustment layer.
            - list[list[int]]: Blend multiple solid color adjustment layers.

        Args:
            group: Layer or group containing layers.
            colors: Color definition for this frame layer generation.
            masks: Masks used to blend this generated layer.
        """
        # Assign a generator task based on colors value
        if isinstance(colors, str):
            # Hex color
            if colors.startswith('#'):
                return psd.create_color_layer(
                    color=colors,
                    layer=group,
                    docref=self.docref)
            # Blended texture layers
            return self.create_blended_layer(
                group=group,
                colors=colors,
                masks=masks)
        if isinstance(colors, list):
            if all(isinstance(c, str) for c in colors):
                # Hex colors
                if colors[0].startswith('#'):
                    return psd.create_color_layer(
                        color=colors,
                        layer=group,
                        docref=self.docref)
                # Blended texture layers
                return self.create_blended_layer(
                    group=group,
                    colors=colors,
                    masks=masks)
            if all(isinstance(c, int) for c in colors):
                # RGB/CMYK adjustment layer
                return psd.create_color_layer(
                    color=colors,
                    layer=group,
                    docref=self.docref)
            if all(isinstance(c, dict) for c in colors):
                # Gradient adjustment layer
                return psd.create_gradient_layer(
                    colors=colors,
                    layer=group,
                    docref=self.docref)
            if all(isinstance(c, list) for c in colors):
                # Blended RGB/CMYK adjustment layers
                return self.create_blended_solid_color(
                    group=group,
                    colors=colors,
                    masks=masks)

        # Failed to match a recognized color notation
        if group:
            self.log(f"Couldn't generate frame element: '{group.name}'")

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
                group=self.pt_group,
                colors=self.pt_colors,
                masks=self.pt_masks)

        # Color Indicator -> Blended solid color layers
        if self.is_type_shifted and self.indicator_group:
            self.generate_layer(
                group=self.indicator_group,
                colors=self.indicator_colors,
                masks=self.indicator_masks)

        # Pinlines -> Solid color or gradient layers
        for group in [g for g in self.pinlines_groups if g]:
            group.visible = True
            self.generate_layer(
                group=group,
                colors=self.pinlines_colors,
                masks=self.pinlines_masks)

        # Twins -> Blended texture layers
        if self.twins_group:
            self.generate_layer(
                group=self.twins_group,
                colors=self.twins_colors,
                masks=self.twins_masks)

        # Textbox -> Blended texture layers
        if self.textbox_group:
            self.generate_layer(
                group=self.textbox_group,
                colors=self.textbox_colors,
                masks=self.textbox_masks)

        # Background layer -> Blended texture layers
        if self.background_group:
            self.generate_layer(
                group=self.background_group,
                colors=self.background_colors,
                masks=self.background_masks)

        # Legendary crown
        if self.is_legendary:
            self.enable_crown()

    def enable_shape_layers(self) -> None:
        """Enable required vector shape layers provided by `enabled_shapes`."""

        # Enable each shape
        for shape in self.enabled_shapes:
            if shape:
                shape.visible = True

    def enable_layer_masks(self) -> None:
        """Enable or copy required layer masks provided by `enabled_masks`."""

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
        self.generate_layer(
            group=self.crown_group,
            colors=self.crown_colors,
            masks=self.crown_masks)

        # Enable Hollow Crown
        if self.is_hollow_crown:
            self.enable_hollow_crown(
                masks=[self.crown_group],
                vector_masks=[self.pinlines_group])

    def enable_hollow_crown(self, **kwargs) -> None:
        """Enable the Hollow Crown within the Legendary Crown, only called if card is Legendary Nyx or Companion.

        Keyword Args:
            masks (list[ArtLayer | LayerSet]): List of layers containing masks to enable.
            vector_masks (list[ArtLayer | LayerSet]): List of layers containing vector masks to enable.
        """

        # Layer masks to enable
        for m in kwargs.get('masks', []):
            psd.enable_mask(m)

        # Vector masks to enable
        for m in kwargs.get('vector_masks', []):
            psd.enable_vector_mask(m)

        # Enable shadow
        if self.crown_shadow_layer:
            self.crown_shadow_layer.visible = True
