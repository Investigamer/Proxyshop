"""
* NORMAL TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    AnchorPosition,
    SolidColor,
    ElementPlacement
)
from photoshop.api._layerSet import ArtLayer, LayerSet

# Local Imports
from src.enums.photoshop import Dimensions
from src.enums.settings import ExpansionSymbolMode
from src.helpers import get_line_count
from src.layouts import BasicLandLayout
from src.templates._core import (
    StarterTemplate,
    NormalTemplate,
    NormalEssentialsTemplate,
    DynamicVectorTemplate,
    NormalVectorTemplate
)
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.constants import con
from src.settings import cfg
import src.helpers as psd


"""
* ADDON TEMPLATES
* These templates use normal.psd and are fundamentally the same as NormalTemplate
with certain features enabled.
"""


class FullartTemplate (NormalTemplate):
    """Fullart treatment for the Normal template. Adds translucent type bar and textbox."""
    template_suffix = "Fullart"

    """
    TOGGLE
    """

    @property
    def is_fullart(self) -> bool:
        return True

    """
    LAYERS
    """

    @cached_property
    def overlay_group(self) -> LayerSet:
        """Glass overlay that replaces textbox and twins."""
        return psd.getLayerSet("Overlay")

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:
        # Mask textbox and type bar, add glass overlay
        super().enable_frame_layers()
        psd.enable_vector_mask(self.pinlines_layer.parent)
        psd.enable_mask(self.twins_layer.parent)
        self.overlay_group.visible = True

    def basic_text_layers(self) -> None:
        # White typeline
        super().basic_text_layers()
        psd.enable_layer_fx(self.text_layer_type)
        self.text_layer_type.textItem.color = psd.rgb_white()

    def rules_text_and_pt_layers(self) -> None:
        # White rules text
        super().rules_text_and_pt_layers()
        psd.enable_layer_fx(self.text_layer_rules)
        self.text_layer_rules.textItem.color = psd.rgb_white()

        # White divider
        if self.layout.flavor_text and self.layout.oracle_text and cfg.flavor_divider:
            psd.enable_layer_fx(self.divider_layer)


class StargazingTemplate (FullartTemplate):
    """Stargazing template from 'Theros: Beyond Death' showcase cards. Always uses nyx backgrounds."""
    template_suffix = "Stargazing"

    """
    TOGGLE
    """

    @property
    def is_fullart(self) -> bool:
        return True

    @property
    def is_nyx(self) -> bool:
        return True

    """
    LAYERS
    """

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        # Use glass overlay for both twins
        return

    @property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Use darker PT boxes
        return psd.getLayer(self.twins, LAYERS.PT_BOX + ' Dark')

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:
        # Only extend this method to NormalTemplate, skip Fullart
        super(FullartTemplate, self).enable_frame_layers()

        # Glass cutouts
        psd.enable_vector_mask(self.background_layer.parent)
        psd.enable_vector_mask(self.pinlines_layer.parent)

        # Glass overlays
        self.overlay_group.visible = True
        psd.getLayer("Name", self.overlay_group).visible = True

    def enable_crown(self) -> None:
        super().enable_crown()
        psd.enable_vector_mask(self.crown_layer.parent)

    def basic_text_layers(self) -> None:
        super().basic_text_layers()
        psd.enable_layer_fx(self.text_layer_name)
        self.text_layer_name.textItem.color = psd.rgb_white()

    def rules_text_and_pt_layers(self) -> None:
        super().rules_text_and_pt_layers()
        self.text_layer_pt.textItem.color = psd.rgb_white()


"""
* CHILD TEMPLATES
* Structured nearly identically to NormalTemplate but uses a different PSD file.
"""


class ExtendedTemplate (NormalTemplate):
    """
    * An extended-art version of the normal template.
    * Empty edge outside the art reference is always content aware filled.
    """
    template_suffix = "Extended"

    @property
    def is_content_aware_enabled(self) -> bool:
        return True


class ExtendedDarkTemplate (ExtendedTemplate):
    """
    * A dark version of the Extended template.
    * Popularized by MaleMPC on MPCAutofill back in the day.
    """

    def rules_text_and_pt_layers(self) -> None:
        # White rules text
        super().rules_text_and_pt_layers()
        self.text_layer_rules.textItem.color = psd.rgb_white()

    def enable_frame_layers(self) -> None:
        # Enable the dark textbox overlay
        super().enable_frame_layers()
        psd.getLayer("Dark", "Overlays").visible = True

        # White divider
        if self.layout.flavor_text and self.layout.oracle_text and cfg.flavor_divider:
            psd.enable_layer_fx(self.divider_layer)


class BorderlessTemplate (ExtendedTemplate):
    """
    * The borderless showcase template first used on the Women's Day Secret Lair.
    * Doesn't have any background layers, needs a layer mask on the pinlines group when card is legendary.
    """
    template_suffix = "Borderless"

    """
    TOGGLE
    """

    @property
    def is_fullart(self) -> bool:
        return True

    """
    LAYERS
    """

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    """
    METHODS
    """

    def enable_crown(self) -> None:
        # Enable the Legendary crown, no hollow crown or border swap.
        psd.enable_mask(self.pinlines_layer.parent)
        self.crown_layer.visible = True


class InventionTemplate (NormalEssentialsTemplate):
    """Kaladesh Invention template. Uses either Bronze or Silver frame layers depending on setting."""
    template_suffix = "Masterpiece"

    """
    TOGGLE
    """

    @cached_property
    def is_fullart(self) -> bool:
        return True

    @property
    def is_land(self) -> bool:
        return False

    """
    DETAILS
    """

    @cached_property
    def twins(self) -> str:
        return str(cfg.get_setting(
            section="FRAME",
            key="Accent",
            default="Silver",
            is_bool=False
        ))

    @cached_property
    def background(self) -> str:
        return self.twins


class ExpeditionTemplate (NormalEssentialsTemplate):
    """
    Zendikar Rising Expedition template. Masks pinlines for legendary cards, has a single static background layer,
    doesn't support color indicator, companion, or nyx layers.
    """
    template_suffix = "Expedition"

    """
    TOGGLE
    """

    @property
    def is_land(self) -> bool:
        return False

    @property
    def is_fullart(self) -> bool:
        return True

    """
    LAYERS
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # No separate creature text layer
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_group)

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        # No colored background layer
        return

    """
    METHODS
    """

    def enable_crown(self):
        # No hollow crown
        self.crown_layer.visible = True
        psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
        psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True

        # Enable legendary cutout on background and pinlines
        psd.enable_mask(psd.getLayer('Background'))
        psd.enable_mask(self.pinlines_layer.parent)


class SnowTemplate (NormalEssentialsTemplate):
    """A snow template with textures from Kaldheim's snow cards."""
    template_suffix = "Snow"


class MiracleTemplate (NormalTemplate):
    """A template for miracle cards introduced in Avacyn Restored."""

    @property
    def is_legendary(self) -> bool:
        return False


"""
* ALTERNATE TEMPLATES
* Structured similar to NormalTemplate but extends to StarterTemplate.
"""


class ClassicTemplate (StarterTemplate):
    """A template for 7th Edition frame. Lacks some of the Normal Template features."""

    """
    TOGGLE
    """

    @property
    def is_type_shifted(self) -> bool:
        # Color indicator not supported
        return False

    @cached_property
    def promo_star(self) -> str:
        return cfg.get_setting(
            section="FRAME",
            key="Promo.Star",
            default=False
        )

    @cached_property
    def template_suffix(self) -> str:
        if self.promo_star:
            return "Promo Classic"
        return "Classic"

    @cached_property
    def is_fullart(self) -> bool:
        # Colorless cards use Fullart reference
        if self.is_colorless:
            return True
        return False

    """
    LAYERS and REFERENCES
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(
            LAYERS.TEXTBOX_REFERENCE_LAND if self.is_land
            else LAYERS.TEXTBOX_REFERENCE,
            self.text_group
        )

    """
    METHODS
    """

    def collector_info_authentic(self) -> None:
        """
        Called to generate realistic collector info.
        """
        # Hide basic layers
        psd.getLayer(LAYERS.ARTIST, self.legal_group).visible = False
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Get the collector layers
        collector_group = psd.getLayerSet(LAYERS.COLLECTOR, LAYERS.LEGAL)
        artist = psd.getLayer(LAYERS.TOP_LINE, collector_group)
        info = psd.getLayer(LAYERS.BOTTOM_LINE, collector_group)
        collector_group.visible = True

        # Correct color for non-black border
        if self.border_color != 'black':
            artist.textItem.color = psd.rgb_black()
            info.textItem.color = psd.rgb_black()

        # Establish the collector data
        if '/' in self.layout.collector_data:
            number = self.layout.collector_data[:-2]
        else:
            number = self.layout.collector_data[2:]

        # Apply the collector info
        psd.replace_text(info, "NUM", number)
        psd.replace_text(info, "SET", self.layout.set)
        psd.replace_text(artist, "Artist", self.layout.artist)

    def rules_text_and_pt_layers(self):

        # Add rules text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_rules,
                contents = self.layout.oracle_text,
                flavor = self.layout.flavor_text,
                centered = self.is_centered,
                reference = self.textbox_reference,
                divider = psd.getLayer(LAYERS.DIVIDER, self.text_group)
            )
        )

        # Add Power / Toughness
        if self.is_creature:
            self.text.append(
                text_classes.TextField(
                    layer = self.text_layer_pt,
                    contents = f"{self.layout.power}/{self.layout.toughness}"
                )
            )
        else:
            self.text_layer_pt.visible = False

    def enable_frame_layers(self):
        # Resize expansion symbol
        self.expansion_symbol_layer.resize(90, 90, AnchorPosition.MiddleCenter)
        if self.is_land:
            self.expansion_symbol_layer.translate(0, 8)

        # Simple one image background, Land or Nonland
        psd.getLayer(
            self.background,
            LAYERS.LAND if self.is_land else LAYERS.NONLAND
        ).visible = True

        # Add the promo star
        if self.promo_star:
            psd.getLayerSet("Promo Star", LAYERS.TEXT_AND_ICONS).visible = True

    def hook_large_mana(self) -> None:
        # Adjust mana cost position for large symbols
        self.text_layer_mana.translate(0, -5)


"""
* VECTOR TEMPLATES
* Normal templates that use vectorized layer structure.
"""


class EtchedTemplate (NormalVectorTemplate):
    """
    Etched template first introduced in Commander Legends. Uses pinline colors for the background,
    except for Artifact cards. Uses pinline colors for the textbox always. No hollow crown, no companion or
    nyx layers.
    """
    template_suffix = "Etched"

    def __init__(self, layout):
        super().__init__(layout)

        # Establish preferred pinline colors
        con.pinline_colors.update({
            'W': [252, 254, 255],
            'U': [0, 117, 190],
            'B': [39, 38, 36],
            'R': [239, 56, 39],
            'G': [0, 123, 67],
            'Gold': [246, 210, 98],
            'Land': [136, 120, 98],
            'Artifact': [194, 210, 221],
            'Colorless': [194, 210, 221]
        })

    """
    GROUPS
    """

    @cached_property
    def background_group(self) -> Optional[LayerSet]:
        # No background
        return

    """
    COLORS
    """

    @cached_property
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Artifact color even for colored artifacts
        if self.is_artifact:
            return psd.get_pinline_gradient(LAYERS.ARTIFACT)
        return psd.get_pinline_gradient(self.pinlines)

    @cached_property
    def crown_colors(self) -> Optional[str]:
        # Use Artifact color even for colored artifacts
        if self.is_artifact:
            return LAYERS.ARTIFACT
        return self.pinlines

    @cached_property
    def textbox_colors(self) -> Optional[str]:
        # Normal pinline coloring rules
        return self.pinlines

    """
    LAYERS
    """

    @cached_property
    def divider_layer(self) -> Optional[ArtLayer]:
        # Divider is grouped
        return psd.getLayerSet(LAYERS.DIVIDER, self.text_group)

    """
    METHODS
    """

    def enable_crown(self) -> None:
        # Enable pinlines mask
        super().enable_crown()
        psd.enable_mask(self.pinlines_group)


class ClassicRemasteredTemplate (DynamicVectorTemplate):
    """
    Based on iDerp's Classic Remastered template, modified to work with Proxyshop, colored pinlines added for
    land generation. PT box added for creatures. Does not support Nyx or Companion layers.
    """
    template_suffix = "Classic Remastered"

    """
    SETTINGS
    """

    @cached_property
    def color_limit(self) -> int:
        """Returns the number of frame colors allowed plus 1."""
        return int(cfg.get_setting("FRAME", "Max.Colors", "3", is_bool=False)) + 1

    @cached_property
    def gold_pt(self) -> bool:
        """Returns True if PT for multicolored cards should be gold."""
        return bool(cfg.get_setting("FRAME", "Gold.PT", False))

    """
    TOGGLE
    """

    @property
    def is_name_shifted(self) -> bool:
        # No transform icon support
        return False

    """
    COLORS
    """

    @cached_property
    def background(self) -> str:
        # Replace Vehicle with Artifact
        if self.layout.background == LAYERS.VEHICLE:
            return LAYERS.ARTIFACT
        return self.layout.background

    @cached_property
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        # Only apply pinlines for lands and artifacts
        if self.is_land or self.is_artifact:
            if not self.identity or len(self.identity) >= self.color_limit:
                return psd.get_pinline_gradient(self.pinlines)
            return psd.get_pinline_gradient(self.identity)
        return []

    @cached_property
    def textbox_colors(self) -> list[str]:
        # Only blend textbox colors for hybrid and land cards
        if self.is_land:
            # 2-3 color lands
            if 1 < len(self.identity) < self.color_limit and self.is_land:
                # Dual or tri colors
                return [f"{n} {LAYERS.LAND}" for n in self.identity]
            # Plain land background
            if self.pinlines == LAYERS.LAND:
                return [LAYERS.LAND]
            # All other land backgrounds
            return [f"{self.pinlines} {LAYERS.LAND}"]
        # Hybrid cards
        if self.is_hybrid:
            return list(self.pinlines)
        # Just one layer
        return [self.background]

    @cached_property
    def background_colors(self) -> Union[str, list[str]]:
        # Add support for 2 and 3 color identity on non-land, non-artifact cards
        if 1 < len(self.identity) < self.color_limit and not self.is_artifact and not self.is_land:
            return list(self.identity)
        return self.background

    @cached_property
    def crown_colors(self) -> Optional[str]:
        # Use the same as background colors
        return self.background_colors

    """
    GROUPS
    """

    @cached_property
    def pinlines_group(self) -> LayerSet:
        # Pinlines and textbox combined
        return psd.getLayerSet(LAYERS.PINLINES_TEXTBOX)

    @cached_property
    def pinlines_groups(self) -> list[LayerSet]:
        # Return empty if no pinlines colors provided
        if not self.pinlines_colors:
            return []

        # Two main pinlines groups
        groups: list[LayerSet] = [
            psd.getLayerSet("Pinlines Top", self.pinlines_group),
            psd.getLayerSet("Pinlines Bottom", self.pinlines_group)
        ]

        # Add the crown pinlines if needed
        if self.is_legendary:
            groups.append(psd.getLayerSet(LAYERS.PINLINES, LAYERS.LEGENDARY_CROWN))
        return groups

    @cached_property
    def textbox_group(self) -> LayerSet:
        # Must apply correct layer effects
        group = psd.getLayerSet(LAYERS.TEXTBOX, self.pinlines_group)
        psd.copy_layer_fx(
            psd.getLayer("EFFECTS LAND" if self.pinlines_colors else "EFFECTS", group),
            group
        )
        return group

    """
    LAYERS
    """

    @property
    def border_layer(self) -> Optional[ArtLayer]:
        # No need for separate border layers
        return

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        # No name and typeline plates
        return

    @cached_property
    def pt_layer(self) -> ArtLayer:
        # For hybrid cards, use the last color
        if not self.gold_pt and 0 < len(self.background_colors) < self.color_limit:
            name = self.background_colors[-1]
        else:
            name = self.twins
        layer = psd.getLayer(name, LAYERS.PT_BOX)
        layer.parent.visible = True
        return layer

    @cached_property
    def mask_layers(self) -> list[ArtLayer]:
        if 1 < len(self.identity) < self.color_limit:
            return [psd.getLayer(layer, self.mask_group) for layer in con.masks[len(self.identity)]]
        return []

    """
    SHAPES
    """

    @cached_property
    def pinlines_shape(self) -> Optional[LayerSet]:
        # Null if pinlines aren't provided
        if not self.pinlines_groups:
            return
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.pinlines_groups[0], LAYERS.SHAPE]
        )

    @cached_property
    def twins_shape(self) -> Optional[LayerSet]:
        return

    """
    REFERENCES
    """

    @cached_property
    def pt_top_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(
            f"Flipside {LAYERS.PT_TOP_REFERENCE}" if (
                    self.is_transform and self.is_flipside_creature
            ) else LAYERS.PT_TOP_REFERENCE, self.text_group
        )

    """
    METHODS
    """

    def enable_transform_layers(self):

        # No transform layers
        pass

    def transform_text_layers(self) -> None:

        # Add flipside Power/Toughness
        if self.is_front and self.is_flipside_creature:
            self.text.append(
                text_classes.TextField(
                    layer=psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_group),
                    contents=str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness)
                )
            )

    def hook_large_mana(self) -> None:

        # Adjust mana cost position for large symbols
        if not self.is_legendary:
            self.text_layer_mana.translate(0, -10)


class UniversesBeyondTemplate (DynamicVectorTemplate):
    """
    Template used for crossover sets like WH40K, Transformers, Street Fighter, etc.
    This template is built using the Silvan style of creating vector shapes and applying the colors
    and textures in the form of clipping masks. It's a little more involved, but it demonstrates
    an alternative way to build a highly complex template which can work for multiple card types.
    Credit to Kyle of Card Conjurer, WarpDandy, SilvanMTG, Chilli and MrTeferi.
    """
    template_suffix = "Universes Beyond"

    def __init__(self, layout):
        super().__init__(layout)

        # Establish preferred pinline colors
        con.pinline_colors.update({
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

    """
    COLORS
    """

    @cached_property
    def crown_color_map(self) -> dict:
        return {
            'W': [248, 244, 240],
            'U': [0, 109, 174],
            'B': [57, 52, 49],
            'R': [222, 60, 35],
            'G': [0, 109, 66],
            'Gold': [239, 209, 107],
            'Land': [165, 150, 132],
            'Artifact': [181, 197, 205],
            'Colorless': [214, 214, 220]
        }

    @cached_property
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for colors
        return psd.get_pinline_gradient(self.pinlines, color_map=self.crown_color_map)

    """
    LAYERS
    """

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Support Vehicle, regular layers, and back side darkened layers
        if self.background == LAYERS.VEHICLE:
            layer = psd.getLayer(self.background, LAYERS.PT_BOX)
        elif self.is_transform and not self.is_front:
            layer = psd.getLayer(f'{self.twins} Back', LAYERS.PT_BOX)
        else:
            layer = psd.getLayer(self.twins, LAYERS.PT_BOX)
        layer.parent.visible = True
        return layer

    """
    MASKS
    """

    @cached_property
    def pinlines_mask(self) -> Optional[ArtLayer]:
        # This layer contains the mask for the correct pinlines
        if self.is_transform and self.is_front:
            return psd.getLayer(LAYERS.NORMAL, [self.mask_group, LAYERS.PINLINES])
        return psd.getLayer(LAYERS.NORMAL, [self.mask_group, LAYERS.PINLINES])

    """
    SHAPES
    """

    @cached_property
    def pinlines_shape(self) -> Optional[LayerSet]:
        # Pinlines shape is in a layer group
        name = (
            LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK
        ) if self.is_transform else LAYERS.NORMAL
        return psd.getLayerSet(name, [self.pinlines_group, LAYERS.SHAPE])

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:
        super().enable_frame_layers()

        # Translucent colorless shapes
        if self.is_colorless and self.twins_shape and self.textbox_shape:
            psd.set_fill_opacity(60, self.twins_group)
            psd.set_fill_opacity(60, self.textbox_group)

        # Add mask to pinlines
        psd.copy_layer_mask(self.pinlines_mask, self.pinlines_group)

    def enable_crown(self) -> None:

        # Generate a solid color or gradient layer for the crown group
        self.crown_group.visible = True
        self.pinlines_action(self.pinlines_colors, self.crown_group)

        # Enable Legendary pinline connector
        psd.getLayerSet(LAYERS.LEGENDARY, self.pinlines_shape.parent).visible = True


class LOTRTemplate (NormalVectorTemplate):
    """
    * Lord of the Rings template introduced in Lord of The Rings: Tales of Middle Earth.
    * Credit to Tupinambá (Pedro Neves) for the master template
    * With additional support from CompC and MrTeferi
    """
    template_suffix = "Lord of the Rings"

    def __init__(self, layout):
        super().__init__(layout)

        # Establish preferred pinline colors
        con.pinline_colors.update({
            'W': [230, 220, 185],
            'U': [72, 142, 191],
            'B': [126, 128, 127],
            'R': [217, 94, 76],
            'G': [97, 143, 102],
            'Gold': [246, 213, 125],
            'Land': [181, 162, 149],
            'Artifact': [210, 219, 227],
            'Colorless': [210, 219, 227]
        })

    """
    COLORS
    """

    @cached_property
    def dark_color_map(self) -> dict:
        return {
            'W': [134, 123, 105],
            'U': [44, 51, 103],
            'B': [44, 43, 39],
            'R': [118, 34, 34],
            'G': [13, 68, 45],
            'Gold': [158, 124, 78],
            'Land': [103, 90, 74],
            'Artifact': [61, 88, 109],
            'Colorless': [78, 91, 101]
        }

    @cached_property
    def twins_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for colors
        return psd.get_pinline_gradient(self.twins, color_map=self.dark_color_map)

    @cached_property
    def pt_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for colors
        return psd.get_pinline_gradient(self.twins, color_map=self.dark_color_map)

    """
    GROUPS
    """

    @cached_property
    def pinlines_groups(self) -> list[LayerSet]:
        groups = [self.pinlines_group]
        if self.is_legendary:
            groups.append(self.crown_group)
        return groups

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:

        # Legendary crown
        if self.is_legendary:
            self.crown_group.visible = True
            psd.enable_mask(self.pinlines_group)

        # Generate a solid color or gradient layer for PT Box
        if self.is_creature and self.pt_group:
            self.pt_group.visible = True
            psd.create_color_layer(self.pt_colors, self.pt_group)

        # Color Indicator, doesn't natively support color blending
        if self.is_type_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

        # Generate a solid color or gradient layer for each pinline group
        for group in self.pinlines_groups:
            if group:
                group.visible = True
                self.pinlines_action(self.pinlines_colors, group)

        # Generate a solid color or gradient layer for Twins
        if self.twins_group:
            psd.create_color_layer(self.twins_colors, self.twins_group)

        # Textbox, supports color blending
        if self.textbox_group:
            self.create_blended_layer(group=self.textbox_group, colors=self.twins)

        # Background layer, supports color blending
        if self.background_group:
            self.create_blended_layer(group=self.background_group, colors=self.pinlines)


class BorderlessVectorTemplate (DynamicVectorTemplate):
    """Borderless template first used in the Womens Day Secret Lair, redone with vector shapes."""
    template_suffix = "Borderless"

    def __init__(self, layout):
        if not cfg.exit_early:
            cfg.exit_early = self.is_nickname
        super().__init__(layout)

    """
    DETAILS
    """

    @cached_property
    def size(self) -> str:
        """Layer name associated with the size of the textbox."""
        # Check for textless
        if self.is_textless:
            return "Textless"

        # Get the user's preferred setting
        size = str(cfg.get_setting(
            section="FRAME",
            key="Textbox.Size",
            default="Automatic",
            is_bool=False
        ))

        # Determine the automatic size
        if size == "Automatic":
            # Set up our test layer and test text
            test_layer = psd.getLayer(self.text_layer_rules_name, [self.text_group, "Tall"])
            test_text = self.layout.oracle_text
            if self.layout.flavor_text:
                test_text += f'\r{self.layout.flavor_text}'
            test_layer.textItem.contents = test_text.replace('\n', '\r')

            # Get the number of lines in our test text and decide what size
            num = get_line_count(test_layer)
            if num < 5:
                return "Short"
            if num < 6:
                return "Medium"
            if num < 7:
                return "Normal"
            return "Tall"
        return size

    @cached_property
    def type(self) -> str:
        """Layer name associated with the frame type."""
        if self.is_transform and self.is_front:
            return LAYERS.TRANSFORM_FRONT
        if self.is_transform or self.is_mdfc:
            return LAYERS.TRANSFORM_BACK
        return LAYERS.NORMAL

    @cached_property
    def mask(self) -> str:
        """Layer name associated with the overall frame mask."""
        if self.is_transform or self.is_mdfc:
            return f"{self.size} {self.type}"
        return self.size

    @cached_property
    def art_frame(self) -> str:
        # Use different positioning based on textbox size
        return f"{LAYERS.ART_FRAME} {self.size}"

    @cached_property
    def twins_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        """Function to call to generate twins colors. Hybrid cards allow dual color twins."""
        return psd.create_color_layer if isinstance(self.twins_colors, SolidColor) else psd.create_gradient_layer

    """
    TOGGLE
    """

    @property
    def is_fullart(self) -> bool:
        return True

    @property
    def is_content_aware_enabled(self) -> bool:
        return True

    @cached_property
    def is_token(self) -> bool:
        """Return True if this is a Token card."""
        return bool('Token' in self.layout.type_line_raw)

    @cached_property
    def is_textless(self) -> bool:
        """Return True if this a textless render."""
        if isinstance(self.layout, BasicLandLayout):
            return True
        if not any([self.layout.oracle_text, self.layout.flavor_text]):
            return True
        if cfg.get_setting(section="FRAME", key="Textless", default=False):
            return True
        return False

    @cached_property
    def is_nickname(self) -> bool:
        """Return True if this a nickname render."""
        return cfg.get_setting(section="FRAME", key="Nickname", default=False)

    """
    COLORS
    """

    @cached_property
    def dark_color_map(self) -> dict:
        return {
            'W': "958676",
            'U': "13699d",
            'B': "332f2c",
            'R': "a7493c",
            'G': "2f572c",
            'Gold': "8d7b48",
            'Land': "7c6a57",
            'Artifact': "5d6b73",
            'Colorless': "686767"
        }

    @cached_property
    def crown_color_map(self) -> dict:
        return {
            'W': "f8f4f0",
            'U': "006dae",
            'B': "393431",
            'R': "de3c23",
            'G': "006d42",
            'Gold': "efd16b",
            'Land': "a59684",
            'Artifact': "b5c5cd",
            'Colorless': "d6d6dc"
        }

    @cached_property
    def twins_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for Twins colors
        return psd.get_pinline_gradient(
            # Use right-half color on Twins for hybrid
            self.pinlines if self.is_hybrid else self.twins,
            color_map=self.dark_color_map
        )

    @cached_property
    def pt_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for PT colors
        return psd.get_pinline_gradient(
            # Use right-half color on PT for hybrid
            self.pinlines[1] if self.is_hybrid else self.twins,
            color_map=self.dark_color_map
        )

    @cached_property
    def textbox_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for Textbox colors
        return psd.get_pinline_gradient(self.pinlines, color_map=self.dark_color_map)

    @cached_property
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for Crown colors
        return psd.get_pinline_gradient(self.pinlines, color_map=self.crown_color_map)

    """
    GROUPS
    """

    @cached_property
    def pt_group(self) -> Optional[LayerSet]:
        if self.is_textless and cfg.symbol_mode == ExpansionSymbolMode.Disabled:
            return psd.getLayerSet(f"{LAYERS.PT_BOX} {LAYERS.TEXTLESS}")
        return super().pt_group

    @cached_property
    def crown_group(self) -> LayerSet:
        # Need to get the inner group so textured overlay can be applied above the colors
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def nickname_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.NICKNAME)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules_name(self) -> str:
        """Calculate the name of this layer separately, so we can use it for automatic textbox sizing."""
        if self.is_creature:
            # Is a creature, Flipside P/T?
            return LAYERS.RULES_TEXT_CREATURE_FLIP if (
                    self.is_transform and self.is_flipside_creature
            ) else LAYERS.RULES_TEXT_CREATURE

        # Not a creature, Flipside P/T?
        self.text_layer_pt.opacity = 0
        return LAYERS.RULES_TEXT_NONCREATURE_FLIP if (
                self.is_transform and self.is_flipside_creature
        ) else LAYERS.RULES_TEXT_NONCREATURE

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.text_layer_rules_name, [self.text_group, self.size])

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Add support for nickname
        if self.is_nickname:
            layer = psd.getLayer(LAYERS.NICKNAME, self.text_group)
            super().text_layer_name.textItem.contents = "ENTER NAME HERE"
            layer.visible = True
            return layer
        return super().text_layer_name

    """
    REFERENCES
    """

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.size, [self.text_group, LAYERS.TEXTBOX_REFERENCE])

    """
    VECTOR SHAPES
    """

    @cached_property
    def textbox_shape(self) -> Optional[LayerSet]:
        # Return None if textless
        if self.is_textless:
            return
        # Enable TF Front addition if required
        if self.is_transform and self.is_front:
            psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.textbox_group, LAYERS.SHAPE]).visible = True
        return psd.getLayer(self.size, [self.textbox_group, LAYERS.SHAPE])

    @cached_property
    def pinlines_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        # Choose the name pinline
        if self.is_transform:
            name = LAYERS.TRANSFORM
        elif self.is_mdfc:
            name = LAYERS.MDFC
        else:
            name = LAYERS.NORMAL
        layers = [
            psd.getLayerSet(name, [self.pinlines_group, LAYERS.SHAPE, LAYERS.NAME]),
            psd.getLayer(
                LAYERS.TEXTLESS if self.is_textless else self.size,
                [self.pinlines_group, LAYERS.SHAPE, LAYERS.TYPE_LINE]),
        ]
        # Add nickname if needed
        if self.is_nickname:
            layers.append(psd.getLayerSet(
                LAYERS.NICKNAME, [self.crown_group if self.is_legendary else self.pinlines_group, LAYERS.SHAPE])
            )
        # If textless return just the name and title
        if self.is_textless:
            return layers
        # Add TF Front addition if required
        if self.is_transform and self.is_front:
            layers.append(psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.pinlines_group, LAYERS.SHAPE, LAYERS.TEXTBOX]))
        # Add the textbox
        return [*layers, psd.getLayer(self.size, [self.pinlines_group, LAYERS.SHAPE, LAYERS.TEXTBOX])]

    @cached_property
    def twins_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        # Card Name and Typeline box
        return [
            psd.getLayer(
                LAYERS.TRANSFORM if self.is_transform or self.is_mdfc else LAYERS.NORMAL,
                [self.twins_group, LAYERS.SHAPE, LAYERS.NAME]),
            psd.getLayer(
                LAYERS.TEXTLESS if self.is_textless else self.size,
                [self.twins_group, LAYERS.SHAPE, LAYERS.TYPE_LINE])
        ]

    @cached_property
    def nickname_shape(self) -> ArtLayer:
        # Nickname box
        return psd.getLayer(
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL,
            [self.nickname_group, LAYERS.SHAPE]
        )

    """
    MASKS
    """

    @cached_property
    def border_mask(self) -> Optional[ArtLayer]:
        # Check for textless
        if self.is_textless:
            return psd.getLayer(LAYERS.TEXTLESS, [self.mask_group, LAYERS.BORDER])
        if self.is_transform and self.is_front:
            return psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.mask_group, LAYERS.BORDER])
        return

    @cached_property
    def pinlines_mask(self) -> Optional[ArtLayer]:
        # Check for textless
        if self.is_textless:
            addendum = f" {LAYERS.TRANSFORM}" if self.is_transform or self.is_mdfc else ""
            return psd.getLayer(LAYERS.TEXTLESS + addendum, [self.mask_group, LAYERS.PINLINES])
        return psd.getLayer(self.mask, [self.mask_group, LAYERS.PINLINES])

    """
    ADJUSTMENTS
    """

    @cached_property
    def back_adjustment_layer(self) -> ArtLayer:
        """Adjustment layer that darkens layers for the back side of double faced cards."""
        return psd.getLayer(LAYERS.BACK, LAYERS.EFFECTS)

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:

        # Generate a solid color or gradient layer for PT Box
        if self.is_creature and self.pt_group and not (
            self.is_textless and cfg.symbol_mode != ExpansionSymbolMode.Disabled
        ):
            self.pt_group.visible = True
            psd.create_color_layer(self.pt_colors, self.pt_group)

        # Color Indicator, simple rasterized layer
        # TODO: Create vector-based color indicator
        if self.is_type_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

        # Generate a solid color or gradient layer for each pinline group
        for group in [g for g in self.pinlines_groups if g]:
            group.visible = True
            self.pinlines_action(self.pinlines_colors, group)

        # Generate a solid color or gradient layer for Twins
        if self.twins_group:
            self.twins_action(self.twins_colors, self.twins_group)

        # Generate a solid color or gradient layer for Textbox
        if self.textbox_group:
            self.pinlines_action(self.textbox_colors, self.textbox_group)

        # Legendary crown
        if self.is_legendary:
            self.enable_crown()

        # Border mask
        if self.border_mask:
            psd.copy_layer_mask(self.border_mask, self.border_group)

        # Twins Shape
        for shape in self.twins_shapes:
            shape.visible = True

        # Pinlines Shape
        for shape in self.pinlines_shapes:
            shape.visible = True
        psd.copy_layer_mask(self.pinlines_mask, self.pinlines_group)
        psd.apply_mask_to_layer_fx(self.pinlines_group)

        # Textbox Shape
        if self.textbox_shape:
            self.textbox_shape.visible = True

        # Add Transform related layers
        if self.is_transform:
            self.enable_transform_layers()

        # Add MDFC related layers
        if self.is_mdfc:
            self.enable_mdfc_layers()

        # Add Token shadow
        if self.is_token:
            psd.getLayer('Token', self.text_group).visible = True

        # Add nickname backdrop
        if self.is_nickname:
            self.nickname_shape.visible = True
            self.twins_action(self.twins_colors, self.nickname_group)

    def basic_text_layers(self) -> None:
        """Add essential text layers: Mana cost, Card name, Typeline."""
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_mana,
                contents = self.layout.mana_cost
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_type,
                contents = f"{self.layout.type_line} — {self.layout.power}/{self.layout.toughness}" if all([
                    self.is_textless, self.is_creature, cfg.symbol_mode != ExpansionSymbolMode.Disabled
                ]) else self.layout.type_line,
                reference = psd.getLayer(LAYERS.PT_BOX, [self.pt_group, LAYERS.SHAPE]) if all([
                    self.is_textless, self.is_creature, cfg.symbol_mode == ExpansionSymbolMode.Disabled
                ]) else self.expansion_symbol_layer
            )
        ])

        # Add nickname or regular name
        if not self.is_nickname:
            self.text.append(
                text_classes.ScaledTextField(
                    layer = self.text_layer_name,
                    contents = self.layout.name,
                    reference = self.text_layer_mana
                ))
        else:
            self.text.append(
                text_classes.ScaledWidthTextField(
                    layer = self.text_layer_name,
                    contents = self.layout.name,
                    reference = self.nickname_shape
                )
            )

    def rules_text_and_pt_layers(self) -> None:

        # Only add PT layer if textless
        if self.is_textless:
            # Make positioning adjustments
            if self.color_indicator_layer:
                self.color_indicator_layer.translate(-10, 0)
            self.text_layer_type.translate(-10, 0)

            if self.is_creature and cfg.symbol_mode == ExpansionSymbolMode.Disabled:
                # Align PT text
                psd.align_all(self.text_layer_pt, self.pt_group)

                # Add PT text
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_pt,
                        contents=f"{self.layout.power}/{self.layout.toughness}"
                    )
                )
            else:
                # Adjust expansion symbol over
                self.text_layer_pt.visible = False
                self.expansion_symbol_layer.translate(10, 0)
            return
        super().rules_text_and_pt_layers()

    def post_text_layers(self) -> None:

        # Align the typeline, expansion symbol, and color indicator on the type bar
        psd.disable_layer_fx(self.text_layer_type)
        psd.align_vertical(self.text_layer_type, self.pinlines_shapes[1])
        psd.enable_layer_fx(self.text_layer_type)
        if cfg.symbol_mode != ExpansionSymbolMode.Disabled:
            psd.align_vertical(self.expansion_symbol_layer, self.pinlines_shapes[1])
        if self.color_indicator_layer:
            psd.align_vertical(self.color_indicator_layer, self.pinlines_shapes[1])

        # Token adjustments
        if self.is_token:
            psd.align(Dimensions.CenterX, self.text_layer_name, self.twins_shapes[0])
            psd.set_font(self.text_layer_name, con.font_subtext)

        # Nickname adjustments
        if self.is_nickname:
            psd.disable_layer_fx(self.text_layer_name)
            psd.align(Dimensions.CenterY, self.text_layer_name, self.nickname_shape)
            psd.enable_layer_fx(self.text_layer_name)

    def enable_crown(self) -> None:

        # Enable Legendary Crown group and layers
        self.crown_group.visible = True
        self.pinlines_action(self.crown_colors, self.crown_group)
        psd.enable_vector_mask(self.pinlines_group)
        psd.copy_layer_mask(self.pinlines_mask, self.crown_group.parent)

        # Change to nickname effects if needed
        if self.is_nickname:
            psd.copy_layer_fx(psd.getLayer(LAYERS.NICKNAME, LAYERS.EFFECTS), self.crown_group.parent)

    def enable_transform_layers(self):

        # Enable transform icon and circle backing
        psd.getLayerSet(LAYERS.TRANSFORM, self.text_group).visible = True
        self.transform_icon_layer.visible = True

        # Enable backside brightness shift
        if not self.is_front:

            # Add effect for textbox
            textbox_adj = self.back_adjustment_layer.duplicate(self.textbox_group, ElementPlacement.PlaceInside)
            textbox_adj.grouped = True

            # Add effect for twins
            twins_adj = self.back_adjustment_layer.duplicate(self.twins_group, ElementPlacement.PlaceInside)
            twins_adj.grouped = True

            # Add effect for PT Box
            if self.is_creature:
                pt_adj = self.back_adjustment_layer.duplicate(self.pt_group, ElementPlacement.PlaceInside)
                pt_adj.grouped = True

    def enable_mdfc_layers(self):

        # Resize the textbox reference
        psd.select_layer_bounds(psd.getLayer(LAYERS.MDFC, self.textbox_reference.parent))
        self.textbox_reference.visible = True
        self.active_layer = self.textbox_reference
        self.docref.selection.clear()
        self.docref.selection.deselect()
        self.textbox_reference.visible = False

        # Enable MDFC group
        self.dfc_group.visible = True
        super().enable_mdfc_layers()
