"""
* CORE PROXYSHOP TEMPLATES
"""
# Standard Library Imports
import os.path as osp
from contextlib import suppress
from pathlib import Path
from threading import Event
from typing import Optional, Callable, Any, Union, Iterable

# Third Party Imports
from pathvalidate import sanitize_filename
from photoshop.api.application import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api._selection import Selection
from photoshop.api import (
    ElementPlacement,
    SaveOptions,
    SolidColor,
    BlendMode)
from PIL import Image

# Local Imports
from src import APP, CON, CONSOLE, CFG, ENV, PATH
from src.cards import strip_reminder_text
from src.enums.mtg import (
    MagicIcons,
    watermark_color_map,
    basic_watermark_color_map)
import src.helpers as psd
from src.frame_logic import is_multicolor_string
from src.text_layers import (
    TextField,
    ScaledTextField,
    FormattedTextArea,
    FormattedTextField,
    FormattedTextLayer)
from src.enums.adobe import Dimensions
from src.enums.layers import LAYERS
from src.enums.settings import (
    CollectorMode,
    OutputFileType,
    CollectorPromo,
    WatermarkMode,
    BorderColor)
from src.enums.adobe import LayerContainer
from src.helpers.effects import LayerEffects
from src.utils.adobe import PhotoshopHandler, ReferenceLayer
from src.utils.properties import auto_prop_cached
from src.utils.exceptions import PS_EXCEPTIONS, get_photoshop_error_message, try_photoshop
from src.utils.files import get_unique_filename
from src.utils.regex import Reg
from src.api.scryfall import get_card_scan
from src.utils.strings import msg_warn, msg_error

"""
* Template Classes
"""


class BaseTemplate:
    """Master Template for Proxyshop all others should extend to.

    Notes:
        - Contains all the core architecture that is required for any template to function in Proxyshop,
            as well as a ton of optional built-in utility properties and methods for building templates.
    """
    frame_suffix = 'Normal'
    template_suffix = ''

    def __init__(self, layout: Any, **kwargs):

        # Setup manual properties
        self.layout = layout
        self._text = []

    """
    * Enabled Method Lists
    """

    @property
    def pre_render_methods(self) -> list[Callable]:
        """list[Callable]: Methods called before rendering begins.

        Methods:
            `process_layout_data`: Processes layout data before it is used to generate the card.
        """
        return [self.process_layout_data]

    @property
    def frame_layer_methods(self) -> list[Callable]:
        """list[Callable]: Methods called to insert and enable frame layers.

        Methods:
            `color_border`: Changes the border color if required and supported by the template.
            `enable_frame_layers`:
        """
        return [self.color_border, self.enable_frame_layers]

    @property
    def text_layer_methods(self) -> list[Callable]:
        """list[Callable]: Methods called to insert and format text layers."""
        return [
            self.collector_info,
            self.basic_text_layers,
            self.rules_text_and_pt_layers
        ]

    @property
    def post_text_methods(self) -> list[Callable]:
        """list[Callable]: Methods called after text is inserted and formatted."""
        return []

    @property
    def post_save_methods(self) -> list[Callable]:
        """list[Callable]: Methods called after the rendered image is saved."""
        return []

    """
    * Hook Method List
    """

    @property
    def hooks(self) -> list[Callable]:
        """list[Callable]: List of methods that will be called during the hooks execution step"""
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
    * App Properties
    """

    @auto_prop_cached
    def event(self) -> Event:
        """Event: Threading Event used to signal thread cancellation."""
        return Event()

    @auto_prop_cached
    def console(self) -> type[CONSOLE]:
        """type[CONSOLE]: Console output object used to communicate with the user."""
        return CONSOLE

    @property
    def app(self) -> PhotoshopHandler:
        """PhotoshopHandler: Photoshop Application object used to communicate with Photoshop."""
        return APP

    @auto_prop_cached
    def docref(self) -> Optional[Document]:
        """Optional[Document]: This template's document open in Photoshop."""
        if doc := psd.get_document(osp.basename(self.layout.template_file)):
            return doc
        return

    @auto_prop_cached
    def doc_selection(self) -> Selection:
        """Selection: Active document selection object."""
        return self.docref.selection

    @property
    def active_layer(self) -> Union[ArtLayer, LayerSet]:
        """Union[ArtLayer, LayerSet]: Get the currently active layer in the Photoshop document."""
        return self.docref.activeLayer

    @active_layer.setter
    def active_layer(self, value: Union[ArtLayer, LayerSet]):
        """Set the currently active layer in the Photoshop document.

        Args:
            value: An ArtLayer or LayerSet to make active.
        """
        self.docref.activeLayer = value

    """
    * SolidColor objects
    """

    @auto_prop_cached
    def RGB_BLACK(self) -> SolidColor:
        """SolidColor: A solid color object with RGB [0, 0, 0]."""
        return psd.rgb_black()

    @auto_prop_cached
    def RGB_WHITE(self) -> SolidColor:
        """SolidColor: A solid color object with RGB [255, 255, 255]."""
        return psd.rgb_white()

    """
    * File Saving
    """

    @auto_prop_cached
    def save_mode(self) -> Callable:
        """Callable: Function called to save the rendered image."""
        if CFG.output_file_type == OutputFileType.PNG:
            return psd.save_document_png
        if CFG.output_file_type == OutputFileType.PSD:
            return psd.save_document_psd
        return psd.save_document_jpeg

    @auto_prop_cached
    def output_directory(self) -> Path:
        """PathL Directory to save the rendered image."""
        if ENV.TEST_MODE:
            path = PATH.OUT / self.__class__.__name__
            path.mkdir(mode=777, parents=True, exist_ok=True)
            return path
        return PATH.OUT

    @auto_prop_cached
    def output_file_name(self) -> Path:
        """Path: The formatted filename for the rendered image."""
        name, tag_map = CFG.output_file_name, {
            '#name': self.layout.name_raw,
            '#artist': self.layout.artist,
            '#set': self.layout.set,
            '#num': str(self.layout.collector_number),
            '#frame': self.frame_suffix,
            '#suffix': self.template_suffix,
            '#creator': self.layout.creator,
            '#lang': self.layout.lang
        }

        # Replace conditional tags
        for n in Reg.PATH_CONDITION.findall(name):
            case_new, case = n, f'<{n}>'
            for tag, val in tag_map.items():
                if tag in case and not val:
                    name, case_new = name.replace(case, ''), ''
                    break
                if tag in case:
                    case_new = case_new.replace(tag, val)
            if case_new:
                name = name.replace(case, case_new)

        # Replace other tags
        for tag, value in tag_map.items():
            if value:
                name = name.replace(tag, value)
        path = Path(
            self.output_directory,
            sanitize_filename(name)
        ).with_suffix(f'.{CFG.output_file_type}')

        # Are we overwriting duplicate names?
        if not CFG.overwrite_duplicate:
            path = get_unique_filename(path)
        return path

    """
    * Cosmetic Extendable Checks
    """

    @property
    def is_hollow_crown(self) -> bool:
        """bool: Governs whether a hollow crown should be rendered."""
        return False

    @property
    def is_fullart(self) -> bool:
        """bool: Returns True if art must be treated as Fullart."""
        return False

    """
    * Boolean Checks
    """

    @property
    def is_creature(self) -> bool:
        """bool: Governs whether to add PT box and use Creature rules text."""
        return self.layout.is_creature

    @property
    def is_legendary(self) -> bool:
        """bool: Enables the legendary crown step."""
        return self.layout.is_legendary

    @property
    def is_land(self) -> bool:
        """bool: Governs whether to use normal or land pinlines group."""
        return self.layout.is_land

    @property
    def is_artifact(self) -> bool:
        """bool: Utility definition for custom templates. Returns True if card is an Artifact."""
        return self.layout.is_artifact

    @property
    def is_vehicle(self) -> bool:
        """bool: Utility definition for custom templates. Returns True if card is a Vehicle."""
        return self.layout.is_vehicle

    @property
    def is_hybrid(self) -> bool:
        """bool: Utility definition for custom templates. Returns True if card is hybrid color."""
        return self.layout.is_hybrid

    @property
    def is_colorless(self) -> bool:
        """bool: Enforces fullart framing for card art on many templates."""
        return self.layout.is_colorless

    @property
    def is_front(self) -> bool:
        """bool: Governs render behavior on MDFC and Transform cards."""
        return self.layout.is_front

    @property
    def is_transform(self) -> bool:
        """bool: Governs behavior on double faced card varieties."""
        return self.layout.is_transform

    @property
    def is_mdfc(self) -> bool:
        """bool: Governs behavior on double faced card varieties."""
        return self.layout.is_mdfc

    @property
    def is_companion(self) -> bool:
        """bool: Enables companion cosmetic elements."""
        return self.layout.is_companion

    @property
    def is_nyx(self) -> bool:
        """bool: Enables nyxtouched cosmetic elements."""
        return self.layout.is_nyx

    @property
    def is_snow(self) -> bool:
        """bool: Enables snow cosmetic elements."""
        return self.layout.is_snow

    @property
    def is_miracle(self) -> bool:
        """bool: Enables miracle cosmetic elements."""
        return self.layout.is_miracle

    @property
    def is_token(self) -> bool:
        """bool: Enables token cosmetic elements."""
        return self.layout.is_token

    @property
    def is_emblem(self) -> bool:
        """bool: Enables emblem cosmetic elements."""
        return self.layout.is_emblem

    """
    * Cached Properties
    * Calculated in BaseTemplate class
    """

    @auto_prop_cached
    def is_basic_land(self) -> bool:
        """bool: Governs Basic Land watermark and other Basic Land behavior."""
        return self.layout.is_basic_land

    @auto_prop_cached
    def is_centered(self) -> bool:
        """bool: Governs whether rules text is centered."""
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text)

    @auto_prop_cached
    def is_name_shifted(self) -> bool:
        """bool: Governs whether to use the shifted name text layer."""
        return bool(self.is_transform or self.is_mdfc)

    @auto_prop_cached
    def is_type_shifted(self) -> bool:
        """bool: Governs whether to use the shifted typeline text layer."""
        return bool(self.layout.color_indicator)

    @auto_prop_cached
    def is_flipside_creature(self) -> bool:
        """bool: Governs double faced cards where opposing side is a creature."""
        return bool(self.layout.other_face_power and self.layout.other_face_toughness)

    @auto_prop_cached
    def is_art_vertical(self) -> bool:
        """bool: Returns True if art provided is vertically oriented, False if it is horizontal."""
        with Image.open(self.layout.art_file) as image:
            width, height = image.size
        if height > (width * 1.1):
            # Vertical orientation
            return True
        # Horizontal orientation
        return False

    @auto_prop_cached
    def is_content_aware_enabled(self) -> bool:
        """bool: Governs whether content aware fill should be performed during the art loading step."""
        if self.is_fullart and all([n not in self.art_reference.name for n in ['Full', 'Borderless']]):
            # By default, fill when we want a fullart image but didn't receive one
            return True
        return False

    @auto_prop_cached
    def is_collector_promo(self) -> bool:
        """bool: Governs whether to use promo star in collector info."""
        if CFG.collector_promo == CollectorPromo.Always:
            return True
        if self.layout.is_promo and CFG.collector_promo == CollectorPromo.Automatic:
            return True
        return False

    """
    * Frame Details
    """

    @property
    def art_frame(self) -> str:
        """str: Normal frame to use for positioning the art."""
        return LAYERS.ART_FRAME

    @property
    def art_frame_vertical(self) -> str:
        """str: Vertical orientation frame to use for positioning the art."""
        return LAYERS.FULL_ART_FRAME

    @auto_prop_cached
    def twins(self) -> str:
        """str: Name of the Twins layer, also usually the PT layer."""
        return self.layout.twins

    @auto_prop_cached
    def pinlines(self) -> str:
        """str: Name of the Pinlines layer."""
        return self.layout.pinlines

    @auto_prop_cached
    def identity(self) -> str:
        """str: Color identity of the card, e.g. WU."""
        return self.layout.identity

    @auto_prop_cached
    def background(self) -> str:
        """str: Name of the Background layer."""
        if not self.is_vehicle and self.layout.background == LAYERS.VEHICLE:
            return LAYERS.ARTIFACT
        return self.layout.background

    @auto_prop_cached
    def color_limit(self) -> int:
        """int: Number of colors where frame elements will no longer split (becomes gold)."""
        return 3

    """
    * Layer Groups
    """

    @auto_prop_cached
    def legal_group(self) -> LayerSet:
        """LayerSet: Group containing artist credit, collector info, and other legal details."""
        return self.docref.layerSets[LAYERS.LEGAL]

    @auto_prop_cached
    def border_group(self) -> Optional[Union[LayerSet, ArtLayer]]:
        """Optional[Union[LayerSet, ArtLayer]]: Group, or sometimes a layer, containing the card border."""
        if group := psd.getLayerSet(LAYERS.BORDER, self.docref):
            return group
        if layer := psd.getLayer(LAYERS.BORDER, self.docref):
            return layer
        return

    @auto_prop_cached
    def text_group(self) -> Optional[LayerSet]:
        """Optional[LayerSet]: Text and icon group, contains rules text and necessary symbols."""
        with suppress(Exception):
            return self.docref.layerSets[LAYERS.TEXT_AND_ICONS]
        return self.docref

    @auto_prop_cached
    def dfc_group(self) -> Optional[LayerSet]:
        """Optional[LayerSet]: Group containing double face elements."""
        face = LAYERS.FRONT if self.is_front else LAYERS.BACK
        if self.is_transform:
            return psd.getLayerSet(face, [self.text_group, LAYERS.TRANSFORM])
        if self.is_mdfc:
            return psd.getLayerSet(f'{LAYERS.MDFC} {face}', self.text_group)
        return

    @auto_prop_cached
    def mask_group(self) -> Optional[LayerSet]:
        """LayerSet: Group containing masks used to blend and adjust various layers."""
        with suppress(Exception):
            return self.docref.layerSets[LAYERS.MASKS]
        return

    """
    * Text Layers
    """

    @auto_prop_cached
    def text_layer_creator(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Proxy creator name text layer."""
        return psd.getLayer(LAYERS.CREATOR, self.legal_group)

    @auto_prop_cached
    def text_layer_name(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Card name text layer."""
        if self.is_name_shifted:
            psd.getLayer(LAYERS.NAME, self.text_group).visible = False
            name = psd.getLayer(LAYERS.NAME_SHIFT, self.text_group)
            name.visible = True
            return name
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @auto_prop_cached
    def text_layer_mana(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Card mana cost text layer."""
        return psd.getLayer(LAYERS.MANA_COST, self.text_group)

    @auto_prop_cached
    def text_layer_type(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Card typeline text layer."""
        if self.is_type_shifted:
            psd.getLayer(LAYERS.TYPE_LINE, self.text_group).visible = False
            typeline = psd.getLayer(LAYERS.TYPE_LINE_SHIFT, self.text_group)
            typeline.visible = True
            return typeline
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_group)

    @auto_prop_cached
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Card rules text layer."""
        if self.is_creature:
            return psd.getLayer(LAYERS.RULES_TEXT_CREATURE, self.text_group)
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_group)

    @auto_prop_cached
    def text_layer_pt(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Card power and toughness text layer."""
        return psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_group)

    @auto_prop_cached
    def divider_layer(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Divider layer between rules text and flavor text."""
        if self.is_transform and self.is_front and self.is_flipside_creature:
            if TF_DIVIDER := psd.getLayer('Divider TF', self.text_group):
                return TF_DIVIDER
        return psd.getLayer(LAYERS.DIVIDER, self.text_group)

    """
    * Frame Layers
    """

    @property
    def art_layer(self) -> ArtLayer:
        """ArtLayer: Layer the art image is imported into."""
        return psd.getLayer(LAYERS.DEFAULT, self.docref)

    @auto_prop_cached
    def twins_layer(self) -> Optional[ArtLayer]:
        """Name and title boxes layer."""
        return psd.getLayer(self.twins, LAYERS.TWINS)

    @auto_prop_cached
    def pinlines_layer(self) -> Optional[ArtLayer]:
        """Pinlines (and textbox) layer."""
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    @auto_prop_cached
    def background_layer(self) -> Optional[ArtLayer]:
        """Background texture layer."""
        # Try finding Vehicle background
        if self.is_vehicle and self.background == LAYERS.VEHICLE:
            return psd.getLayer(
                LAYERS.VEHICLE, LAYERS.BACKGROUND
            ) or psd.getLayer(
                LAYERS.ARTIFACT, LAYERS.BACKGROUND)
        # All other backgrounds
        return psd.getLayer(self.background, LAYERS.BACKGROUND)

    @auto_prop_cached
    def pt_layer(self) -> Optional[ArtLayer]:
        """Power and toughness box layer."""
        # Test for Vehicle PT support
        if self.is_vehicle and self.background == LAYERS.VEHICLE:
            if layer := psd.getLayer(LAYERS.VEHICLE, LAYERS.PT_BOX):
                # Change font to white for Vehicle PT box
                self.text_layer_pt.textItem.color = self.RGB_WHITE
                return layer
        return psd.getLayer(self.twins, LAYERS.PT_BOX)

    @auto_prop_cached
    def crown_layer(self) -> Optional[ArtLayer]:
        """Legendary crown layer."""
        return psd.getLayer(self.pinlines, LAYERS.LEGENDARY_CROWN)

    @auto_prop_cached
    def crown_shadow_layer(self) -> Union[ArtLayer, LayerSet, None]:
        """Legendary crown hollow shadow layer."""
        return psd.getLayer(LAYERS.HOLLOW_CROWN_SHADOW, self.docref)

    @auto_prop_cached
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        """Color indicator icon layer."""
        if self.layout.color_indicator:
            return psd.getLayer(self.layout.color_indicator, LAYERS.COLOR_INDICATOR)
        return

    @auto_prop_cached
    def transform_icon_layer(self) -> Optional[ArtLayer]:
        """Optional[ArtLayer]: Transform icon layer."""
        return psd.getLayer(self.layout.transform_icon, self.dfc_group)

    """
    * Reference Layers
    """

    @auto_prop_cached
    def art_reference(self) -> ReferenceLayer:
        """ReferenceLayer: Reference frame used to scale and position the art layer."""
        # Check if art is vertically oriented, or forced vertical, and for valid vertical frame
        if self.is_art_vertical or (self.is_fullart and CFG.vertical_fullart):
            if layer := psd.get_reference_layer(self.art_frame_vertical):
                return layer
        # Check for normal art frame
        return psd.get_reference_layer(self.art_frame) or psd.get_reference_layer(LAYERS.ART_FRAME)

    @auto_prop_cached
    def name_reference(self) -> Optional[ArtLayer]:
        """ArtLayer: By default, name uses Mana Cost as a reference to check collision against."""
        if self.is_basic_land:
            return
        return self.text_layer_mana

    @auto_prop_cached
    def type_reference(self) -> Optional[ArtLayer]:
        """ArtLayer: By default, typeline uses the expansion symbol to check collision against,
        otherwise fallback to the expansion symbols reference layer."""
        if self.is_basic_land:
            return
        return self.expansion_symbol_layer or self.expansion_reference

    @auto_prop_cached
    def textbox_reference(self) -> ReferenceLayer:
        """ReferenceLayer: Reference frame used to scale and position the rules text layer."""
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.text_group)

    @auto_prop_cached
    def pt_reference(self) -> Optional[ReferenceLayer]:
        """ArtLayer: Reference used to check rules text overlap with the PT Box."""
        if not self.is_creature:
            return
        return psd.get_reference_layer(LAYERS.PT_REFERENCE, self.text_group)

    """
    * Blending Masks
    """

    @auto_prop_cached
    def mask_layers(self) -> list[ArtLayer]:
        """List of layers containing masks used to blend multicolored layers."""
        if not self.mask_group:
            return []
        if mask := psd.getLayer(LAYERS.HALF, self.mask_group):
            return [mask]
        return []

    """
    * Processing Layout Data
    """

    def process_layout_data(self) -> None:
        """Performs any required pre-processing on the provided layout data."""

        # Strip flavor text, string or list
        if CFG.remove_flavor:
            self.layout.flavor_text = "" if isinstance(
                self.layout.flavor_text, str
            ) else ['' for _ in self.layout.flavor_text]

        # Strip reminder text, string or list
        if CFG.remove_reminder:
            self.layout.oracle_text = strip_reminder_text(
                self.layout.oracle_text
            ) if isinstance(
                self.layout.oracle_text, str
            ) else [strip_reminder_text(n) for n in self.layout.oracle_text]

    """
    * Loading Artwork
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
        """Loads the specified art file into the specified layer."""

        # Check for fullart test image
        if ENV.TEST_MODE and self.is_fullart:
            self.layout.art_file = PATH.SRC_IMG / "test-fa.jpg"

        # Paste the file into the art
        self.active_layer = self.art_layer
        if self.art_action:
            psd.paste_file(
                layer=self.art_layer,
                path=self.layout.art_file,
                action=self.art_action,
                action_args=self.art_action_args,
                docref=self.docref)
        else:
            psd.import_art(
                layer=self.art_layer,
                path=self.layout.art_file,
                docref=self.docref)

        # Frame the artwork
        psd.frame_layer(self.active_layer, self.art_reference)

        # Perform content aware fill if needed
        if self.is_content_aware_enabled:

            # Perform a generative fill
            if CFG.generative_fill:
                docref = psd.generative_fill_edges(
                    layer=self.art_layer,
                    feather=CFG.feathered_fill,
                    close_doc=not CFG.select_variation,
                    docref=self.docref)
                if docref:
                    self.console.await_choice(
                        self.event, msg="Select a Generative Fill variation, then click Continue ...")
                    docref.close(SaveOptions.SaveChanges)
                return

            # Perform a content aware fill
            psd.content_aware_fill_edges(self.art_layer, CFG.feathered_fill)

    def paste_scryfall_scan(self, rotate: bool = False, visible: bool = True) -> Optional[ArtLayer]:
        """Downloads the card's scryfall scan, pastes it into the document next to the active layer,
        and frames it to fill the given reference layer.

        Args:
            rotate: Will rotate the card horizontally if True, useful for Planar cards.
            visible: Whether to leave the layer visible or hide it.

        Returns:
            ArtLayer if Scryfall scan was imported, otherwise None.
        """
        # Try to grab the scan from Scryfall
        if not self.layout.scryfall_scan:
            return
        scryfall_scan = get_card_scan(self.layout.scryfall_scan)
        if not scryfall_scan:
            return

        # Paste the scan into a new layer
        if layer := psd.import_art_into_new_layer(
                path=scryfall_scan,
                name="Scryfall Reference",
                docref=self.docref
        ):
            # Rotate the layer if necessary
            if rotate:
                layer.rotate(90)

            # Frame the layer and position it above the art layer
            bleed = int(self.docref.resolution / 8)
            dims = psd.get_dimensions_from_bounds(
                (bleed, bleed, self.docref.width - bleed, self.docref.height - bleed))
            psd.frame_layer(layer, dims)
            layer.move(self.art_layer, ElementPlacement.PlaceBefore)
            layer.visible = visible
            return layer

    """
    * Collector Info
    """

    def collector_info(self) -> None:
        """Format and add the collector info at the bottom."""

        # Ignore this step if legal layer not present
        if not self.legal_group:
            return

        # If creator is specified add the text
        if self.layout.creator and self.text_layer_creator:
            self.text_layer_creator.textItem.contents = self.layout.creator

        # Which collector info mode?
        if CFG.collector_mode in [
            CollectorMode.Default, CollectorMode.Modern
        ] and self.layout.collector_data:
            return self.collector_info_authentic()
        elif CFG.collector_mode == CollectorMode.ArtistOnly:
            return self.collector_info_artist_only()
        return self.collector_info_basic()

    def collector_info_basic(self) -> None:
        """Called to generate basic collector info."""

        # Collector layers
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        set_layer = psd.getLayer(LAYERS.SET, self.legal_group)
        set_TI = set_layer.textItem

        # Correct color for non-black border
        if self.border_color != BorderColor.Black:
            set_TI.color = self.RGB_BLACK
            artist_layer.textItem.color = self.RGB_BLACK

        # Fill optional collector star
        if self.is_collector_promo:
            psd.replace_text(set_layer, "•", MagicIcons.COLLECTOR_STAR)

        # Fill language, artist, and set
        if self.layout.lang != "en":
            psd.replace_text(set_layer, "EN", self.layout.lang.upper())
        psd.replace_text(artist_layer, "Artist", self.layout.artist)
        set_TI.contents = self.layout.set + set_TI.contents

    def collector_info_authentic(self) -> None:
        """Called to generate realistic collector info."""

        # Hide basic layers
        psd.getLayer(LAYERS.ARTIST, self.legal_group).visible = False
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Get the collector layers
        group = psd.getLayerSet(LAYERS.COLLECTOR, self.legal_group)
        top = psd.getLayer(LAYERS.TOP, group).textItem
        bottom = psd.getLayer(LAYERS.BOTTOM, group)
        group.visible = True

        # Correct color for non-black border
        if self.border_color != 'black':
            top.color = self.RGB_BLACK
            bottom.textItem.color = self.RGB_BLACK

        # Fill in language if needed
        if self.layout.lang != "en":
            psd.replace_text(bottom, "EN", self.layout.lang.upper())

        # Fill optional collector star
        if self.is_collector_promo:
            psd.replace_text(bottom, "•", MagicIcons.COLLECTOR_STAR)

        # Apply the collector info
        top.contents = self.layout.collector_data
        psd.replace_text(bottom, "SET", self.layout.set)
        psd.replace_text(bottom, "Artist", self.layout.artist)

    def collector_info_artist_only(self) -> None:
        """Called to generate 'Artist Only' collector info."""

        # Collector layers
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        psd.getLayer(LAYERS.SET, self.legal_group).visible = False

        # Correct color for non-black border
        if self.border_color != BorderColor.Black:
            artist_layer.textItem.color = self.RGB_BLACK

        # Insert artist name
        psd.replace_text(artist_layer, "Artist", self.layout.artist)

    """
    * Expansion Symbol
    """

    @property
    def expansion_symbol_alignments(self) -> list[Dimensions]:
        """Alignments used for positioning the expansion symbol"""
        return [Dimensions.Right, Dimensions.CenterY]

    @auto_prop_cached
    def expansion_symbol_layer(self) -> Optional[ArtLayer]:
        """Expansion symbol layer, value set during the `load_expansion_symbol` method."""
        return

    @auto_prop_cached
    def expansion_reference(self) -> Optional[ArtLayer]:
        """Expansion symbol reference layer"""
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, self.text_group)

    def load_expansion_symbol(self) -> None:
        """Imports and positions the expansion symbol SVG image."""

        # Check for expansion symbol disabled
        if not CFG.symbol_enabled or not self.expansion_reference:
            return
        if not self.layout.symbol_svg:
            return self.log("Expansion symbol disabled, SVG file not found.")

        # Try to import the expansion symbol
        try:

            # Import and place the symbol
            svg = psd.import_svg(
                path=str(self.layout.symbol_svg),
                ref=self.expansion_reference,
                placement=ElementPlacement.PlaceBefore,
                docref=self.docref)

            # Frame the symbol
            psd.frame_layer_by_height(
                layer=svg,
                ref=self.expansion_reference,
                alignments=self.expansion_symbol_alignments)

            # Rename and reset property
            svg.name = 'Expansion Symbol'
            self.expansion_symbol_layer = svg

        except Exception as e:
            return self.log('Expansion symbol disabled due to an error.', e)

    """
    * Watermark
    """

    @auto_prop_cached
    def watermark_blend_mode(self) -> BlendMode:
        """Blend mode to use on the Watermark layer."""
        return BlendMode.ColorBurn

    @auto_prop_cached
    def watermark_color_map(self) -> dict:
        """Maps color values for Watermark."""
        return watermark_color_map.copy()

    @auto_prop_cached
    def watermark_colors(self) -> list[SolidColor]:
        """Colors to use for the Watermark."""
        if self.pinlines in self.watermark_color_map:
            return [self.watermark_color_map.get(self.pinlines, self.RGB_WHITE)]
        elif len(self.identity) < 3:
            return [self.watermark_color_map.get(c, self.RGB_WHITE) for c in self.identity]
        return []

    @auto_prop_cached
    def watermark_fx(self) -> list[LayerEffects]:
        """Defines the layer effects to use for the Watermark."""
        if len(self.watermark_colors) == 1:
            return [{
                'type': 'color-overlay', 'opacity': 100,
                'color': self.watermark_colors[0]
            }]
        if len(self.watermark_colors) == 2:
            return [{
                'type': 'gradient-overlay', 'rotation': 0,
                'colors': [
                    {'color': self.watermark_colors[0], 'location': 0, 'midpoint': 50},
                    {'color': self.watermark_colors[1], 'location': 4096, 'midpoint': 50}
                ]
            }]
        return []

    def create_watermark(self) -> None:
        """Builds the watermark."""
        # Required values to generate a Watermark
        if not all([
            self.layout.watermark_svg,
            self.layout.watermark,
            self.textbox_reference,
            self.watermark_colors,
            self.text_group
        ]):
            return

        # Get watermark custom settings if available
        wm_details = CON.watermarks.get(self.layout.watermark, {})

        # Import and frame the watermark
        wm = psd.import_svg(
            path=self.layout.watermark_svg,
            ref=self.text_group,
            placement=ElementPlacement.PlaceAfter,
            docref=self.docref)
        psd.frame_layer(
            layer=wm,
            ref=self.textbox_reference.dims,
            smallest=True,
            scale=wm_details.get('scale', 80))

        # Apply opacity, blending, and effects
        wm.opacity = wm_details.get('opacity', CFG.watermark_opacity)
        wm.blendMode = self.watermark_blend_mode
        psd.apply_fx(wm, self.watermark_fx)

    """
    * Basic Land Watermark
    """

    @auto_prop_cached
    def basic_watermark_color_map(self) -> dict:
        """Maps color values for Basic Land Watermark."""
        return basic_watermark_color_map.copy()

    @auto_prop_cached
    def basic_watermark_color(self) -> SolidColor:
        """Color to use for the Basic Land Watermark."""
        return psd.get_color(self.basic_watermark_color_map[self.layout.pinlines])

    @auto_prop_cached
    def basic_watermark_fx(self) -> list[LayerEffects]:
        """Defines the layer effects used on the Basic Land Watermark."""
        return [
            {
                'type': 'color-overlay', 'opacity': 100, 'color': self.basic_watermark_color},
            {
                'type': 'bevel', 'size': 28, 'softness': 14, 'depth': 100,
                'shadow_opacity': 72, 'highlight_opacity': 70,
                'rotation': 45, 'altitude': 22
            }
        ]

    def create_basic_watermark(self) -> None:
        """Builds a basic land watermark."""

        # Generate the watermark
        wm = psd.import_svg(
            path=self.layout.watermark_basic,
            ref=self.text_group,
            placement=ElementPlacement.PlaceAfter,
            docref=self.docref)
        psd.frame_layer_by_height(
            layer=wm,
            ref=self.textbox_reference.dims,
            scale=75)

        # Add effects
        psd.apply_fx(wm, self.basic_watermark_fx)

        # Add snow effects
        if self.is_snow:
            self.add_basic_watermark_snow_effects(wm)

        # Remove rules text step
        self.rules_text_and_pt_layers = lambda: None
        self.layout.oracle_text = ''
        self.layout.flavor_text = ''

    def add_basic_watermark_snow_effects(self, wm: ArtLayer):
        """Adds optional snow effects for 'Snow' Basic Land watermarks.

        Args:
            wm: ArtLayer containing the Basic Land Watermark.
        """
        pass

    """
    * Border
    """

    @auto_prop_cached
    def border_color(self) -> str:
        """Use 'black' unless an alternate color and a valid border group is provided."""
        if CFG.border_color != BorderColor.Black and self.border_group:
            return CFG.border_color
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
    * Formatted Text Layers
    """

    @property
    def text(self) -> list[FormattedTextLayer]:
        """List of text layer objects to execute."""
        return self._text

    @text.setter
    def text(self, value):
        """Add text layer to execute."""
        self._text = value

    def format_text_layers(self) -> None:
        """Validate and execute each formatted text layer."""
        for t in self.text:
            # Check for cancelled thread each iteration
            if self.event.is_set():
                return
            # Validate and execute
            if t and t.validate():
                t.execute()

    """
    * Document Actions
    """

    def check_photoshop(self) -> None:
        """Check if Photoshop is responsive to automation."""
        # Ensure the Photoshop Application is responsive
        check = self.app.refresh_app()
        if not isinstance(check, OSError):
            return

        # Connection with Photoshop couldn't be established, try again?
        if not self.console.await_choice(
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
                psd.reset_document(self.docref)
        except PS_EXCEPTIONS:
            pass
        self.console.end_await()

    """
    * Tasks and Logging
    """

    def log(self, text: str, e: Union[Exception] = None) -> None:
        """Writes a message to console if test mode isn't enabled, logs an exception if provided.

        Args:
            text: Message to write to console.
            e: Exception to log if provided.
        """
        if e:
            self.console.log_exception(e)
        if not ENV.TEST_MODE:
            self.console.update(text)

    def run_tasks(
            self,
            funcs: list[Callable],
            message: str,
            warning: bool = False,
            args: Union[Iterable[Any], None] = None,
            kwargs: Optional[dict] = None,
    ) -> bool:
        """Run a list of functions, checking for thread cancellation and exceptions on each.

        Args:
            funcs: List of functions to perform.
            message: Error message to raise if exception occurs.
            warning: Warn the user if True, otherwise raise error.
            args: Optional arguments to pass to the func. Empty tuple if not provided.
            kwargs: Optional keyword arguments to pass to the func. Empty dict if not provided.

        Returns:
            True if tasks completed, False if exception occurs or thread is cancelled.
        """

        # Default args and kwargs
        args = args or ()
        kwargs = kwargs or {}

        # Execute each function
        for func in funcs:
            if self.event.is_set():
                # Thread operation has been cancelled
                return False
            try:
                # Run the task
                func(*args, **kwargs)
            except Exception as e:
                # Raise error or warning
                if not warning:
                    self.raise_error(message=message, error=e)
                    return False
                self.raise_warning(message=message, error=e)
        return True

    def raise_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Raise an error on the console display.

        Args:
            message: Message to be displayed
            error: Exception object
        """
        self.console.log_error(
            thr=self.event,
            card=self.layout.name,
            template=self.layout.template_file,
            msg=f'{msg_error(message)}\n'
                f'Check [b]/logs/error.txt[/b] for details.',
            e=error)
        self.reset()

    def raise_warning(self, message: str, error: Exception = None) -> None:
        """Raise a warning on the console display.

        Args:
            message: Message to be displayed.
            error: Exception object.
        """
        if error:
            self.console.log_exception(error)
            message += "\nCheck [b]/logs/error.txt[/b] for details."
        self.console.update(msg_warn(message), exception=error)

    """
    * Layer Generator Utilities
    * These methods create layers dynamically by blending rasterized layers or solid color
    adjustment layers together using masks.
    """

    def create_blended_layer(
            self,
            group: LayerSet,
            colors: Union[None, str, list[str]] = None,
            masks: Optional[list[ArtLayer]] = None,
            **kwargs
    ):
        """Either enable a single frame layer or create a multicolor layer using a gradient mask.

        Args:
            group: Group to look for the color layers within.
            colors: Color layers to look for.
            masks: Masks to use for blending the layers.
        """
        # Ensure masks is a list
        masks = masks or []

        # Establish our colors
        colors = colors or self.identity or self.pinlines
        if isinstance(colors, str) and not is_multicolor_string(colors):
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
            if 'blend_mode' in kwargs:
                layer.blendMode = kwargs['blend_mode']
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
            masks: Optional[list[Union[ArtLayer, LayerSet]]] = None,
            **kwargs
    ) -> None:
        """Either enable a single frame layer or create a multicolor layer using a gradient mask.

        Args:
            group: Group to look for the color layers within.
            colors: Color layers to look for.
            masks: Masks to use for blending the layers.

        Keyword Args:
            blend_mode (BlendMode): Sets the blend mode of the generated solid color layers.
        """
        # Ensure masks is a list
        masks = masks or []

        # Enable each layer color
        layers: list[ArtLayer] = []
        for i, color in enumerate(colors):
            layer = psd.smart_layer(psd.create_color_layer(color, group))
            if 'blend_mode' in kwargs:
                layer.blendMode = kwargs['blend_mode']

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers and len(masks) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(masks[i - 1], layers[i - 1])
            layers.append(layer)

    def generate_layer(
            self, group: Union[ArtLayer, LayerSet],
            colors: Union[list[list[int]], list[int], list[dict], list[str], str],
            masks: Optional[list[ArtLayer]] = None,
            **kwargs
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
                    docref=self.docref,
                    **kwargs)
            # Blended texture layers
            return self.create_blended_layer(
                group=group,
                colors=colors,
                masks=masks,
                **kwargs)
        if isinstance(colors, list):
            if all(isinstance(c, str) for c in colors):
                # Hex colors
                if colors[0].startswith('#'):
                    return psd.create_color_layer(
                        color=colors,
                        layer=group,
                        docref=self.docref,
                        **kwargs)
                # Blended texture layers
                return self.create_blended_layer(
                    group=group,
                    colors=colors,
                    masks=masks,
                    **kwargs)
            if all(isinstance(c, int) for c in colors):
                # RGB/CMYK adjustment layer
                return psd.create_color_layer(
                    color=colors,
                    layer=group,
                    docref=self.docref,
                    **kwargs)
            if all(isinstance(c, dict) for c in colors):
                # Gradient adjustment layer
                return psd.create_gradient_layer(
                    colors=colors,
                    layer=group,
                    docref=self.docref,
                    **kwargs)
            if all(isinstance(c, list) for c in colors):
                # Blended RGB/CMYK adjustment layers
                return self.create_blended_solid_color(
                    group=group,
                    colors=colors,
                    masks=masks,
                    **kwargs)

        # Failed to match a recognized color notation
        if group:
            self.log(f"Couldn't generate frame element: '{group.name}'")

    """
    * Extendable Methods
    * These methods are called during the execution chain but must be written in the child class.
    """

    def enable_frame_layers(self) -> None:
        """Enable the correct layers for this card's frame."""
        pass

    def enable_crown(self) -> None:
        """Enable layers required by the Legendary Crown."""
        pass

    def enable_hollow_crown(self) -> None:
        """Enable layers required by the Hollow Legendary Crown modification"""
        pass

    def basic_text_layers(self) -> None:
        """Establish mana cost, name (scaled to clear mana cost), and typeline (scaled to not overlap set symbol)."""
        pass

    def rules_text_and_pt_layers(self) -> None:
        """Set up the card's rules and power/toughness text based on whether the card is a creature."""
        pass

    """
    * Execution Sequence
    """

    def execute(self) -> bool:
        """Perform actions to render the card using this template.

        Notes:
            - Each action is wrapped in an exception check and breakpoint to cancel the thread
                if a cancellation signal was sent by the user.
            - Never override this method!
        """
        # Preliminary Photoshop check
        if not self.run_tasks(
                funcs=[self.check_photoshop],
                message="Unable to reach Photoshop!"
        ):
            return False

        # Pre-process layout data
        if not self.run_tasks(
                funcs=self.pre_render_methods,
                message="Pre-processing layout data failed!"
        ):
            return False

        # Load in the PSD template
        if not self.run_tasks(
                funcs=[self.app.load],
                message="PSD template failed to load!",
                args=[str(self.layout.template_file)]
        ):
            return False

        # Load in artwork and frame it
        if not self.run_tasks(
                funcs=[self.load_artwork],
                message="Unable to load artwork!"
        ):
            return False

        # Load in Scryfall scan and frame it
        if CFG.import_scryfall_scan:
            self.run_tasks(
                funcs=[self.paste_scryfall_scan],
                message="Couldn't import Scryfall scan, continuing without it!",
                warning=True)

        # Add expansion symbol
        self.run_tasks(
            funcs=[self.load_expansion_symbol],
            message="Unable to generate expansion symbol!",
            warning=True)

        # Add watermark
        if CFG.enable_basic_watermark and self.is_basic_land:
            # Basic land watermark
            if not self.run_tasks(
                    funcs=[self.create_basic_watermark],
                    message="Unable to generate basic land watermark!"
            ):
                return False
        elif CFG.watermark_mode is not WatermarkMode.Disabled:
            # Normal watermark
            if not self.run_tasks(
                    funcs=[self.create_watermark],
                    message="Unable to generate watermark!"
            ):
                return False

        # Enable layers to build our frame
        if not self.run_tasks(
                funcs=self.frame_layer_methods,
                message="Enabling layers failed!"
        ):
            return False

        # Format text layers
        if not self.run_tasks(
                funcs=[
                    *self.text_layer_methods,
                    self.format_text_layers,
                    *self.post_text_methods
                ],
                message="Formatting text layers failed!"
        ):
            return False

        # Specific hooks
        if not self.run_tasks(
                funcs=self.hooks,
                message="Encountered an error during triggered hooks step!"
        ):
            return False

        # Manual edit step?
        if CFG.exit_early and not ENV.TEST_MODE:
            self.console.await_choice(self.event)

        # Save the document
        if not self.run_tasks(
                funcs=[self.save_mode],
                message="Error during file save process!",
                kwargs={'path': self.output_file_name, 'docref': self.docref}
        ):
            return False

        # Post save methods
        if not self.run_tasks(
                funcs=self.post_save_methods,
                message="Image saved, but an error was encountered during the post-save step!"
        ):
            return False

        # Reset document, return success
        if not ENV.TEST_MODE:
            self.console.update(f"[b]{self.output_file_name.stem}[/b] rendered successfully!")
        self.reset()
        return True


class StarterTemplate(BaseTemplate):
    """Utility Template between Base and Normal in complexity.

    Notes:
        - Adds basic text layers to the render process.
        - Extend this template when doing more complicated templates which require
            rewriting large portions of the `NormalTemplate` functionality.
    """

    def basic_text_layers(self) -> None:
        """Add essential text layers: Mana cost, Card name, Typeline."""
        self.text.extend([
            FormattedTextField(
                layer=self.text_layer_mana,
                contents=self.layout.mana_cost
            ),
            ScaledTextField(
                layer=self.text_layer_name,
                contents=self.layout.name,
                reference=self.name_reference
            ),
            ScaledTextField(
                layer=self.text_layer_type,
                contents=self.layout.type_line,
                reference=self.type_reference
            )])


class NormalTemplate(StarterTemplate):
    """Utility Template containing the most common "batteries included" functionality.

    Notes:
        - Adds remaining logic that is required for any normal M15 style card, including:
            - Rules and PT text.
            - Enabling typical frame layers.
            - Enabling the legendary crown / hollow crown if supported.
        - Extend this template for broad support of most typical card functionality.
    """

    @auto_prop_cached
    def is_fullart(self) -> bool:
        """Colorless cards use Fullart reference."""
        return self.is_colorless

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and power/toughness text."""
        self.text.extend([
            FormattedTextArea(
                layer=self.text_layer_rules,
                contents=self.layout.oracle_text,
                flavor=self.layout.flavor_text,
                reference=self.textbox_reference,
                divider=self.divider_layer,
                pt_reference=self.pt_reference,
                centered=self.is_centered
            ),
            TextField(
                layer=self.text_layer_pt,
                contents=f"{self.layout.power}/{self.layout.toughness}"
            ) if self.is_creature else None
        ])

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self) -> None:
        """Enable layers which make-up the frame of the card."""

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
        """Enable layers which make-up the Legendary crown."""

        # Enable crown and legendary border
        self.crown_layer.visible = True
        if self.border_group and isinstance(self.border_group, LayerContainer):
            psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
            psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True

        # Call hollow crown step
        if self.is_hollow_crown:
            self.enable_hollow_crown(
                psd.getLayer(LAYERS.SHADOWS))

    def enable_hollow_crown(self, shadows: Optional[ArtLayer] = None) -> None:
        """Enable the hollow legendary crown."""
        if shadows:
            psd.enable_mask(shadows)
        psd.enable_mask(self.crown_layer.parent)
        psd.enable_mask(self.pinlines_layer.parent)
        self.crown_shadow_layer.visible = True


class NormalEssentialsTemplate(NormalTemplate):
    """
    * Original extendable class for creating an M15 Style template without Nyx or Companion layers.
    * DEPRECATED, left here for backwards compatibility.
    """
