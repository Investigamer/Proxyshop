"""
* NORMAL TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional, Union
from re import sub

# Third Party Imports
from photoshop.api import (
    AnchorPosition,
    SolidColor
)
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.mtg import pinline_color_map
from src.enums.photoshop import Dimensions
from src.enums.settings import (
    ExpansionSymbolMode,
    BorderlessColorMode,
    BorderlessTextbox, ModernClassicCrown
)
from src.frame_logic import contains_frame_colors
from src.helpers import get_line_count
from src.layouts import BasicLandLayout, TokenLayout
from src.templates._core import (
    StarterTemplate,
    NormalTemplate,
    NormalEssentialsTemplate
)
from src.templates._vector import VectorTemplate
from src.templates.transform import VectorTransformMod
from src.templates.mdfc import VectorMDFCMod
from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextField,
    FormattedTextArea,
    ScaledWidthTextField
)
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
        # Use darker PT boxes except for Vehicle
        if self.is_vehicle:
            if layer := psd.getLayer(LAYERS.VEHICLE, LAYERS.PT_BOX):
                return layer
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
        if self.is_creature:
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
    def background(self) -> str:
        # Reroute Vehicle -> Artifact
        if self.layout.background == LAYERS.VEHICLE:
            return LAYERS.ARTIFACT
        return self.layout.background

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
    DETAILS
    """

    @cached_property
    def template_suffix(self) -> str:
        if self.is_promo_star:
            return "Promo Classic"
        return "Classic"

    """
    TOGGLE
    """

    @cached_property
    def is_promo_star(self) -> str:
        return cfg.get_setting(
            section="FRAME",
            key="Promo.Star",
            default=False
        )

    @cached_property
    def is_extended(self) -> str:
        return cfg.get_setting(
            section="FRAME",
            key="Extended.Art",
            default=False
        )

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        # Force enable if Extended Art is toggled
        return True if self.is_extended else super().is_content_aware_enabled

    @property
    def is_type_shifted(self) -> bool:
        # Color indicator not supported
        return False

    @cached_property
    def is_fullart(self) -> bool:
        # Colorless cards use Fullart reference
        if self.is_colorless:
            return True
        return False

    """
    FRAME LAYERS
    """

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Only use split colors for lands and hybrid color, otherwise revert to background (gold)
        return psd.getLayer(
            self.background if len(self.pinlines) == 2 and not self.is_hybrid and not self.is_land else self.pinlines,
            LAYERS.LAND if self.is_land else LAYERS.NONLAND)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    """
    REFERENCES
    """

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(
            LAYERS.TEXTBOX_REFERENCE_LAND if self.is_land
            else LAYERS.TEXTBOX_REFERENCE,
            self.text_group
        )

    @cached_property
    def expansion_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(
            f"{LAYERS.EXPANSION_REFERENCE} {LAYERS.LAND}" if self.is_land
            else LAYERS.EXPANSION_REFERENCE,
            self.text_group
        )

    """
    MASKS
    """

    @cached_property
    def border_mask(self) -> ArtLayer:
        return psd.getLayer(LAYERS.EXTENDED, LAYERS.MASKS)

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
        number = self.layout.collector_data[:-2] if (
            '/' in self.layout.collector_data
        ) else self.layout.collector_data[2:]

        # Apply the collector info
        psd.replace_text(info, "NUM", number)
        psd.replace_text(info, "SET", self.layout.set)
        psd.replace_text(artist, "Artist", self.layout.artist)

    def rules_text_and_pt_layers(self):

        # Add rules text
        self.text.append(
            FormattedTextArea(
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
                TextField(
                    layer = self.text_layer_pt,
                    contents = f"{self.layout.power}/{self.layout.toughness}"
                )
            )

    def enable_frame_layers(self):
        # Resize expansion symbol
        self.expansion_symbol_layer.resize(90, 90, AnchorPosition.MiddleCenter)
        if self.is_land:
            self.expansion_symbol_layer.translate(0, 8)

        # Simple one image background
        self.pinlines_layer.visible = True

        # Add the promo star
        if self.is_promo_star:
            psd.getLayerSet("Promo Star", LAYERS.TEXT_AND_ICONS).visible = True

        # Make Extended Art modifications
        if self.is_extended:

            # Copy extended mask to Border
            psd.copy_layer_mask(self.border_mask, self.border_group)

            # Enable extended mask on Pinlines
            psd.enable_mask(self.pinlines_layer.parent)
            psd.enable_vector_mask(self.pinlines_layer.parent)

    def hook_large_mana(self) -> None:
        # Adjust mana cost position for large symbols
        self.text_layer_mana.translate(0, -5)


"""
* VECTOR TEMPLATES
* Normal templates that use vectorized layer structure.
"""


class EtchedTemplate (VectorTemplate):
    """
    Etched template first introduced in Commander Legends. Uses pinline colors for the background,
    except for Artifact cards. Uses pinline colors for the textbox always. No hollow crown, no companion or
    nyx layers.
    """
    template_suffix = "Etched"

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
    def pinlines_color_map(self) -> dict:
        # Update some colors
        return {
            **pinline_color_map.copy(),
            'W': [252, 254, 255],
            'Land': [136, 120, 98],
            'Artifact': [194, 210, 221],
            'Colorless': [194, 210, 221]
        }

    @cached_property
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Artifact color even for colored artifacts
        if self.is_artifact and not self.is_land:
            return psd.get_pinline_gradient(LAYERS.ARTIFACT, color_map=self.pinlines_color_map)
        return psd.get_pinline_gradient(self.pinlines, color_map=self.pinlines_color_map)

    @cached_property
    def crown_colors(self) -> Optional[str]:
        # Use Artifact color even for colored artifacts
        if self.is_artifact and not self.is_land:
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
    SHAPES
    """

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Enable Legendary pinlines shape if card is Legendary."""
        if self.is_legendary:
            return [psd.getLayer(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])]
        return []

    """
    MASKS
    """

    @cached_property
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Enable pinlines mask if card is Legendary."""
        return [psd.getLayer(LAYERS.NORMAL, [self.pinlines_group, LAYERS.SHAPE])] if self.is_legendary else []

    """
    METHODS
    """

    def enable_crown(self) -> None:
        """Enable the Legendary crown, only called if card is Legendary."""

        # Enable Legendary Crown group and layers
        psd.getLayer(f"{LAYERS.LEGENDARY} {LAYERS.SHADOWS}").visible = True


class ClassicRemasteredTemplate (VectorTransformMod, VectorTemplate):
    """
    Based on iDerp's Classic Remastered template, modified to work with Proxyshop, colored pinlines added for
    land generation. PT box added for creatures. Does not support Nyx or Companion layers.
    """
    template_suffix = "Classic Remastered"

    """
    DETAILS
    """

    @cached_property
    def color_limit(self) -> int:
        """Supports 2 and 3 color limit setting."""
        return int(cfg.get_setting("FRAME", "Max.Colors", "3", is_bool=False)) + 1

    @cached_property
    def gold_pt(self) -> bool:
        """Returns True if PT for multicolored cards should be gold."""
        return bool(cfg.get_setting("FRAME", "Gold.PT", False))

    @cached_property
    def background(self) -> str:
        """Disallow Vehicle backgrounds."""
        if self.layout.background == LAYERS.VEHICLE:
            return LAYERS.ARTIFACT
        return self.layout.background

    """
    TOGGLE
    """

    @property
    def is_name_shifted(self) -> bool:
        """No Transform icon support."""
        return False

    """
    COLORS
    """

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
    def twins_group(self) -> Optional[LayerSet]:
        return

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

    @cached_property
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

    """
    MASKS
    """

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
        """Pinlines are only provided for Land and Artifact cards."""
        if not self.pinlines_groups:
            return
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.pinlines_groups[0], LAYERS.SHAPE]
        )

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """No need for Twins or Border shape."""
        return [self.pinlines_shape, self.textbox_shape]

    """
    REFERENCES
    """

    @cached_property
    def pt_top_reference(self) -> Optional[ArtLayer]:
        """Support alternate reference for flipside PT."""
        return psd.getLayer(
            f"Flipside {LAYERS.PT_TOP_REFERENCE}" if (
                self.is_transform and self.is_front and self.is_flipside_creature
            ) else LAYERS.PT_TOP_REFERENCE, self.text_group
        )

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        """Use smaller Textbox Reference if Pinlines are added."""
        return psd.getLayer(
            f"{LAYERS.TEXTBOX_REFERENCE} {LAYERS.PINLINES}" if self.pinlines_colors else LAYERS.TEXTBOX_REFERENCE,
            self.text_group
        )

    """
    HOOKS
    """

    def hook_large_mana(self) -> None:

        # Adjust mana cost position for large symbols
        if not self.is_legendary:
            self.text_layer_mana.translate(0, -10)

    """
    METHODS
    """

    def enable_hollow_crown(self, **kwargs) -> None:

        # No hollow crown
        pass

    """
    TRANSFORM METHODS
    """

    def enable_transform_layers(self) -> None:

        # No transform layers
        pass

    def text_layers_transform_back(self) -> None:

        # No back side text changes
        pass


class UniversesBeyondTemplate (VectorTransformMod, VectorTemplate):
    """
    Template used for crossover sets like WH40K, Transformers, Street Fighter, etc.
    This template is built using the Silvan style of creating vector shapes and applying the colors
    and textures in the form of clipping masks. It's a little more involved, but it demonstrates
    an alternative way to build a highly complex template which can work for multiple card types.
    Credit to Kyle of Card Conjurer, WarpDandy, SilvanMTG, Chilli and MrTeferi.
    """
    template_suffix = "Universes Beyond"

    """
    COLORS
    """

    @cached_property
    def pinline_color_map(self) -> dict:
        return {
            **pinline_color_map.copy(),
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

    @cached_property
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        # Return SolidColor or Gradient dict notation for colored adjustment layers
        return psd.get_pinline_gradient(self.pinlines, color_map=self.crown_color_map)

    """
    GROUPS
    """

    @cached_property
    def background_group(self) -> Optional[LayerSet]:
        if self.is_colorless:
            return
        return super().background_group

    """
    LAYERS
    """

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Support Vehicle PT
        layer = psd.getLayer(LAYERS.VEHICLE if self.is_vehicle == LAYERS.VEHICLE else self.twins, LAYERS.PT_BOX)
        layer.parent.visible = True
        return layer

    """
    MASKS
    """

    @cached_property
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Masks enabled or copied."""
        return [
            # Pinlines mask, supports Transform Front
            [psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
                [self.mask_group, LAYERS.PINLINES]
            ), self.pinlines_group]
        ]

    """
    SHAPES
    """

    @cached_property
    def pinlines_shape(self) -> Optional[LayerSet]:
        # Support Normal and Transform Front
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

    def enable_crown(self) -> None:

        # Generate a solid color or gradient layer for the crown group
        self.crown_group.visible = True
        self.pinlines_action(self.crown_colors, layer=self.crown_group)

        # Enable Legendary pinline connector
        psd.getLayerSet(LAYERS.LEGENDARY, self.pinlines_shape.parent).visible = True

    """
    TRANSFORM METHODS
    """

    def enable_transform_layers_back(self) -> None:
        super().enable_transform_layers_back()

        # Enable brightness shift on back face layers
        psd.getLayerSet(LAYERS.BACK, self.pt_group).visible = True
        psd.getLayerSet(LAYERS.BACK, self.twins_group).visible = True
        psd.getLayer(LAYERS.BACK, self.textbox_group).visible = True


class LOTRTemplate (VectorTemplate):
    """
    * Lord of the Rings template introduced in Lord of The Rings: Tales of Middle Earth.
    * Credit to Tupinambá (Pedro Neves) for the master template
    * With additional support from CompC and MrTeferi
    """
    template_suffix = "Lord of the Rings"

    """
    COLOR MAPS
    """

    @cached_property
    def pinline_color_map(self) -> dict:
        return {
            **pinline_color_map.copy(),
            'W': [230, 220, 185],
            'U': [72, 142, 191],
            'B': [126, 128, 127],
            'R': [217, 94, 76],
            'G': [97, 143, 102],
            'Gold': [246, 213, 125],
            'Land': [181, 162, 149],
            'Artifact': [210, 219, 227],
            'Colorless': [210, 219, 227]
        }

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
            'Colorless': [78, 91, 101],
            'Vehicle': "4c3314"
        }

    """
    COLORS
    """

    @cached_property
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.pinline_color_map)

    @cached_property
    def twins_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(self.twins, color_map=self.dark_color_map)

    @cached_property
    def pt_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            LAYERS.VEHICLE if self.is_vehicle else self.twins,
            color_map=self.dark_color_map)

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
    MASKS
    """

    @cached_property
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        # Mask Pinlines if Legendary
        if self.is_legendary:
            return [self.pinlines_group]
        return []

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:

        # Enable layer masks
        self.enable_layer_masks()

        # Generate a solid color or gradient layer for PT Box
        if self.is_creature and self.pt_group:
            self.pt_group.visible = True
            psd.create_color_layer(self.pt_colors, layer=self.pt_group)

        # Color Indicator, create blended color adjustment layers
        if self.is_type_shifted and self.indicator_group:
            self.create_blended_solid_color(
                group=self.indicator_group,
                colors=self.indicator_colors,
                masks=self.indicator_masks)

        # Generate a solid color or gradient layer for each pinline group
        for group in [g for g in self.pinlines_groups if g]:
            group.visible = True
            self.pinlines_action(self.pinlines_colors, layer=group)

        # Generate a solid color or gradient layer for Twins
        if self.twins_group:
            psd.create_color_layer(self.twins_colors, layer=self.twins_group)

        # Textbox, supports color blending
        if self.textbox_group:
            self.create_blended_layer(
                group=self.textbox_group,
                colors=self.twins)

        # Background layer, supports color blending
        if self.background_group:
            self.create_blended_layer(
                group=self.background_group,
                colors=self.pinlines)

        # Legendary crown
        if self.is_legendary:
            self.crown_group.visible = True


class BorderlessVectorTemplate (VectorMDFCMod, VectorTransformMod, VectorTemplate):
    """Borderless template first used in the Womens Day Secret Lair, redone with vector shapes."""
    template_suffix = "Borderless"

    def __init__(self, layout, **kwargs):
        self.layout = layout

        if not cfg.exit_early:
            cfg.exit_early = self.is_nickname and not self.nickname

        if self.is_nickname_in_oracle:
            if 'Legendary' in layout.type_line and ',' in layout.name:
                original_short_name = sub(r"\,.*", "", layout.name).strip()
                layout.oracle_text = layout.oracle_text.replace(layout.name, original_short_name)
                
                nick_short_name = sub(r"\,.*", "", self.nickname).strip()
                layout.oracle_text = layout.oracle_text.replace(original_short_name, self.nickname, 1)
                layout.oracle_text = layout.oracle_text.replace(original_short_name, nick_short_name)
            else:
                layout.oracle_text = layout.oracle_text.replace(layout.name, self.nickname)

        super().__init__(layout, **kwargs)

    """
    SETTINGS
    """

    @cached_property
    def size(self) -> str:
        """Layer name associated with the size of the textbox."""
        # Check for textless
        if self.is_textless:
            return BorderlessTextbox.Textless

        # Get the user's preferred setting
        size = str(cfg.get_option(
            section="FRAME",
            key="Textbox.Size",
            enum_class=BorderlessTextbox,
            default=BorderlessTextbox.Automatic
        ))

        # Determine the automatic size
        if size == BorderlessTextbox.Automatic:
            # Set up our test text layer
            test_layer = psd.getLayer(self.text_layer_rules_name, [self.text_group, "Tall"])
            test_text = self.layout.oracle_text
            if self.layout.flavor_text:
                test_text += f'\r{self.layout.flavor_text}'
            test_layer.textItem.contents = test_text.replace('\n', '\r')

            # Get the number of lines in our test text and decide what size
            num = get_line_count(test_layer)
            if num < 5:
                return BorderlessTextbox.Short
            if num < 6:
                return BorderlessTextbox.Medium
            if num < 7:
                return BorderlessTextbox.Normal
            return BorderlessTextbox.Tall
        return size

    @cached_property
    def color_limit(self) -> int:
        # Built in setting, dual and triple color split
        return int(cfg.get_setting(
            section="COLORS",
            key="Max.Colors",
            default="2",
            is_bool=False)) + 1

    @cached_property
    def drop_shadow_enabled(self) -> bool:
        """Returns True if Drop Shadow text setting is enabled."""
        return bool(cfg.get_setting(
            section="TEXT",
            key="Drop.Shadow",
            default=True))

    @cached_property
    def crown_texture_enabled(self) -> bool:
        """Returns True if Legendary crown clipping texture should be enabled."""
        return bool(cfg.get_setting(
            section="FRAME",
            key="Crown.Texture",
            default=True))

    @cached_property
    def multicolor_textbox(self) -> bool:
        """Returns True if Textbox for multicolored cards should use blended colors."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Multicolor.Textbox",
            default=True))

    @cached_property
    def multicolor_pinlines(self) -> bool:
        """Returns True if Pinlines and Crown for multicolored cards should use blended colors."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Multicolor.Pinlines",
            default=True))

    @cached_property
    def multicolor_twins(self) -> bool:
        """Returns True if Twins for multicolored cards should use blended colors."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Multicolor.Twins",
            default=False))

    @cached_property
    def multicolor_pt(self) -> bool:
        """Returns True if PT Box for multicolored cards should use the last color."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Multicolor.PT",
            default=False))

    @cached_property
    def hybrid_colored(self) -> bool:
        """Returns True if Twins and PT should be colored on Hybrid cards."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Hybrid.Colored",
            default=True))

    @cached_property
    def front_face_colors(self) -> bool:
        """Returns True if lighter color map should be used on front face DFC cards."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Front.Face.Colors",
            default=True))

    @cached_property
    def land_colorshift(self) -> bool:
        """Returns True if Land cards should use the darker brown color."""
        return bool(cfg.get_setting(
            section="COLORS",
            key="Land.Colorshift",
            default=False))

    @cached_property
    def artifact_color_mode(self) -> str:
        """Setting determining what elements to color for colored artifacts.."""
        return cfg.get_option(
            section="COLORS",
            key="Artifact.Color.Mode",
            enum_class=BorderlessColorMode)

    """
    DETAILS
    """

    @cached_property
    def frame_type(self) -> str:
        """Layer name associated with the holistic frame type."""
        if self.is_textless:
            # Textless / Textless Transform
            return f"{self.size} {LAYERS.TRANSFORM}" if (
                self.is_transform or self.is_mdfc
            ) else self.size
        if self.is_transform and self.is_front:
            # Size TF Front
            return f"{self.size} {LAYERS.TRANSFORM_FRONT}"
        if self.is_transform or self.is_mdfc:
            # Size TF Back
            return f"{self.size} {LAYERS.TRANSFORM_BACK}"
        return self.size

    @cached_property
    def art_frame(self) -> str:
        # Use different positioning based on textbox size
        return f"{LAYERS.ART_FRAME} {self.size}"

    @cached_property
    def twins_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        """Function to call to generate twins colors. Can differ from pinlines_action."""
        return psd.create_color_layer if isinstance(self.twins_colors, SolidColor) else psd.create_gradient_layer

    @cached_property
    def textbox_action(self) -> Union[psd.create_color_layer, psd.create_gradient_layer]:
        """Function to call to generate textbox colors. Can differ from pinlines_action."""
        return psd.create_color_layer if isinstance(self.textbox_colors, SolidColor) else psd.create_gradient_layer

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
        return bool(isinstance(self.layout, TokenLayout))

    @cached_property
    def is_textless(self) -> bool:
        """Return True if this a textless render."""
        if isinstance(self.layout, BasicLandLayout):
            return True
        if not any([self.layout.oracle_text, self.layout.flavor_text]):
            return True
        return bool(cfg.get_setting(section="FRAME", key="Textless", default=False))

    @cached_property
    def is_nickname(self) -> bool:
        """Return True if this a nickname render."""
        return cfg.get_setting(section="TEXT", key="Nickname", default=False) or self.nickname is not None

    @cached_property
    def is_nickname_in_oracle(self) -> bool:
        """Return True if this a nickname render that should put its nickname into the oracle text."""
        return self.nickname is not None and cfg.get_setting(section="TEXT", key="Nickname.In.Oracle", default=True)

    @cached_property
    def nickname(self) -> str | None:
        """Return the nick name, if available."""
        return self.layout.file.get('additional_cfg', {}).get('nick', None)

    @cached_property
    def is_multicolor(self) -> bool:
        """Whether the card is multicolor and within the color limit range."""
        return bool(1 <= len(self.identity) < self.color_limit)

    @cached_property
    def is_centered(self) -> bool:
        """Conditions for rules text centering, avoid the flipside PT cutout."""
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
            and not (
                # Not centered if using a small textbox with Flipside PT
                self.is_flipside_creature and self.is_front and self.size in [
                    BorderlessTextbox.Automatic,
                    BorderlessTextbox.Medium,
                    BorderlessTextbox.Short
                ]
            )
        )

    @cached_property
    def is_pt_enabled(self) -> bool:
        """Return True if a separate Power/Toughness text layer is used for this render."""
        return self.is_creature and (not self.is_textless or cfg.symbol_mode == ExpansionSymbolMode.Disabled)

    @cached_property
    def is_drop_shadow(self) -> bool:
        """Return True if drop shadow setting is enabled."""
        return bool(
            self.drop_shadow_enabled and not
            ((self.is_mdfc or self.is_transform) and self.is_front and self.front_face_colors)
        )

    @cached_property
    def is_authentic_front(self) -> bool:
        """Return True if rendering a front face DFC card with authentic lighter colors."""
        return bool((self.is_mdfc or self.is_transform) and self.is_front and self.front_face_colors)

    """
    COLOR MAPS
    """

    @cached_property
    def dark_color_map(self) -> dict:
        return {
            'W': "958676",
            'U': "045482",
            'B': "282523",
            'R': "93362a",
            'G': "134f23",
            'Gold': "9a883f",
            'Land': "684e30" if self.land_colorshift else "a79c8e",
            'Hybrid': "a79c8e",
            'Artifact': "48555c",
            'Colorless': "74726b",
            'Vehicle': "4c3314"
        }

    @cached_property
    def light_color_map(self) -> dict:
        return {
            'W': "faf8f2",
            'U': "d2edfa",
            'B': "c9c2be",
            'R': "f8c7b0",
            'G': "dbfadc",
            'Gold': "f5e5a4",
            'Land': "f0ddce",
            'Hybrid': "f0ddce",
            'Artifact': "cde0e9",
            'Colorless': "e2d8d4",
            'Vehicle': "4c3314"
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
    def gradient_location_map(self) -> dict:
        return {
            2: [.40, .60],
            3: [.29, .40, .60, .71],
            4: [.20, .30, .45, .55, .70, .80],
            5: [.20, .25, .35, .45, .55, .65, .75, .80]
        }

    """
    COLORS
    """

    @cached_property
    def twins_colors(self) -> Union[SolidColor, list[dict]]:

        # Default to twins
        colors = self.twins

        # Color enabled hybrid OR color enabled multicolor
        if (self.is_hybrid and self.hybrid_colored) or (self.is_multicolor and self.multicolor_twins):
            colors = self.identity
        # Color disabled hybrid cards
        elif self.is_hybrid:
            colors = LAYERS.HYBRID

        # Use artifact background if artifact mode isn't colored
        if self.is_artifact and not self.is_land and self.artifact_color_mode not in [
            BorderlessColorMode.Twins_And_PT,
            BorderlessColorMode.Twins,
            BorderlessColorMode.All
        ]:
            colors = LAYERS.ARTIFACT

        # Return Solid Color or Gradient notation
        return psd.get_pinline_gradient(
            colors=colors,
            color_map=self.light_color_map if self.is_authentic_front else self.dark_color_map,
            location_map=self.gradient_location_map)

    @cached_property
    def pt_colors(self) -> Union[SolidColor, list[dict]]:

        # Default to twins, or Vehicle for non-colored vehicle artifacts
        colors = self.twins

        # Color enabled hybrid OR color enabled multicolor
        if (self.is_hybrid and self.hybrid_colored) or (self.is_multicolor and self.multicolor_pt):
            colors = self.identity[-1]
        # Use Hybrid color for color-disabled hybrid cards
        elif self.is_hybrid:
            colors = LAYERS.HYBRID

        # Use background color if artifact mode isn't colored
        if self.is_artifact and not self.is_land and self.artifact_color_mode not in [
            BorderlessColorMode.Twins_And_PT,
            BorderlessColorMode.All,
            BorderlessColorMode.PT
        ]:
            colors = LAYERS.ARTIFACT

        # Use Vehicle for non-colored artifacts
        if colors == LAYERS.ARTIFACT and self.is_vehicle:
            colors = LAYERS.VEHICLE

        # Return Solid Color or Gradient notation
        return psd.get_pinline_gradient(
            colors=colors,
            color_map=self.light_color_map if self.is_authentic_front else self.dark_color_map)

    @cached_property
    def textbox_colors(self) -> Union[SolidColor, list[dict]]:

        # Default to twins
        colors = self.twins

        # Hybrid OR color enabled multicolor
        if self.is_hybrid or (self.is_multicolor and self.multicolor_textbox):
            colors = self.identity

        # Use background color if artifact mod isn't colored
        if self.is_artifact and self.artifact_color_mode not in [
            BorderlessColorMode.Textbox,
            BorderlessColorMode.All
        ]:
            colors = LAYERS.ARTIFACT

        # Return Solid Color or Gradient notation
        return psd.get_pinline_gradient(
            colors=colors,
            color_map=self.light_color_map if self.is_authentic_front else self.dark_color_map,
            location_map=self.gradient_location_map)

    @cached_property
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Solid Color or Gradient adjustment layer for Crown colors
        return psd.get_pinline_gradient(
            # Use identity for hybrid OR color enabled multicolor
            self.identity if self.is_hybrid or (self.is_multicolor and self.multicolor_pinlines) else (
                # Use pinlines if not a color code
                self.pinlines if not contains_frame_colors(self.pinlines) else LAYERS.GOLD
            ),
            color_map=self.crown_color_map,
            location_map=self.gradient_location_map)

    @cached_property
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        # Use alternate gradient location map
        return psd.get_pinline_gradient(
            # Use identity for hybrid OR color enabled multicolor
            self.identity if self.is_hybrid or (self.is_multicolor and self.multicolor_pinlines) else (
                # Use pinlines if not a color code
                self.pinlines if not contains_frame_colors(self.pinlines) else LAYERS.GOLD
            ),
            color_map=self.pinline_color_map,
            location_map=self.gradient_location_map)

    """
    GROUPS
    """

    @cached_property
    def pt_group(self) -> Optional[LayerSet]:
        """PT Box group, alternative Textless option used when Expansion Symbol is disabled."""
        if self.is_textless and cfg.symbol_mode == ExpansionSymbolMode.Disabled:
            return psd.getLayerSet(f"{LAYERS.PT_BOX} {LAYERS.TEXTLESS}")
        return super().pt_group

    @cached_property
    def crown_group(self) -> LayerSet:
        """Legendary Crown group, use inner group to allow textured overlays above."""
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def nickname_group(self) -> LayerSet:
        """Nickname frame element group."""
        return psd.getLayerSet(LAYERS.NICKNAME)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules_name(self) -> str:
        """Compute the name of this layer separately, so we can use it for automatic textbox sizing."""
        if self.is_creature:
            # Is a creature, Flipside P/T?
            return LAYERS.RULES_TEXT_CREATURE_FLIP if (
                    self.is_transform and self.is_flipside_creature
            ) else LAYERS.RULES_TEXT_CREATURE

        # Not a creature, Flipside P/T?
        return LAYERS.RULES_TEXT_NONCREATURE_FLIP if (
                self.is_transform and self.is_flipside_creature
        ) else LAYERS.RULES_TEXT_NONCREATURE

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Card rules text layer, use pre-computed layer name."""
        return psd.getLayer(self.text_layer_rules_name, [self.text_group, self.size])

    @property
    def text_layer_name(self) -> Optional[ArtLayer]:
        """Card name text layer, allow support for Nickname."""
        if self.is_nickname:
            layer = psd.getLayer(LAYERS.NICKNAME, self.text_group)
            layer.visible = True
            return layer
        return super().text_layer_name

    @cached_property
    def text_layer_nickname(self) -> Optional[ArtLayer]:
        """Card nickname text layer, allow support for Nickname."""
        layer = super().text_layer_name
        layer.textItem.contents = "ENTER NAME HERE"
        if self.nickname:
            return layer
        return None

    """
    REFERENCES
    """

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        """Use size appropriate textbox reference."""
        return psd.getLayer(self.size, [self.text_group, LAYERS.TEXTBOX_REFERENCE])

    """
    VECTOR SHAPES
    """

    @cached_property
    def textbox_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        """Support a size appropriate textbox shape and Transform Front addition."""

        # Return None if textless
        if self.is_textless:
            return []

        # Enable Transform Front addition if required
        names = [self.size, LAYERS.TRANSFORM_FRONT] if self.is_transform and self.is_front else [self.size]
        return [psd.getLayer(n, [self.textbox_group, LAYERS.SHAPE]) for n in names]

    @cached_property
    def pinlines_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        """Support a variety of pinlines shapes including Transform, MDFC, Textless, Nickname, etc."""

        # Name and typeline
        layers = [
            psd.getLayerSet(
                LAYERS.TRANSFORM if self.is_transform else (LAYERS.MDFC if self.is_mdfc else LAYERS.NORMAL),
                [self.pinlines_group, LAYERS.SHAPE, LAYERS.NAME]),
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

        # Add Transform Front addition if required
        names = [self.size, LAYERS.TRANSFORM_FRONT] if self.is_transform and self.is_front else [self.size]
        return [*layers, *[psd.getLayer(n, [self.pinlines_group, LAYERS.SHAPE, LAYERS.TEXTBOX]) for n in names]]

    @cached_property
    def twins_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        """Separate shapes for Name and Typeline box."""
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
        """Vector shape for Nickname box."""
        return psd.getLayer(
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL,
            [self.nickname_group, LAYERS.SHAPE]
        )

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Add Nickname vector shape if needed."""
        shapes = [self.nickname_shape] if self.is_nickname else []
        return [
            *self.pinlines_shapes,
            *self.twins_shapes,
            *self.textbox_shapes,
            *shapes,
        ]

    """
    MASKS
    """

    @cached_property
    def border_mask(self) -> Optional[list]:
        """Support border mask for Textless and front face Transform modifications."""
        if self.is_textless:
            return [psd.getLayer(LAYERS.TEXTLESS, [self.mask_group, LAYERS.BORDER]), self.border_group]
        if self.is_transform and self.is_front:
            return [psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.mask_group, LAYERS.BORDER]), self.border_group]
        return

    @cached_property
    def pinlines_mask(self) -> dict:
        """Use pre-calculated frame type to find pinlines mask. This mask hides overlapping layer effects."""
        return {
            'mask': psd.getLayer(self.frame_type, [self.mask_group, LAYERS.PINLINES]),
            'layer': self.pinlines_group,
            'funcs': [psd.apply_mask_to_layer_fx]
        }

    @cached_property
    def pinlines_vector_mask(self) -> Optional[dict]:
        """Enable the pinlines vector mask if card is Legendary. """
        if not self.is_legendary:
            return
        return {
            'mask': self.pinlines_group,
            'vector': True
        }

    @cached_property
    def crown_mask(self) -> Optional[dict]:
        """Copy the pinlines mask to Legendary crown if card is Legendary."""
        if not self.is_legendary:
            return
        return {
            'mask': self.pinlines_mask['mask'],
            'layer': self.crown_group.parent,
            'funcs': [psd.apply_mask_to_layer_fx]
        }

    @cached_property
    def textbox_reference_mask(self) -> Optional[dict]:
        """Mask used to resize the textbox reference."""
        if not self.is_mdfc:
            return
        return {
            'mask': psd.getLayer(LAYERS.MDFC, [self.mask_group, LAYERS.TEXTBOX_REFERENCE]),
            'layer': self.textbox_reference,
            'funcs': [psd.apply_mask]
        }

    @cached_property
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Masks that should be copied or enabled."""
        return [
            self.crown_mask,
            self.border_mask,
            self.pinlines_mask,
            self.pinlines_vector_mask,
            self.textbox_reference_mask
        ]

    """
    EFFECTS
    """

    @cached_property
    def nickname_fx(self) -> ArtLayer:
        return psd.getLayer(LAYERS.NICKNAME, LAYERS.EFFECTS)

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:

        # Enable vector shapes
        self.enable_shape_layers()

        # Enable layer masks
        self.enable_layer_masks()

        # PT Box -> Solid color layer
        if self.is_pt_enabled:
            self.pt_group.visible = True
            psd.create_color_layer(
                color=self.pt_colors,
                layer=self.pt_group)

        # Color Indicator -> Blended solid colors layers
        if self.is_type_shifted and self.indicator_group:
            self.create_blended_solid_color(
                group=self.indicator_group,
                colors=self.indicator_colors,
                masks=self.indicator_masks)

        # Pinlines -> Solid color or gradient layer
        for group in [g for g in self.pinlines_groups if g]:
            group.visible = True
            self.pinlines_action(self.pinlines_colors, layer=group)

        # Twins -> Solid color or gradient layer
        if self.twins_group:
            self.twins_action(self.twins_colors, layer=self.twins_group)

        # Textbox -> Solid color or gradient layer
        if self.textbox_group and not self.is_textless:
            self.textbox_action(self.textbox_colors, layer=self.textbox_group)

        # Nickname -> Solid color or gradient layer
        if self.is_nickname:
            self.twins_action(self.twins_colors, layer=self.nickname_group)

        # Enable Token shadow
        if self.is_token:
            psd.getLayer(LAYERS.TOKEN, self.text_group).visible = True

        # Legendary crown
        if self.is_legendary:
            self.enable_crown()

    def basic_text_layers(self) -> None:

        # Establish whether this is a textless creature render with no symbol
        self.text.extend([
            FormattedTextField(
                layer = self.text_layer_mana,
                contents = self.layout.mana_cost
            ),
            ScaledTextField(
                layer = self.text_layer_type,
                # Add Power/Toughness if rendering textless creature WITH symbol
                contents = f"{self.layout.type_line} — {self.layout.power}/{self.layout.toughness}" if
                self.is_creature and not self.is_pt_enabled else self.layout.type_line,
                # Use PT box as right reference if rendering textless creature WITHOUT symbol
                reference = psd.getLayer(LAYERS.PT_BOX, [self.pt_group, LAYERS.SHAPE]) if
                self.is_textless and self.is_pt_enabled else self.expansion_symbol_layer
            )
        ])

        # Add nickname or regular name
        if not self.is_nickname:
            self.text.append(
                ScaledTextField(
                    layer = self.text_layer_name,
                    contents = self.layout.name,
                    reference = self.text_layer_mana
                ))
        else:
            self.text.append(
                    ScaledWidthTextField(
                    layer = self.text_layer_name,
                    contents = self.layout.name,
                    reference = self.nickname_shape
                ))

            # If nickname is not entered by user add that too
            if self.text_layer_nickname is not None:
                self.text.append(
                    ScaledTextField(
                        layer = self.text_layer_nickname,
                        contents = self.nickname,
                        reference = self.text_layer_mana
                    ))

    def rules_text_and_pt_layers(self) -> None:

        # Call super if not a Textless render
        if not self.is_textless:
            return super().rules_text_and_pt_layers()

        # Make positioning adjustments
        if self.is_type_shifted:
            self.indicator_group.translate(-10, 0)
        self.text_layer_type.translate(-10, 0)

        # Align and add PT text for creatures with no expansion symbol
        if self.is_pt_enabled:
            psd.align_all(self.text_layer_pt, self.pt_group)
            self.text.append(
                TextField(
                    layer = self.text_layer_pt,
                    contents = f"{self.layout.power}/{self.layout.toughness}"
                ))
            return

        # Otherwise just shift the symbol over
        self.expansion_symbol_layer.translate(10, 0)

    def enable_crown(self) -> None:

        # Enable Legendary Crown group and layers
        self.crown_group.visible = True
        self.pinlines_action(self.crown_colors, layer=self.crown_group)

        # Remove crown textures if disabled
        if not self.crown_texture_enabled:
            for n in ["Shading", "Highlight", "Overlay"]:
                psd.getLayer(n, self.crown_group.parent).visible = False

        # Change to nickname effects if needed
        if self.is_nickname:
            psd.copy_layer_fx(self.nickname_fx, self.crown_group.parent)

    def post_text_layers(self) -> None:

        # Align typeline, symbol, and indicator
        if self.size != BorderlessTextbox.Tall:

            # Get the delta between the highest box and the target box
            shape = psd.getLayer(LAYERS.TALL, [self.pinlines_group, LAYERS.SHAPE, LAYERS.TYPE_LINE])
            shape_center = psd.get_layer_dimensions(shape)[Dimensions.CenterY]
            delta = psd.get_layer_dimensions(self.pinlines_shapes[1])[Dimensions.CenterY] - shape_center
            self.text_layer_type.translate(0, delta)

            # Shift expansion symbol
            if cfg.symbol_mode != ExpansionSymbolMode.Disabled:
                self.expansion_symbol_layer.translate(0, delta)

            # Shift indicator
            if self.is_type_shifted:
                self.indicator_group.parent.translate(0, delta)

        # Token adjustments
        if self.is_token:
            self.text_layer_name.textItem.font = con.font_subtext
            psd.align_horizontal(self.text_layer_name, self.twins_shapes[0])

        # Nickname adjustments
        if self.is_nickname:
            psd.align_vertical(self.text_layer_name, self.nickname_shape)

        # Add drop shadow if enabled and allowed
        if self.is_drop_shadow:

            # Name and Typeline
            psd.enable_layer_fx(self.text_layer_name)
            psd.enable_layer_fx(self.text_layer_type)

            # Rules text if not textless
            if not self.is_textless:
                psd.enable_layer_fx(self.text_layer_rules)

            # Flipside PT for front face Transform
            if self.is_flipside_creature and self.is_front and self.is_transform:
                psd.enable_layer_fx(self.text_layer_flipside_pt)

        # Allow exception for PT drop shadow on front face Vehicle cards
        if (self.is_drop_shadow or (self.drop_shadow_enabled and self.is_vehicle)) and self.is_pt_enabled:
            psd.enable_layer_fx(self.text_layer_pt)

    """
    TRANSFORM METHODS
    """

    def text_layers_transform_front(self) -> None:
        super().text_layers_transform_front()

        # Use black text
        if self.is_authentic_front:
            self.swap_font_color()

        # Switch flipside PT to light gray
        if not self.is_authentic_front and self.is_flipside_creature:
            self.text_layer_flipside_pt.textItem.color = psd.get_rgb(*[186, 186, 186])

    def text_layers_transform_back(self):

        # No back side changes
        pass

    """
    MDFC METHODS
    """

    def text_layers_mdfc_front(self) -> None:

        # Switch to black text
        if self.is_authentic_front:
            self.swap_font_color()

    """
    UTILITY METHODS
    """

    def swap_font_color(self, color: SolidColor = None) -> None:
        """
        Switch the font color of each key text layer.
        @param color: SolidColor object, will use black if not provided.
        """

        # Ensure a color is chosen
        color = color or self.RGB_BLACK

        # Name and Typeline
        self.text_layer_name.textItem.color = color
        self.text_layer_type.textItem.color = color

        # Rules text if not textless
        if not self.is_textless:
            self.text_layer_rules.textItem.color = color

        # PT if card is creature
        if self.is_pt_enabled and not self.is_vehicle:
            self.text_layer_pt.textItem.color = color


class ClassicModernTemplate(VectorTransformMod, VectorMDFCMod, VectorTemplate):
    """A modern frame version of iDerp's 'Classic Remastered' template."""

    """
    BOOL
    """

    @property
    def is_vehicle(self) -> bool:
        return False

    @property
    def is_extended(self) -> bool:
        return True

    @property
    def is_content_aware_enabled(self) -> bool:
        return True

    """
    SETTINGS
    """

    @cached_property
    def crown_mode(self) -> str:
        """Whether to use pinlines when generating the Legendary Crown."""
        return cfg.get_option("FRAME", "Crown.Mode", ModernClassicCrown)

    """
    COLOR MAPS
    """

    @cached_property
    def pinline_color_map(self) -> dict:
        """Maps color values for the Pinlines."""
        return {
            **pinline_color_map.copy(),
            "Land": "#604a33"
        }

    """
    COLORS
    """

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
    def crown_colors(self) -> Union[str, SolidColor, list[dict]]:
        """Support multicolor based on color limit."""
        if self.crown_mode == ModernClassicCrown.TextureBackground:
            return self.background
        return self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines

    """
    SHAPES
    """

    @cached_property
    def crown_shape(self) -> Optional[ArtLayer]:
        # Support Normal and Extended
        return psd.getLayer(
            LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL,
            [LAYERS.LEGENDARY_CROWN, LAYERS.SHAPE])

    @cached_property
    def border_shape(self) -> Optional[ArtLayer]:
        # Support Normal and Legendary
        return psd.getLayer(
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL,
            LAYERS.BORDER)

    @cached_property
    def pinlines_shape(self) -> list[Union[ArtLayer, LayerSet]]:
        # Add transform cutout textbox
        masks = [
            psd.getLayer(
                LAYERS.TRANSFORM_FRONT,
                [self.pinlines_group, LAYERS.SHAPE, LAYERS.TEXTBOX]
            )
        ] if self.is_transform and self.is_front else []
        # Add Twins shape, supports Normal and Transform
        return [
            *masks,
            psd.getLayerSet(
                LAYERS.TRANSFORM if self.is_transform else (
                    LAYERS.MDFC if self.is_mdfc else LAYERS.NORMAL),
                [self.pinlines_group, LAYERS.SHAPE, LAYERS.NAME]),
        ]

    @cached_property
    def textbox_shape(self) -> list[Union[ArtLayer, LayerSet]]:
        return [
            psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.textbox_group, LAYERS.SHAPE])
        ] if self.is_transform and self.is_front else []

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        crown = [self.crown_shape] if self.is_legendary else []
        return [
            self.border_shape,
            self.twins_shape,
            *self.pinlines_shape,
            *self.textbox_shape,
            *crown]

    """
    MASKS
    """

    @cached_property
    def twins_mask(self) -> list[dict]:
        return [{
            'mask': self.twins_group,
            'vector': True
        }] if self.is_extended else []

    @cached_property
    def border_mask(self) -> list[Union[ArtLayer, LayerSet]]:
        return [
            psd.getLayer(
                LAYERS.MDFC if self.is_mdfc and not self.is_legendary else LAYERS.NORMAL,
                [self.mask_group, LAYERS.BORDER, LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL]
            ), self.border_group
        ]

    @cached_property
    def background_mask(self) -> list[Union[ArtLayer, LayerSet]]:
        return [
            psd.getLayer(
                LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL,
                [self.mask_group, LAYERS.BACKGROUND]
            ), self.background_group
        ]

    @cached_property
    def pinlines_mask(self) -> list[Union[list, dict]]:
        # Mask covering top on Legendary cards
        masks: list[Union[list, dict]] = [{
            'mask': self.pinlines_group,
            'vector': True
        }] if self.is_legendary else []
        # Fade mask and covering layer effects
        return [*masks, {
            'mask': psd.getLayer(
                LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
                [self.mask_group, LAYERS.PINLINES, LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL]),
            'layer': self.pinlines_group,
            'funcs': [psd.apply_mask_to_layer_fx]
        }]

    @cached_property
    def textbox_reference_mask(self) -> Optional[dict]:
        """Mask used to resize the textbox reference."""
        if not self.is_mdfc:
            return
        return {
            'mask': psd.getLayer(LAYERS.MDFC, [self.mask_group, LAYERS.TEXTBOX_REFERENCE]),
            'layer': self.textbox_reference,
            'funcs': [psd.apply_mask]
        }

    @cached_property
    def enabled_masks(self) -> list[Union[list, dict]]:
        return [
            self.border_mask,
            self.background_mask,
            *self.pinlines_mask,
            *self.twins_mask,
            self.textbox_reference_mask
        ]

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:
        if self.is_creature:
            self.pt_group.visible = True
        super().enable_frame_layers()

    def enable_crown(self) -> None:
        """Enable the Legendary crown, only called if card is Legendary."""

        # Generate Legendary Crown using pinline colors
        if self.crown_mode == ModernClassicCrown.Pinlines:
            self.pinlines_action(
                self.pinlines_colors,
                self.crown_group)
            return

        # Generate Legendary Crown using textures
        self.create_blended_layer(
            group=self.crown_group,
            colors=self.crown_colors,
            masks=self.crown_masks)

    """
    TRANSFORM METHODS
    """

    def enable_transform_layers_back(self) -> None:

        # Use darker Twins and PT texture
        if self.is_creature:
            psd.getLayer(LAYERS.LIGHTEN, self.pt_group).visible = False
        psd.getLayer(LAYERS.LIGHTEN, self.twins_group).visible = False
        super().enable_transform_layers_back()

    """
    MDFC METHODS
    """

    def enable_mdfc_layers_back(self) -> None:

        # Use darker Twins and PT texture and white font color
        if self.is_creature:
            psd.getLayer(LAYERS.LIGHTEN, self.pt_group).opacity = 10
            self.text_layer_pt.textItem.color = self.RGB_WHITE
            psd.enable_layer_fx(self.text_layer_pt)
        psd.getLayer(LAYERS.LIGHTEN, self.twins_group).opacity = 10
        self.text_layer_name.textItem.color = self.RGB_WHITE
        psd.enable_layer_fx(self.text_layer_name)
        super().enable_transform_layers_back()
