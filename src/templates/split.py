"""
* SPLIT TEMPLATES
"""
from os import path as osp
from functools import cached_property
from typing import Union, Optional

from photoshop.api import ElementPlacement, SolidColor, AnchorPosition, BlendMode
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

from src.constants import con
from src.enums.layers import LAYERS
from src.frame_logic import contains_frame_colors
from src.layouts import SplitLayout
from src.settings import cfg
from src.templates import BaseTemplate
import src.text_layers as text_classes
import src.helpers as psd
from src.utils.strings import normalize_str


class SplitTemplate (BaseTemplate):
    """
    * A template for split cards introduced in Invasion.

    Adds:
        * Must return all properties shared by both halves as a list of two items (left, right).
        * Must overwrite a lot of core functionality to navigate rendering 2 cards in one template.
    """

    def __init__(self, layout: SplitLayout):
        super().__init__(layout)

    """
    BOOL
    """

    @cached_property
    def is_centered(self) -> list[bool]:
        return [
            bool(
                len(self.layout.flavor_text[i]) <= 1
                and len(self.layout.oracle_text[i]) <= 70
                and "\n" not in self.layout.oracle_text[i]
            ) for i in range(2)
        ]

    @cached_property
    def is_fuse(self) -> bool:
        return bool('Fuse' in self.layout.keywords)

    """
    COLORS
    """

    @cached_property
    def color_limit(self) -> int:
        return 3

    @cached_property
    def fuse_pinlines(self) -> str:
        return self.layout.pinlines[0] + self.layout.pinlines[1]

    @cached_property
    def fuse_textbox_colors(self) -> str:
        if len(self.fuse_pinlines) > 3:
            return LAYERS.GOLD
        return self.fuse_pinlines

    @cached_property
    def fuse_pinline_colors(self) -> Union[SolidColor, list[dict]]:
        locations = {
            **con.gradient_locations.copy(),
            2: [.50, .54],
            3: [.28, .33, .71, .76],
            4: [.28, .33, .50, .54, .71, .76]
        }
        return psd.get_pinline_gradient(self.fuse_pinlines, location_map=locations)

    @cached_property
    def fuse_pinlines_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        return psd.create_color_layer if isinstance(
            self.fuse_pinline_colors, SolidColor
        ) else psd.create_gradient_layer

    @cached_property
    def pinlines_colors(self) -> list[Union[SolidColor, list[dict]]]:
        locations = [
            {**con.gradient_locations.copy(), 2: [.28, .33]},
            {**con.gradient_locations.copy(), 2: [.71, .76]}
        ]
        return [psd.get_pinline_gradient(p, location_map=locations[i]) for i, p in enumerate(self.layout.pinlines)]

    @cached_property
    def pinlines_action(self) -> list[Union[psd.create_color_layer, psd.create_gradient_layer]]:
        return [
            psd.create_color_layer if isinstance(
                colors, SolidColor
            ) else psd.create_gradient_layer for colors in self.pinlines_colors
        ]

    """
    GROUPS
    """

    @cached_property
    def fuse_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet('Fuse')

    @cached_property
    def fuse_textbox_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.TEXTBOX, self.fuse_group)

    @cached_property
    def fuse_pinlines_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.PINLINES, self.fuse_group)

    @cached_property
    def text_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, LAYERS.LEFT)

    @cached_property
    def card_groups(self):
        return [
            psd.getLayerSet(LAYERS.LEFT),
            psd.getLayerSet(LAYERS.RIGHT)
        ]

    @cached_property
    def pinlines_groups(self) -> list[LayerSet]:
        return [psd.getLayerSet(LAYERS.PINLINES, group) for group in self.card_groups]

    @cached_property
    def twins_groups(self) -> list[LayerSet]:
        return [psd.getLayerSet(LAYERS.TWINS, group) for group in self.card_groups]

    @cached_property
    def textbox_groups(self) -> list[LayerSet]:
        return [psd.getLayerSet(LAYERS.TEXTBOX, group) for group in self.card_groups]

    @cached_property
    def background_groups(self) -> list[LayerSet]:
        return [psd.getLayerSet(LAYERS.BACKGROUND, group) for group in self.card_groups]

    """
    REFERENCES
    """

    @cached_property
    def textbox_reference(self) -> list[ArtLayer]:
        return [psd.getLayer(
            LAYERS.TEXTBOX_REFERENCE + ' Fuse' if self.is_fuse else LAYERS.TEXTBOX_REFERENCE,
            [group, LAYERS.TEXT_AND_ICONS]) for group in self.card_groups
        ]

    @cached_property
    def twins_reference(self) -> list[ArtLayer]:
        return [psd.getLayer('Reference', [group, LAYERS.TWINS]) for group in self.card_groups]

    @cached_property
    def background_reference(self) -> list[ArtLayer]:
        return [psd.getLayer('Reference', [group, LAYERS.BACKGROUND]) for group in self.card_groups]

    @cached_property
    def art_reference(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.ART_FRAME, group) for group in self.card_groups]

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.NAME, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def text_layer_rules(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.RULES_TEXT, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def text_layer_type(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.TYPE_LINE, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def text_layer_mana(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.MANA_COST, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def expansion_reference_layer_right(self) -> None:
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, [LAYERS.RIGHT, LAYERS.TEXT_AND_ICONS])

    @cached_property
    def expansion_symbols(self) -> list[ArtLayer]:
        layer = self.expansion_symbol_layer.duplicate(self.expansion_reference_layer_right, ElementPlacement.PlaceAfter)
        psd.align_right(layer, self.expansion_reference_layer_right)
        return [self.expansion_symbol_layer, layer]

    @cached_property
    def divider_layer(self) -> list[Optional[ArtLayer]]:
        return [None, None]

    """
    LAYERS
    """

    @cached_property
    def art_layer(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.DEFAULT, group) for group in self.card_groups]

    @cached_property
    def background_layer(self) -> list[ArtLayer]:
        return [psd.getLayer(b, LAYERS.BACKGROUND) for b in self.layout.background]

    @cached_property
    def twins_layer(self) -> list[ArtLayer]:
        return [psd.getLayer(t, LAYERS.TWINS) for t in self.layout.twins]

    @cached_property
    def textbox_layer(self) -> list[ArtLayer]:
        return [psd.getLayer(t, LAYERS.TEXTBOX) for t in self.layout.pinlines]

    @cached_property
    def mask_layers(self) -> list[ArtLayer]:
        return [psd.getLayer(LAYERS.HALF, LAYERS.MASKS)]

    """
    METHODS
    """

    def create_blended_layer(
        self,
        group: LayerSet,
        colors: Union[None, str, list[str]] = None
    ):
        """
        Either enable a single frame layer or create a multicolor layer using a gradient mask.
        @param group: Group to look for the color layers within.
        @param colors: Color layers to look for.
        """
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
            if layers and len(self.mask_layers) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(self.mask_layers[i - 1], layers[i - 1])

            # Add to the layer list
            layers.append(layer)

    def load_artwork(self) -> None:

        # Check for fullart test image
        if cfg.test_mode and self.is_fullart:
            self.layout.filename = [osp.join(con.path_img, "test-fa.png")] * 2
        elif cfg.test_mode:
            self.layout.filename = [self.layout.filename] * 2

        # Manually select a second artwork if not provided
        if len(self.layout.filename) == 1:
            self.console.update("Please select the second split art!")
            file = self.app.openDialog()
            if not file:
                self.console.update('No art selected, cancelling render.')
                self.console.cancel_thread(thr=self.event)
                return

            # Place new art in the correct order
            if normalize_str(self.layout.name[0]) == normalize_str(self.layout.file['name']):
                self.layout.filename.append(file[0])
            else:
                self.layout.filename.insert(0, file[0])

        # Load art for each side
        for i, ref in enumerate(self.art_reference):

            # Import the file into the art layer
            self.active_layer = self.art_layer[i]
            if self.art_action:
                psd.paste_file(self.art_layer[i], self.layout.filename[i], self.art_action, self.art_action_args)
            else:
                psd.import_art(self.art_layer[i], self.layout.filename[i])

            # Frame the artwork
            psd.frame_layer(self.active_layer, ref)

            # Perform content aware fill if needed
            if self.is_content_aware_enabled:
                action = psd.generative_fill_edges if cfg.generative_fill else psd.content_aware_fill_edges
                action(self.art_layer[i])

    def create_watermark(self) -> None:

        # Add watermark to each side if needed
        for i, watermark in enumerate(self.layout.watermark):

            # Is the watermark from Scryfall supported?
            wm_path = osp.join(con.path_img, f"watermarks/{watermark}.svg")
            if not watermark or not osp.exists(wm_path):
                return

            # Decide what colors to use
            colors = []
            if len(self.layout.pinlines[i]) == 2:
                colors.extend([con.watermark_colors[c] for c in self.layout.pinlines[i] if c in con.watermark_colors])
            elif self.layout.pinlines[i] in con.watermark_colors:
                colors.append(con.watermark_colors[self.layout.pinlines[i]])

            # Check for valid reference, valid colors, valid text layers group for placement
            if not self.textbox_reference or not colors:
                return

            # Get watermark custom settings if available
            wm_details = con.watermarks.get(watermark, {})

            # Generate the watermark
            wm = psd.import_svg(wm_path)
            psd.frame_layer(wm, self.textbox_reference[i], smallest=True)
            wm.resize(
                wm_details.get('scale', 80),
                wm_details.get('scale', 80),
                AnchorPosition.MiddleCenter)
            wm.move(self.textbox_reference[i], ElementPlacement.PlaceAfter)
            wm.blendMode = BlendMode.ColorBurn
            wm.opacity = wm_details.get('opacity', cfg.watermark_opacity)

            # Add the colors
            fx = []
            if len(colors) == 1:
                fx.append({
                    'type': 'color-overlay',
                    'opacity': 100,
                    'color': psd.get_color(colors[0])
                })
            elif len(colors) == 2:
                fx.append({
                    'type': 'gradient-overlay',
                    'rotation': 0,
                    'colors': [
                        {'color': colors[0], 'location': 0, 'midpoint': 50},
                        {'color': colors[1], 'location': 4096, 'midpoint': 50}
                    ]
                })
            psd.apply_fx(wm, fx)

    def basic_text_layers(self) -> None:

        # Base text layers for each side
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
                    reference = self.expansion_symbols[i]
                )
            ])

    def rules_text_and_pt_layers(self) -> None:

        # Rules text for each side
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

        # Frame layers for each side
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
            self.pinlines_action[i](self.pinlines_colors[i], self.pinlines_groups[i])

        # Fuse addone
        if self.is_fuse:
            psd.getLayer(LAYERS.BORDER + ' Fuse').visible = True
            self.fuse_group.visible = True
            self.fuse_pinlines_action(self.fuse_pinline_colors, self.fuse_pinlines_group)
            self.create_blended_layer(self.fuse_textbox_group, self.fuse_textbox_colors)

    def post_text_layers(self) -> None:
        psd.rotate_counter_clockwise()
