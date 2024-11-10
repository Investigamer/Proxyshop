"""
* Templates: Split
"""
# Standard Library Imports
from functools import cached_property
from pathlib import Path
from typing import Union, Optional

# Third Party Imports
from omnitils.strings import normalize_str
from photoshop.api import ElementPlacement, SolidColor, BlendMode
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import CFG, CON, ENV
from src.enums.layers import LAYERS
import src.helpers as psd
from src.helpers import LayerEffects
from src.layouts import SplitLayout
from src.schema.adobe import EffectColorOverlay, EffectGradientOverlay
from src.schema.colors import GradientColor
from src.templates import BaseTemplate
from src.text_layers import FormattedTextField, FormattedTextArea, ScaledTextField
from src.utils.adobe import ReferenceLayer

"""
* Template Classes
"""


class SplitTemplate(BaseTemplate):
    """
    * A template for split cards introduced in Invasion.

    Adds:
        * Must return all properties shared by both halves as a list of two items (left, right).
        * Must overwrite a lot of core functionality to navigate rendering 2 cards in one template.

    Todo:
        * Formalize as a vector template, implement 'Modifier' class.
    """
    is_vehicle = False
    is_artifact = False

    # Color and gradient maps
    fuse_gradient_locations = {
        **CON.gradient_locations.copy(),
        2: [.50, .54],
        3: [.28, .33, .71, .76],
        4: [.28, .33, .50, .54, .71, .76]
    }
    pinline_gradient_locations = [
        {**CON.gradient_locations.copy(), 2: [.28, .33]},
        {**CON.gradient_locations.copy(), 2: [.71, .76]}
    ]

    def __init__(self, layout: SplitLayout, **kwargs):
        super().__init__(layout, **kwargs)

    """
    * Mixin Methods
    """

    @property
    def post_text_methods(self):
        """Rotate card sideways."""
        return [*super().post_text_methods, psd.rotate_counter_clockwise]

    """
    * Bool Properties
    """

    @cached_property
    def is_centered(self) -> list[bool]:
        """Allow centered text for each side independently."""
        return [
            bool(
                len(self.layout.flavor_text[i]) <= 1
                and len(self.layout.oracle_text[i]) <= 70
                and "\n" not in self.layout.oracle_text[i]
            ) for i in range(2)
        ]

    @cached_property
    def is_fuse(self) -> bool:
        """Determine if this is a 'Fuse' split card."""
        return bool('Fuse' in self.layout.keywords)

    """
    * Colors
    """

    @cached_property
    def color_limit(self) -> int:
        """One more than the max number of colors this card can split by."""
        return 3

    @cached_property
    def fuse_pinlines(self) -> str:
        """Merged pinline colors of each side."""
        if self.pinlines[0] != self.pinlines[1]:
            return self.pinlines[0] + self.pinlines[1]
        return self.pinlines[0]

    @cached_property
    def fuse_textbox_colors(self) -> str:
        """Gold if Fuse colors are more than 3, otherwise use Fuse colors."""
        if len(self.fuse_pinlines) > 3:
            return LAYERS.GOLD
        return self.fuse_pinlines

    @cached_property
    def fuse_pinline_colors(self) -> Union[list[int], list[dict]]:
        """Color definition for Fuse pinlines."""
        return psd.get_pinline_gradient(
            self.fuse_pinlines, location_map=self.fuse_gradient_locations)

    @cached_property
    def fuse_pinlines_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        """Action used to render Fuse pinlines."""
        return psd.create_color_layer if isinstance(
            self.fuse_pinline_colors, SolidColor
        ) else psd.create_gradient_layer

    @cached_property
    def pinlines_colors(self) -> list[Union[list[int], list[dict]]]:
        """Color definitions used for pinlines of each side."""
        return [
            psd.get_pinline_gradient(p, location_map=self.pinline_gradient_locations[i])
            for i, p in enumerate(self.pinlines)]

    @cached_property
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

    @cached_property
    def fuse_group(self) -> Optional[LayerSet]:
        """Fuse elements parent group."""
        return psd.getLayerSet('Fuse')

    @cached_property
    def fuse_textbox_group(self) -> Optional[LayerSet]:
        """Fuse textbox group."""
        return psd.getLayerSet(LAYERS.TEXTBOX, self.fuse_group)

    @cached_property
    def fuse_pinlines_group(self) -> Optional[LayerSet]:
        """Fuse pinlines group."""
        return psd.getLayerSet(LAYERS.PINLINES, self.fuse_group)

    @cached_property
    def text_group(self) -> Optional[LayerSet]:
        """One text and icons group located in the 'Left' side group."""
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, LAYERS.LEFT)

    @cached_property
    def card_groups(self):
        """Left and Right side parent groups."""
        return [
            psd.getLayerSet(LAYERS.LEFT),
            psd.getLayerSet(LAYERS.RIGHT)
        ]

    @cached_property
    def pinlines_groups(self) -> list[LayerSet]:
        """Pinlines group for each side."""
        return [psd.getLayerSet(LAYERS.PINLINES, group) for group in self.card_groups]

    @cached_property
    def twins_groups(self) -> list[LayerSet]:
        """Twins group for each side."""
        return [psd.getLayerSet(LAYERS.TWINS, group) for group in self.card_groups]

    @cached_property
    def textbox_groups(self) -> list[LayerSet]:
        """Textbox group for each side."""
        return [psd.getLayerSet(LAYERS.TEXTBOX, group) for group in self.card_groups]

    @cached_property
    def background_groups(self) -> list[LayerSet]:
        """Background group for each side."""
        return [psd.getLayerSet(LAYERS.BACKGROUND, group) for group in self.card_groups]

    """
    * References
    """

    @cached_property
    def textbox_reference(self) -> list[ArtLayer]:
        """Textbox positioning reference for each side."""
        return [
            psd.get_reference_layer(
                LAYERS.TEXTBOX_REFERENCE + ' Fuse' if self.is_fuse else LAYERS.TEXTBOX_REFERENCE,
                psd.getLayerSet(LAYERS.TEXT_AND_ICONS, group)
            ) for group in self.card_groups]

    @cached_property
    def name_reference(self) -> list[ArtLayer]:
        """list[ArtLayer]: Name reference for each side."""
        return self.text_layer_name

    @cached_property
    def type_reference(self) -> list[ArtLayer]:
        """list[ArtLayer]: Typeline reference for each side."""
        return [
            n or self.expansion_reference[i]
            for i, n in enumerate(self.expansion_symbols)]

    @cached_property
    def twins_reference(self) -> list[ArtLayer]:
        """Twins positioning reference for each side."""
        return [psd.getLayer('Reference', [group, LAYERS.TWINS]) for group in self.card_groups]

    @cached_property
    def background_reference(self) -> list[ArtLayer]:
        """Background positioning reference for each side."""
        return [psd.getLayer('Reference', [group, LAYERS.BACKGROUND]) for group in self.card_groups]

    @cached_property
    def art_reference(self) -> list[ArtLayer]:
        """Art layer positioning reference for each side."""
        return [psd.getLayer(LAYERS.ART_FRAME, group) for group in self.card_groups]

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name(self) -> list[ArtLayer]:
        """Name text layer for each side."""
        return [psd.getLayer(LAYERS.NAME, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def text_layer_rules(self) -> list[ArtLayer]:
        """Rules text layer for each side."""
        return [psd.getLayer(LAYERS.RULES_TEXT, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def text_layer_type(self) -> list[ArtLayer]:
        """Typeline text layer for each side."""
        return [psd.getLayer(LAYERS.TYPE_LINE, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    @cached_property
    def text_layer_mana(self) -> list[ArtLayer]:
        """Mana cost text layer for each side."""
        return [psd.getLayer(LAYERS.MANA_COST, [self.card_groups[i], LAYERS.TEXT_AND_ICONS]) for i in range(2)]

    """
    * Expansion Symbol
    """

    @cached_property
    def expansion_references(self) -> list[ArtLayer]:
        """Expansion reference for each side."""
        return [self.expansion_reference, self.expansion_reference_right]

    @cached_property
    def expansion_reference_right(self) -> None:
        """Right side expansion symbol reference."""
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, [LAYERS.RIGHT, LAYERS.TEXT_AND_ICONS])

    @cached_property
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

    @cached_property
    def art_layer(self) -> list[ArtLayer]:
        """Art layer for each side."""
        return [psd.getLayer(LAYERS.DEFAULT, group) for group in self.card_groups]

    @cached_property
    def background_layer(self) -> list[ArtLayer]:
        """Background layer for each side."""
        return [psd.getLayer(b, LAYERS.BACKGROUND) for b in self.background]

    @cached_property
    def twins_layer(self) -> list[ArtLayer]:
        """Twins layer for each side."""
        return [psd.getLayer(t, LAYERS.TWINS) for t in self.twins]

    @cached_property
    def textbox_layer(self) -> list[ArtLayer]:
        """Textbox layer for each side."""
        return [psd.getLayer(t, LAYERS.TEXTBOX) for t in self.pinlines]

    @cached_property
    def divider_layer(self) -> list[Optional[ArtLayer]]:
        """Divider layer for each side. List updated if either side has flavor text."""
        return [None, None]

    """
    * Blending Masks
    """

    @cached_property
    def mask_layers(self) -> list[ArtLayer]:
        """Blending masks supported by this template."""
        return [psd.getLayer(LAYERS.HALF, LAYERS.MASKS)]

    """
    * Watermarks
    """

    @cached_property
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
            else:
                colors.append([])
        return colors

    @cached_property
    def watermark_fx(self) -> list[list[LayerEffects]]:
        """A list of LayerEffects' objects for each face."""
        fx: list[list[LayerEffects]] = []
        for color in self.watermark_colors:
            if len(color) == 1:
                # Single color watermark
                fx.append([EffectColorOverlay(
                    opacity=100,
                    color=color[0]
                )])
            elif len(color) == 2:
                # Dual color watermark
                fx.append([EffectGradientOverlay(
                    rotation=0,
                    colors=[
                        GradientColor(
                            color=color[0],
                            location=0,
                            midpoint=50),
                        GradientColor(
                            color=color[1],
                            location=4096,
                            midpoint=50)
                    ]
                )])
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
            wm_details = CON.watermarks.get(watermark, {})

            # Import and frame the watermark
            wm = psd.import_svg(
                path=self.layout.watermark_svg[i],
                ref=self.textbox_reference[i],
                placement=ElementPlacement.PlaceAfter,
                docref=self.docref)
            psd.frame_layer(
                layer=wm,
                ref=self.textbox_reference[i],
                smallest=True,
                scale=wm_details.get('scale', 80))

            # Apply opacity, blending, and effects
            wm.opacity = wm_details.get('opacity', CFG.watermark_opacity)
            wm.blendMode = BlendMode.ColorBurn
            psd.apply_fx(wm, self.watermark_fx[i])

    """
    * Loading Files
    """

    def load_artwork(
        self,
        art_file: Optional[str | Path | list[str | Path]] = None,
        art_layer: Optional[list[ArtLayer]] = None,
        art_reference: Optional[list[ReferenceLayer]] = None
    ) -> None:
        """Loads the specified art file into the specified layer.

        Args:
            art_file: Optional path (as str or Path) to art file. Will use `self.layout.art_file`
                if not provided.
            art_layer: Optional `ArtLayer` where art image should be placed when imported. Will use `self.art_layer`
                property if not provided.
            art_reference: Optional `ReferenceLayer` that should be used to position and scale the imported
                image. Will use `self.art_reference` property if not provided.`
        """

        # Set default values
        art_file = art_file or self.layout.art_file
        art_layer = art_layer or self.art_layer
        art_reference = art_reference or self.art_reference

        # Double up art for test mode
        if ENV.TEST_MODE and not isinstance(art_file, list):
            art_file = [art_file] * 2

        # Second art not provided
        if len(art_file) == 1:

            # Manually select a second art
            self.console.update("Please select the second split art!")
            file = self.app.openDialog()
            if not file:
                self.console.update('No art selected, cancelling render.')
                self.console.cancel_thread(thr=self.event)
                return

            # Place new art in the correct order
            if normalize_str(self.layout.name[0]) == normalize_str(self.layout.file['name']):
                art_file.append(file[0])
            else:
                art_file.insert(0, file[0])

        # Load art for each side
        for i, ref in enumerate(art_reference):
            super().load_artwork(
                art_file=art_file[i],
                art_layer=art_layer[i],
                art_reference=ref)

    """
    * Frame Layer Methods
    """

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
            background = self.background_layer[i].duplicate(
                self.background_groups[i], ElementPlacement.PlaceInside)
            background.visible = True
            psd.align_horizontal(background, self.background_reference[i])

            # Copy textbox and position
            textbox = self.textbox_layer[i].duplicate(
                self.textbox_groups[i], ElementPlacement.PlaceInside)
            textbox.visible = True
            self.active_layer = textbox
            psd.align_horizontal(textbox, self.textbox_reference[i].dims)
            if self.is_fuse:
                psd.select_bounds(self.textbox_reference[i].bounds, self.doc_selection)
                self.doc_selection.invert()
                self.doc_selection.clear()
            self.doc_selection.deselect()

            # Apply pinlines
            self.generate_layer(
                group=self.pinlines_groups[i],
                colors=self.pinlines_colors[i])

        # Fuse addone
        if self.is_fuse:
            psd.getLayer(f'{LAYERS.BORDER} Fuse').visible = True
            self.fuse_group.visible = True
            self.generate_layer(
                group=self.fuse_pinlines_group,
                colors=self.fuse_pinline_colors)
            self.generate_layer(
                group=self.fuse_textbox_group,
                colors=self.fuse_textbox_colors,
                masks=self.mask_layers)

    """
    * Text Layer Methods
    """

    def basic_text_layers(self) -> None:
        """Add basic text layers for each side."""
        for i in range(2):
            self.text.extend([
                FormattedTextField(
                    layer=self.text_layer_mana[i],
                    contents=self.layout.mana_cost[i]
                ),
                ScaledTextField(
                    layer=self.text_layer_name[i],
                    contents=self.layout.name[i],
                    reference=self.name_reference[i]
                ),
                ScaledTextField(
                    layer=self.text_layer_type[i],
                    contents=self.layout.type_line[i],
                    reference=self.type_reference[i]
                )])

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and P/T text for each face."""
        for i in range(2):
            self.text.append(
                FormattedTextArea(
                    layer=self.text_layer_rules[i],
                    contents=self.layout.oracle_text[i],
                    flavor=self.layout.flavor_text[i],
                    reference=self.textbox_reference[i],
                    divider=self.divider_layer[i],
                    centered=self.is_centered[i]))
