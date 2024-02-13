"""
* Normal Templates
"""
# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import AnchorPosition, SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import CFG, CON
from src.utils.adobe import ReferenceLayer
from src.utils.properties import auto_prop_cached
from src.enums.mtg import pinlines_color_map, MagicIcons
from src.enums.adobe import Dimensions
from src.enums.settings import (
    BorderlessColorMode,
    BorderlessTextbox,
    ModernClassicCrown,
    CollectorMode)
from src.frame_logic import is_multicolor_string
from src.helpers import get_line_count, LayerEffects
from src.templates._core import NormalTemplate
from src.templates._cosmetic import ExtendedMod, FullartMod, NyxMod, VectorBorderlessMod, CompanionMod
from src.templates._vector import VectorTemplate
from src.templates.transform import VectorTransformMod
from src.templates.mdfc import VectorMDFCMod
from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextField,
    FormattedTextArea,
    ScaledWidthTextField)
from src.enums.layers import LAYERS
import src.helpers as psd

"""
* Extendable Templates
"""


class M15Template(NyxMod, CompanionMod, NormalTemplate):
    """Standard M15 Template

    Adds:
        * Support for Nyx background and hollow crown layers.
        * Support for Companion hollow crown layers.

    Todo:
        * Support for snow layers?
    """


"""
* ADDON TEMPLATES
* These templates use `normal.psd` and are fundamentally the same as NormalTemplate
with certain features enabled or disabled.
"""


class FullartTemplate(FullartMod, M15Template):
    """Fullart treatment for the Normal template. Adds translucent type bar and textbox."""

    """
    * Layers
    """

    @auto_prop_cached
    def overlay_group(self) -> LayerSet:
        """Glass overlay that replaces textbox and twins."""
        return psd.getLayerSet("Overlay")

    """
    * Methods
    """

    def enable_frame_layers(self) -> None:
        """Mask textbox and type bar, add glass overlay."""
        super().enable_frame_layers()
        psd.enable_vector_mask(self.pinlines_layer.parent)
        psd.enable_mask(self.twins_layer.parent)
        self.overlay_group.visible = True

    def basic_text_layers(self) -> None:
        """White typeline."""
        super().basic_text_layers()
        psd.enable_layer_fx(self.text_layer_type)
        self.text_layer_type.textItem.color = psd.rgb_white()

    def rules_text_and_pt_layers(self) -> None:
        """White rules text and divider."""
        super().rules_text_and_pt_layers()
        psd.enable_layer_fx(self.text_layer_rules)
        self.text_layer_rules.textItem.color = psd.rgb_white()

        # Make the divider white
        if self.layout.flavor_text and self.layout.oracle_text and CFG.flavor_divider:
            psd.enable_layer_fx(self.divider_layer)


class StargazingTemplate(FullartTemplate):
    """Stargazing template from 'Theros: Beyond Death' showcase cards. Always uses nyx backgrounds."""
    template_suffix = 'Stargazing'

    # Static Properties
    is_nyx = True
    twins_layer = None

    """
    * Layers
    """

    @property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Use darker PT boxes except for Vehicle
        if self.is_vehicle:
            if layer := psd.getLayer(LAYERS.VEHICLE, LAYERS.PT_BOX):
                return layer
        return psd.getLayer(self.twins, LAYERS.PT_BOX + ' Dark')

    """
    * Methods
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


class ExtendedTemplate(ExtendedMod, M15Template):
    """
    * An extended-art version of the normal template.
    * Empty edge outside the art reference is always content aware filled.
    """

    @auto_prop_cached
    def template_suffix(self) -> str:
        return 'Dark Mode' if self.is_dark_mode else ''

    """
    * Bool
    """

    @auto_prop_cached
    def is_dark_mode(self) -> bool:
        """Governs whether Dark Mode is enabled."""
        return bool(CFG.get_setting('FRAME', 'Dark.Mode', default=False))

    """
    * Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Small rules text changes for dark mode."""
        super().rules_text_and_pt_layers()

        # White rules text for dark mode
        if self.is_dark_mode:
            self.text_layer_rules.textItem.color = psd.rgb_white()

    def enable_frame_layers(self) -> None:
        """Small layer changes for dark mode."""
        super().enable_frame_layers()

        # Dark mode changes
        if self.is_dark_mode:
            psd.getLayer("Dark", "Overlays").visible = True

            # White divider
            if self.layout.flavor_text and self.layout.oracle_text and CFG.flavor_divider:
                psd.enable_layer_fx(self.divider_layer)


class InventionTemplate(FullartMod, NormalTemplate):
    """Kaladesh Invention template. Uses either Bronze or Silver frame layers depending on setting."""
    template_suffix = 'Masterpiece'

    # Static Properties
    is_land = False

    """
    * Frame Details
    """

    @auto_prop_cached
    def twins(self) -> str:
        """str: Pull twins color from settings. Silver or Bronze."""
        return str(CFG.get_setting(
            section="FRAME",
            key="Accent",
            default="Silver",
            is_bool=False
        ))

    @auto_prop_cached
    def background(self) -> str:
        """str: Reuse twins color pulled from settings."""
        return self.twins


class ExpeditionTemplate(FullartMod, NormalTemplate):
    """Zendikar Rising Expedition template. Masks pinlines for legendary cards, has a single static background layer,
    doesn't support color indicator, companion, or nyx layers.
    """
    template_suffix = 'Expedition'

    # Static Properties
    is_land = False
    background_layer = None

    """
    * Layers
    """

    @auto_prop_cached
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """No separate creature text layer."""
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and power/toughness text."""

        # No Creature-specific rules text
        self.text.append(
            FormattedTextArea(
                layer=self.text_layer_rules,
                contents=self.layout.oracle_text,
                flavor=self.layout.flavor_text,
                reference=self.textbox_reference,
                divider=self.divider_layer,
                centered=self.is_centered))

        # Add PT for Creature
        if self.is_creature:
            self.text.append(
                TextField(
                    layer=self.text_layer_pt,
                    contents=f'{self.layout.power}/'
                             f'{self.layout.toughness}'))

    """
    * Frame Layer Methods
    """

    def enable_crown(self):
        # No hollow crown
        self.crown_layer.visible = True
        psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
        psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True

        # Enable legendary cutout on background and pinlines
        psd.enable_mask(psd.getLayer('Background'))
        psd.enable_mask(self.pinlines_layer.parent)


class SnowTemplate(NormalTemplate):
    """A snow template with textures from Kaldheim's snow cards."""
    template_suffix = 'Snow'


class MiracleTemplate(NyxMod, NormalTemplate):
    """A template for miracle cards introduced in Avacyn Restored."""

    # Static Properties
    is_legendary = False
    is_vehicle = False


class ClassicTemplate(NormalTemplate):
    """A template for 7th Edition frame. Lacks some of the Normal Template features."""
    frame_suffix = 'Classic'

    """
    * Frame Details
    """

    @auto_prop_cached
    def template_suffix(self) -> str:
        """Add Promo if promo star enabled."""
        return 'Promo' if self.is_promo_star else ''

    """
    * Settings
    """

    @auto_prop_cached
    def is_promo_star(self) -> bool:
        """bool: Whether to enable the Promo Star overlay."""
        return CFG.get_setting(
            section='FRAME',
            key='Promo.Star',
            default=False)

    @auto_prop_cached
    def is_extended(self) -> bool:
        """bool: Whether to render using Extended Art framing."""
        return CFG.get_setting(
            section='FRAME',
            key='Extended.Art',
            default=False)

    @auto_prop_cached
    def is_align_collector_left(self) -> bool:
        """CollectorAlign: Which collector alignment to use."""
        return CFG.get_setting(
            section='TEXT',
            key='Collector.Align.Left',
            default=False)

    """
    * Bool Properties
    """

    @auto_prop_cached
    def is_content_aware_enabled(self) -> bool:
        """Force enabled if Extended Art is toggled."""
        return True if self.is_extended else super().is_content_aware_enabled

    """
    * Frame Layers
    """

    @auto_prop_cached
    def pinlines_layer(self) -> ArtLayer:
        """Only use split colors for land and hybrid cards, otherwise gold."""
        return psd.getLayer(
            self.background if len(self.pinlines) == 2 and not self.is_hybrid and not self.is_land else self.pinlines,
            LAYERS.LAND if self.is_land else LAYERS.NONLAND)

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_rules(self) -> ArtLayer:
        """ArtLayer: Does not change depending on Creature/Noncreature."""
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @auto_prop_cached
    def text_layer_type(self) -> ArtLayer:
        """ArtLayer: Card typeline text layer, used shifted version when color indicator is present."""
        if self.is_type_shifted:
            return psd.getLayer(LAYERS.TYPE_LINE_SHIFT, self.text_group)
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    """
    * References
    """

    @auto_prop_cached
    def collector_reference(self) -> ReferenceLayer:
        """ReferenceLayer: Reference used to position the collector info."""
        return psd.get_reference_layer(LAYERS.COLLECTOR_REFERENCE, self.legal_group)

    @auto_prop_cached
    def textbox_reference(self) -> ArtLayer:
        """ArtLayer: Separately positioned box for 'Land' cards."""
        return psd.get_reference_layer(
            LAYERS.TEXTBOX_REFERENCE_LAND if self.is_land
            else LAYERS.TEXTBOX_REFERENCE,
            self.text_group)

    @auto_prop_cached
    def expansion_reference(self) -> ArtLayer:
        """ArtLayer: Separately positioned box for 'Land' cards."""
        return psd.getLayer(
            f"{LAYERS.EXPANSION_REFERENCE} {LAYERS.LAND}" if self.is_land
            else LAYERS.EXPANSION_REFERENCE,
            self.text_group)

    """
    * Masks
    """

    @auto_prop_cached
    def border_mask(self) -> ArtLayer:
        """ArtLayer: Contains a mask used to change the border to an Extended Art border."""
        return psd.getLayer(LAYERS.EXTENDED, LAYERS.MASKS)

    """
    * Layout Data Methods
    """

    def process_layout_data(self) -> None:
        """Remove rarity letter from collector data."""
        super().process_layout_data()
        self.layout.collector_data = self.layout.collector_data[:-2] if (
                '/' in self.layout.collector_data
        ) else self.layout.collector_data[2:]

    """
    * Collector Info Methods
    """

    def collector_info(self) -> None:
        """Format and add the collector info at the bottom."""

        # Which collector info mode?
        if CFG.collector_mode in [
            CollectorMode.Default, CollectorMode.Modern
        ] and self.layout.collector_data:
            layers = self.collector_info_authentic()
        elif CFG.collector_mode == CollectorMode.ArtistOnly:
            layers = self.collector_info_artist_only()
        else:
            layers = self.collector_info_basic()

        # Shift collector text
        if self.is_align_collector_left:
            [psd.align_left(n, ref=self.collector_reference.dims) for n in layers]

    def collector_info_basic(self) -> list[ArtLayer]:
        """Called to generate basic collector info."""

        # Get artist and info layers
        artist = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        info = psd.getLayer(LAYERS.SET, self.legal_group)

        # Fill optional promo star
        if self.is_collector_promo:
            psd.replace_text(info, "•", MagicIcons.COLLECTOR_STAR)

        # Apply the collector info
        if self.layout.lang != 'en':
            psd.replace_text(info, 'EN', self.layout.lang.upper())
        psd.replace_text(artist, "Artist", self.layout.artist)
        psd.replace_text(info, 'SET', self.layout.set)
        return [artist, info]

    def collector_info_authentic(self) -> list[ArtLayer]:
        """Classic presents authentic collector info differently."""

        # Hide basic 'Set' layer
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Get artist and info layers, reveal info layer
        artist = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        info = psd.getLayer(LAYERS.COLLECTOR, self.legal_group)
        info.visible = True

        # Fill optional promo star
        if self.is_collector_promo:
            psd.replace_text(info, "•", MagicIcons.COLLECTOR_STAR)

        # Apply the collector info
        psd.replace_text(artist, 'Artist', self.layout.artist)
        psd.replace_text(info, 'SET', self.layout.set)
        psd.replace_text(info, 'NUM', self.layout.collector_data)
        return [artist, info]

    def collector_info_artist_only(self) -> list[ArtLayer]:
        """Called to generate 'Artist Only' collector info."""

        # Collector layers
        artist = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Apply the collector info
        psd.replace_text(artist, "Artist", self.layout.artist)
        return [artist]

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self):
        """Enable layers which create the frame of the card. Simplified, does not support Legendary Crown."""

        # Resize expansion symbol
        if self.expansion_symbol_layer:
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

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self):
        """Does not require a separate text area definition for Creature cards."""

        # Add rules text
        self.text.append(
            FormattedTextArea(
                layer=self.text_layer_rules,
                contents=self.layout.oracle_text,
                flavor=self.layout.flavor_text,
                centered=self.is_centered,
                reference=self.textbox_reference,
                divider=self.divider_layer))

        # Add Power / Toughness
        if self.is_creature:
            self.text.append(
                TextField(
                    layer=self.text_layer_pt,
                    contents=f'{self.layout.power}/'
                             f'{self.layout.toughness}'))

    """
    * Hook Methods
    """

    def hook_large_mana(self) -> None:
        """Adjust mana cost position for large symbols."""
        self.text_layer_mana.translate(0, -5)


"""
* VECTOR TEMPLATES
* Normal templates that use vectorized layer structure.
"""


class EtchedTemplate(VectorTemplate):
    """
    Etched template first introduced in Commander Legends. Uses pinline colors for the background,
    except for Artifact cards. Uses pinline colors for the textbox always. No hollow crown, no companion or
    nyx layers.
    """
    template_suffix = 'Etched'

    # Static properties
    background_group = None

    # Color Maps
    pinlines_color_map = {
        **pinlines_color_map.copy(),
        'W': [252, 254, 255],
        'Land': [136, 120, 98],
        'Artifact': [194, 210, 221],
        'Colorless': [194, 210, 221]}

    """
    * Colors
    """

    @auto_prop_cached
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        # Use Artifact color even for colored artifacts
        if self.is_artifact and not self.is_land:
            return psd.get_pinline_gradient(LAYERS.ARTIFACT, color_map=self.pinlines_color_map)
        return psd.get_pinline_gradient(self.pinlines, color_map=self.pinlines_color_map)

    @auto_prop_cached
    def crown_colors(self) -> Optional[str]:
        # Use Artifact color even for colored artifacts
        if self.is_artifact and not self.is_land:
            return LAYERS.ARTIFACT
        return self.pinlines

    @auto_prop_cached
    def textbox_colors(self) -> Optional[str]:
        # Normal pinline coloring rules
        return self.pinlines

    """
    * Layers
    """

    @auto_prop_cached
    def divider_layer(self) -> Optional[ArtLayer]:
        # Divider is grouped
        return psd.getLayerSet(LAYERS.DIVIDER, self.text_group)

    """
    * Shapes
    """

    @auto_prop_cached
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """Enable Legendary pinlines shape if card is Legendary."""
        if self.is_legendary:
            return [psd.getLayer(LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE])]
        return []

    """
    * Masks
    """

    @auto_prop_cached
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Enable pinlines mask if card is Legendary."""
        return [psd.getLayer(LAYERS.NORMAL, [self.pinlines_group, LAYERS.SHAPE])] if self.is_legendary else []

    """
    * Methods
    """

    def enable_crown(self) -> None:
        """Enable Legendary Crown shape."""
        psd.getLayer(f"{LAYERS.LEGENDARY} {LAYERS.SHADOWS}").visible = True


class ClassicRemasteredTemplate(VectorTransformMod, VectorTemplate):
    """
    Based on iDerp's Classic Remastered template, modified to work with Proxyshop, colored pinlines added for
    land generation. PT box added for creatures. Does not support Nyx or Companion layers.
    """
    frame_suffix = 'Classic'
    template_suffix = 'Remastered'

    # Static properties
    is_vehicle = False
    is_name_shifted = False
    twins_group = None

    """
    * Frame Details
    """

    @auto_prop_cached
    def color_limit(self) -> int:
        """Supports 2 and 3 color limit setting."""
        return int(CFG.get_setting("FRAME", "Max.Colors", "3", is_bool=False)) + 1

    @auto_prop_cached
    def gold_pt(self) -> bool:
        """Returns True if PT for multicolored cards should be gold."""
        return bool(CFG.get_setting("FRAME", "Gold.PT", False))

    """
    * Bool
    """

    @auto_prop_cached
    def has_pinlines(self):
        """bool: Allow pinlines for Land and Artifact cards."""
        return bool(self.is_land or self.is_artifact)

    """
    * Colors
    """

    @auto_prop_cached
    def pinlines_colors(self) -> Union[list[int], list[dict]]:
        """Union[list[int], list[dict]]: Allow pinlines on Land and Artifact cards."""
        if self.has_pinlines:
            if len(self.identity) >= self.color_limit:
                if len(self.identity) == 2:
                    # Color limit 1
                    return psd.get_pinline_gradient(LAYERS.GOLD)
                # Color limit exceeded
                return psd.get_pinline_gradient(self.pinlines)
            # Color limit in range
            return psd.get_pinline_gradient(self.identity)
        return []

    @auto_prop_cached
    def pt_colors(self) -> str:
        """str: Single layer name, use last color for hybrid cards."""
        if not self.gold_pt and 0 < len(self.background_colors) < self.color_limit:
            return self.background_colors[-1]
        return self.twins

    @auto_prop_cached
    def textbox_colors(self) -> list[str]:
        """list[str]: Only blend textbox colors for hybrid and land cards."""
        if self.is_land:
            # Within color limit
            if 1 < len(self.identity) < self.color_limit:
                return [f'{n} {LAYERS.LAND}' for n in self.identity]
            # 1 Color limit
            if len(self.identity) == 2:
                return [f'{LAYERS.GOLD} {LAYERS.LAND}']
            # Plain land background
            if self.pinlines == LAYERS.LAND:
                return [LAYERS.LAND]
            # All other land backgrounds
            return [f"{self.pinlines} {LAYERS.LAND}"]
        # Hybrid cards
        if self.is_hybrid:
            # Within color limit
            if 1 < len(self.identity) < self.color_limit:
                return list(self.identity)
            # 1 Color limit
            if len(self.identity) == 2:
                return [LAYERS.GOLD]
            return [self.pinlines]
        # Just one layer
        return [self.background]

    @auto_prop_cached
    def background_colors(self) -> list[str]:
        """list[str]: Supports blended colors on non-Land, non-Artifact cards."""
        if 1 < len(self.identity) < self.color_limit and not self.has_pinlines:
            return list(self.identity)
        if len(self.identity) == 2 and not self.has_pinlines:
            return [LAYERS.GOLD]
        return [self.background]

    @auto_prop_cached
    def crown_colors(self) -> list[str]:
        """list[str]: Use the same colors as background."""
        return self.background_colors

    """
    * Groups
    """

    @auto_prop_cached
    def pinlines_group(self) -> LayerSet:
        """LayerSet: Pinlines and textbox combined."""
        return psd.getLayerSet(LAYERS.PINLINES_TEXTBOX)

    @auto_prop_cached
    def pinlines_groups(self) -> list[LayerSet]:
        """list[LayerSet]: Return empty if no pinlines colors provided."""
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

    @auto_prop_cached
    def textbox_group(self) -> LayerSet:
        """LayerSet: Must apply correct layer effects."""
        group = psd.getLayerSet(LAYERS.TEXTBOX, self.pinlines_group)
        psd.copy_layer_fx(
            psd.getLayer("EFFECTS LAND" if self.pinlines_colors else "EFFECTS", group),
            group)
        return group

    """
    * Masks
    """

    @auto_prop_cached
    def mask_layers(self) -> list[ArtLayer]:
        """list[ArtLayer]: A list of layers containing masks based on how many color splits."""
        if 1 < len(self.identity) < self.color_limit:
            return [psd.getLayer(n, self.mask_group) for n in CON.masks[len(self.identity)]]
        return []

    """
    * Shapes
    """

    @auto_prop_cached
    def pinlines_shape(self) -> Optional[LayerSet]:
        """Pinlines are only provided for Land and Artifact cards."""
        if not self.pinlines_groups:
            return
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT if self.is_transform and self.is_front else LAYERS.NORMAL,
            [self.pinlines_groups[0], LAYERS.SHAPE]
        )

    @auto_prop_cached
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        """No need for Twins or Border shape."""
        return [self.pinlines_shape, self.textbox_shape]

    """
    * References
    """

    @auto_prop_cached
    def pt_reference(self) -> Optional[ArtLayer]:
        """Support alternate reference for flipside PT."""
        return psd.getLayer(
            f'{LAYERS.PT_REFERENCE} Flip' if (
                    self.is_transform and self.is_front and self.is_flipside_creature
            ) else LAYERS.PT_REFERENCE, self.text_group)

    @auto_prop_cached
    def textbox_reference(self) -> Optional[ArtLayer]:
        """Use smaller Textbox Reference if Pinlines are added."""
        return psd.get_reference_layer(
            f"{LAYERS.TEXTBOX_REFERENCE} {LAYERS.PINLINES}"
            if self.pinlines_colors else LAYERS.TEXTBOX_REFERENCE,
            self.text_group)

    """
    * Hooks
    """

    def hook_large_mana(self) -> None:
        """Adjust mana cost position for large symbols."""
        if not self.is_legendary:
            self.text_layer_mana.translate(0, -10)

    """
    * Methods
    """

    def enable_hollow_crown(self, **kwargs) -> None:
        """No hollow crown."""
        pass

    """
    * Transform Methods
    """

    def enable_transform_layers(self) -> None:
        """No Transform layers."""
        pass

    def text_layers_transform_back(self) -> None:
        """No back-side text changes."""
        pass


class UniversesBeyondTemplate(VectorTransformMod, VectorTemplate):
    """
    Template used for crossover sets like WH40K, Transformers, Street Fighter, etc.
    This template is built using the Silvan style of creating vector shapes and applying the colors
    and textures in the form of clipping masks. It's a little more involved, but it demonstrates
    an alternative way to build a highly complex template which can work for multiple card types.
    Credit to Kyle of Card Conjurer, WarpDandy, SilvanMTG, Chilli and MrTeferi.
    """
    template_suffix = 'Universes Beyond'

    # Color Maps
    pinlines_color_map = {
        **pinlines_color_map.copy(),
        'W': [246, 247, 241],
        'U': [0, 131, 193],
        'B': [44, 40, 33],
        'R': [237, 66, 31],
        'G': [5, 129, 64],
        'Gold': [239, 209, 107],
        'Land': [165, 150, 132],
        'Artifact': [227, 228, 230],
        'Colorless': [227, 228, 230]}

    """
    * Colors
    """

    @auto_prop_cached
    def pt_colors(self) -> str:
        """str: Layer texture name, supports Vehicle PT but doesn't need white text."""
        return LAYERS.VEHICLE if self.is_vehicle == LAYERS.VEHICLE else self.twins

    @auto_prop_cached
    def crown_colors(self) -> Union[list[int], list[dict]]:
        """list[int] | list[dict]: Solid color or gradient adjustment layer notation."""
        return psd.get_pinline_gradient(self.pinlines, color_map=self.crown_color_map)

    """
    * Groups
    """

    @auto_prop_cached
    def background_group(self) -> Optional[LayerSet]:
        """Optional[LayerSet]: No background for 'Colorless' cards."""
        if self.is_colorless:
            return
        return super().background_group

    """
    * Masks
    """

    @auto_prop_cached
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
    * Shapes
    """

    @auto_prop_cached
    def pinlines_shape(self) -> Optional[LayerSet]:
        # Support Normal and Transform Front
        name = (
            LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK
        ) if self.is_transform else LAYERS.NORMAL
        return psd.getLayerSet(name, [self.pinlines_group, LAYERS.SHAPE])

    """
    * Methods
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
        self.generate_layer(
            group=self.crown_group,
            colors=self.crown_colors)

        # Enable Legendary pinline connector
        psd.getLayerSet(
            LAYERS.LEGENDARY,
            self.pinlines_shape.parent
        ).visible = True

    """
    * Transform Methods
    """

    def enable_transform_layers_back(self) -> None:
        super().enable_transform_layers_back()

        # Enable brightness shift on back face layers
        psd.getLayerSet(LAYERS.BACK, self.pt_group).visible = True
        psd.getLayerSet(LAYERS.BACK, self.twins_group).visible = True
        psd.getLayer(LAYERS.BACK, self.textbox_group).visible = True


class LOTRTemplate(VectorTemplate):
    """
    * Lord of the Rings template introduced in Lord of The Rings: Tales of Middle Earth.
    * Credit to Tupinambá (Pedro Neves) for the master template
    * With additional support from CompC and MrTeferi
    """
    template_suffix = 'Lord of the Rings'

    # Static Properties
    enabled_shapes = []

    # Color Maps
    pinlines_color_map = {
        **pinlines_color_map.copy(),
        'W': [230, 220, 185],
        'U': [72, 142, 191],
        'B': [126, 128, 127],
        'R': [217, 94, 76],
        'G': [97, 143, 102],
        'Gold': [246, 213, 125],
        'Land': [181, 162, 149],
        'Artifact': [210, 219, 227],
        'Colorless': [210, 219, 227]}
    dark_color_map = {
        **pinlines_color_map.copy(),
        'W': [134, 123, 105],
        'U': [44, 51, 103],
        'B': [44, 43, 39],
        'R': [118, 34, 34],
        'G': [13, 68, 45],
        'Gold': [158, 124, 78],
        'Land': [103, 90, 74],
        'Artifact': [61, 88, 109],
        'Colorless': [78, 91, 101],
        'Vehicle': [76, 51, 20]}

    """
    * Colors
    """

    @auto_prop_cached
    def crown_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.pinlines_color_map)

    @auto_prop_cached
    def twins_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            colors=self.twins,
            color_map=self.dark_color_map)

    @auto_prop_cached
    def pt_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            colors=LAYERS.VEHICLE if self.is_vehicle else self.twins,
            color_map=self.dark_color_map)

    @auto_prop_cached
    def textbox_colors(self) -> str:
        """str: Just use twins value for texture name."""
        return self.twins

    @auto_prop_cached
    def background_colors(self) -> str:
        """str: Just use pinlines value for texture name."""
        return self.pinlines

    """
    * Groups
    """

    @auto_prop_cached
    def pinlines_groups(self) -> list[LayerSet]:
        """Pinlines and crown pinlines addon."""
        groups = [self.pinlines_group]
        if self.is_legendary:
            groups.append(self.crown_group)
        return groups

    """
    * Masks
    """

    @auto_prop_cached
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Mask Pinlines if Legendary."""
        if self.is_legendary:
            return [self.pinlines_group]
        return []

    """
    * Frame Layer Methods
    """

    def enable_crown(self) -> None:
        """Enable the Legendary crown group only."""
        self.crown_group.visible = True


class BorderlessVectorTemplate(VectorBorderlessMod, VectorMDFCMod, VectorTransformMod, VectorTemplate):
    """Borderless template first used in the Womens Day Secret Lair, redone with vector shapes."""

    def __init__(self, layout, **kwargs):
        if not CFG.exit_early:
            CFG.exit_early = self.is_nickname
        super().__init__(layout, **kwargs)

    # Color Maps
    light_color_map = {
        'W': "#faf8f2",
        'U': "#d2edfa",
        'B': "#c9c2be",
        'R': "#f8c7b0",
        'G': "#dbfadc",
        'Gold': "#f5e5a4",
        'Land': "#f0ddce",
        'Hybrid': "f#0ddce",
        'Artifact': "#cde0e9",
        'Colorless': "#e2d8d4",
        'Vehicle': "#4c3314"}
    crown_color_map = {
        'W': "#f8f4f0",
        'U': "#006dae",
        'B': "#393431",
        'R': "#de3c23",
        'G': "#006d42",
        'Gold': "#efd16b",
        'Land': "#a59684",
        'Artifact': "#b5c5cd",
        'Colorless': "#d6d6dc"}
    gradient_location_map = {
        2: [.40, .60],
        3: [.29, .40, .60, .71],
        4: [.20, .30, .45, .55, .70, .80],
        5: [.20, .25, .35, .45, .55, .65, .75, .80]}

    # Static Properties
    mask_layers = []
    background_group = None

    """
    * Mixin Methods
    """

    @property
    def post_text_methods(self):
        """Add post-text adjustments method."""
        funcs = []
        if self.size != BorderlessTextbox.Tall:
            funcs.append(self.textbox_positioning)
        if self.is_token:
            funcs.append(self.token_adjustments)
        if self.is_textless:
            funcs.append(self.textless_adjustments)
        if self.is_nickname:
            funcs.append(self.nickname_adjustments)
        return [*super().post_text_methods, *funcs, self.text_layer_fx]

    """
    * Settings
    """

    @auto_prop_cached
    def size(self) -> str:
        """Layer name associated with the size of the textbox."""

        # Check for textless
        if self.is_textless:
            return BorderlessTextbox.Textless

        # Get the user's preferred setting
        size = str(CFG.get_option(
            section="FRAME",
            key="Textbox.Size",
            enum_class=BorderlessTextbox,
            default=BorderlessTextbox.Automatic
        ))

        # Determine the automatic size
        if size == BorderlessTextbox.Automatic:

            # Check for basic land
            if self.is_basic_land:
                return BorderlessTextbox.Short

            # Set up our test text layer
            test_layer = psd.getLayer(self.text_layer_rules_name, [self.text_group, "Tall"])
            test_text = self.layout.oracle_text
            if self.layout.flavor_text:
                test_text += f'\r{self.layout.flavor_text}'
            test_layer.textItem.contents = test_text.replace('\n', '\r')

            # Get the number of lines in our test text and decide what size
            num = get_line_count(test_layer, self.docref)
            if num < 5:
                return BorderlessTextbox.Short
            if num < 6:
                return BorderlessTextbox.Medium
            if num < 7:
                return BorderlessTextbox.Normal
            return BorderlessTextbox.Tall
        return size

    @auto_prop_cached
    def color_limit(self) -> int:
        # Built in setting, dual and triple color split
        return int(CFG.get_setting(
            section="COLORS",
            key="Max.Colors",
            default="2",
            is_bool=False)) + 1

    @auto_prop_cached
    def drop_shadow_enabled(self) -> bool:
        """Returns True if Drop Shadow text setting is enabled."""
        return bool(CFG.get_setting(
            section="TEXT",
            key="Drop.Shadow",
            default=True))

    @auto_prop_cached
    def crown_texture_enabled(self) -> bool:
        """Returns True if Legendary crown clipping texture should be enabled."""
        return bool(CFG.get_setting(
            section="FRAME",
            key="Crown.Texture",
            default=True))

    @auto_prop_cached
    def multicolor_textbox(self) -> bool:
        """Returns True if Textbox for multicolored cards should use blended colors."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Multicolor.Textbox",
            default=True))

    @auto_prop_cached
    def multicolor_pinlines(self) -> bool:
        """Returns True if Pinlines and Crown for multicolored cards should use blended colors."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Multicolor.Pinlines",
            default=True))

    @auto_prop_cached
    def multicolor_twins(self) -> bool:
        """Returns True if Twins for multicolored cards should use blended colors."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Multicolor.Twins",
            default=False))

    @auto_prop_cached
    def multicolor_pt(self) -> bool:
        """Returns True if PT Box for multicolored cards should use the last color."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Multicolor.PT",
            default=False))

    @auto_prop_cached
    def hybrid_colored(self) -> bool:
        """Returns True if Twins and PT should be colored on Hybrid cards."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Hybrid.Colored",
            default=True))

    @auto_prop_cached
    def front_face_colors(self) -> bool:
        """Returns True if lighter color map should be used on front face DFC cards."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Front.Face.Colors",
            default=True))

    @auto_prop_cached
    def land_colorshift(self) -> bool:
        """Returns True if Land cards should use the darker brown color."""
        return bool(CFG.get_setting(
            section="COLORS",
            key="Land.Colorshift",
            default=False))

    @auto_prop_cached
    def artifact_color_mode(self) -> str:
        """Setting determining what elements to color for colored artifacts.."""
        return CFG.get_option(
            section="COLORS",
            key="Artifact.Color.Mode",
            enum_class=BorderlessColorMode)

    """
    * Frame Details
    """

    @auto_prop_cached
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

    @auto_prop_cached
    def art_frame(self) -> str:
        # Use different positioning based on textbox size
        return f"{LAYERS.ART_FRAME} {self.size}"

    """
    * Bool
    """

    @property
    def is_basic_land(self):
        """Disable basic land watermark if Textless is enabled."""
        if bool(CFG.get_setting(section="FRAME", key="Textless", default=False)):
            return False
        return super().is_basic_land

    @auto_prop_cached
    def is_textless(self) -> bool:
        """Return True if this a textless render."""
        if not any([self.layout.oracle_text, self.layout.flavor_text, self.is_basic_land]):
            return True
        return bool(CFG.get_setting(section="FRAME", key="Textless", default=False))

    @auto_prop_cached
    def is_nickname(self) -> bool:
        """Return True if this a nickname render."""
        return CFG.get_setting(section="TEXT", key="Nickname", default=False)

    @auto_prop_cached
    def is_multicolor(self) -> bool:
        """Whether the card is multicolor and within the color limit range."""
        return bool(1 <= len(self.identity) < self.color_limit)

    @auto_prop_cached
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
                ]))

    @auto_prop_cached
    def is_pt_enabled(self) -> bool:
        """Return True if a separate Power/Toughness text layer is used for this render."""
        return self.is_creature and (not self.is_textless or not CFG.symbol_enabled)

    @auto_prop_cached
    def is_drop_shadow(self) -> bool:
        """Return True if drop shadow setting is enabled."""
        return bool(
            self.drop_shadow_enabled and not
            ((self.is_mdfc or self.is_transform) and self.is_front and self.front_face_colors))

    @auto_prop_cached
    def is_authentic_front(self) -> bool:
        """Return True if rendering a front face DFC card with authentic lighter colors."""
        return bool((self.is_mdfc or self.is_transform) and self.is_front and self.front_face_colors)

    """
    * Color Maps
    """

    @auto_prop_cached
    def dark_color_map(self) -> dict:
        return {
            'W': "#958676",
            'U': "#045482",
            'B': "#282523",
            'R': "#93362a",
            'G': "#134f23",
            'Gold': "#9a883f",
            'Land': "#684e30" if self.land_colorshift else "#a79c8e",
            'Hybrid': "#a79c8e",
            'Artifact': "#48555c",
            'Colorless': "#74726b",
            'Vehicle': "#4c3314"
        }

    """
    * Colors
    """

    @auto_prop_cached
    def twins_colors(self) -> Union[list[int], list[dict]]:

        # Default to twins
        colors = self.twins

        # Color enabled hybrid OR color enabled multicolor
        if (self.is_hybrid and self.hybrid_colored) or (self.is_multicolor and self.multicolor_twins):
            colors = self.identity
        # Color disabled hybrid cards
        elif self.is_hybrid:
            colors = LAYERS.HYBRID

        # Use artifact twins if artifact mode isn't colored
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

    @auto_prop_cached
    def pt_colors(self) -> Union[list[int], list[dict]]:

        # Default to twins, or Vehicle for non-colored vehicle artifacts
        colors = self.twins

        # Color enabled hybrid OR color enabled multicolor
        if (self.is_hybrid and self.hybrid_colored) or (self.is_multicolor and self.multicolor_pt):
            colors = self.identity[-1]
        # Use Hybrid color for color-disabled hybrid cards
        elif self.is_hybrid:
            colors = LAYERS.HYBRID

        # Use artifact twins color if artifact mode isn't colored
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

    @auto_prop_cached
    def textbox_colors(self) -> Union[list[int], list[dict]]:

        # Default to twins
        colors = self.twins

        # Hybrid OR color enabled multicolor
        if self.is_hybrid or (self.is_multicolor and self.multicolor_textbox):
            colors = self.identity

        # Use artifact textbox color if artifact mod isn't colored
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

    @auto_prop_cached
    def crown_colors(self) -> Union[list[int], list[dict]]:
        # Use Solid Color or Gradient adjustment layer for Crown colors
        return psd.get_pinline_gradient(
            # Use identity for hybrid OR color enabled multicolor
            colors=self.identity if self.is_hybrid or (self.is_multicolor and self.multicolor_pinlines) else (
                # Use pinlines if not a color code
                self.pinlines if not is_multicolor_string(self.pinlines) else LAYERS.GOLD),
            color_map=self.crown_color_map,
            location_map=self.gradient_location_map)

    @auto_prop_cached
    def pinlines_colors(self) -> Union[list[int], list[dict]]:
        # Use alternate gradient location map
        return psd.get_pinline_gradient(
            # Use identity for hybrid OR color enabled multicolor
            colors=self.identity if self.is_hybrid or (self.is_multicolor and self.multicolor_pinlines) else (
                # Use pinlines if not a color code
                self.pinlines if not is_multicolor_string(self.pinlines) else LAYERS.GOLD),
            color_map=self.pinlines_color_map,
            location_map=self.gradient_location_map)

    """
    * Groups
    """

    @auto_prop_cached
    def pt_group(self) -> Optional[LayerSet]:
        """PT Box group, alternative Textless option used when Expansion Symbol is disabled."""
        if self.is_textless and CFG.symbol_enabled:
            return
        if self.is_textless and self.is_pt_enabled:
            return psd.getLayerSet(f'{LAYERS.PT_BOX} {LAYERS.TEXTLESS}')
        return super().pt_group

    @auto_prop_cached
    def crown_group(self) -> LayerSet:
        """Legendary Crown group, use inner group to allow textured overlays above."""
        return psd.getLayerSet(LAYERS.LEGENDARY_CROWN, LAYERS.LEGENDARY_CROWN)

    @auto_prop_cached
    def nickname_group(self) -> LayerSet:
        """Nickname frame element group."""
        return psd.getLayerSet(LAYERS.NICKNAME)

    @auto_prop_cached
    def textbox_group(self) -> Optional[LayerSet]:
        """Optional[LayerSet]: Textbox group if not a 'Textless' render."""
        if self.is_textless:
            return
        return super().textbox_group

    """
    * Text Layers
    """

    @auto_prop_cached
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

    @auto_prop_cached
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Card rules text layer, use pre-computed layer name."""
        return psd.getLayer(self.text_layer_rules_name, [self.text_group, self.size])

    @auto_prop_cached
    def text_layer_name(self) -> Optional[ArtLayer]:
        """Card name text layer, allow support for Nickname."""
        if self.is_nickname:
            layer = psd.getLayer(LAYERS.NICKNAME, self.text_group)
            super().text_layer_name.textItem.contents = "ENTER NAME HERE"
            layer.visible = True
            return layer
        return super().text_layer_name

    """
    * References
    """

    @auto_prop_cached
    def textbox_reference(self) -> Optional[ReferenceLayer]:
        """Use size appropriate textbox reference."""
        ref = psd.get_reference_layer(self.size, psd.getLayerSet(LAYERS.TEXTBOX_REFERENCE, self.text_group))
        if self.is_mdfc:
            psd.copy_layer_mask(
                layer_from=psd.getLayer(LAYERS.MDFC, [self.mask_group, LAYERS.TEXTBOX_REFERENCE]),
                layer_to=ref)
            psd.apply_mask(ref)
            ref.visible = False
        return ref

    """
    * Shapes
    """

    @auto_prop_cached
    def textbox_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        """Support a size appropriate textbox shape and Transform Front addition."""

        # Return None if textless
        if self.is_textless:
            return []

        # Enable Transform Front addition if required
        names = [self.size, LAYERS.TRANSFORM_FRONT] if self.is_transform and self.is_front else [self.size]
        return [psd.getLayer(n, [self.textbox_group, LAYERS.SHAPE]) for n in names]

    @auto_prop_cached
    def pinlines_shapes(self) -> list[Union[ArtLayer, LayerSet]]:
        """Support a variety of pinlines shapes including Transform, MDFC, Textless, Nickname, etc."""

        # Name and typeline
        layers = [
            psd.getLayerSet(
                LAYERS.TRANSFORM if self.is_transform else (LAYERS.MDFC if self.is_mdfc else LAYERS.NORMAL),
                [self.pinlines_group, LAYERS.SHAPE, LAYERS.NAME]),
            psd.getLayer(
                LAYERS.TEXTLESS if self.is_textless else self.size,
                [self.pinlines_group, LAYERS.SHAPE, LAYERS.TYPE_LINE])
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

    @auto_prop_cached
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

    @auto_prop_cached
    def nickname_shape(self) -> ArtLayer:
        """Vector shape for Nickname box."""
        return psd.getLayer(
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL,
            [self.nickname_group, LAYERS.SHAPE]
        )

    @auto_prop_cached
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
    * Masks
    """

    @auto_prop_cached
    def border_mask(self) -> Optional[list]:
        """Support border mask for Textless and front face Transform modifications."""
        if self.is_textless:
            return [psd.getLayer(LAYERS.TEXTLESS, [self.mask_group, LAYERS.BORDER]), self.border_group]
        if self.is_transform and self.is_front:
            return [psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.mask_group, LAYERS.BORDER]), self.border_group]
        return

    @auto_prop_cached
    def pinlines_mask(self) -> dict:
        """Use pre-calculated frame type to find pinlines mask. This mask hides overlapping layer effects."""
        return {
            'mask': psd.getLayer(self.frame_type, [self.mask_group, LAYERS.PINLINES]),
            'layer': self.pinlines_group,
            'funcs': [psd.apply_mask_to_layer_fx]
        }

    @auto_prop_cached
    def pinlines_vector_mask(self) -> Optional[dict]:
        """Enable the pinlines vector mask if card is Legendary. """
        if not self.is_legendary:
            return
        return {
            'mask': self.pinlines_group,
            'vector': True
        }

    @auto_prop_cached
    def crown_mask(self) -> Optional[dict]:
        """Copy the pinlines mask to Legendary crown if card is Legendary."""
        if not self.is_legendary:
            return
        return {
            'mask': self.pinlines_mask['mask'],
            'layer': self.crown_group.parent,
            'funcs': [psd.apply_mask_to_layer_fx]}

    @auto_prop_cached
    def enabled_masks(self) -> list[Union[dict, list, ArtLayer, LayerSet, None]]:
        """Masks that should be copied or enabled."""
        return [
            self.crown_mask,
            self.border_mask,
            self.pinlines_mask,
            self.pinlines_vector_mask]

    """
    * Effects
    """

    @auto_prop_cached
    def nickname_fx(self) -> ArtLayer:
        """ArtLayer: Layer containing nickname effects."""
        return psd.getLayer(LAYERS.NICKNAME, LAYERS.EFFECTS)

    """
    * Watermarks
    """

    @auto_prop_cached
    def basic_watermark_fx(self) -> list[LayerEffects]:
        """Defines the layer effects used on the Basic Land Watermark."""
        sizes = {
            # Bevel thickness based on textbox size
            BorderlessTextbox.Short: 20,
            BorderlessTextbox.Medium: 22,
            BorderlessTextbox.Normal: 25,
            BorderlessTextbox.Tall: 28}
        return [
            {'type': 'color-overlay', 'opacity': 100, 'color': self.basic_watermark_color},
            {
                'size': sizes.get(self.size),
                'type': 'bevel', 'softness': 14, 'depth': 100,
                'shadow_opacity': 72, 'highlight_opacity': 70,
                'rotation': 45, 'altitude': 22
            }
        ]

    """
    * Frame Layer Methods
    """

    def enable_crown(self) -> None:
        """Allow modifying crown texture based on setting."""
        super().enable_crown()

        # Remove crown textures if disabled
        if not self.crown_texture_enabled:
            for n in ["Shading", "Highlight", "Overlay"]:
                psd.getLayer(n, self.crown_group.parent).visible = False

    """
    * Text Layer Methods
    """

    def basic_text_layers(self) -> None:

        # Establish whether this is a textless creature render with no symbol
        self.text.extend([
            FormattedTextField(
                layer=self.text_layer_mana,
                contents=self.layout.mana_cost
            ),
            ScaledTextField(
                layer=self.text_layer_type,
                # Add Power/Toughness if rendering textless creature WITH symbol
                contents=f"{self.layout.type_line} — {self.layout.power}/{self.layout.toughness}" if
                self.is_creature and not self.is_pt_enabled else self.layout.type_line,
                # Use PT box as right reference if rendering textless creature WITHOUT symbol
                reference=psd.getLayer(LAYERS.PT_BOX, [self.pt_group, LAYERS.SHAPE])
                if self.is_textless and self.is_pt_enabled else self.type_reference
            )
        ])

        # Add nickname or regular name
        self.text.append(
            ScaledTextField(
                layer=self.text_layer_name,
                contents=self.layout.name,
                reference=self.name_reference
            ) if not self.is_nickname else
            ScaledWidthTextField(
                layer=self.text_layer_name,
                contents=self.layout.name,
                reference=self.nickname_shape
            ))

    def rules_text_and_pt_layers(self) -> None:
        """Skip this step for 'Textless' renders."""
        if self.is_textless:
            if self.is_pt_enabled:
                self.text.append(
                    TextField(
                        layer=self.text_layer_pt,
                        contents=f'{self.layout.power}/'
                                 f'{self.layout.toughness}'))
            return
        super().rules_text_and_pt_layers()

    """
    * Post Text Methods
    """

    def textless_adjustments(self) -> None:
        """Actions taken if this is a 'Textless' render."""

        # Make positioning adjustments
        if self.is_type_shifted:
            self.indicator_group.translate(-10, 0)
        self.text_layer_type.translate(-10, 0)

        # Align and add PT text for creatures with no expansion symbol
        if self.is_pt_enabled:
            psd.align_all(
                layer=self.text_layer_pt,
                ref=psd.getLayer(LAYERS.PT_BOX, [
                    self.pt_group, LAYERS.SHAPE]))
            return

        # Otherwise just shift the symbol over
        if self.expansion_symbol_layer:
            self.expansion_symbol_layer.translate(10, 0)

    def token_adjustments(self) -> None:
        """Actions taken if this is a 'Token' card."""

        # Change name font and center it
        self.text_layer_name.textItem.font = CON.font_artist
        psd.align_horizontal(self.text_layer_name, self.twins_shapes[0])

        # Add name plate shadow
        psd.getLayer(LAYERS.TOKEN, self.text_group).visible = True

    def nickname_adjustments(self) -> None:
        """Actions taken if this is a 'Nickname' render."""

        # Nickname plate -> Solid color or gradient layer
        if self.is_nickname:
            self.generate_layer(
                group=self.nickname_group,
                colors=self.twins_colors)

        # Center the name
        psd.align_vertical(self.text_layer_name, self.nickname_shape)

        # Copy effects to legendary crown
        if self.is_legendary:
            psd.copy_layer_fx(self.nickname_fx, self.crown_group.parent)

    def textbox_positioning(self) -> None:
        """Reposition various elements when textbox size isn't 'Tall' (the default)."""

        # Get the delta between the highest box and the target box
        shape = psd.getLayer(LAYERS.TALL, [
            self.pinlines_group,
            LAYERS.SHAPE,
            LAYERS.TYPE_LINE])
        dims_ref = psd.get_layer_dimensions(shape)
        dims_obj = psd.get_layer_dimensions(self.pinlines_shapes[1])
        delta = dims_obj[Dimensions.CenterY] - dims_ref[Dimensions.CenterY]
        self.text_layer_type.translate(0, delta)

        # Shift expansion symbol
        if CFG.symbol_enabled and self.expansion_symbol_layer:
            self.expansion_symbol_layer.translate(0, delta)

        # Shift indicator
        if self.is_type_shifted:
            self.indicator_group.parent.translate(0, delta)

    def text_layer_fx(self) -> None:
        """Handles all specialized text adjustments for a variety of render settings."""

        # Add drop shadow if enabled and allowed
        if self.is_drop_shadow:

            # Name and Typeline
            psd.enable_layer_fx(self.text_layer_name)
            psd.enable_layer_fx(self.text_layer_type)

            # Rules text if not textless
            if not self.is_textless and not self.is_basic_land:
                psd.enable_layer_fx(self.text_layer_rules)

            # Flipside PT for front face Transform
            if self.is_flipside_creature and self.is_front and self.is_transform:
                psd.enable_layer_fx(self.text_layer_flipside_pt)

        # Allow exception for PT drop shadow on front face Vehicle cards
        if (self.is_drop_shadow or (self.drop_shadow_enabled and self.is_vehicle)) and self.is_pt_enabled:
            psd.enable_layer_fx(self.text_layer_pt)

    """
    * Transform Methods
    """

    def text_layers_transform_front(self) -> None:
        """Switch font colors on 'Authentic' front face cards."""
        super().text_layers_transform_front()

        # Use black text
        if self.is_authentic_front:
            self.swap_font_color()

        # Switch flipside PT to light gray
        if not self.is_authentic_front and self.is_flipside_creature:
            self.text_layer_flipside_pt.textItem.color = psd.get_rgb(*[186, 186, 186])

    def text_layers_transform_back(self):
        """No back-side Transform changes."""
        pass

    """
    * MDFC Methods
    """

    def text_layers_mdfc_front(self) -> None:
        """Switch font colors on 'Authentic' front face cards."""
        if self.is_authentic_front:
            self.swap_font_color()

    """
    * Util Methods
    """

    def swap_font_color(self, color: SolidColor = None) -> None:
        """Switch the font color of each key text layer.

        Args:
            color: SolidColor object, will use black if not provided.
        """

        # Ensure a color is chosen
        color = color or self.RGB_BLACK

        # Name and Typeline
        self.text_layer_name.textItem.color = color
        self.text_layer_type.textItem.color = color

        # Rules text if not textless
        if not self.is_textless:
            self.text_layer_rules.textItem.color = color

        # PT if card is a non-vehicle creature
        if self.is_pt_enabled and not self.is_vehicle:
            self.text_layer_pt.textItem.color = color


class ClassicModernTemplate(VectorTransformMod, VectorMDFCMod, VectorTemplate):
    """A modern frame version of iDerp's 'Classic Remastered' template."""

    # Static properties
    is_vehicle = False

    # Color Maps
    pinlines_color_map = {**pinlines_color_map.copy(), "Land": "#604a33"}

    """
    * Bool
    """

    @property
    def is_extended(self) -> bool:
        """TODO: Based on whether the extended setting is enabled."""
        return True

    @property
    def is_content_aware_enabled(self) -> bool:
        """Force enabled if 'is_extended' setting is enabled."""
        return True if self.is_extended else super().is_content_aware_enabled

    """
    * Settings
    """

    @auto_prop_cached
    def crown_mode(self) -> str:
        """Whether to use pinlines when generating the Legendary Crown."""
        return CFG.get_option("FRAME", "Crown.Mode", ModernClassicCrown)

    """
    * References
    """

    @auto_prop_cached
    def textbox_reference(self) -> Optional[ArtLayer]:
        """Use a mask to reduce reference size for MDFC cards."""
        ref = super().textbox_reference
        if self.is_mdfc:
            psd.copy_layer_mask(
                layer_from=psd.getLayer(LAYERS.MDFC, [self.mask_group, LAYERS.TEXTBOX_REFERENCE]),
                layer_to=ref)
            psd.apply_mask(ref)
            ref.visible = False
        return ref

    """
    * Colors
    """

    @auto_prop_cached
    def textbox_colors(self) -> list[str]:
        # Only blend textbox colors for hybrid and land cards
        if self.is_land:
            # 2-3 color lands
            if 1 < len(self.identity) < self.color_limit and self.is_land:
                # Dual or tri colors
                return [f'{n} {LAYERS.LAND}' for n in self.identity]
            # Plain land background
            if self.pinlines == LAYERS.LAND:
                return [LAYERS.LAND]
            # All other land backgrounds
            return [f'{self.pinlines} {LAYERS.LAND}']
        # Hybrid cards
        if self.is_hybrid:
            return list(self.pinlines)
        # Just one layer
        return [self.background]

    @auto_prop_cached
    def crown_colors(self) -> str:
        """Support multicolor based on color limit."""
        if self.crown_mode == ModernClassicCrown.TextureBackground:
            return self.background
        return self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines

    """
    * Shapes
    """

    @auto_prop_cached
    def crown_shape(self) -> Optional[ArtLayer]:
        # Support Normal and Extended
        return psd.getLayer(
            LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL,
            [LAYERS.LEGENDARY_CROWN, LAYERS.SHAPE])

    @auto_prop_cached
    def border_shape(self) -> Optional[ArtLayer]:
        # Support Normal and Legendary
        return psd.getLayer(
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL,
            LAYERS.BORDER)

    @auto_prop_cached
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

    @auto_prop_cached
    def textbox_shape(self) -> list[Union[ArtLayer, LayerSet]]:
        return [
            psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.textbox_group, LAYERS.SHAPE])
        ] if self.is_transform and self.is_front else []

    @auto_prop_cached
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        crown = [self.crown_shape] if self.is_legendary else []
        return [
            self.border_shape,
            self.twins_shape,
            *self.pinlines_shape,
            *self.textbox_shape,
            *crown]

    """
    * Masks
    """

    @auto_prop_cached
    def twins_mask(self) -> list[dict]:
        return [{
            'mask': self.twins_group,
            'vector': True
        }] if self.is_extended else []

    @auto_prop_cached
    def border_mask(self) -> list[Union[ArtLayer, LayerSet]]:
        return [
            psd.getLayer(
                LAYERS.MDFC if self.is_mdfc and not self.is_legendary else LAYERS.NORMAL,
                [self.mask_group, LAYERS.BORDER, LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL]
            ), self.border_group
        ]

    @auto_prop_cached
    def background_mask(self) -> list[Union[ArtLayer, LayerSet]]:
        return [
            psd.getLayer(
                LAYERS.EXTENDED if self.is_extended else LAYERS.NORMAL,
                [self.mask_group, LAYERS.BACKGROUND]
            ), self.background_group
        ]

    @auto_prop_cached
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

    @auto_prop_cached
    def enabled_masks(self) -> list[Union[list, dict]]:
        return [
            self.border_mask,
            self.background_mask,
            *self.pinlines_mask,
            *self.twins_mask
        ]

    """
    * Frame Layer Methods
    """

    def enable_crown(self) -> None:
        """Enable the Legendary crown, only called if card is Legendary."""

        # Generate Legendary Crown using pinline colors
        if self.crown_mode == ModernClassicCrown.Pinlines:
            self.generate_layer(
                group=self.crown_group,
                colors=self.pinlines_colors)
            return

        # Generate Legendary Crown using textures
        self.generate_layer(
            group=self.crown_group,
            colors=self.crown_colors,
            masks=self.crown_masks)

    """
    * Transform Methods
    """

    def enable_transform_layers_back(self) -> None:

        # Use darker Twins and PT texture
        if self.is_creature:
            psd.getLayer(LAYERS.LIGHTEN, self.pt_group).visible = False
        psd.getLayer(LAYERS.LIGHTEN, self.twins_group).visible = False
        super().enable_transform_layers_back()

    """
    * MDFC Methods
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
