"""
* CORE PROXYSHOP TEMPLATES
"""

from collections.abc import Callable, Sequence
from contextlib import suppress
from datetime import UTC, datetime
from functools import cached_property
from logging import getLogger
from pathlib import Path
from re import Match, sub
from threading import Event
from traceback import format_stack
from typing import TYPE_CHECKING, Any, Unpack

from omnitils.files import get_unique_filename
from photoshop.api import SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api._selection import Selection
from photoshop.api.enumerations import BlendMode, ElementPlacement, SaveOptions
from PIL import Image

import src.helpers as psd
from src import APP, CON
from src._state import PATH, WatermarkFormat
from src.cards import sanitize_card_filename, strip_reminder_text
from src.enums.layers import LAYERS
from src.enums.mtg import CardFonts, CardTextPatterns, MagicIcons
from src.enums.settings import (
    BorderColor,
    CollectorMode,
    CollectorPromo,
    FillMode,
    OutputFileType,
    WatermarkMode,
)
from src.frame_logic import is_multicolor_string
from src.helpers.adjustments import CreateColorLayerKwargs
from src.helpers.effects import LayerEffects
from src.helpers.position import DimensionNames
from src.helpers.text import get_font_size, override_text_style_ranges
from src.layouts import NormalLayout, SplitLayout
from src.schema.adobe import EffectBevel, EffectColorOverlay, EffectGradientOverlay
from src.schema.colors import (
    ColorObject,
    GradientColor,
    GradientConfig,
    basic_watermark_color_map,
    is_rgb_or_cmyk_tuple,
    watermark_color_map,
)
from src.text_layers import (
    FormattedTextArea,
    FormattedTextField,
    FormattedTextLayer,
    ScaledTextField,
    TextField,
)
from src.utils.adobe import (
    PS_EXCEPTIONS,
    PhotoshopHandler,
    ReferenceLayer,
    get_photoshop_error_message,
    try_photoshop,
)
from src.utils.scryfall import get_card_scan
from src.utils.text import format_string_with_indices
from src.utils.windows import WindowState

if TYPE_CHECKING:
    from src.gui.qml.models.file_dialog_model import FileDialogModel
    from src.gui.qml.models.message_dialog_content_model import (
        MessageDialogContentModel,
    )
    from src.render.setup import RenderOperation

_logger = getLogger(__name__)

"""
* Template Classes
"""


class BaseTemplate:
    """Master Template for Proxyshop all others should extend to.

    Notes:
        - Contains all the core architecture that is required for any template to function in Proxyshop,
            as well as a ton of optional built-in utility properties and methods for building templates.
    """

    frame_suffix = "Normal"
    template_suffix = ""

    def __init__(self, layout: NormalLayout):
        # Setup manual properties
        self.layout = layout
        self.config = layout.config

    """
    * Enabled Method Lists
    """

    @cached_property
    def pre_render_methods(self) -> list[Callable[[], None]]:
        """list[Callable]: Methods called before rendering begins.

        Methods:
            `process_layout_data`: Processes layout data before it is used to generate the card.
        """
        return [self.process_layout_data]

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        """list[Callable]: Methods called to insert and enable frame layers.

        Methods:
            `color_border`: Changes the border color if required and supported by the template.
            `enable_frame_layers`:
        """
        return [self.color_border, self.enable_frame_layers]

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """list[Callable]: Methods called to insert and format text layers."""
        return [
            self.collector_info,
            self.basic_text_layers,
            self.rules_text_and_pt_layers,
        ]

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """list[Callable]: Methods called after text is inserted and formatted."""
        return []

    @cached_property
    def post_save_methods(self) -> list[Callable[[], None]]:
        """list[Callable]: Methods called after the rendered image is saved."""
        return []

    """
    * Hook Method List
    """

    @cached_property
    def hooks(self) -> list[Callable[[], None]]:
        """list[Callable]: List of methods that will be called during the hooks execution step"""
        hooks: list[Callable[[], None]] = []
        if self.is_creature:
            # Creature hook
            hooks.append(self.hook_creature)
        if "P" in self.layout.mana_cost or "/" in self.layout.mana_cost:
            # Large mana symbol hook
            hooks.append(self.hook_large_mana)
        return hooks

    def hook_creature(self) -> None:
        """Run this if card is a creature."""

    def hook_large_mana(self) -> None:
        """Run this if card has a large mana symbol."""

    """
    * App Properties
    """

    @cached_property
    def render_operation(self) -> RenderOperation:
        raise ValueError("Render operation not assigned")

    @cached_property
    def file_dialog(self) -> FileDialogModel | None:
        return None

    @cached_property
    def message_dialog(self) -> MessageDialogContentModel | None:
        return None

    @cached_property
    def event(self) -> Event:
        """Event: Threading Event used to signal thread cancellation."""
        return Event()

    @property
    def app(self) -> PhotoshopHandler:
        """PhotoshopHandler: Photoshop Application object used to communicate with Photoshop."""
        return APP.instance

    @cached_property
    def docref(self) -> Document:
        """This template's document open in Photoshop."""
        if doc := psd.get_document(self.layout.template_file.name):
            return doc
        raise ValueError("Failed to get document reference for the template.")

    @cached_property
    def doc_selection(self) -> Selection:
        """Selection: Active document selection object."""
        return self.docref.selection

    @property
    def active_layer(self) -> ArtLayer | LayerSet:
        """Union[ArtLayer, LayerSet]: Get the currently active layer in the Photoshop document."""
        return self.docref.activeLayer

    @active_layer.setter
    def active_layer(self, value: ArtLayer | LayerSet):
        """Set the currently active layer in the Photoshop document.

        Args:
            value: An ArtLayer or LayerSet to make active.
        """
        self.docref.activeLayer = value

    """
    * SolidColor objects
    """

    @cached_property
    def RGB_BLACK(self) -> SolidColor:
        """SolidColor: A solid color object with RGB [0, 0, 0]."""
        return psd.rgb_black()

    @cached_property
    def RGB_WHITE(self) -> SolidColor:
        """SolidColor: A solid color object with RGB [255, 255, 255]."""
        return psd.rgb_white()

    """
    * File Saving
    """

    @cached_property
    def save_mode(self) -> Callable[[Path, Document | None], None]:
        """Callable: Function called to save the rendered image."""
        if self.config.output_file_type == OutputFileType.PNG:
            return lambda pth, doc: psd.save_document_png(
                pth, doc, self.config.png_compression_level
            )
        if self.config.output_file_type == OutputFileType.PSD:
            return psd.save_document_psd
        return psd.save_document_jpeg

    @cached_property
    def output_directory(self) -> Path:
        """Directory where the rendered image will be saved to."""
        if output_directory := self.layout.file["kwargs"].get("dir", None):
            return PATH.OUT / output_directory
        return PATH.OUT

    @cached_property
    def output_file_name(self) -> Path:
        """The formatted path for the rendered image."""
        name, tag_map = (
            self.config.output_file_name,
            {
                "#name": self.layout.name_raw,
                "#artist": self.layout.artist,
                "#set": self.layout.set,
                "#num": str(self.layout.collector_number),
                "#frame": self.frame_suffix,
                "#suffix": self.template_suffix,
                "#creator": self.layout.creator,
                "#lang": self.layout.lang,
            },
        )

        # Replace conditional tags
        for n in CardTextPatterns.PATH_CONDITION.findall(name):
            case_new, case = n, f"<{n}>"
            for tag, val in tag_map.items():
                if tag in case and not val:
                    name, case_new = name.replace(case, ""), ""
                    break
                if tag in case:
                    case_new = case_new.replace(tag, val)
            if case_new:
                name = name.replace(case, case_new)

        # Replace other tags
        for tag, value in tag_map.items():
            if value:
                name = name.replace(tag, value)

        path = Path(self.output_directory, sanitize_card_filename(name)).with_suffix(
            f".{self.config.output_file_type}"
        )

        # Are we overwriting duplicate names?
        if not self.config.overwrite_duplicate:
            path = get_unique_filename(path)
        return path

    """
    * Cosmetic Extendable Checks
    """

    @cached_property
    def is_hollow_crown(self) -> bool:
        """bool: Governs whether a hollow crown should be rendered."""
        return False

    @cached_property
    def is_fullart(self) -> bool:
        """bool: Returns True if art must be treated as Fullart."""
        return False

    """
    * Boolean Checks
    """

    @cached_property
    def is_creature(self) -> bool:
        """bool: Governs whether to add PT box and use Creature rules text."""
        return self.layout.is_creature

    @cached_property
    def is_legendary(self) -> bool:
        """bool: Enables the legendary crown step."""
        return self.layout.is_legendary

    @cached_property
    def is_land(self) -> bool:
        """bool: Governs whether to use normal or land pinlines group."""
        return self.layout.is_land

    @cached_property
    def is_artifact(self) -> bool:
        """bool: Utility definition for custom templates. Returns True if card is an Artifact."""
        return self.layout.is_artifact

    @cached_property
    def is_vehicle(self) -> bool:
        """bool: Utility definition for custom templates. Returns True if card is a Vehicle."""
        return self.layout.is_vehicle

    @cached_property
    def is_hybrid(self) -> bool:
        """bool: Utility definition for custom templates. Returns True if card is hybrid color."""
        return self.layout.is_hybrid

    @cached_property
    def is_colorless(self) -> bool:
        """bool: Enforces fullart framing for card art on many templates."""
        return self.layout.is_colorless

    @cached_property
    def is_front(self) -> bool:
        """bool: Governs render behavior on MDFC and Transform cards."""
        return self.layout.is_front

    @cached_property
    def is_transform(self) -> bool:
        """bool: Governs behavior on double faced card varieties."""
        return self.layout.is_transform

    @cached_property
    def is_mdfc(self) -> bool:
        """bool: Governs behavior on double faced card varieties."""
        return self.layout.is_mdfc

    @cached_property
    def is_companion(self) -> bool:
        """bool: Enables companion cosmetic elements."""
        return self.layout.is_companion

    @cached_property
    def is_nyx(self) -> bool:
        """bool: Enables nyxtouched cosmetic elements."""
        return self.layout.is_nyx

    @cached_property
    def is_snow(self) -> bool:
        """bool: Enables snow cosmetic elements."""
        return self.layout.is_snow

    @cached_property
    def is_miracle(self) -> bool:
        """bool: Enables miracle cosmetic elements."""
        return self.layout.is_miracle

    @cached_property
    def is_token(self) -> bool:
        """bool: Enables token cosmetic elements."""
        return self.layout.is_token

    @cached_property
    def is_emblem(self) -> bool:
        """bool: Enables emblem cosmetic elements."""
        return self.layout.is_emblem

    """
    * Cached Properties
    * Calculated in BaseTemplate class
    """

    @cached_property
    def is_basic_land(self) -> bool:
        """bool: Governs Basic Land watermark and other Basic Land behavior."""
        return self.layout.is_basic_land

    @cached_property
    def is_centered(self) -> bool:
        """bool: Governs whether rules text is centered."""
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
        )

    @cached_property
    def is_name_shifted(self) -> bool:
        """bool: Governs whether to use the shifted name text layer."""
        return bool(self.is_transform or self.is_mdfc)

    @cached_property
    def is_type_shifted(self) -> bool:
        """bool: Governs whether to use the shifted typeline text layer."""
        return bool(self.layout.color_indicator)

    @cached_property
    def is_flipside_creature(self) -> bool:
        """bool: Governs double faced cards where opposing side is a creature."""
        return bool(self.layout.other_face_power and self.layout.other_face_toughness)

    @cached_property
    def is_art_vertical(self) -> bool:
        """bool: Returns True if art provided is vertically oriented, False if it is horizontal."""
        with Image.open(self.layout.art_file) as image:
            width, height = image.size
        return height > (width * 1.1)

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        """bool: Governs whether content aware fill should be performed during the art loading step."""
        if self.is_fullart and (
            not self.art_reference
            or all(n not in self.art_reference.name for n in ["Full", "Borderless"])
        ):
            # By default, fill when we want a fullart image but didn't receive one
            return self.config.fill_mode != FillMode.NO_FILL
        return False

    @cached_property
    def is_collector_promo(self) -> bool:
        """bool: Governs whether to use promo star in collector info."""
        if self.config.collector_promo == CollectorPromo.Always:
            return True
        return (
            self.layout.is_promo
            and self.config.collector_promo == CollectorPromo.Automatic
        )

    """
    * Frame Details
    """

    @cached_property
    def art_frame(self) -> str:
        """str: Normal frame to use for positioning the art."""
        return LAYERS.ART_FRAME

    @cached_property
    def art_frame_vertical(self) -> str:
        """str: Vertical orientation frame to use for positioning the art."""
        return LAYERS.FULL_ART_FRAME

    @cached_property
    def twins(self) -> str:
        """str: Name of the Twins layer, also usually the PT layer."""
        return self.layout.twins

    @cached_property
    def pinlines(self) -> str:
        """str: Name of the Pinlines layer."""
        return self.layout.pinlines

    @cached_property
    def identity(self) -> str:
        """str: Color identity of the card, e.g. WU."""
        return self.layout.identity

    @cached_property
    def background(self) -> str:
        """str: Name of the Background layer."""
        if not self.is_vehicle and self.layout.background == LAYERS.VEHICLE:
            return LAYERS.ARTIFACT
        return self.layout.background

    @cached_property
    def color_limit(self) -> int:
        """int: Number of colors where frame elements will no longer split (becomes gold)."""
        return 3

    """
    * Layer Groups
    """

    @cached_property
    def legal_group(self) -> LayerSet:
        """LayerSet: Group containing artist credit, collector info, and other legal details."""
        return self.docref.layerSets[LAYERS.LEGAL]

    @cached_property
    def collector_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.COLLECTOR, self.legal_group)

    @cached_property
    def border_group(self) -> LayerSet | None:
        """Optional[Union[LayerSet, ArtLayer]]: Group, or sometimes a layer, containing the card border."""
        if group := psd.getLayerSet(LAYERS.BORDER, self.docref):
            return group
        return

    @cached_property
    def text_group(self) -> LayerSet | None:
        """Optional[LayerSet]: Text and icon group, contains rules text and necessary symbols."""
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS)

    @cached_property
    def dfc_group(self) -> LayerSet | None:
        """Optional[LayerSet]: Group containing double face elements."""
        face = LAYERS.FRONT if self.is_front else LAYERS.BACK
        if self.is_transform:
            return psd.getLayerSet(face, [self.text_group, LAYERS.TRANSFORM])
        if self.is_mdfc:
            return psd.getLayerSet(f"{LAYERS.MDFC} {face}", self.text_group)
        return

    @cached_property
    def mask_group(self) -> LayerSet | None:
        """LayerSet: Group containing masks used to blend and adjust various layers."""
        with suppress(Exception):
            return self.docref.layerSets[LAYERS.MASKS]
        return

    """
    * Text Layers
    """

    @cached_property
    def text_layer_artist(self) -> ArtLayer | None:
        """Card artist text layer."""
        return psd.getLayer(LAYERS.ARTIST, self.legal_group)

    @cached_property
    def text_layer_set(self) -> ArtLayer | None:
        """Card set text layer."""
        return psd.getLayer(LAYERS.SET, self.legal_group)

    @cached_property
    def text_layer_collector_first(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.TOP, self.collector_group)

    @cached_property
    def text_layer_collector_second(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.BOTTOM, self.collector_group)

    @cached_property
    def text_layer_creator(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Proxy creator name text layer."""
        return psd.getLayer(LAYERS.CREATOR, self.legal_group)

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Card name text layer."""
        layer = psd.getLayer(LAYERS.NAME, self.text_group)
        if self.is_name_shifted and (
            shift_layer := psd.getLayer(LAYERS.NAME_SHIFT, self.text_group)
        ):
            if layer:
                layer.visible = False
            shift_layer.visible = True
            return shift_layer
        return layer

    @cached_property
    def text_layer_mana(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Card mana cost text layer."""
        return psd.getLayer(LAYERS.MANA_COST, self.text_group)

    @cached_property
    def text_layer_type(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Card typeline text layer."""
        layer = psd.getLayer(LAYERS.TYPE_LINE, self.text_group)
        if layer and self.is_type_shifted:
            layer.visible = False
            if typeline := psd.getLayer(LAYERS.TYPE_LINE_SHIFT, self.text_group):
                typeline.visible = True
            return typeline
        return layer

    @cached_property
    def text_layer_rules(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Card rules text layer."""
        if self.is_creature:
            return psd.getLayer(LAYERS.RULES_TEXT_CREATURE, self.text_group)
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_group)

    @cached_property
    def text_layer_pt(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Card power and toughness text layer."""
        return psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_group)

    @cached_property
    def divider_layer(self) -> ArtLayer | LayerSet | None:
        """Optional[ArtLayer]: Divider layer between rules text and flavor text."""
        if (
            self.is_transform
            and self.is_front
            and self.is_flipside_creature
            and (layer := psd.getLayer("Divider TF", self.text_group))
        ):
            return layer
        return psd.getLayer(LAYERS.DIVIDER, self.text_group)

    """
    * Frame Layers
    """

    @property
    def art_layer(self) -> ArtLayer | None:
        """ArtLayer: Layer the art image is imported into."""
        return psd.getLayer(LAYERS.DEFAULT, self.docref)

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
        """Name and title boxes layer."""
        return psd.getLayer(self.twins, LAYERS.TWINS)

    @cached_property
    def pinlines_layer(self) -> ArtLayer | None:
        """Pinlines (and textbox) layer."""
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        """Background texture layer."""
        # Try finding Vehicle background
        if self.is_vehicle and self.background == LAYERS.VEHICLE:
            return psd.getLayer(LAYERS.VEHICLE, LAYERS.BACKGROUND) or psd.getLayer(
                LAYERS.ARTIFACT, LAYERS.BACKGROUND
            )
        # All other backgrounds
        return psd.getLayer(self.background, LAYERS.BACKGROUND)

    @cached_property
    def pt_layer(self) -> ArtLayer | None:
        """Power and toughness box layer."""
        # Test for Vehicle PT support
        if (
            self.is_vehicle
            and self.background == LAYERS.VEHICLE
            and (layer := psd.getLayer(LAYERS.VEHICLE, LAYERS.PT_BOX))
        ):
            # Change font to white for Vehicle PT box
            if self.text_layer_pt:
                self.text_layer_pt.textItem.color = self.RGB_WHITE
            return layer
        return psd.getLayer(self.twins, LAYERS.PT_BOX)

    @cached_property
    def crown_layer(self) -> ArtLayer | None:
        """Legendary crown layer."""
        return psd.getLayer(self.pinlines, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def crown_shadow_layer(self) -> ArtLayer | LayerSet | None:
        """Legendary crown hollow shadow layer."""
        return psd.getLayer(LAYERS.HOLLOW_CROWN_SHADOW, self.docref)

    @cached_property
    def color_indicator_layer(self) -> ArtLayer | None:
        """Color indicator icon layer."""
        if self.layout.color_indicator:
            return psd.getLayer(self.layout.color_indicator, LAYERS.COLOR_INDICATOR)
        return

    @cached_property
    def transform_icon_layer(self) -> ArtLayer | None:
        """Optional[ArtLayer]: Transform icon layer."""
        return psd.getLayer(self.layout.transform_icon, self.dfc_group)

    """
    * Reference Layers
    """

    @cached_property
    def art_reference(self) -> ReferenceLayer | None:
        """ReferenceLayer: Reference frame used to scale and position the art layer."""
        # Check if art is vertically oriented, or forced vertical, and for valid vertical frame
        if (
            self.is_art_vertical or (self.is_fullart and self.config.vertical_fullart)
        ) and (layer := psd.get_reference_layer(self.art_frame_vertical)):
            return layer
        # Check for normal art frame
        return psd.get_reference_layer(self.art_frame) or psd.get_reference_layer(
            LAYERS.ART_FRAME
        )

    @cached_property
    def name_reference(self) -> ArtLayer | None:
        """ArtLayer: By default, name uses Mana Cost as a reference to check collision against."""
        if self.is_basic_land:
            return
        return self.text_layer_mana

    @cached_property
    def type_reference(self) -> ArtLayer | None:
        """ArtLayer: By default, typeline uses the expansion symbol to check collision against,
        otherwise fallback to the expansion symbols reference layer."""
        if self.is_basic_land:
            return
        return self.expansion_symbol_layer or self.expansion_reference

    @cached_property
    def textbox_reference(self) -> ReferenceLayer | None:
        """ReferenceLayer: Reference frame used to scale and position the rules text layer."""
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.text_group)

    @cached_property
    def pt_reference(self) -> ReferenceLayer | None:
        """ArtLayer: Reference used to check rules text overlap with the PT Box."""
        if not self.is_creature:
            return
        return psd.get_reference_layer(LAYERS.PT_REFERENCE, self.text_group)

    """
    * Blending Masks
    """

    @cached_property
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
        if self.config.remove_flavor:
            if isinstance(self.layout, SplitLayout):
                self.layout.flavor_texts = ["" for _ in self.layout.flavor_texts]
            else:
                self.layout.flavor_text = ""

        # Strip reminder text, string or list
        if self.config.remove_reminder:
            if isinstance(self.layout, SplitLayout):
                self.layout.oracle_texts = [
                    strip_reminder_text(txt) for txt in self.layout.oracle_texts
                ]
            else:
                self.layout.oracle_text = strip_reminder_text(self.layout.oracle_text)

    """
    * Loading Artwork
    """

    @cached_property
    def art_action(self) -> Callable[[], None] | None:
        """Function that is called to perform an action on the imported art."""
        return

    @cached_property
    def art_fill_selection_hook(self) -> Callable[[ArtLayer, Selection], None] | None:
        """A hook for adjusting the selected art area.
        Area outside the selected area will be filled.
        The hook runs before contract, feather, etc."""
        return None

    def load_artwork(
        self,
        art_file: str | Path | None = None,
        art_layer: ArtLayer | None = None,
        art_reference: ReferenceLayer | None = None,
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

        if not art_layer:
            raise ValueError("Failed to get art layer.")

        # Import art file
        if self.art_action:
            # Use action pipeline
            art_layer = psd.paste_file(
                layer=art_layer,
                path=art_file,
                action=self.art_action,
                docref=self.docref,
            )
        else:
            # Use traditional pipeline
            art_layer = psd.import_art(
                layer=art_layer, path=art_file, docref=self.docref
            )

        # Frame the artwork
        if self.layout.is_panorama:
            psd.frame_panorama(
                art_layer,
                self.docref,
                self.layout.panorama_element,
                self.layout.panorama_size,
            )
        elif art_reference:
            psd.frame_layer(layer=art_layer, ref=art_reference)

        if self.config.pause_for_manual_art_alignment and not self.pause(
            "Adjust the art alignment manually."
        ):
            return

        # Perform content aware fill if needed
        if self.is_content_aware_enabled:
            if self.config.fill_mode == FillMode.CONTENT_AWARE_FILL:
                psd.content_aware_fill_edges(
                    layer=art_layer,
                    contract=self.config.fill_contract,
                    smooth=self.config.fill_smooth,
                    feather=self.config.fill_feather,
                    art_selection_hook=self.art_fill_selection_hook,
                )
            elif self.config.fill_mode == FillMode.GENERATIVE_FILL:
                if _doc_generated := psd.generative_fill_edges(
                    layer=art_layer,
                    contract=self.config.fill_contract,
                    smooth=self.config.fill_smooth,
                    feather=self.config.fill_feather,
                    close_doc=bool(not self.config.select_variation),
                    docref=self.docref,
                    art_selection_hook=self.art_fill_selection_hook,
                ):
                    # Document reference was returned, await user intervention
                    if not self.pause("Select a Generative Fill variation."):
                        return
                    _doc_generated.close(SaveOptions.SaveChanges)
                return
            elif self.config.fill_mode == FillMode.REMOVE_CONTENT_FILL:
                psd.remove_content_fill_edges(
                    layer=art_layer,
                    contract=self.config.fill_contract,
                    smooth=self.config.fill_smooth,
                    feather=self.config.fill_feather,
                    art_selection_hook=self.art_fill_selection_hook,
                )

    def paste_scryfall_scan(
        self, rotate: bool = False, visible: bool = True
    ) -> ArtLayer | None:
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
            path=scryfall_scan, name="Scryfall Reference", docref=self.docref
        ):
            # Rotate the layer if necessary
            if rotate:
                layer.rotate(90)

            # Frame the layer and position it above the art layer
            dims = psd.get_card_dimensions(self.docref)
            psd.frame_layer(layer, dims)
            if self.art_layer:
                layer.move(self.art_layer, ElementPlacement.PlaceBefore)
            layer.visible = visible
            return layer

    """
    * Collector Info
    """

    def collector_info(self) -> None:
        """Format and add the collector info at the bottom."""

        # If creator is specified add the text
        if self.layout.creator and self.text_layer_creator:
            self.text_layer_creator.textItem.contents = self.layout.creator

        # Which collector info mode?
        if (
            self.config.collector_mode in [CollectorMode.Normal, CollectorMode.Modern]
            and self.layout.collector_data
        ):
            return self.collector_info_authentic()
        elif self.config.collector_mode == CollectorMode.ArtistOnly:
            return self.collector_info_artist_only()
        elif self.config.collector_mode == CollectorMode.Custom:
            return self.collector_info_custom()
        return self.collector_info_basic()

    def collector_info_basic(self) -> None:
        """Called to generate basic collector info."""

        # Collector layers
        set_TI = self.text_layer_set.textItem if self.text_layer_set else None

        # Correct color for non-black border
        if self.border_color != BorderColor.Black:
            if set_TI:
                set_TI.color = self.RGB_BLACK
            if self.text_layer_artist:
                self.text_layer_artist.textItem.color = self.RGB_BLACK

        # Fill optional collector star
        if self.text_layer_set and self.is_collector_promo:
            psd.replace_text(self.text_layer_set, "•", MagicIcons.COLLECTOR_STAR)

        # Fill language, artist, and set
        if self.text_layer_set and self.layout.lang != "en":
            psd.replace_text(self.text_layer_set, "EN", self.layout.lang.upper())

        if self.text_layer_artist:
            psd.replace_text(self.text_layer_artist, "Artist", self.layout.artist)

        if set_TI:
            set_TI.contents = self.layout.set + set_TI.contents

    def collector_info_authentic(self) -> None:
        """Called to generate realistic collector info."""

        # Hide basic layers
        if self.text_layer_artist:
            self.text_layer_artist.visible = False
        if self.text_layer_set:
            self.text_layer_set.visible = False

        if self.collector_group:
            self.collector_group.visible = True

        # Get the collector layers
        if self.text_layer_collector_first:
            first = self.text_layer_collector_first.textItem

            # Correct color for non-black border
            if self.border_color != "black":
                first.color = self.RGB_BLACK

            # Apply the collector info
            first.contents = self.layout.collector_data

        if self.text_layer_collector_second and self.text_layer_collector_second:
            # Fill in language if needed
            if self.layout.lang != "en":
                psd.replace_text(
                    self.text_layer_collector_second, "EN", self.layout.lang.upper()
                )

            # Fill optional collector star
            if self.is_collector_promo:
                psd.replace_text(
                    self.text_layer_collector_second, "•", MagicIcons.COLLECTOR_STAR
                )

            # Correct color for non-black border
            if self.border_color != "black":
                self.text_layer_collector_second.textItem.color = self.RGB_BLACK

            psd.replace_text(self.text_layer_collector_second, "SET", self.layout.set)
            psd.replace_text(
                self.text_layer_collector_second, "Artist", self.layout.artist
            )

    def collector_info_artist_only(self) -> None:
        """Called to generate 'Artist Only' collector info."""

        # Collector layers
        if self.text_layer_set:
            self.text_layer_set.visible = False

        # Correct color for non-black border
        if self.text_layer_artist and self.border_color != BorderColor.Black:
            self.text_layer_artist.textItem.color = self.RGB_BLACK

        # Insert artist name
        if self.text_layer_artist:
            psd.replace_text(self.text_layer_artist, "Artist", self.layout.artist)

    def collector_info_custom(self) -> None:
        """Formats collector layers according to configured custom format."""
        if layer_a := self.text_layer_set:
            layer_a_ti = layer_a.textItem
            font = layer_a_ti.font
            font_size = get_font_size(layer_a)

            if self.config.collector_line_a_format:
                self.format_collector_info_line_custom(
                    layer_a, self.config.collector_line_a_format
                )
            else:
                layer_a.visible = False

            if layer_b := self.text_layer_artist:
                layer_b_ti = layer_b.textItem
                layer_b_ti.font = font
                layer_b_ti.size = font_size

                if self.config.collector_line_b_format:
                    self.format_collector_info_line_custom(
                        layer_b, self.config.collector_line_b_format
                    )
                else:
                    layer_b.visible = False

    def format_collector_info_line_custom(self, layer: ArtLayer, format: str) -> None:
        """Format collector info line according to given format, e.g.
        `{artist} {date:%Y-%m-%d %H:%M}Z`"""

        # Build values dictionary with all available placeholders
        values = {
            "pen": MagicIcons.PAINTBRUSH_MODERN,
            "artist": self.layout.artist,
            "number": self.layout.collector_number,
            "set": self.layout.set,
            "rarity": self.layout.rarity_letter,
            "lang": self.layout.lang,
        }

        now = datetime.now(tz=UTC)
        id_counter: list[int] = [0]
        prefix = "_TkJqxrzSveisbe_"

        def replace_date(match: Match[str]) -> str:
            new_id = f"{prefix}{id_counter[0]}"
            id_counter[0] += 1
            values[new_id] = now.strftime(match.group(1))
            return f"{{{new_id}}}"

        # Handle {date:<format>} pattern
        format_str = sub(r"\{date:([^}]+)\}", replace_date, format)

        # Format string with values
        formatted_text, indices = format_string_with_indices(format_str, **values)
        layer.textItem.contents = formatted_text

        # Apply specific text styles to substitutions that need them
        if ranges := indices.get("pen"):
            override_text_style_ranges(
                layer, ranges, font=CardFonts.MANA, size=5, tracking=200
            )
        if ranges := indices.get("artist"):
            override_text_style_ranges(
                layer, ranges, font=CardFonts.ARTIST, size=4.6, tracking=0
            )

    """
    * Expansion Symbol
    """

    @cached_property
    def expansion_symbol_alignments(self) -> list[DimensionNames]:
        """Alignments used for positioning the expansion symbol"""
        return ["right", "center_y"]

    @cached_property
    def expansion_symbol_layer(self) -> ArtLayer | None:
        """Expansion symbol layer, value set during the `load_expansion_symbol` method."""
        return

    @cached_property
    def expansion_reference(self) -> ArtLayer | None:
        """Expansion symbol reference layer"""
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, self.text_group)

    def load_expansion_symbol(self) -> None:
        """Imports and positions the expansion symbol SVG image."""

        # Check for expansion symbol disabled
        if not self.config.symbol_enabled or not self.expansion_reference:
            return
        if not self.layout.symbol_svg:
            return _logger.error("Expansion symbol disabled. SVG file not found.")

        # Try to import the expansion symbol
        try:
            # Import and place the symbol
            svg = psd.import_svg(
                path=str(self.layout.symbol_svg),
                ref=self.expansion_reference,
                placement=ElementPlacement.PlaceBefore,
                docref=self.docref,
            )

            # Frame the symbol
            psd.frame_layer_by_height(
                layer=svg,
                ref=self.expansion_reference,
                alignments=self.expansion_symbol_alignments,
            )

            # Rename and reset property
            svg.name = "Expansion Symbol"
            self.expansion_symbol_layer = svg

        except Exception:
            _logger.exception("Expansion symbol disabled due to an error")

    """
    * Watermark
    """

    @cached_property
    def watermark_blend_mode(self) -> BlendMode:
        """Blend mode to use on the Watermark layer."""
        return BlendMode.ColorBurn

    @cached_property
    def watermark_color_map(
        self,
    ) -> dict[str, tuple[float | int, float | int, float | int]]:
        """Maps color values for Watermark."""
        return {**watermark_color_map}

    @cached_property
    def watermark_colors(self) -> list[ColorObject]:
        """Colors to use for the Watermark."""
        if self.pinlines in self.watermark_color_map:
            return [self.watermark_color_map.get(self.pinlines, self.RGB_WHITE)]
        elif len(self.identity) < 3:
            return [
                self.watermark_color_map.get(c, self.RGB_WHITE) for c in self.identity
            ]
        return []

    @cached_property
    def watermark_fx(self) -> list[LayerEffects]:
        """Defines the layer effects to use for the Watermark."""
        if len(self.watermark_colors) == 1:
            return [EffectColorOverlay(opacity=100, color=self.watermark_colors[0])]
        if len(self.watermark_colors) == 2:
            return [
                EffectGradientOverlay(
                    rotation=0,
                    colors=[
                        GradientColor(
                            color=self.watermark_colors[0], location=0, midpoint=50
                        ),
                        GradientColor(
                            color=self.watermark_colors[1], location=4096, midpoint=50
                        ),
                    ],
                )
            ]
        return []

    def create_watermark(self) -> None:
        """Builds the watermark."""
        # Required values to generate a Watermark
        if not (
            self.layout.watermark_svg
            and self.layout.watermark
            and self.textbox_reference
            and self.watermark_colors
            and self.text_group
        ):
            return

        # Get watermark custom settings if available
        wm_details: WatermarkFormat | dict[str, float] = CON.watermarks.get(
            self.layout.watermark, {}
        )

        # Import and frame the watermark
        wm = psd.import_svg(
            path=self.layout.watermark_svg,
            ref=self.text_group,
            placement=ElementPlacement.PlaceAfter,
            docref=self.docref,
        )
        psd.frame_layer(
            layer=wm,
            ref=self.textbox_reference.dims,
            smallest=True,
            scale=wm_details.get("scale", 80),
        )

        # Apply opacity, blending, and effects
        wm.opacity = wm_details.get("opacity", self.config.watermark_opacity)
        wm.blendMode = self.watermark_blend_mode
        psd.apply_fx(wm, self.watermark_fx)

    """
    * Basic Land Watermark
    """

    @cached_property
    def basic_watermark_color_map(
        self,
    ) -> dict[str, tuple[float | int, float | int, float | int]]:
        """Maps color values for Basic Land Watermark."""
        return {**basic_watermark_color_map}

    @cached_property
    def basic_watermark_color(self) -> SolidColor:
        """Color to use for the Basic Land Watermark."""
        return psd.get_color(self.basic_watermark_color_map[self.layout.pinlines])

    @cached_property
    def basic_watermark_fx(self) -> list[LayerEffects]:
        """Defines the layer effects used on the Basic Land Watermark."""
        return [
            EffectColorOverlay(opacity=100, color=self.basic_watermark_color),
            EffectBevel(
                highlight_opacity=70,
                shadow_opacity=72,
                softness=14,
                rotation=45,
                altitude=22,
                depth=100,
                size=28,
            ),
        ]

    def create_basic_watermark(self) -> None:
        """Builds a basic land watermark."""
        if self.layout.watermark_basic:
            # Generate the watermark
            wm = psd.import_svg(
                path=self.layout.watermark_basic,
                ref=self.text_group,
                placement=ElementPlacement.PlaceAfter,
                docref=self.docref,
            )
            if self.textbox_reference:
                psd.frame_layer_by_height(
                    layer=wm, ref=self.textbox_reference.dims, scale=75
                )

            # Add effects
            psd.apply_fx(wm, self.basic_watermark_fx)

            # Add snow effects
            if self.is_snow:
                self.add_basic_watermark_snow_effects(wm)

            # Remove rules text step
            self.rules_text_and_pt_layers = lambda: None
            self.layout.oracle_text = ""
            self.layout.flavor_text = ""

    def add_basic_watermark_snow_effects(self, wm: ArtLayer):
        """Adds optional snow effects for 'Snow' Basic Land watermarks.

        Args:
            wm: ArtLayer containing the Basic Land Watermark.
        """

    """
    * Border
    """

    @cached_property
    def border_color(self) -> str:
        """Use 'black' unless an alternate color and a valid border group is provided."""
        if self.config.border_color != BorderColor.Black and self.border_group:
            return self.config.border_color
        return "black"

    @try_photoshop
    def color_border(self) -> None:
        """Color this card's border based on given setting."""
        if self.border_group is not None:
            if self.layout.is_vertical_panorama:
                self.border_group.visible = False
            elif self.border_color != BorderColor.Black:
                psd.apply_fx(
                    self.border_group,
                    [EffectColorOverlay(color=psd.get_color(self.border_color))],
                )

    """
    * Formatted Text Layers
    """

    @cached_property
    def text(self) -> list[FormattedTextLayer]:
        """List of text layer objects to execute."""
        return []

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
        if not self.pause(
            f"{get_photoshop_error_message(check)}\nPress OK to try again, or Cancel to end the render.",
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

    """
    * Tasks and Logging
    """

    def run_tasks(
        self,
        funcs: list[Callable[[], Any]],
        message: str,
        ignore_exception: bool = False,
    ) -> bool:
        """Run a list of functions, checking for thread cancellation and exceptions on each.

        Args:
            funcs: List of functions to perform.
            message: Error message to raise if exception occurs.
            warning: Warn the user if True, otherwise raise error.

        Returns:
            True if tasks completed, False if exception occurred or thread was cancelled.
        """

        # Execute each function
        for func in funcs:
            # Check if thread was cancelled
            if self.event.is_set():
                return False
            try:
                # Run the task
                func()
            except Exception:
                _logger.exception(self.format_exception_message(message))
                if not ignore_exception:
                    return False
            # Once again, check if thread was cancelled
            if self.event.is_set():
                return False
        return True

    def format_exception_message(self, message: str) -> str:
        return f"An exception occurred while rendering <b>{self.layout.display_name}</b>: {message}"

    """
    * Layer Generator Utilities
    * These methods create layers dynamically by blending rasterized layers or solid color
    adjustment layers together using masks.
    """

    def create_blended_layer(
        self,
        group: LayerSet,
        colors: None | str | list[str] = None,
        masks: list[ArtLayer] | None = None,
        blend_mode: BlendMode | None = None,
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
            if layer:
                layer.visible = True
            return

        # Enable each layer color
        layers: list[ArtLayer] = []
        for i, color in enumerate(colors):
            # Make layer visible
            layer = psd.getLayer(color, group)
            if layer:
                if blend_mode is not None:
                    layer.blendMode = blend_mode
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
        colors: Sequence[ColorObject],
        masks: Sequence[ArtLayer | LayerSet] | None = None,
        blend_mode: BlendMode | None = None,
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
            if blend_mode is not None:
                layer.blendMode = blend_mode

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers and len(masks) >= i:
                layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
                psd.copy_layer_mask(masks[i - 1], layers[i - 1])
            layers.append(layer)

    def generate_layer(
        self,
        group: ArtLayer | LayerSet,
        colors: ColorObject | Sequence[ColorObject] | Sequence[GradientConfig],
        masks: list[ArtLayer] | None = None,
        **kwargs: Unpack[CreateColorLayerKwargs],
    ) -> ArtLayer | None:
        """Takes information about a frame layer group and routes it to the correct
        generation function which blends rasterized layers, blends solid color layers, or
        generates a solid color/gradient adjustment layer.

        Notes:
            The result for a given 'colors' schema:
            - str: Enable and/or blend one or more texture layers, unless string is a hex color, in which
                case create a solid color adjustment layer.
            - Sequence[str]: Blend multiple texture layers.
            - tuple[float, ...]: Create a solid color adjustment layer.
            - Sequence[GradientConfig]: Create a gradient adjustment layer.
            - Sequence[tuple[float, ...]]: Blend multiple solid color adjustment layers.
            - Sequence[SolidColor]: Blend multiple solid color adjustment layers.

        Args:
            group: Layer or group containing layers.
            colors: Color definition for this frame layer generation.
            masks: Masks used to blend this generated layer.
        """
        # Assign a generator task based on colors value
        if isinstance(colors, str):
            # Example: '#FFFFFF'
            # Single adjustment layer
            if colors.startswith("#"):
                return psd.create_color_layer(
                    color=colors, layer=group, docref=self.docref, **kwargs
                )
            # Example: 'Land'
            # Single or blended texture layers
            if isinstance(group, LayerSet):
                return self.create_blended_layer(
                    group=group,
                    colors=colors,
                    masks=masks,
                    blend_mode=kwargs.get("blend_mode", None),
                )
        elif isinstance(colors, SolidColor):
            # Example: SolidColor
            # Single adjustment layer
            return psd.create_color_layer(
                color=colors, layer=group, docref=self.docref, **kwargs
            )
        elif is_rgb_or_cmyk_tuple(colors):
            # Example: [r, g, b]
            # RGB/CMYK adjustment layer
            return psd.create_color_layer(
                color=colors, layer=group, docref=self.docref, **kwargs
            )
        elif len(colors) > 0:
            if all(isinstance(c, str) for c in colors) and isinstance(group, LayerSet):
                str_colors = [color for color in colors if isinstance(color, str)]
                # Example: ['#000000', '#FFFFFF', ...]
                # Blended RGB/CMYK adjustment layers
                if isinstance(colors[0], str) and colors[0].startswith("#"):
                    return self.create_blended_solid_color(
                        group=group,
                        colors=str_colors,
                        masks=masks,
                        blend_mode=kwargs.get("blend_mode", None),
                    )
                # Example: ['W', 'U']
                # Blended texture layers
                return self.create_blended_layer(
                    group=group,
                    colors=str_colors,
                    masks=masks,
                    blend_mode=kwargs.get("blend_mode", None),
                )
            elif all(isinstance(c, dict) for c in colors):
                # Example: [GradientColor, GradientColor, ...]
                # Gradient adjustment layer
                return psd.create_gradient_layer(
                    colors=[color for color in colors if isinstance(color, dict)],
                    layer=group,
                    docref=self.docref,
                    **kwargs,
                )
            elif all(isinstance(c, tuple | SolidColor) for c in colors) and isinstance(
                group, LayerSet
            ):
                # Example 1: [[r, g, b], [r, g, b], ...]
                # Example 2: [SolidColor, SolidColor, ...]
                # Blended RGB/CMYK adjustment layers
                return self.create_blended_solid_color(
                    group=group,
                    colors=[
                        color
                        for color in colors
                        if isinstance(color, SolidColor | tuple | str)
                    ],
                    masks=masks,
                    blend_mode=kwargs.get("blend_mode", None),
                )

        # Failed to match a recognized color notation
        if group:
            _logger.warning(
                f"Couldn't generate layer: <i>{group.name}</i>\n{''.join(format_stack())}"
            )

    """
    * Extendable Methods
    * These methods are called during the execution chain but must be written in the child class.
    """

    def enable_frame_layers(self) -> None:
        """Enable the correct layers for this card's frame."""

    def enable_crown(self) -> None:
        """Enable layers required by the Legendary Crown."""

    def enable_hollow_crown(self) -> None:
        """Enable layers required by the Hollow Legendary Crown modification"""

    def basic_text_layers(self) -> None:
        """Establish mana cost, name (scaled to clear mana cost), and typeline (scaled to not overlap set symbol)."""

    def rules_text_and_pt_layers(self) -> None:
        """Set up the card's rules and power/toughness text based on whether the card is a creature."""

    """
    * Execution Sequence
    """

    def cancel(self) -> None:
        self.event.set()

    def pause(self, message: str | None, show_photoshop: bool = True) -> bool:
        response = self.render_operation.pause_sync(message, show_photoshop)
        if self.config.minimize_photoshop:
            self.app.set_window_state(WindowState.MINIMIZE)
        return response

    async def pause_async(
        self, message: str | None, show_photoshop: bool = True
    ) -> bool:
        response = await self.render_operation.pause(message, show_photoshop)
        if self.config.minimize_photoshop:
            self.app.set_window_state(WindowState.MINIMIZE)
        return response

    async def execute(self) -> bool:
        """Perform actions to render the card using this template.

        Notes:
            - Each action is wrapped in an exception check and breakpoint to cancel the thread
                if a cancellation signal was sent by the user.
            - Never override this method!
        """
        # Preliminary Photoshop check
        if not self.run_tasks(
            funcs=[self.check_photoshop], message="Unable to reach Photoshop!"
        ):
            return False

        if self.config.minimize_photoshop:
            self.app.set_window_state(WindowState.MINIMIZE)

        # Pre-process layout data
        if not self.run_tasks(
            funcs=self.pre_render_methods, message="Pre-processing layout data failed!"
        ):
            return False

        # Load in the PSD template
        if not self.run_tasks(
            funcs=[lambda: self.app.load(self.layout.template_file)],
            message="PSD template failed to load!",
        ):
            return False

        # Load in artwork and frame it
        if not self.run_tasks(
            funcs=[self.load_artwork], message="Unable to load artwork!"
        ):
            return False

        # Load in Scryfall scan and frame it
        if self.config.import_scryfall_scan:
            self.run_tasks(
                funcs=[self.paste_scryfall_scan],
                message="Couldn't import Scryfall scan, continuing without it!",
                ignore_exception=True,
            )

        # Add expansion symbol
        self.run_tasks(
            funcs=[self.load_expansion_symbol],
            message="Unable to generate expansion symbol!",
            ignore_exception=True,
        )

        # Add watermark
        if self.config.enable_basic_watermark and self.is_basic_land:
            # Basic land watermark
            if not self.run_tasks(
                funcs=[self.create_basic_watermark],
                message="Unable to generate basic land watermark!",
            ):
                return False
        elif (
            self.config.watermark_mode is not WatermarkMode.Disabled
            and not self.run_tasks(
                funcs=[self.create_watermark], message="Unable to generate watermark!"
            )
        ):
            # Normal watermark
            return False

        # Enable layers to build our frame
        if not self.run_tasks(
            funcs=self.frame_layer_methods, message="Enabling layers failed!"
        ):
            return False

        # Format text layers
        if not self.run_tasks(
            funcs=[
                *self.text_layer_methods,
                self.format_text_layers,
                *self.post_text_methods,
            ],
            message="Formatting text layers failed!",
        ):
            return False

        # Specific hooks
        if not self.run_tasks(
            funcs=self.hooks,
            message="Encountered an error during triggered hooks step!",
        ):
            return False

        # Manual edit step?
        if self.config.exit_early:
            await self.pause_async("Rendering paused for manual editing.")

        # Make sure output folder exists
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Save the document
        if not self.run_tasks(
            funcs=[lambda: self.save_mode(self.output_file_name, self.docref)],
            message="Error during file save process!",
        ):
            return False

        # Post save methods
        if not self.run_tasks(
            funcs=self.post_save_methods,
            message="Image saved, but an error was encountered during the post-save step!",
        ):
            return False

        # Reset document
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
        if self.text_layer_mana:
            self.text.append(
                FormattedTextField(
                    layer=self.text_layer_mana, contents=self.layout.mana_cost
                )
            )
        if self.text_layer_name:
            self.text.append(
                ScaledTextField(
                    layer=self.text_layer_name,
                    contents=self.layout.name,
                    reference=self.name_reference,
                )
            )
        if self.text_layer_type:
            self.text.append(
                ScaledTextField(
                    layer=self.text_layer_type,
                    contents=self.layout.type_line,
                    reference=self.type_reference,
                )
            )


class NormalTemplate(StarterTemplate):
    """Utility Template containing the most common "batteries included" functionality.

    Notes:
        - Adds remaining logic that is required for any normal M15 style card, including:
            - Rules and PT text.
            - Enabling typical frame layers.
            - Enabling the legendary crown / hollow crown if supported.
        - Extend this template for broad support of most typical card functionality.
    """

    @cached_property
    def is_fullart(self) -> bool:
        """Colorless cards use Fullart reference."""
        return self.is_colorless

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and power/toughness text."""
        if self.text_layer_rules:
            self.text.append(
                FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    flavor=self.layout.flavor_text,
                    reference=self.textbox_reference,
                    divider=self.divider_layer,
                    pt_reference=self.pt_reference,
                    centered=self.is_centered,
                )
            )
        if self.text_layer_pt and self.is_creature:
            self.text.append(
                TextField(
                    layer=self.text_layer_pt,
                    contents=f"{self.layout.power}/{self.layout.toughness}",
                )
            )

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
        if self.crown_layer:
            self.crown_layer.visible = True
        if self.border_group:
            if layer := psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group):
                layer.visible = False
            if layer := psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group):
                layer.visible = True

        # Call hollow crown step
        if self.is_hollow_crown:
            self.enable_hollow_crown()

    def enable_hollow_crown(self) -> None:
        """Enable the hollow legendary crown."""
        if shadows := psd.getLayer(LAYERS.SHADOWS):
            psd.enable_mask(shadows)
        if self.crown_layer and isinstance(
            (parent := self.crown_layer.parent), LayerSet
        ):
            psd.enable_mask(parent)
        if self.pinlines_layer and isinstance(
            (parent := self.pinlines_layer.parent), LayerSet
        ):
            psd.enable_mask(parent)
        if self.crown_shadow_layer:
            self.crown_shadow_layer.visible = True
