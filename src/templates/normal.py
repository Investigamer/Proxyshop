"""
* NORMAL TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional, Union

# Third Party Imports
from photoshop.api import AnchorPosition
from photoshop.api._layerSet import ArtLayer, LayerSet

# Local Imports
from src.templates._core import (
    StarterTemplate,
    NormalTemplate,
    NormalEssentialsTemplate,
    DynamicVectorTemplate, NormalVectorTemplate
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
    def pinlines_colors(self) -> Optional[list[Union[int, dict]]]:
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
    def pinlines_colors(self) -> Optional[list[Union[int, dict]]]:
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
    def crown_colors(self) -> Optional[list[Union[int, dict]]]:
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

        # Add mask to pinlines
        psd.copy_layer_mask(self.pinlines_mask, self.pinlines_group)

    def enable_crown(self) -> None:

        # Generate a solid color or gradient layer for the crown group
        self.crown_group.visible = True
        self.pinlines_action(self.pinlines_colors, self.crown_group)

        # Enable Legendary pinline connector
        print(type(self.pinlines_shape.parent))
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
    def twins_colors(self) -> Optional[list[Union[int, dict]]]:
        # Use Solid Color or Gradient adjustment layer for colors
        return psd.get_pinline_gradient(self.twins, color_map=self.dark_color_map)

    @cached_property
    def pt_colors(self) -> Optional[list[Union[int, dict]]]:
        # Use Solid Color or Gradient adjustment layer for colors
        return psd.get_pinline_gradient(self.twins, color_map=self.dark_color_map)

    """
    GROUPS
    """

    @cached_property
    def pt_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.PT_BOX)

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
