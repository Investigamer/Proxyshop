"""
* CORE PROXYSHOP TEMPLATES
"""
# Standard Library Imports
import os.path as osp
from functools import cached_property
from pathlib import Path
from threading import Event
from typing import Optional, Callable, Any, Union, Iterable

# Third Party Imports
from pathvalidate import sanitize_filename
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document
from photoshop.api import (
    AnchorPosition,
    ElementPlacement,
    SolidColor,
    BlendMode,
    Urgency
)
from PIL import Image

# Local Imports
from src.console import console, Console
from src.enums.mtg import watermark_color_map, MagicIcons, basic_land_color_map
import src.format_text as ft
from src.constants import con
from src.settings import cfg
import src.helpers as psd
from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextField,
    FormattedTextArea,
    CreatureFormattedTextArea
)
from src.enums.photoshop import Dimensions
from src.enums.layers import LAYERS
from src.enums.settings import (
    CollectorMode,
    ExpansionSymbolMode,
    BorderColor,
    OutputFiletype,
    CollectorPromo
)
from src.utils.exceptions import PS_EXCEPTIONS, get_photoshop_error_message
from src.utils.files import get_unique_filename
from src.utils.objects import PhotoshopHandler
from src.utils.scryfall import card_scan
from src.utils.strings import msg_warn, msg_error


class BaseTemplate:
    """
    * Master Template for Proxyshop
    * Contains all the core architecture that is required for any template to function in Proxyshop, as well as
    a ton of optional built-in utility properties and methods for building templates.
    * All template classes should extend to this class at bare minimum.
    """
    template_suffix = ""

    def __init__(self, layout: Any, **kwargs):

        # Strip flavor text, string or list
        if cfg.remove_flavor:
            layout.flavor_text = "" if isinstance(
                layout.flavor_text, str
            ) else [""] * len(layout.flavor_text)

        # Strip reminder text, string or list
        if cfg.remove_reminder:
            layout.oracle_text = ft.strip_reminder_text(layout.oracle_text) if isinstance(
                layout.oracle_text, str
            ) else [ft.strip_reminder_text(n) for n in layout.oracle_text]

        # Setup manual properties
        self.layout = layout
        self._text = []

    def invalidate(self, prop: str):
        # Invalidates a cached property, so it will be computed at next use
        self.__dict__.pop(prop, None)

    @staticmethod
    def try_photoshop(func) -> Callable:
        """
        Decorator to handle trying to run a Photoshop action but allowing exceptions to fail silently.
        @param func: Function being wrapped.
        @return: The result of the wrapped function.
        """
        def wrapper(self, *args):
            try:
                result = func(self, *args)
                return result
            except PS_EXCEPTIONS:
                return
        return wrapper

    """
    METHOD MIXINS
    """

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        """Additional frame layer methods to call. Executed during enable_frame_layers."""
        return []

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Additional text layer methods to call. Executed during basic_text_layers."""
        return []

    @cached_property
    def general_methods(self) -> list[Callable]:
        """Additional general methods to call. Executed during post_text_layers."""
        return []

    """
    APP PROPERTIES
    """

    @cached_property
    def event(self) -> Event:
        """Threading Event used to signal thread cancellation."""
        return Event()

    @cached_property
    def console(self) -> Console:
        """Console output object used to communicate with the user."""
        return console

    @property
    def app(self) -> PhotoshopHandler:
        """Photoshop Application object used to communicate with Photoshop."""
        return con.app

    @cached_property
    def docref(self) -> Optional[Document]:
        """This template's document open in Photoshop."""
        if doc := psd.get_document(osp.basename(self.layout.template_file)):
            return doc
        return

    @property
    def active_layer(self) -> Union[ArtLayer, LayerSet]:
        """Get the currently active layer in the Photoshop document."""
        return self.docref.activeLayer

    @active_layer.setter
    def active_layer(self, value: Union[ArtLayer, LayerSet]):
        """Set the currently active layer in the Photoshop document."""
        self.docref.activeLayer = value

    """
    SOLID COLORS
    """

    @cached_property
    def RGB_BLACK(self) -> SolidColor:
        return psd.rgb_black()

    @cached_property
    def RGB_WHITE(self) -> SolidColor:
        return psd.rgb_white()

    """
    FILE SAVING
    """

    @cached_property
    def save_modes(self) -> dict:
        """Functions representing file saving modes."""
        return {
            OutputFiletype.PNG: psd.save_document_png,
            OutputFiletype.PSD: psd.save_document_psd,
            OutputFiletype.JPG: psd.save_document_jpeg
        }

    @cached_property
    def output_directory(self) -> str:
        """Directory to save the rendered image."""
        if cfg.test_mode:
            class_dir = f'out/{self.__class__.__name__}'
            Path(osp.join(con.cwd, class_dir)).mkdir(mode=711, parents=True, exist_ok=True)
            return class_dir
        return 'out'

    @cached_property
    def output_file_name(self) -> str:
        """The formatted filename for the rendered image."""
        # Establish the suffix to use for this name
        suffix = self.template_suffix
        if cfg.save_artist_name:
            suffix = f"{suffix} {self.layout.artist}" if suffix else self.layout.artist

        # Are we overwriting duplicate names?
        if not cfg.overwrite_duplicate:
            # Generate a name that doesn't exist yet
            return sanitize_filename(
                get_unique_filename(osp.join(con.cwd, "out"), self.layout.name_raw, f'.{cfg.output_filetype}', suffix))
        return sanitize_filename(f"{self.layout.name_raw}{f' ({suffix})' if suffix else ''}")

    """
    BOOL
    """

    @property
    def is_creature(self) -> bool:
        """Governs whether to add PT box and use Creature rules text."""
        return self.layout.is_creature

    @property
    def is_legendary(self) -> bool:
        """Enables the legendary crown step."""
        return self.layout.is_legendary

    @property
    def is_land(self) -> bool:
        """Governs whether to use normal or land pinlines group."""
        return self.layout.is_land

    @property
    def is_companion(self) -> bool:
        """Enables hollow crown step and companion crown layer."""
        return self.layout.is_companion

    @property
    def is_artifact(self) -> bool:
        """Utility definition for custom templates. Returns True if card is an Artifact."""
        return self.layout.is_artifact

    @property
    def is_vehicle(self) -> bool:
        """Utility definition for custom templates. Returns True if card is a Vehicle."""
        return self.layout.is_vehicle

    @property
    def is_hybrid(self) -> bool:
        """Utility definition for custom templates. Returns True if card is hybrid color."""
        return self.layout.is_hybrid

    @property
    def is_colorless(self) -> bool:
        """Enforces fullart framing for card art on many templates."""
        return self.layout.is_colorless

    @property
    def is_nyx(self) -> bool:
        """Enables hollow crown and nyx background layers."""
        return self.layout.is_nyx

    @property
    def is_front(self) -> bool:
        """Governs render behavior on MDFC and Transform cards."""
        return self.layout.is_front

    @property
    def is_transform(self) -> bool:
        """Governs behavior on double faced card varieties."""
        return self.layout.is_transform

    @property
    def is_mdfc(self) -> bool:
        """Governs behavior on double faced card varieties."""
        return self.layout.is_mdfc

    @cached_property
    def is_centered(self) -> bool:
        """Governs whether rules text is centered."""
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
        )

    @property
    def is_name_shifted(self) -> bool:
        """Governs whether to use the shifted name text layer."""
        return bool(self.is_transform or self.is_mdfc)

    @property
    def is_type_shifted(self) -> bool:
        """Governs whether to use the shifted typeline text layer."""
        return bool(self.layout.color_indicator)

    @cached_property
    def is_flipside_creature(self) -> bool:
        """Governs double faced cards where opposing side is a creature."""
        return bool(self.layout.other_face_power and self.layout.other_face_toughness)

    @cached_property
    def is_art_vertical(self) -> bool:
        """Returns True if art provided is vertically oriented, False if it is horizontal."""
        with Image.open(self.layout.art_file) as image:
            width, height = image.size
        if height > (width * 1.1):
            # Vertical orientation
            return True
        # Horizontal orientation
        return False

    @cached_property
    def is_fullart(self) -> bool:
        """Returns True if art must be treated as Fullart."""
        return False

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        """Governs whether content aware fill should be performed during the art loading step."""
        if self.is_fullart and 'Full' not in self.art_reference.name:
            # By default, fill when we want a fullart image but didn't receive one
            return True
        return False

    @cached_property
    def is_collector_promo(self) -> bool:
        """Governs whether to use promo star in collector info."""
        if cfg.collector_promo == CollectorPromo.Always:
            return True
        if self.layout.is_promo and cfg.collector_promo == CollectorPromo.Automatic:
            return True
        return False

    """
    FRAME DETAILS
    """

    @property
    def art_frame(self) -> str:
        """Normal frame to use for positioning the art."""
        return LAYERS.ART_FRAME

    @property
    def art_frame_vertical(self) -> str:
        """Vertical orientation frame to use for positioning the art."""
        return LAYERS.FULL_ART_FRAME

    @cached_property
    def twins(self) -> str:
        """Name of the Twins layer, also usually the PT layer."""
        return self.layout.twins

    @cached_property
    def pinlines(self) -> str:
        """Name of the Pinlines layer."""
        return self.layout.pinlines

    @cached_property
    def identity(self) -> str:
        """Color identity of the card, e.g. WU."""
        return self.layout.identity

    @cached_property
    def background(self) -> str:
        """Name of the Background layer."""
        if not self.is_vehicle and self.layout.background == LAYERS.VEHICLE:
            return LAYERS.ARTIFACT
        return self.layout.background

    @cached_property
    def face_type(self) -> Optional[str]:
        """Name of the double face text and icons group."""
        if self.is_mdfc:
            if self.is_front:
                return LAYERS.MDFC_FRONT
            return LAYERS.MDFC_BACK
        if self.is_transform:
            if self.is_front:
                return LAYERS.TF_FRONT
            return LAYERS.TF_BACK
        return

    """
    LIST OF FORMATTED TEXT ITEMS
    """

    @property
    def text(self) -> list:
        """Text layers to execute."""
        return self._text

    @text.setter
    def text(self, value):
        """Add text layer to execute."""
        self._text = value

    """
    COLORS
    """

    @cached_property
    def watermark_color_map(self) -> dict:
        """Maps color values for Watermarks."""
        return watermark_color_map.copy()

    """
    LAYER GROUPS
    """

    @cached_property
    def legal_group(self) -> Optional[LayerSet]:
        """Group containing artist credit, collector info, and other legal details."""
        return self.docref.layerSets.getByName(con.layers.LEGAL)

    @cached_property
    def border_group(self) -> Optional[Union[LayerSet, ArtLayer]]:
        """Group, or sometimes a layer, containing the card border."""
        if group := psd.getLayerSet(LAYERS.BORDER):
            return group
        if layer := psd.getLayer(LAYERS.BORDER):
            return layer
        return

    @cached_property
    def text_group(self) -> Optional[LayerSet]:
        """Text and icon group, contains rules text and necessary symbols."""
        if group := self.docref.layerSets.getByName(LAYERS.TEXT_AND_ICONS):
            return group
        return self.docref

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        """Group containing double face elements."""
        if self.face_type and self.text_group:
            return psd.getLayerSet(self.face_type, self.text_group)
        return

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_creator(self) -> Optional[ArtLayer]:
        """Proxy creator name text layer."""
        return psd.getLayer(LAYERS.CREATOR, self.legal_group)

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        """Card name text layer."""
        if self.is_name_shifted:
            psd.getLayer(LAYERS.NAME, self.text_group).visible = False
            name = psd.getLayer(LAYERS.NAME_SHIFT, self.text_group)
            name.visible = True
            return name
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_mana(self) -> Optional[ArtLayer]:
        """Card mana cost text layer."""
        return psd.getLayer(LAYERS.MANA_COST, self.text_group)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        """Card typeline text layer."""
        if self.is_type_shifted:
            psd.getLayer(LAYERS.TYPE_LINE, self.text_group).visible = False
            typeline = psd.getLayer(LAYERS.TYPE_LINE_SHIFT, self.text_group)
            typeline.visible = True
            return typeline
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Card rules text layer."""
        if self.is_creature:
            return psd.getLayer(LAYERS.RULES_TEXT_CREATURE, self.text_group)
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_group)

    @cached_property
    def text_layer_pt(self) -> Optional[ArtLayer]:
        """Card power and toughness text layer."""
        return psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_group)

    @cached_property
    def divider_layer(self) -> Optional[ArtLayer]:
        """Divider layer between rules text and flavor text."""
        if self.is_transform and self.is_front and self.is_flipside_creature:
            if TF_DIVIDER := psd.getLayer('Divider TF', self.text_group):
                return TF_DIVIDER
        return psd.getLayer(LAYERS.DIVIDER, self.text_group)

    """
    FRAME LAYERS
    """

    @property
    def art_layer(self) -> ArtLayer:
        """Layer the art image is imported into."""
        return psd.getLayer(LAYERS.DEFAULT)

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        """Name and title boxes layer."""
        return psd.getLayer(self.twins, LAYERS.TWINS)

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        """Pinlines (and textbox) layer."""
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        """Background texture layer."""
        # Try finding Nyx background
        if self.is_nyx:
            if layer := psd.getLayer(self.background, LAYERS.NYX):
                return layer
        # Try finding Vehicle background
        if self.is_vehicle and self.background == LAYERS.VEHICLE:
            return psd.getLayer(
                LAYERS.VEHICLE, LAYERS.BACKGROUND
            ) or psd.getLayer(
                LAYERS.ARTIFACT, LAYERS.BACKGROUND)
        # All other backgrounds
        return psd.getLayer(self.background, LAYERS.BACKGROUND)

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        """Color indicator icon layer."""
        if self.layout.color_indicator:
            return psd.getLayer(self.layout.color_indicator, LAYERS.COLOR_INDICATOR)
        return

    @cached_property
    def transform_icon_layer(self) -> Optional[ArtLayer]:
        """Transform icon layer."""
        return psd.getLayer(self.layout.transform_icon, self.dfc_group)

    @cached_property
    def crown_layer(self) -> Optional[ArtLayer]:
        """Legendary crown layer."""
        return psd.getLayer(self.pinlines, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        """Power and toughness box layer."""
        # Test for Vehicle PT support
        if self.is_vehicle and self.background == LAYERS.VEHICLE:
            if layer := psd.getLayer(LAYERS.VEHICLE, LAYERS.PT_BOX):
                # Change font to white for Vehicle PT box
                self.text_layer_pt.textItem.color = self.RGB_WHITE
                return layer
        return psd.getLayer(self.twins, LAYERS.PT_BOX)

    @cached_property
    def companion_layer(self) -> Optional[ArtLayer]:
        """Companion inner crown layer."""
        return psd.getLayer(self.pinlines, LAYERS.COMPANION)

    @cached_property
    def crown_shadow_layer(self) -> Union[ArtLayer, LayerSet, None]:
        """Legendary crown hollow shadow layer."""
        return psd.getLayer(LAYERS.HOLLOW_CROWN_SHADOW)

    """
    REFERENCE LAYERS
    """

    @cached_property
    def art_reference(self) -> ArtLayer:
        """Reference frame used to scale and position the art layer."""
        # Check if art provided is vertically oriented or vertical fullart is enabled on a fullart template
        if self.is_art_vertical or (self.is_fullart and cfg.vertical_fullart):
            # Check if we have a valid vertical art frame
            if layer := psd.getLayer(self.art_frame_vertical):
                return layer
        # Check for normal art frame
        return psd.getLayer(self.art_frame) or psd.getLayer(LAYERS.ART_FRAME)

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        """Reference frame used to scale and position the rules text layer."""
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE, self.text_group)

    @cached_property
    def pt_top_reference(self) -> Optional[ArtLayer]:
        """Reference used to get the top of the PT box."""
        return psd.getLayer(LAYERS.PT_TOP_REFERENCE, self.text_group)

    @cached_property
    def pt_adjustment_reference(self) -> Optional[ArtLayer]:
        """Reference used to get the location of the PT box."""
        return psd.getLayer(LAYERS.PT_REFERENCE, self.text_group)

    """
    LOADING ARTWORK
    """

    @property
    def art_action(self) -> Optional[Callable]:
        """Function that is called to perform an action on the imported art."""
        return

    @property
    def art_action_args(self) -> Optional[dict]:
        """Args to pass to art_action."""
        return

    def load_artwork(self) -> None:
        """
        Loads the specified art file into the specified layer.
        """
        # Check for fullart test image
        if cfg.test_mode and self.is_fullart:
            self.layout.art_file = osp.join(con.path_img, "test-fa.jpg")

        # Paste the file into the art
        self.active_layer = self.art_layer
        if self.art_action:
            psd.paste_file(self.art_layer, self.layout.art_file, self.art_action, self.art_action_args)
        else:
            psd.import_art(self.art_layer, self.layout.art_file)

        # Frame the artwork
        if self.panorama_mode_enabled:
            self.art_layers = psd.frame_panoramas(self.active_layer, self.art_reference)
        else:
            psd.frame_layer(self.active_layer, self.art_reference)
            self.art_layers = [self.art_layer]

        # Perform content aware fill if needed
        if self.is_content_aware_enabled:
            action = psd.generative_fill_edges if cfg.generative_fill else psd.content_aware_fill_edges
            for art_layer in self.art_layers:
                action(art_layer)

    def paste_scryfall_scan(self, rotate: bool = False, visible: bool = True) -> Optional[ArtLayer]:
        """
        Downloads the card's scryfall scan, pastes it into the document next to the active layer,
        and frames it to fill the given reference layer.
        @param rotate: Will rotate the card horizontally if True, useful for Planar cards.
        @param visible: Whether to leave the layer visible or hide it.
        """
        # Try to grab the scan from Scryfall
        if not self.layout.scryfall_scan or not (scryfall_scan := card_scan(self.layout.scryfall_scan)):
            return

        # Paste the scan into a new layer
        if layer := psd.import_art_into_new_layer(scryfall_scan, "Scryfall Reference"):
            # Rotate the layer if necessary
            if rotate:
                layer.rotate(90)

            # Frame the layer and position it above the art layer
            bleed = int(self.docref.resolution / 8)
            bounds = [bleed, bleed, self.docref.width - bleed, self.docref.height - bleed]
            psd.frame_layer(layer, psd.get_dimensions_from_bounds(bounds))
            layer.move(self.art_layer, ElementPlacement.PlaceBefore)
            layer.visible = visible
            return layer

    """
    COLLECTOR INFO
    """

    def collector_info(self) -> None:
        """Format and add the collector info at the bottom."""
        # Ignore this step if legal layer not present
        if not self.legal_group:
            return

        # If creator is specified add the text
        if self.layout.creator and self.text_layer_creator:
            self.text_layer_creator.textItem.contents = self.layout.creator

        # Use realistic collector information?
        if cfg.collector_mode in [CollectorMode.Default, CollectorMode.Modern] and self.layout.collector_data:
            self.collector_info_authentic()
        else:
            self.collector_info_basic()

    def collector_info_basic(self) -> None:
        """Called to generate basic collector info."""
        # Artist and set layer
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        set_layer = psd.getLayer(LAYERS.SET, self.legal_group)
        if self.border_color != BorderColor.Black:
            # Correct color for non-black border
            set_layer.textItem.color = self.RGB_BLACK
            artist_layer.textItem.color = self.RGB_BLACK
        psd.replace_text(artist_layer, "Artist", self.layout.artist)

        # Disable Set layer if Artist Only mode is enabled
        if cfg.collector_mode == CollectorMode.ArtistOnly:
            set_layer.visible = False
            return

        # Fill optional collector star
        if self.is_collector_promo:
            psd.replace_text(set_layer, "•", MagicIcons.COLLECTOR_STAR)

        # Fill alternate language and set info
        if self.layout.lang != "en":
            psd.replace_text(set_layer, "EN", self.layout.lang.upper())
        set_layer.textItem.contents = self.layout.set + set_layer.textItem.contents

    def collector_info_authentic(self) -> None:
        """Called to generate realistic collector info."""
        # Hide basic layers
        psd.getLayer(LAYERS.ARTIST, self.legal_group).opacity = 0
        psd.getLayer(LAYERS.SET, self.legal_group).opacity = 0

        # Get the collector layers
        collector_group = psd.getLayerSet(LAYERS.COLLECTOR, LAYERS.LEGAL)
        collector_top = psd.getLayer(LAYERS.TOP_LINE, collector_group).textItem
        collector_bottom = psd.getLayer(LAYERS.BOTTOM_LINE, collector_group)
        collector_group.visible = True

        # Correct color for non-black border
        if self.border_color != 'black':
            collector_top.color = self.RGB_BLACK
            collector_bottom.textItem.color = self.RGB_BLACK

        # Fill in language if needed
        if self.layout.lang != "en":
            psd.replace_text(collector_bottom, "EN", self.layout.lang.upper())

        # Fill optional collector star
        if self.is_collector_promo:
            psd.replace_text(collector_bottom, "•", MagicIcons.COLLECTOR_STAR)

        # Apply the collector info
        collector_top.contents = self.layout.collector_data
        psd.replace_text(collector_bottom, "SET", self.layout.set)
        psd.replace_text(collector_bottom, "Artist", self.layout.artist)

    """
    EXPANSION SYMBOL
    """

    @property
    def expansion_symbol_alignments(self) -> list[Dimensions]:
        """Alignments used for positioning the expansion symbol"""
        return [Dimensions.Right, Dimensions.CenterY]

    @cached_property
    def expansion_symbol_layer(self) -> Optional[ArtLayer]:
        """Expansion symbol layer"""
        return psd.getLayer(LAYERS.EXPANSION_SYMBOL, self.text_group)

    @cached_property
    def expansion_reference(self) -> Optional[ArtLayer]:
        """Expansion symbol reference layer"""
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, self.text_group)

    def expansion_symbol(self) -> None:
        """Builds the user's preferred type of expansion symbol."""
        if cfg.symbol_mode == ExpansionSymbolMode.Disabled:
            # Expansion symbol disabled
            self.expansion_symbol_layer.textItem.contents = ''
            return

        # Create a group for generated layers, clear style
        group = self.app.activeDocument.layerSets.add()
        group.move(self.expansion_symbol_layer, ElementPlacement.PlaceAfter)

        # Call the necessary creator
        try:
            if cfg.symbol_mode in [ExpansionSymbolMode.Font, 'default']:
                self.create_expansion_symbol(group)
            elif cfg.symbol_mode == ExpansionSymbolMode.SVG:
                self.create_expansion_symbol_svg(group)
        except Exception as e:
            self.console.log_exception(e)
            if not cfg.test_mode:
                self.console.update("Expansion symbol generation failed!\n"
                                    "Disabling expansion symbol.")
            group.visible = False

        # Merge and refresh cache
        group.merge().name = "Expansion Symbol"
        self.expansion_symbol_layer.name = "Expansion Symbol Old"
        self.expansion_symbol_layer.opacity = 0
        self.invalidate('expansion_symbol_layer')

        # Frame the symbol
        psd.frame_layer(
            self.expansion_symbol_layer,
            self.expansion_reference,
            smallest=True,
            alignments=self.expansion_symbol_alignments
        )

    def create_expansion_symbol(self, group: LayerSet) -> None:
        """
        Builds the expansion symbol using the newer layer effects methodology.
        @param group: The LayerSet to add generated layers to.
        """
        # Set the starting character and format our layer array
        symbols = psd.process_expansion_symbol_info(
            self.layout.symbol_font, self.layout.rarity.lower()
        )

        # Create each symbol layer
        for i, lay in enumerate(symbols):
            # Establish new current layer
            current_layer = self.expansion_symbol_layer.duplicate(group, ElementPlacement.PlaceAtEnd)
            current_layer.textItem.contents = lay['char']
            self.active_layer = current_layer
            layer_fx, fill_layer = [], None

            # Change font color
            if lay.get('color'):
                current_layer.textItem.color = lay['color']

            # Stroke fx
            if lay.get('stroke'):
                layer_fx.append(lay['stroke'])

            # Rarity gradient overlay fx
            if lay.get('rarity') and lay.get('gradient'):
                layer_fx.append(lay['gradient'])

            # Drop shadow fx
            if lay.get('drop-shadow'):
                layer_fx.append(lay['drop-shadow'])

            # Apply layer FX
            if layer_fx:
                psd.apply_fx(current_layer, layer_fx)

            # Rarity background fill
            if lay.get('fill') == 'rarity' and lay.get('gradient'):
                # Apply fill before rarity
                psd.rasterize_layer_fx(current_layer)
                fill_layer = psd.fill_empty_area(current_layer, self.RGB_BLACK)
                psd.apply_fx(fill_layer, [lay['gradient']])
            elif lay.get('fill'):
                psd.rasterize_layer_fx(current_layer)
                fill_layer = psd.fill_empty_area(current_layer, lay['fill'])

            # Merge if there is a filled layer
            if fill_layer:
                current_layer = psd.merge_layers([current_layer, fill_layer])

            # Scale factor
            if lay.get('scale'):
                current_layer.resize(lay['scale']*100, lay['scale']*100, AnchorPosition.MiddleCenter)

    def create_expansion_symbol_svg(self, group: LayerSet) -> None:
        """
        Creates an expansion symbol using SVG library. Falls back on default mode if SVG not available.
        @param group: The LayerSet to add generated layers to.
        """
        # SVG file exists?
        if not self.layout.symbol_svg:
            return self.create_expansion_symbol(group)

        # Import the SVG and place it correctly
        svg = psd.import_svg(str(self.layout.symbol_svg))
        svg.move(group, ElementPlacement.PlaceInside)

    """
    WATERMARK
    """

    def create_watermark(self) -> None:
        """Builds the watermark."""
        # Is the watermark from Scryfall supported?
        wm_path = osp.join(con.path_img, f"watermarks/{self.layout.watermark}.svg")
        if not self.layout.watermark or not osp.exists(wm_path):
            return

        # Decide what colors to use
        colors = []
        if len(self.pinlines) == 2:
            colors.extend([self.watermark_color_map[c] for c in self.pinlines if c in self.watermark_color_map])
        elif self.pinlines in self.watermark_color_map:
            colors.append(self.watermark_color_map[self.pinlines])

        # Check for valid reference, valid colors, valid text layers group for placement
        if not self.textbox_reference or not colors or not self.text_group:
            return

        # Get watermark custom settings if available
        wm_details = con.watermarks.get(self.layout.watermark, {})

        # Generate the watermark
        wm = psd.import_svg(wm_path)
        psd.frame_layer(wm, self.textbox_reference, smallest=True)
        wm.resize(
            wm_details.get('scale', 80),
            wm_details.get('scale', 80),
            AnchorPosition.MiddleCenter)
        wm.move(self.text_group, ElementPlacement.PlaceAfter)
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

    def create_basic_watermark(self) -> None:
        """Builds a basic land watermark."""

        # Remove text
        self.layout.oracle_text = ''

        # Generate the watermark
        wm = psd.import_svg(osp.join(con.path_img, f"watermarks/basics/{self.layout.pinlines.lower()}.svg"))
        psd.frame_layer(wm, self.textbox_reference, smallest=True)
        wm.resize(80, 80, AnchorPosition.MiddleCenter)
        wm.move(self.text_group, ElementPlacement.PlaceAfter)

        # Add effects
        psd.apply_fx(wm, [
            {
                'type': 'color-overlay',
                'opacity': 100,
                'color': psd.get_color(
                    basic_land_color_map[self.layout.pinlines])
            },
            {
                'type': 'bevel'
            }
        ])

    """
    BORDER
    """

    @cached_property
    def border_color(self) -> str:
        """Use 'black' unless an alternate color and a valid border group is provided."""
        if cfg.border_color != BorderColor.Black and self.border_group:
            return cfg.border_color
        return 'black'

    @try_photoshop
    def color_border(self) -> None:
        """Color this card's border based on given setting."""
        if self.border_color != BorderColor.Black:
            psd.apply_fx(self.border_group, [{
                'type': 'color-overlay',
                'color': psd.get_color(self.border_color)
            }])

    """
    DOCUMENT ACTIONS
    """

    def check_photoshop(self) -> None:
        """Check if Photoshop is responsive to automation."""
        # Ensure the Photoshop Application is responsive
        check = self.app.refresh_app()
        if not isinstance(check, OSError):
            return

        # Connection with Photoshop couldn't be established, try again?
        if not console.await_choice(
            self.event, get_photoshop_error_message(check),
            end="Hit Continue to try again, or Cancel to end the operation.\n\n"
        ):
            # Cancel the operation
            raise OSError(check)
        self.check_photoshop()

    def reset(self) -> None:
        """Reset the document, purge the cache, end await."""
        try:
            if self.docref:
                psd.reset_document()
                self.app.purge(4)
        except PS_EXCEPTIONS:
            pass
        console.end_await()

    def run_tasks(
        self,
        funcs: list[Callable],
        message: str,
        warning: bool = False,
        args: Union[Iterable[Any], None] = None
    ) -> tuple[bool, bool]:
        """
        Run a list of functions, checking for thread cancellation and exceptions on each.
        @param funcs: List of functions to perform.
        @param message: Error message to raise if exception occurs.
        @param warning: Warn the user if True, otherwise raise error.
        @param args: Optional arguments to pass to the func. Empty tuple if not provided.
        @return: True if tasks completed, False if exception occurs or thread is cancelled.
        """
        # No arguments provided?
        if not args:
            args = ()
        # Execute each function
        for func in funcs:
            if self.event.is_set():
                # Thread operation has been cancelled
                return False, False
            try:
                # Run the task
                func(*args)
            except Exception as e:
                # Prompt the user for an error
                if not warning:
                    return False, self.raise_error(message=message, error=e)
                console.log_exception(e)
                self.raise_warning(message)
        return True, True

    def raise_error(self, message: str, error: Optional[Exception] = None) -> bool:
        """
        Raise an error on the console display.
        @param message: Message to be displayed
        @param error: Exception object
        @return: True if continuing, False if cancelling.
        """
        result = console.log_error(
            self.event, self.layout.name, self.layout.template_file,
            f"{msg_error(message)}\nCheck [b]/logs/error.txt[/b] for details.",
            error
        )
        self.reset()
        return result

    @staticmethod
    def raise_warning(message: str, error: Exception = None) -> None:
        """
        Raise a warning on the console display.
        @param message: Message to be displayed
        @param error: Exception object
        @return:
        """
        if error:
            message += "\nCheck [b]/logs/error.txt[/b] for details."
        console.update(msg_warn(message), exception=error)

    """
    HOOKS
    """

    @cached_property
    def hooks(self) -> list[Callable]:
        """List of methods that will be called during the hooks execution step"""
        hooks = []
        if self.is_creature:
            # Creature hook
            hooks.append(self.hook_creature)
        if 'P' in self.layout.mana_cost or '/' in self.layout.mana_cost:
            # Large mana symbol hook
            hooks.append(self.hook_large_mana)
        return hooks

    def hook_creature(self) -> None:
        """Run this if card is a creature."""
        pass

    def hook_large_mana(self) -> None:
        """Run this if card has a large mana symbol."""
        pass

    """
    EXTENDABLE METHODS
    * These methods are called during the execution chain but must be written in the child class.
    """

    def enable_frame_layers(self) -> None:
        """Enable the correct layers for this card's frame."""
        pass

    def basic_text_layers(self) -> None:
        """Establish mana cost, name (scaled to clear mana cost), and typeline (scaled to not overlap set symbol)."""
        pass

    def rules_text_and_pt_layers(self) -> None:
        """Set up the card's rules and power/toughness text based on whether the card is a creature."""
        pass

    def post_text_layers(self) -> None:
        """Write code that will be processed after text layers are executed."""
        pass

    def post_execute(self) -> None:
        """Write code that will be processed after execute completes."""
        pass

    """
    Execution Sequence
    """

    def execute(self) -> bool:
        """
        Perform actions to render the card using this template. Each action is wrapped in an
        exception check and a breakpoint to cancel the thread if a cancellation signal was
        sent by the user. NEVER override this method!
        """
        # Preliminary Photoshop check
        check = self.run_tasks(
            [self.check_photoshop],
            "Error"
        )
        if not all(check):
            return check[1]

        # Load in the PSD template
        check = self.run_tasks(
            [self.app.load],
            "PSD template failed to load!",
            args=[self.layout.template_file]
        )
        if not all(check):
            return check[1]

        # Ensure maximum urgency
        self.docref.info.urgency = Urgency.High

        # Reload the symbol color map
        check = self.run_tasks([ft.symbol_map.load], "Failed to load the symbol color map!")
        if not all(check):
            return check[1]

        # Load in artwork and frame it
        check = self.run_tasks([self.load_artwork], "Unable to load artwork!")
        if not all(check):
            return check[1]

        # Load in Scryfall scan and frame it
        if cfg.import_scryfall_scan:
            check = self.run_tasks(
                [self.paste_scryfall_scan],
                "Couldn't import Scryfall scan, continuing without it!",
                warning=True
            )
            if not all(check):
                return check[1]

        # Add collector info
        check = self.run_tasks([self.collector_info], "Unable to insert collector info!")
        if not all(check):
            return check[1]

        # Add expansion symbol
        check = self.run_tasks([self.expansion_symbol], "Unable to generate expansion symbol!")
        if not all(check):
            return check[1]

        # Add watermark
        is_basic_land = bool('Basic Land' in self.layout.type_line_raw)
        if cfg.enable_watermark and not is_basic_land:
            check = self.run_tasks(
                [self.create_watermark],
                "Unable to generate watermark!")
            if not all(check):
                return check[1]
        elif is_basic_land and self.layout.card_class != con.basic_class:
            check = self.run_tasks(
                [self.create_basic_watermark],
                "Unable to generate basic land watermark!")
            if not all(check):
                return check[1]

        # Select text layers
        check = self.run_tasks(
            [self.basic_text_layers, self.rules_text_and_pt_layers, *self.text_layer_methods],
            "Selecting text layers failed!"
        )
        if not all(check):
            return check[1]

        # Enable layers to build our frame
        check = self.run_tasks(
            [self.color_border, self.enable_frame_layers, *self.frame_layer_methods],
            "Enabling layers failed!")
        if not all(check):
            return check[1]

        # Input and format each text layer
        check = self.run_tasks([layer.execute for layer in self.text if layer], "Formatting text failed!")
        if not all(check):
            return check[1]

        # Specific hooks
        check = self.run_tasks(self.hooks, "Encountered an error during triggered hooks step!")
        if not all(check):
            return check[1]

        # Post text layer execution
        check = self.run_tasks([self.post_text_layers, *self.general_methods], "Post text formatting execution failed!")
        if not all(check):
            return check[1]

        # Manual edit step?
        if cfg.exit_early and not cfg.test_mode:
            console.await_choice(self.event)

        # Save the document
        for (i, art_layer) in enumerate(self.art_layers):
            for other_layer in self.art_layers:
                other_layer.visible = False
            art_layer.visible = True

            output_file_name = self.output_file_name
            if i > 0:
                output_file_name += f" ({i})"

            check = self.run_tasks(
                [self.save_modes.get(cfg.output_filetype, psd.save_document_jpeg)],
                "Error during file save process!",
                args=(output_file_name, self.output_directory)
            )
            if not all(check):
                return check[1]

        # Post execution code
        check = self.run_tasks(
            [self.post_execute],
            "Image saved, but an error was encountered in the post execution step!"
        )
        if not all(check):
            return check[1]

        # Reset document, return success
        if not cfg.test_mode:
            console.update(f"[b]{self.output_file_name}[/b] rendered successfully!")
        self.reset()
        return True


class StarterTemplate (BaseTemplate):
    """
    * Utility Template between Base and Normal
    * Adds basic text layers to the render process.
    * In most cases this is the class you'll extend to when doing more complicated templates which require
    rewriting large portions of the NormalTemplate functionality.
    """

    def basic_text_layers(self) -> None:
        """Add essential text layers: Mana cost, Card name, Typeline."""
        self.text.extend([
            FormattedTextField(
                layer = self.text_layer_mana,
                contents = self.layout.mana_cost
            ),
            ScaledTextField(
                layer = self.text_layer_name,
                contents = self.layout.name,
                reference = self.text_layer_mana
            ),
            ScaledTextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line,
                reference = self.expansion_symbol_layer
            )
        ])


class NormalTemplate (StarterTemplate):
    """
    * Standard M15 Template
    * Adds remaining logic that is required for any normal M15 style card, including Rules and PT text, enabling
    frame layers, enabling the legendary crown, and enabling a hollow crown if needed.
    * In most cases this will be the template you want to extend to, unless creating a template for non-normal
    types like planeswalker, double faced cards, etc. This template contains all the essential bells and whistles
    """

    @cached_property
    def is_fullart(self) -> bool:
        # Colorless cards use Fullart reference
        if self.is_colorless:
            return True
        return False

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:

        # Rules Text and Power / Toughness
        self.text.extend([
            CreatureFormattedTextArea(
                layer = self.text_layer_rules,
                contents = self.layout.oracle_text,
                flavor = self.layout.flavor_text,
                reference = self.textbox_reference,
                divider = self.divider_layer,
                pt_reference = self.pt_adjustment_reference,
                pt_top_reference = self.pt_top_reference,
                centered = self.is_centered
            ) if self.is_creature else FormattedTextArea(
                layer = self.text_layer_rules,
                contents = self.layout.oracle_text,
                flavor = self.layout.flavor_text,
                reference = self.textbox_reference,
                divider = self.divider_layer,
                centered = self.is_centered
            ),
            TextField(
                layer = self.text_layer_pt,
                contents = f"{self.layout.power}/{self.layout.toughness}"
            ) if self.is_creature else None
        ])

    def enable_frame_layers(self) -> None:

        # Twins
        if self.twins_layer:
            self.twins_layer.visible = True

        # PT Box
        if self.is_creature and self.pt_layer:
            self.pt_layer.visible = True

        # Pinlines
        if self.pinlines_layer:
            self.pinlines_layer.visible = True

        # Color Indicator
        if self.is_type_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

        # Background
        if self.background_layer:
            self.background_layer.visible = True

        # Legendary crown
        if self.is_legendary and self.crown_layer:
            self.enable_crown()

    def enable_crown(self) -> None:
        """Enable the Legendary crown."""
        self.crown_layer.visible = True
        if isinstance(self.border_group, LayerSet):
            # Swap Normal border for Legendary border
            psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
            psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True

        # Nyx/Companion: Enable the hollow crown shadow and layer mask on crown, pinlines, and shadows
        if self.is_nyx or self.is_companion:
            self.enable_hollow_crown()

            # Enable companion texture
            if self.is_companion and self.companion_layer:
                self.companion_layer.visible = True

    def enable_hollow_crown(self, shadows: Optional[ArtLayer] = None) -> None:
        """Enable the hollow legendary crown."""
        if not shadows:
            shadows = psd.getLayer(LAYERS.SHADOWS)
        psd.enable_mask(self.crown_layer.parent)
        psd.enable_mask(self.pinlines_layer.parent)
        psd.enable_mask(shadows)
        psd.getLayer(LAYERS.HOLLOW_CROWN_SHADOW).visible = True


class NormalEssentialsTemplate (NormalTemplate):
    """Normal Template without support for Nyx layers, companion layers, hollow crown, etc."""

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False
