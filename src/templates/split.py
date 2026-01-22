"""
* Templates: Split
"""

from _ctypes import COMError
from functools import cached_property
from pathlib import Path
from typing import Callable

from omnitils.strings import normalize_str
from photoshop.api import BlendMode, ElementPlacement, SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
from src import CFG, CON
from src.enums.layers import LAYERS
from src.helpers import LayerEffects
from src.helpers.colors import GradientConfig
from src.helpers.effects import copy_layer_fx
from src.helpers.layers import get_reference_layer
from src.layouts import SplitLayout
from src.schema.adobe import EffectColorOverlay, EffectGradientOverlay
from src.schema.colors import ColorObject, GradientColor
from src.templates import BaseTemplate
from src.text_layers import FormattedTextArea, FormattedTextField, ScaledTextField
from src.utils.adobe import ReferenceLayer


class SplitMod(BaseTemplate):
    """
    * A modifier class for split cards introduced in Invasion.

    Adds for each side:
        * Art
        * Text fields
        * Color definitions
    """

    sides: list[str] = [LAYERS.LEFT, LAYERS.RIGHT]

    # refion Color maps

    @cached_property
    def fuse_gradient_locations(self) -> dict[int, list[int | float]]:
        return {
            **CON.gradient_locations,
            2: [0.50, 0.54],
            3: [0.28, 0.33, 0.71, 0.76],
            4: [0.28, 0.33, 0.50, 0.54, 0.71, 0.76],
        }

    @cached_property
    def pinline_gradient_locations(self) -> list[dict[int, list[int | float]]]:
        return [
            {**CON.gradient_locations, 2: [0.28, 0.33]},
            {**CON.gradient_locations, 2: [0.71, 0.76]},
        ]

    # endregion Color maps

    # region Settings

    @cached_property
    def color_limit(self) -> int:
        """One more than the max number of colors this card can split by."""
        setting = CFG.get_setting(
            section="COLORS", key="Max.Colors", default="2", is_bool=False
        )
        if isinstance(setting, str):
            return int(setting) + 1
        raise ValueError(f"Received invalid value for color limit: {setting}")

    # endregion Settings

    # region Checks

    @cached_property
    def is_split(self) -> bool:
        return isinstance(self.layout, SplitLayout)

    @cached_property
    def text_centerings(self) -> list[bool]:
        """Allow centered text for each side independently."""
        if isinstance(self.layout, SplitLayout):
            return [
                bool(
                    len(self.layout.flavor_texts[i]) <= 1
                    and len(self.layout.oracle_texts[i]) <= 70
                    and "\n" not in self.layout.oracle_texts[i]
                )
                for i in range(len(self.sides))
            ]
        return []

    @cached_property
    def is_fuse(self) -> bool:
        """Determine if this is a 'Fuse' split card."""
        return bool("Fuse" in self.layout.keywords)

    @cached_property
    def has_unified_typeline(self) -> bool:
        """Determine if the card has only one shared typeline."""
        if isinstance(self.layout, SplitLayout):
            return " Room" in self.layout.type_line
        return False

    # endregion Checks

    # region Mixin methods

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        methods = super().frame_layer_methods
        if self.is_split:
            methods.append(self.frame_layers_split)
        return methods

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Rotate card sideways."""
        methods = super().post_text_methods
        if self.is_split:
            methods.append(psd.rotate_counter_clockwise)
        return methods

    # endregion Mixin methods

    # region Colors

    @cached_property
    def fuse_pinlines(self) -> str:
        """Merged pinline colors of each side."""
        if isinstance(self.layout, SplitLayout):
            if self.layout.pinline_identities[0] != self.layout.pinline_identities[1]:
                return (
                    self.layout.pinline_identities[0]
                    + self.layout.pinline_identities[1]
                )
            return self.layout.pinline_identities[0]
        raise NotImplementedError("Fuse colors doesn't support this layout.")

    @cached_property
    def fuse_textbox_colors(self) -> str:
        """Gold if Fuse colors are more than color_limit, otherwise use Fuse colors."""
        if len(self.fuse_pinlines) > self.color_limit:
            return LAYERS.GOLD
        return self.fuse_pinlines

    @cached_property
    def fuse_pinline_colors(
        self,
    ) -> ColorObject | list[ColorObject] | list[GradientConfig]:
        """Color definition for Fuse pinlines."""
        return psd.get_pinline_gradient(
            self.fuse_pinlines, location_map=self.fuse_gradient_locations
        )

    @cached_property
    def pinlines_colors_split(
        self,
    ) -> list[(ColorObject | list[ColorObject] | list[GradientConfig])]:
        """Color definitions used for pinlines of each side."""
        if isinstance(self.layout, SplitLayout):
            return [
                psd.get_pinline_gradient(
                    p, location_map=self.pinline_gradient_locations[i]
                )
                for i, p in enumerate(self.layout.pinline_identities)
            ]
        return []

    # endregion Colors

    # region Groups

    @cached_property
    def fuse_group(self) -> LayerSet | None:
        """Fuse elements parent group."""
        return psd.getLayerSet("Fuse")

    @cached_property
    def fuse_textbox_group(self) -> LayerSet | None:
        """Fuse textbox group."""
        return psd.getLayerSet(LAYERS.TEXTBOX, self.fuse_group)

    @cached_property
    def fuse_pinlines_group(self) -> LayerSet | None:
        """Fuse pinlines group."""
        return psd.getLayerSet(LAYERS.PINLINES, self.fuse_group)

    @cached_property
    def text_groups(self) -> list[LayerSet | None]:
        """Text and icons group for each side."""
        return [psd.getLayerSet(LAYERS.TEXT_AND_ICONS, side) for side in self.sides]

    @cached_property
    def card_groups(self) -> list[LayerSet | None]:
        """Left and Right side parent groups."""
        return [psd.getLayerSet(side) for side in self.sides]

    @cached_property
    def pinlines_groups_split(self) -> list[LayerSet | None]:
        """Pinlines group for each side."""
        return [psd.getLayerSet(LAYERS.PINLINES, group) for group in self.card_groups]

    @cached_property
    def twins_groups(self) -> list[LayerSet | None]:
        """Twins group for each side."""
        return [psd.getLayerSet(LAYERS.TWINS, group) for group in self.card_groups]

    @cached_property
    def textbox_groups(self) -> list[LayerSet | None]:
        """Textbox group for each side."""
        return [psd.getLayerSet(LAYERS.TEXTBOX, group) for group in self.card_groups]

    @cached_property
    def background_groups(self) -> list[LayerSet | None]:
        """Background group for each side."""
        return [psd.getLayerSet(LAYERS.BACKGROUND, group) for group in self.card_groups]

    # endregion Groups

    # region Reference layers

    @cached_property
    def name_references(self) -> list[ReferenceLayer | None]:
        """Name reference for each side."""
        return [ReferenceLayer(layer) for layer in self.text_layers_mana]

    @cached_property
    def type_references(self) -> list[ReferenceLayer | None]:
        """Typeline reference for each side."""
        return self.expansion_references

    @cached_property
    def expansion_reference(self) -> ArtLayer | None:
        if self.is_split:
            return self.expansion_references[-1 if self.has_unified_typeline else 0]
        return super().expansion_reference

    @cached_property
    def expansion_references(self) -> list[ReferenceLayer | None]:
        """Expansion symbol reference for each side."""
        return [
            get_reference_layer(LAYERS.EXPANSION_REFERENCE, group)
            for group in self.text_groups
        ]

    @cached_property
    def textbox_references(self) -> list[ReferenceLayer | None]:
        """Textbox positioning reference for each side."""
        return [
            psd.get_reference_layer(
                LAYERS.TEXTBOX_REFERENCE + " Fuse"
                if self.is_fuse
                else LAYERS.TEXTBOX_REFERENCE,
                psd.getLayerSet(LAYERS.TEXT_AND_ICONS, group),
            )
            for group in self.card_groups
        ]

    @cached_property
    def background_reference(self) -> list[ArtLayer | None]:
        """Background positioning reference for each side."""
        return [
            psd.getLayer("Reference", [group, LAYERS.BACKGROUND])
            for group in self.card_groups
        ]

    @cached_property
    def art_references(self) -> list[ReferenceLayer | None]:
        """Art layer positioning reference for each side."""
        return [
            get_reference_layer(LAYERS.ART_FRAME, group) for group in self.card_groups
        ]

    # endregion Reference layers

    # region Shape layers

    @cached_property
    def art_layers(self) -> list[ArtLayer | None]:
        """Art layer for each side."""
        return [psd.getLayer(LAYERS.DEFAULT, group) for group in self.card_groups]

    @cached_property
    def rules_text_dividers(self) -> list[ArtLayer | None]:
        """Divider layer for each side."""
        return [None] * len(self.sides)

    # endregion Shape layers

    # region Text layers

    @cached_property
    def text_layers_name(self) -> list[ArtLayer | None]:
        """Name text layer for each side."""
        return [psd.getLayer(LAYERS.NAME, [group]) for group in self.text_groups]

    @cached_property
    def text_layers_rules(self) -> list[ArtLayer | None]:
        """Rules text layer for each side."""
        return [psd.getLayer(LAYERS.RULES_TEXT, [group]) for group in self.text_groups]

    @cached_property
    def text_layers_type(self) -> list[ArtLayer | None]:
        """Typeline text layer for each side."""
        return [psd.getLayer(LAYERS.TYPE_LINE, [group]) for group in self.text_groups]

    @cached_property
    def text_layers_mana(self) -> list[ArtLayer | None]:
        """Mana cost text layer for each side."""
        return [psd.getLayer(LAYERS.MANA_COST, [group]) for group in self.text_groups]

    # endregion Text layers

    # region Expansion Symbol

    def load_expansion_symbol(self) -> None:
        super().load_expansion_symbol()
        if self.is_split:
            self.expansion_symbols

    @cached_property
    def expansion_symbols(self) -> list[ArtLayer | None]:
        """Expansion symbol layer for each side."""
        if not self.has_unified_typeline and self.expansion_symbol_layer:
            symbols: list[ArtLayer | None] = [self.expansion_symbol_layer]
            for layer_ref in self.expansion_references[1:]:
                if layer_ref:
                    symbol_duplicate = self.expansion_symbol_layer.duplicate(
                        layer_ref, ElementPlacement.PlaceAfter
                    )
                    psd.align_right(symbol_duplicate, layer_ref)
                    try:
                        copy_layer_fx(self.expansion_symbol_layer, symbol_duplicate)
                    except COMError:
                        pass
                    symbols.append(symbol_duplicate)
                else:
                    symbols.append(None)
            return symbols
        return [self.expansion_symbol_layer]

    # endregion Expansion Symbol

    # region Artwork

    def load_artwork(
        self,
        art_file: str | Path | None = None,
        art_layer: ArtLayer | None = None,
        art_reference: ReferenceLayer | None = None,
    ) -> None:
        if not self.is_fullart and self.is_split:
            return self.load_artworks([art_file] if art_file else None)
        else:
            return super().load_artwork(art_file, art_layer, art_reference)

    def load_artworks(
        self,
        art_files: list[str | Path] | None = None,
        art_layers: list[ArtLayer | None] | None = None,
        art_references: list[ReferenceLayer | None] | None = None,
    ) -> None:
        """Loads art for each side."""

        if isinstance(self.layout, SplitLayout):
            # Set default values
            art_files = art_files or [*self.layout.art_files]
            art_layers = art_layers or self.art_layers
            art_references = art_references or self.art_references

            # Second art not provided
            if len(art_files) == 1:
                # Manually select a second art
                self.console.update("Please select the second split art!")
                file: list[str] = self.app.openDialog()
                if not file:
                    self.console.update("No art selected, cancelling render.")
                    self.console.cancel_thread(thr=self.event)
                    return

                # Place new art in the correct order
                if normalize_str(self.layout.names[0]) == normalize_str(
                    self.layout.file["name"]
                ):
                    art_files.append(file[0])
                else:
                    art_files.insert(0, file[0])

            # Load art for each side
            for i, (art_file, layer, ref) in enumerate(
                zip(art_files, art_layers, art_references)
            ):
                if art_file and layer and ref:
                    super().load_artwork(
                        art_file=art_files[i],
                        art_layer=art_layers[i],
                        art_reference=ref,
                    )

    # endregion Artwork

    # region Watermarks

    @cached_property
    def watermarks_colors(self) -> list[list[SolidColor | list[int]]]:
        """A list of 'SolidColor' objects for each face."""
        if isinstance(self.layout, SplitLayout):
            colors: list[list[SolidColor | list[int]]] = []
            for i, pinline in enumerate(self.layout.pinline_identities):
                if pinline in self.watermark_color_map:
                    # Named pinline colors
                    colors.append(
                        [self.watermark_color_map.get(pinline, self.RGB_WHITE)]
                    )
                elif len(self.identity[i]) < self.color_limit:
                    # Dual color based on identity
                    colors.append(
                        [
                            self.watermark_color_map.get(c, self.RGB_WHITE)
                            for c in self.identity[i]
                        ]
                    )
                else:
                    colors.append([])
        raise NotImplementedError("Watermarks colors doesn't support this layout.")

    @cached_property
    def watermark_fxs(self) -> list[list[LayerEffects]]:
        """A list of LayerEffects' objects for each face."""
        fx: list[list[LayerEffects]] = []
        for color in self.watermarks_colors:
            if len(color) == 1:
                # Single color watermark
                fx.append([EffectColorOverlay(opacity=100, color=color[0])])
            elif len(color) == 2:
                # Dual color watermark
                fx.append(
                    [
                        EffectGradientOverlay(
                            rotation=0,
                            colors=[
                                GradientColor(color=color[0], location=0, midpoint=50),
                                GradientColor(
                                    color=color[1], location=4096, midpoint=50
                                ),
                            ],
                        )
                    ]
                )
            else:
                fx.append([])
        return fx

    def create_watermark(self) -> None:
        """Render a watermark for each side that has one."""

        if isinstance(self.layout, SplitLayout):
            # Add watermark to each side if needed
            for i, watermark in enumerate(self.layout.watermarks):
                # Required values to generate a Watermark
                if (
                    watermark
                    and (mark := self.layout.watermark_svgs[i])
                    and (textbox_ref := self.textbox_references[i])
                ):
                    # Get watermark custom settings if available
                    wm_details = CON.watermarks.get(watermark, {})

                    # Import and frame the watermark
                    wm = psd.import_svg(
                        path=mark,
                        ref=textbox_ref,
                        placement=ElementPlacement.PlaceAfter,
                        docref=self.docref,
                    )
                    psd.frame_layer(
                        layer=wm,
                        ref=textbox_ref,
                        smallest=True,
                        scale=wm_details.get("scale", 80),
                    )

                    # Apply opacity, blending, and effects
                    wm.opacity = wm_details.get("opacity", CFG.watermark_opacity)
                    wm.blendMode = BlendMode.ColorBurn
                    psd.apply_fx(wm, self.watermark_fxs[i])
        else:
            return super().create_watermark()

    # endregion Watermarks

    # region Frame layer methods

    def frame_layers_split(self) -> None:
        """Enable frame layers required by Split cards. None by default."""
        pass

    # endregion Frame layer methods

    # region Text layer methods

    def basic_text_layers(self) -> None:
        """Add basic text layers for each side."""
        if isinstance(self.layout, SplitLayout):
            for i in range(len(self.sides)):
                if (name := self.text_layers_name[i]) and (
                    mana := self.text_layers_mana[i]
                ):
                    self.text.extend(
                        [
                            FormattedTextField(
                                layer=mana,
                                contents=self.layout.mana_costs[i],
                            ),
                            ScaledTextField(
                                layer=name,
                                contents=self.layout.names[i],
                                reference=self.name_references[i],
                            ),
                        ]
                    )

                if (not self.has_unified_typeline or i == 0) and (
                    layer := self.text_layers_type[i]
                ):
                    self.text.append(
                        ScaledTextField(
                            layer=layer,
                            contents=self.layout.type_lines[i],
                            reference=self.type_references[
                                -1 if self.has_unified_typeline else i
                            ],
                        )
                    )
        else:
            return super().basic_text_layers()

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and P/T text for each side."""
        if isinstance(self.layout, SplitLayout):
            for i in range(len(self.sides)):
                if layer := self.text_layers_rules[i]:
                    self.text.append(
                        FormattedTextArea(
                            layer=layer,
                            contents=self.layout.oracle_texts[i],
                            flavor=self.layout.flavor_texts[i],
                            reference=self.textbox_references[i],
                            divider=self.rules_text_dividers[i],
                            centered=self.text_centerings[i],
                        )
                    )
        else:
            return super().rules_text_and_pt_layers()

    # endregion Text layer methods


class SplitTemplate(SplitMod):
    """
    * A template for split cards.

    In addition to SplitMod, adds for each side:
        * Frame layers
    """

    # region Reference layers

    @cached_property
    def twins_references(self) -> list[ArtLayer | None]:
        """Twins positioning reference for each side."""
        return [
            psd.getLayer("Reference", [group, LAYERS.TWINS])
            for group in self.card_groups
        ]

    # endregion Reference layers

    # region Shape layers

    @cached_property
    def background_layers(self) -> list[ArtLayer | None]:
        """Background layer for each side."""
        if isinstance(self.layout, SplitLayout):
            return [psd.getLayer(b, LAYERS.BACKGROUND) for b in self.layout.backgrounds]
        return [None] * len(self.sides)

    @cached_property
    def twins_layers(self) -> list[ArtLayer | None]:
        """Twins layer for each side."""
        if isinstance(self.layout, SplitLayout):
            return [psd.getLayer(t, LAYERS.TWINS) for t in self.layout.twins_identities]
        return [None] * len(self.sides)

    @cached_property
    def textbox_layers(self) -> list[ArtLayer | None]:
        """Textbox layer for each side."""
        if isinstance(self.layout, SplitLayout):
            return [
                psd.getLayer(t, LAYERS.TEXTBOX) for t in self.layout.pinline_identities
            ]
        return [None] * len(self.sides)

    # endregion Shape layers

    # region Blending masks

    @cached_property
    def mask_layers(self) -> list[ArtLayer]:
        """Blending masks supported by this template."""
        if self.is_split:
            if layer := psd.getLayer(LAYERS.HALF, LAYERS.MASKS):
                return [layer]
            return []
        return super().mask_layers

    # endregion Blending masks

    # region Frame layer methods

    def frame_layers_split(self) -> None:
        """Enable frame layers for each side. Add Fuse layers if required."""

        # Frame layers
        for i in range(len(self.sides)):
            if (group := self.twins_groups[i]) and (layer := self.twins_layers[i]):
                # Copy twins and position
                layer.visible = True
                twins = layer.parent.duplicate(group, ElementPlacement.PlaceBefore)
                layer.visible = False
                twins.visible = True

                if ref := self.twins_references[i]:
                    psd.align_horizontal(twins, ref)

            if layer := self.background_layers[i]:
                # Copy background and position
                background = layer.duplicate(
                    self.background_groups[i], ElementPlacement.PlaceInside
                )
                background.visible = True

                if ref := self.background_reference[i]:
                    psd.align_horizontal(background, ref)

            if layer := self.textbox_layers[i]:
                # Copy textbox and position
                textbox = layer.duplicate(
                    self.textbox_groups[i], ElementPlacement.PlaceInside
                )
                textbox.visible = True

                if ref := self.textbox_references[i]:
                    self.active_layer = textbox
                    psd.align_horizontal(textbox, ref.dims)
                    if self.is_fuse:
                        psd.select_bounds(ref.bounds, self.doc_selection)
                        self.doc_selection.invert()
                        self.doc_selection.clear()
                    self.doc_selection.deselect()

            if group := self.pinlines_groups_split[i]:
                # Apply pinlines
                self.generate_layer(group=group, colors=self.pinlines_colors_split[i])

        # Fuse addon
        if self.is_fuse:
            if layer := psd.getLayer(f"{LAYERS.BORDER} Fuse"):
                layer.visible = True
            if self.fuse_group:
                self.fuse_group.visible = True
            if self.fuse_pinlines_group:
                self.generate_layer(
                    group=self.fuse_pinlines_group, colors=self.fuse_pinline_colors
                )
            if self.fuse_textbox_group:
                self.generate_layer(
                    group=self.fuse_textbox_group,
                    colors=self.fuse_textbox_colors,
                    masks=self.mask_layers,
                )

    # endregion Frame layer methods
