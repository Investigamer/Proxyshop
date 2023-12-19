"""
* Templates: Split
"""
# Standard Library Imports
from typing import Union, Optional

# Third Party Imports
from photoshop.api import ElementPlacement, SolidColor, AnchorPosition, BlendMode
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import CFG, CON, ENV, PATH
from src.enums.layers import LAYERS
from src.frame_logic import contains_frame_colors
import src.helpers as psd
from src.helpers import LayerEffects
from src.layouts import SplitLayout
from src.templates import BaseTemplate
import src.text_layers as text_classes
from src.utils.properties import auto_prop_cached
from src.utils.strings import normalize_str

"""
* Template Classes
"""


class SplitTemplate (BaseTemplate):
    """
    * A template for split cards introduced in Invasion.

    Adds:
        * Must return all properties shared by both halves as a list of two items (left, right).
        * Must overwrite a lot of core functionality to navigate rendering 2 cards in one template.
    """
    is_vehicle = False
    is_artifact = False

    def __init__(self, layout: SplitLayout):
        super().__init__(layout)

    """
    * Bool Properties
    """

    @auto_prop_cached
    def is_centered(self) -> list[bool]:
        """Allow centered text for each side independently."""
        return [
            bool(
                len(self.layout.flavor_text[i]) <= 1
                and len(self.layout.oracle_text[i]) <= 70
                and "\n" not in self.layout.oracle_text[i]
            ) for i in range(2)
        ]

    @auto_prop_cached
    def is_fuse(self) -> bool:
        """Determine if this is a 'Fuse' split card."""
        return bool('Fuse' in self.layout.keywords)

    """
    * Colors
    """

    @auto_prop_cached
    def color_limit(self) -> int:
        """One more than the max number of colors this card can split by."""
        return 3

    @auto_prop_cached
    def fuse_pinlines(self) -> str:
        """Merged pinline colors of each side."""
        if self.pinlines[0] != self.pinlines[1]:
            return self.pinlines[0] + self.pinlines[1]
        return self.pinlines[0]

    @auto_prop_cached
    def fuse_textbox_colors(self) -> str:
        """Gold if Fuse colors are more than 3, otherwise use Fuse colors."""
        if len(self.fuse_pinlines) > 3:
            return LAYERS.GOLD
        return self.fuse_pinlines

    @auto_prop_cached
    def fuse_pinline_colors(self) -> Union[SolidColor, list[dict]]:
        """Color definition for Fuse pinlines."""
        locations = {
            **CON.gradient_locations.copy(),
            2: [.50, .54],
            3: [.28, .33, .71, .76],
            4: [.28, .33, .50, .54, .71, .76]}
        return psd.get_pinline_gradient(
            self.fuse_pinlines, location_map=locations)

    @auto_prop_cached
    def fuse_pinlines_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        """Action used to render Fuse pinlines."""
        return psd.create_color_layer if isinstance(
            self.fuse_pinline_colors, SolidColor
        ) else psd.create_gradient_layer

    @auto_prop_cached
    def pinlines_colors(self) -> list[Union[SolidColor, list[dict]]]:
        """Color definitions used for pinlines of each side."""
        locations = [
            {**CON.gradient_locations.copy(), 2: [.28, .33]},
            {**CON.gradient_locations.copy(), 2: [.71, .76]}
        ]
        return [
            psd.get_pinline_gradient(p, location_map=locations[i])
            for i, p in enumerate(self.pinlines)]

    @auto_prop_cached
    def pinlines_action(self) -> list[Union[psd.create_color_layer, psd.create_gradient_layer]]:
        """Action used to render the pinlines of each side."""
        return [
            psd.create_color_layer if isinstance(
                colors, SolidColor
            ) else psd.create_gradient_layer
            for colors in self.pinlines_colors]

    """
    * Layer Groups
    """

    @auto_prop_cached
    def fuse_group(self) -> Optional[LayerSet]:
        """Fuse elements parent group."""
        return psd.getLayerSet('Fuse')

    @auto_prop_cached
    def fuse_textbox_group(self) -> Optional[LayerSet]:
        """Fuse textbox group."""
        return psd.getLayerSet(LAYERS.TEXTBOX, self.fuse_group)

    @auto_prop_cached
    def fuse_pinlines_group(self) -> Optional[LayerSet]:
        """Fuse pinlines group."""
        return psd.getLayerSet(LAYERS.PINLINES, self.fuse_group)

    @auto_prop_cached
    def text_group(self) -> Optional[LayerSet]:
        """One text and icons group located in the 'Left' side group."""
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, LAYERS.LEFT)

    @auto_prop_cached
    def card_groups(self):
        """Left and Right side parent groups."""
        return [
            psd.getLayerSet(LAYERS.LEFT),
            psd.getLayerSet(LAYERS.RIGHT)
        ]

    @auto_prop_cached
    def pinlines_groups(self) -> list[LayerSet]:
        """Pinlines group for each side."""
        return [psd.getLayerSet(LAYERS.PINLINES, group) for group in self.card_groups]

    @auto_prop_cached
    def twins_groups(self) -> list[LayerSet]:
        """Twins group for each side."""
        return [psd.getLayerSet(LAYERS.TWINS, group) for group in self.card_groups]

    @auto_prop_cached
    def textbox_groups(self) -> list[LayerSet]:
        """Textbox group for each side."""
        return [psd.getLayerSet(LAYERS.TEXTBOX, group) for group in self.card_groups]

    @auto_prop_cached
    def background_groups(self) -> list[LayerSet]:
        """Background group for each side."""
        return [psd.getLayerSet(LAYERS.BACKGROUND, group) for group in self.card_groups]

    """
    * References
    """

    @auto_prop_cached
    def textbox_reference(self) -> list[ArtLayer]:
        """Textbox positioning reference for each side."""
        return [psd.getLayer(
            LAYERS.TEXTBOX_REFERENCE + ' Fuse' if self.is_fuse else LAYERS.TEXTBOX_REFERENCE,
            [group, LAYERS.TEXT_AND_ICONS]) for group in self.card_groups
        ]

    @auto_prop_cached
    def twins_reference(self) -> list[ArtLayer]:
        """Twins positioning reference for each side."""
        return [psd.getLayer('Reference', [group, LAYERS.TWINS]) for group in self.card_groups]

    @auto_prop_cached
    def background_reference(self) -> list[ArtLayer]:
        """Background positioning reference for each side."""
        return [psd.getLayer('Reference', [group, LAYERS.BACKGROUND]) for group in self.card_groups]

    @auto_prop_cached
    def art_reference(self) -> list[ArtLayer]:
        """Art layer positioning reference for each side."""
        return [psd.getLayer(LAYERS.ART_FRAME, group) for group in self.card_groups]

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_name(self) -> list[ArtLayer]:
        """Name text layer for each side."""
        return [psd.getLayer(LAYERS.NAME, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @auto_prop_cached
    def text_layer_rules(self) -> list[ArtLayer]:
        """Rules text layer for each side."""
        return [psd.getLayer(LAYERS.RULES_TEXT, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @auto_prop_cached
    def text_layer_type(self) -> list[ArtLayer]:
        """Typeline text layer for each side."""
        return [psd.getLayer(LAYERS.TYPE_LINE, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @auto_prop_cached
    def text_layer_mana(self) -> list[ArtLayer]:
        """Mana cost text layer for each side."""
        return [psd.getLayer(LAYERS.MANA_COST, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    """
    * Expansion Symbol
    """

    @auto_prop_cached
    def expansion_references(self) -> list[ArtLayer]:
        """Expansion reference for each side."""
        return [self.expansion_reference, self.expansion_reference_right]

    @auto_prop_cached
    def expansion_reference_right(self) -> None:
        """Right side expansion symbol reference."""
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, [LAYERS.RIGHT, LAYERS.TEXT_AND_ICONS])

    @auto_prop_cached
    def expansion_symbols(self) -> list[Optional[ArtLayer]]:
        """Expansion symbol layers for each side. Right side is generated duplicating the left side."""
        if self.expansion_symbol_layer:
            layer = self.expansion_symbol_layer.duplicate(self.expansion_reference_right, ElementPlacement.PlaceAfter)
            psd.align_right(layer, self.expansion_reference_right)
            return [self.expansion_symbol_layer, layer]
        return [None, None]

    """
    * Layers
    """

    @auto_prop_cached
    def art_layer(self) -> list[ArtLayer]:
        """Art layer for each side."""
        return [psd.getLayer(LAYERS.DEFAULT, group) for group in self.card_groups]

    @auto_prop_cached
    def background_layer(self) -> list[ArtLayer]:
        """Background layer for each side."""
        return [psd.getLayer(b, LAYERS.BACKGROUND) for b in self.background]

    @auto_prop_cached
    def twins_layer(self) -> list[ArtLayer]:
        """Twins layer for each side."""
        return [psd.getLayer(t, LAYERS.TWINS) for t in self.twins]

    @auto_prop_cached
    def textbox_layer(self) -> list[ArtLayer]:
        """Textbox layer for each side."""
        return [psd.getLayer(t, LAYERS.TEXTBOX) for t in self.pinlines]

    @auto_prop_cached
    def divider_layer(self) -> list[Optional[ArtLayer]]:
        """Divider layer for each side. List updated if either side has flavor text."""
        return [None, None]

    """
    * Blending Masks
    """

    @auto_prop_cached
    def mask_layers(self) -> list[ArtLayer]:
        """Blending masks supported by this template."""
        return [psd.getLayer(LAYERS.HALF, LAYERS.MASKS)]

    """
    * Watermarks
    """

    @auto_prop_cached
    def watermark_colors(self) -> list[list[SolidColor]]:
        """A list of 'SolidColor' objects for each face."""
        colors = []
        for i, pinline in enumerate(self.pinlines):
            if pinline in self.watermark_color_map:
                # Named pinline colors
                colors.append([self.watermark_color_map.get(pinline, self.RGB_WHITE)])
            elif len(self.identity[i]) < 3:
                # Dual color based on identity
                colors.append([
                    self.watermark_color_map.get(c, self.RGB_WHITE)
                    for c in self.identity[i]])
            colors.append([])
        return colors

    @auto_prop_cached
    def watermark_fx(self) -> list[list[LayerEffects]]:
        """A list of LayerEffects' objects for each face."""
        fx: list[list[LayerEffects]] = []
        for color in self.watermark_colors:
            if len(color) == 1:
                fx.append([{
                    'type': 'color-overlay',
                    'opacity': 100,
                    'color': color[0]
                }])
            elif len(color) == 2:
                fx.append([{
                    'type': 'gradient-overlay',
                    'rotation': 0,
                    'colors': [
                        {'color': color[0], 'location': 0, 'midpoint': 50},
                        {'color': color[1], 'location': 4096, 'midpoint': 50}
                    ]
                }])
            else:
                fx.append([])
        return fx

    def create_watermark(self) -> None:
        """Render a watermark for each side that has one."""

        # Add watermark to each side if needed
        for i, watermark in enumerate(self.layout.watermark):

            # Required values to generate a Watermark
            if not all([
                self.layout.watermark_svg[i],
                self.textbox_reference[i],
                self.watermark_colors[i],
                watermark
            ]):
                return

            # Get watermark custom settings if available
            wm_details = CON.watermarks.get(self.layout.watermark[i], {})

            # Generate the watermark
            wm = psd.import_svg(str(self.layout.watermark_svg[i]))
            psd.frame_layer(wm, self.textbox_reference[i], smallest=True)
            wm.resize(
                wm_details.get('scale', 80),
                wm_details.get('scale', 80),
                AnchorPosition.MiddleCenter)
            wm.move(self.textbox_reference[i], ElementPlacement.PlaceAfter)
            wm.blendMode = BlendMode.ColorBurn
            wm.opacity = wm_details.get('opacity', CFG.watermark_opacity)

            # Add the colors
            psd.apply_fx(wm, self.watermark_fx[i])

    """
    * Methods
    """

    def create_blended_layer(
        self,
        group: LayerSet,
        colors: Union[str, list[str]]
    ) -> None:
        """Either enable a single frame layer or create a multicolor layer using a gradient mask.

        Args:
            group: Group to look for the color layers within.
            colors: Color layers to look for.
        """

        # Establish our colors
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
            if layers and len(self.mask_layers) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(self.mask_layers[i - 1], layers[i - 1])

            # Add to the layer list
            layers.append(layer)

    def load_artwork(self) -> None:
        """Lead artwork for each face."""

        # Check for fullart test image
        if ENV.TEST_MODE and self.is_fullart:
            p = (PATH.SRC_IMG / 'test-fa').with_suffix('.png')
            self.layout.art_file = [p, p]
        elif ENV.TEST_MODE:
            self.layout.art_file = [
                self.layout.art_file,
                self.layout.art_file]

        # Manually select a second artwork if not provided
        if len(self.layout.art_file) == 1:
            self.console.update("Please select the second split art!")
            file = self.app.openDialog()
            if not file:
                self.console.update('No art selected, cancelling render.')
                self.console.cancel_thread(thr=self.event)
                return

            # Place new art in the correct order
            if normalize_str(self.layout.name[0]) == normalize_str(self.layout.file['name']):
                self.layout.art_file.append(file[0])
            else:
                self.layout.art_file.insert(0, file[0])

        # Load art for each side
        for i, ref in enumerate(self.art_reference):

            # Import the file into the art layer
            self.active_layer = self.art_layer[i]
            if self.art_action:
                psd.paste_file(self.art_layer[i], self.layout.art_file[i], self.art_action, self.art_action_args)
            else:
                psd.import_art(self.art_layer[i], self.layout.art_file[i])

            # Frame the artwork
            psd.frame_layer(self.active_layer, ref)

            # Perform content aware fill if needed
            if self.is_content_aware_enabled:
                action = psd.generative_fill_edges if CFG.generative_fill else psd.content_aware_fill_edges
                action(self.art_layer[i])

    def basic_text_layers(self) -> None:
        """Add basic text layers for each side."""
        for i in range(2):
            self.text.extend([
                text_classes.FormattedTextField(
                    layer = self.text_layer_mana[i],
                    contents = self.layout.mana_cost[i]
                ),
                text_classes.ScaledTextField(
                    layer = self.text_layer_name[i],
                    contents = self.layout.name[i],
                    reference = self.text_layer_mana[i]
                ),
                text_classes.ScaledTextField(
                    layer = self.text_layer_type[i],
                    contents = self.layout.type_line[i],
                    reference = self.expansion_symbols[i] or self.expansion_reference[i]
                )
            ])

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and P/T text for each face."""
        for i in range(2):
            self.text.append(
                text_classes.FormattedTextArea(
                    layer = self.text_layer_rules[i],
                    contents = self.layout.oracle_text[i],
                    flavor = self.layout.flavor_text[i],
                    reference = self.textbox_reference[i],
                    divider = self.divider_layer[i],
                    centered = self.is_centered[i]
                )
            )

    def enable_frame_layers(self) -> None:
        """Enable frame layers for each side. Add Fuse layers if required."""

        # Frame layers
        for i in range(2):
            # Copy twins and position
            self.twins_layer[i].visible = True
            twins = self.twins_layer[i].parent.duplicate(self.twins_groups[i], ElementPlacement.PlaceBefore)
            self.twins_layer[i].visible = False
            twins.visible = True
            psd.align_horizontal(twins, self.twins_reference[i])

            # Copy background and position
            background = self.background_layer[i].duplicate(self.background_groups[i], ElementPlacement.PlaceInside)
            background.visible = True
            psd.align_horizontal(background, self.background_reference[i])

            # Copy textbox and position
            textbox = self.textbox_layer[i].duplicate(self.textbox_groups[i], ElementPlacement.PlaceInside)
            textbox.visible = True
            self.active_layer = textbox
            psd.select_layer_bounds(self.textbox_reference[i])
            psd.align_horizontal(textbox)
            if self.is_fuse:
                self.docref.selection.invert()
                self.docref.selection.clear()
            self.docref.selection.deselect()

            # Apply pinlines
            self.pinlines_action[i](self.pinlines_colors[i], layer=self.pinlines_groups[i])

        # Fuse addone
        if self.is_fuse:
            psd.getLayer(LAYERS.BORDER + ' Fuse').visible = True
            self.fuse_group.visible = True
            self.fuse_pinlines_action(
                self.fuse_pinline_colors,
                layer=self.fuse_pinlines_group)
            self.create_blended_layer(
                group=self.fuse_textbox_group,
                colors=self.fuse_textbox_colors)

    def post_text_layers(self) -> None:
        """Rotate image to make it vertical."""
        psd.rotate_counter_clockwise()
