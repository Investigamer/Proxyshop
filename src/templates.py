"""
CORE TEMPLATES
"""
# Standard Library Imports
import os.path as osp
from functools import cached_property
from threading import Event
from typing import Optional, Callable, Any, Union

# Third Party Imports
from PIL import Image
from pathvalidate import sanitize_filename
from photoshop.api import (
    AnchorPosition,
    ElementPlacement,
    ColorBlendMode,
    BlendMode,
    Urgency
)
from photoshop.api.application import ArtLayer, Photoshop
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document

# Local Imports
from src.env.__console__ import console, Console
from src.frame_logic import format_expansion_symbol_info
import src.text_layers as text_classes
import src.format_text as ft
from src.constants import con
from src.layouts import CardLayout
from src.settings import cfg
import src.helpers as psd
from src.utils.enums_photoshop import Alignment
from src.utils.enums_layers import LAYERS
from src.utils.exceptions import PS_EXCEPTIONS
from src.utils.files import get_unique_filename
from src.utils.scryfall import card_scan
from src.utils.strings import msg_warn, msg_error, is_multiline
from src.utils.regex import Reg


class BaseTemplate:
    """
    Set up variables for things which are common to all templates, extend this at bare minimum.
    """
    template_suffix = ""

    def __init__(self, layout: CardLayout):

        # Setup manual properties
        self.layout = layout
        self.tx_layers = []

        # Load PSD file
        try:
            self.load_template()
        except Exception as e:
            self.raise_error("PSD template failed to load!", e, document=False)

        # Remove flavor or reminder text
        if cfg.remove_flavor:
            self.layout.flavor_text = ""
        if cfg.remove_reminder:
            self.layout.oracle_text = ft.strip_reminder_text(layout.oracle_text)

    def invalidate(self, prop: str):
        # Invalidates a cached property, so it will be computed at next use
        self.__dict__.pop(prop, None)

    """
    BOOL
    """

    @property
    def is_creature(self) -> bool:
        # Governs whether to add PT box and use Creature rules text
        return self.layout.is_creature

    @property
    def is_legendary(self) -> bool:
        # Governs whether to add legendary crown
        return self.layout.is_legendary

    @property
    def is_land(self) -> bool:
        # Governs pinlines group
        return self.layout.is_land

    @property
    def is_companion(self) -> bool:
        # Enables hollow crown and companion crown layer
        return self.layout.is_companion

    @property
    def is_colorless(self) -> bool:
        # Changes art frame to full art on NormalTemplate
        return self.layout.is_colorless

    @property
    def is_nyx(self) -> bool:
        # Whether to use Nyx backgrounds and hollow crown
        return self.layout.is_nyx

    @property
    def is_front(self) -> bool:
        # Which side influences mdfc and transform
        return self.layout.card['front']

    @property
    def is_transform(self) -> bool:
        # Is this a transform card?
        return self.layout.is_transform

    @property
    def is_mdfc(self) -> bool:
        # Is this a transform card?
        return self.layout.is_mdfc

    @cached_property
    def is_centered(self) -> bool:
        # Center the rules text
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
        )

    @property
    def name_shifted(self) -> bool:
        # Use right shifted name?
        return bool(self.is_transform or self.is_mdfc)

    @property
    def type_line_shifted(self) -> bool:
        # Use right shifted Type line?
        return bool(self.layout.color_indicator)

    @cached_property
    def other_face_is_creature(self) -> bool:
        # Governs transform cards other side creature P/T
        return bool(self.layout.other_face_power and self.layout.other_face_toughness)

    """
    APP PROPERTIES
    """

    @cached_property
    def event(self) -> Event:
        # Event tracking Thread status
        return Event()

    @cached_property
    def console(self) -> Console:
        # Console output object
        return console

    @cached_property
    def app(self) -> Photoshop:
        # Photoshop Application object
        return con.app

    @cached_property
    def docref(self) -> Optional[Document]:
        # The current template document
        if doc := psd.get_document(osp.basename(self.layout.template_file)):
            return doc
        return

    @property
    def active_layer(self) -> Union[ArtLayer, LayerSet]:
        # Current active layer
        return self.docref.activeLayer

    @active_layer.setter
    def active_layer(self, value: Union[ArtLayer, LayerSet]):
        # Set the active layer
        self.docref.activeLayer = value

    """
    RENDER PROPERTIES
    """

    @property
    def art_action(self) -> Optional[Callable]:
        # Function that is called to perform an action on the imported art
        return

    @property
    def art_action_args(self) -> Optional[dict]:
        # Args to pass to the art_action
        return

    @cached_property
    def hooks(self) -> list[Callable]:
        # List of hooks that will be called during the hooks execution step
        hooks = []
        if self.is_creature:
            hooks.append(self.hook_creature)
        return hooks

    @cached_property
    def save_modes(self) -> dict:
        # Functions representing file saving modes
        return {
            'png': psd.save_document_png,
            'psd': psd.save_document_psd,
            'jpg': psd.save_document_jpeg,
            'jpeg': psd.save_document_jpeg
        }

    @cached_property
    def output_file_name(self) -> str:
        # Format the filename for the output image
        suffix = self.template_suffix
        if cfg.save_artist_name:
            suffix = f"{suffix} {self.layout.artist}" if suffix else self.layout.artist
        name = self.layout.name_raw

        # Check if name already exists
        if not cfg.overwrite_duplicate:
            name = get_unique_filename(osp.join(con.cwd, "out"), name, f'.{cfg.output_filetype}', suffix)
        return sanitize_filename(name)

    """
    LIST OF FORMATTED TEXT OBJECTS
    """

    @property
    def text(self) -> list:
        # Text layers to execute
        return self.tx_layers

    @text.setter
    def text(self, value):
        # Add text layer to execute
        self.tx_layers = value

    """
    LAYER GROUPS
    """

    @cached_property
    def legal_group(self) -> Optional[LayerSet]:
        # Legal group
        return self.docref.layerSets.getByName(con.layers.LEGAL)

    @cached_property
    def border_group(self) -> Optional[LayerSet]:
        # Border group
        if group := psd.getLayerSet(LAYERS.BORDER):
            return group
        if layer := psd.getLayer(LAYERS.BORDER):
            return layer
        return

    @cached_property
    def text_layers(self) -> Optional[LayerSet]:
        # Text and icon group
        if group := self.docref.layerSets.getByName(LAYERS.TEXT_AND_ICONS):
            return group
        return self.docref

    @cached_property
    def dfc_group(self) -> Optional[LayerSet]:
        # Double face layer group
        if self.face_type and self.text_layers:
            return psd.getLayerSet(self.face_type, self.text_layers)
        return

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_creator(self) -> Optional[ArtLayer]:
        # Creator name layer
        return psd.getLayer("Creator", self.legal_group)

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # CARD NAME
        if self.name_shifted:
            psd.getLayer(LAYERS.NAME, self.text_layers).visible = False
            name = psd.getLayer(LAYERS.NAME_SHIFT, self.text_layers)
            name.visible = True
            return name
        return psd.getLayer(LAYERS.NAME, self.text_layers)

    @cached_property
    def text_layer_mana(self) -> Optional[ArtLayer]:
        # CARD MANA COST
        return psd.getLayer(LAYERS.MANA_COST, self.text_layers)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # CARD TYPELINE
        if self.type_line_shifted:
            psd.getLayer(LAYERS.TYPE_LINE, self.text_layers).visible = False
            typeline = psd.getLayer(LAYERS.TYPE_LINE_SHIFT, self.text_layers)
            typeline.visible = True
            return typeline
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_layers)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # CARD RULES TEXT
        if self.is_creature:
            rules_text = psd.getLayer(LAYERS.RULES_TEXT_CREATURE, self.text_layers)
            rules_text.visible = True
            return rules_text
        # Noncreature card - use the normal rules text layer and disable the p/t layer
        if self.text_layer_pt:
            self.text_layer_pt.visible = False
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_layers)

    @cached_property
    def text_layer_pt(self) -> Optional[ArtLayer]:
        # CARD POWER/TOUGHNESS
        return psd.getLayer(LAYERS.POWER_TOUGHNESS, self.text_layers)

    @cached_property
    def divider_layer(self) -> Optional[ArtLayer]:
        # Shorter flavor divider if flipside P/T is present
        if self.is_transform and self.is_front and self.other_face_is_creature:
            if TF_DIVIDER := psd.getLayer('Divider TF', self.text_layers):
                return TF_DIVIDER
        return psd.getLayer(LAYERS.DIVIDER, self.text_layers)

    """
    FRAME DETAILS
    """

    @cached_property
    def twins(self) -> str:
        # Name of the Twins layer
        # Also corresponds to PT Box typically
        return self.layout.twins

    @cached_property
    def pinlines(self) -> str:
        # Name of the Pinlines layer
        return self.layout.pinlines

    @cached_property
    def background(self) -> str:
        # Name of the Background layer
        return self.layout.background

    @cached_property
    def face_type(self) -> Optional[str]:
        # MDFC face type
        if self.is_mdfc:
            if self.is_front:
                return LAYERS.MDFC_FRONT
            return LAYERS.MDFC_BACK
        # Transform face type
        if self.is_transform:
            if self.is_front:
                return LAYERS.TF_FRONT
            return LAYERS.TF_BACK
        return

    @cached_property
    def border_color(self) -> str:
        # Ensure a valid border color based on config setting and Border availability
        if not cfg.border_color or cfg.border_color not in con.colors:
            return 'black'
        if self.border_group:
            return cfg.border_color
        return 'black'

    @property
    def art_reference(self) -> str:
        return LAYERS.ART_FRAME

    @cached_property
    def art_reference_layer(self) -> ArtLayer:
        # Select a main reference layer
        if isinstance(self.art_reference, ArtLayer):
            # Art reference given as a layer
            layer = self.art_reference
        else:
            # Art reference given as a string
            layer = psd.getLayer(self.art_reference) or psd.getLayer(LAYERS.ART_FRAME)

        # Is the reference already Full Art?
        if not any(map(str(layer.name).__contains__, ["Full Art", "Fullart"])):
            # Check if we have a Full Art image
            with Image.open(self.layout.filename) as image:
                width, height = image.size
            if height > (width * 1.2):
                # Use "Full Art" frame if available
                return psd.getLayer(LAYERS.FULL_ART_FRAME) or layer
        return layer

    """
    FRAME LAYERS
    """

    @property
    def art_layer(self) -> ArtLayer:
        # Layer the art is imported into
        return psd.getLayer(LAYERS.DEFAULT)

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        # Twins
        return psd.getLayer(self.twins, LAYERS.TWINS)

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Pinlines
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        # Background
        if self.is_nyx:
            return psd.getLayer(self.background, LAYERS.NYX)
        return psd.getLayer(self.background, LAYERS.BACKGROUND)

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        # Color Indicator
        if self.layout.color_indicator:
            return psd.getLayer(self.layout.color_indicator, LAYERS.COLOR_INDICATOR)
        return

    @cached_property
    def transform_icon(self) -> Optional[ArtLayer]:
        # Transform Icon
        return psd.getLayer(self.layout.transform_icon, self.dfc_group)

    @cached_property
    def crown_layer(self) -> Optional[ArtLayer]:
        # Legendary Crown
        return psd.getLayer(self.pinlines, LAYERS.LEGENDARY_CROWN)

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Power/Toughness box
        return psd.getLayer(self.twins, LAYERS.PT_BOX)

    @cached_property
    def companion_layer(self) -> Optional[ArtLayer]:
        # Companion inner crown
        return psd.getLayer(self.pinlines, LAYERS.COMPANION)

    """
    REFERENCE LAYERS
    """

    @cached_property
    def textbox_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE, self.text_layers)

    """
    EXPANSION SYMBOL PROPERTIES
    """

    @property
    def expansion_symbol_anchor(self) -> AnchorPosition:
        return AnchorPosition.MiddleRight

    @property
    def expansion_symbol_alignments(self) -> list[Alignment]:
        return [Alignment.CenterVertical, Alignment.Right]

    @cached_property
    def expansion_gradient_layer(self):
        # Expansion symbol rarity gradient layer
        return psd.getLayer(self.layout.rarity, self.text_layers)

    @cached_property
    def expansion_reference_layer(self):
        # Expansion symbol reference layer
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, self.text_layers)

    @cached_property
    def expansion_symbol_layer(self) -> Optional[ArtLayer]:
        # Expansion symbol layer
        return psd.getLayer(LAYERS.EXPANSION_SYMBOL, self.text_layers)

    """
    METHODS
    """

    def collector_info(self) -> None:
        """
        Format and add the collector info at the bottom.
        """
        # Ignore this step if legal layer not present
        if not self.legal_group:
            return

        # If creator is specified add the text
        if self.layout.creator and self.text_layer_creator:
            self.text_layer_creator.textItem.contents = self.layout.creator

        # Use realistic collector information?
        if all([self.layout.collector_number, self.layout.rarity, cfg.real_collector]):
            self.collector_info_authentic()
        else:
            self.collector_info_basic()

    def collector_info_basic(self):
        """
        Called to generate basic collector info.
        """
        # Layers we need
        set_layer = psd.getLayer("Set", self.legal_group)
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        if self.border_color != 'black':
            set_layer.textItem.color = psd.rgb_black()
            artist_layer.textItem.color = psd.rgb_black()

        # Fill in language if needed
        if self.layout.lang != "en":
            psd.replace_text(set_layer, "EN", self.layout.lang.upper())

        # Fill set info / artist info
        set_layer.textItem.contents = self.layout.set + set_layer.textItem.contents
        psd.replace_text(artist_layer, "Artist", self.layout.artist)

    def collector_info_authentic(self):
        """
        Called to generate realistic collector info.
        """
        # Reveal collector group, hide classic layers
        collector_group = psd.getLayerSet(LAYERS.COLLECTOR, LAYERS.LEGAL)
        collector_group.visible = True
        psd.getLayer("Artist", self.legal_group).visible = False
        psd.getLayer("Set", self.legal_group).visible = False
        if pen_layer := psd.getLayer("Pen", self.legal_group):
            pen_layer.visible = False

        # Get the collector layers
        collector_top = psd.getLayer(LAYERS.TOP_LINE, collector_group).textItem
        collector_bottom = psd.getLayer(LAYERS.BOTTOM_LINE, collector_group)
        if self.border_color != 'black':
            collector_top.color = psd.rgb_black()
            collector_bottom.textItem.color = psd.rgb_black()

        # Fill in language if needed
        if self.layout.lang != "en":
            psd.replace_text(collector_bottom, "EN", self.layout.lang.upper())

        # Apply the collector info
        collector_top.contents = self.layout.collector_info_top
        psd.replace_text(collector_bottom, "SET", self.layout.set)
        psd.replace_text(collector_bottom, "Artist", self.layout.artist)

    def expansion_symbol(self) -> None:
        """
        Builds the user's preferred type of expansion symbol.
        """
        if cfg.symbol_mode not in ['default', 'classic', 'svg']:
            self.expansion_symbol_layer.textItem.contents = ''
            return

        # Create a group for generated layers, clear style
        group = self.app.activeDocument.layerSets.add()
        group.move(self.expansion_symbol_layer, ElementPlacement.PlaceAfter)
        psd.clear_layer_style(self.expansion_symbol_layer)

        # Call the necessary creator
        if cfg.symbol_mode == 'default':
            self.create_expansion_symbol(group)
        elif cfg.symbol_mode == 'classic':
            self.create_expansion_symbol_classic(group)
        elif cfg.symbol_mode == 'svg':
            self.create_expansion_symbol_svg(group)

        # Merge and refresh cache
        group.merge().name = "Expansion Symbol"
        self.expansion_symbol_layer.name = "Expansion Symbol Old"
        self.expansion_symbol_layer.opacity = 0
        self.invalidate('expansion_symbol_layer')

        # Frame the symbol
        psd.frame_layer(
            self.expansion_symbol_layer,
            self.expansion_reference_layer,
            smallest=True,
            anchor=self.expansion_symbol_anchor,
            alignments=self.expansion_symbol_alignments
        )

    def create_expansion_symbol(self, group: LayerSet) -> None:
        """
        Builds the expansion symbol using the newer layer effects methodology.
        @param group: The LayerSet to add generated layers to.
        """
        # Set the starting character and format our layer array
        symbols = psd.process_expansion_symbol_info(
            self.layout.symbol, self.layout.rarity.lower()
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
                psd.rasterize_layer_style(current_layer)
                fill_layer = psd.fill_expansion_symbol(current_layer, psd.rgb_black())
                psd.apply_fx(fill_layer, [lay['gradient']])
            elif lay.get('fill'):
                psd.rasterize_layer_style(current_layer)
                fill_layer = psd.fill_expansion_symbol(current_layer, lay['fill'])

            # Merge if there is a filled layer
            if fill_layer:
                current_layer = psd.merge_layers([current_layer, fill_layer])

            # Scale factor
            if lay.get('scale'):
                current_layer.resize(lay['scale']*100, lay['scale']*100, self.expansion_symbol_anchor)

    def create_expansion_symbol_classic(self, group: LayerSet) -> None:
        """
        Builds the expansion symbol using the classic method that uses gradient layers.
        Falls back on default mode if gradient layers aren't present.
        @param group: The LayerSet to add generated layers to.
        """
        # Check if the gradient layer is available
        if not self.expansion_gradient_layer and self.layout.rarity != 'common':
            self.create_expansion_symbol(group)
            return

        # Set the starting character and format our layer array
        symbols = format_expansion_symbol_info(
            self.layout.symbol, self.layout.rarity
        )

        def apply_rarity(layer) -> ArtLayer:
            # Apply rarity gradient to this layer
            mask_layer = self.expansion_gradient_layer.duplicate(layer, ElementPlacement.PlaceBefore)
            mask_layer.grouped = True
            mask_layer.visible = True
            psd.select_layer_bounds(layer)
            self.activeLayer = mask_layer
            psd.align_horizontal()
            psd.align_vertical()
            psd.clear_selection()
            layer = psd.merge_layers([mask_layer, layer])
            return layer

        def apply_fill(layer, color=psd.rgb_black()):
            # Make active and fill background
            self.app.activeDocument.activeLayer = layer
            return psd.fill_expansion_symbol(self.expansion_reference_layer, color)

        # Create each symbol layer
        for i, lay in enumerate(symbols):
            # Establish new current layer
            current_layer = self.expansion_symbol_layer.duplicate(group, ElementPlacement.PlaceAtEnd)
            current_layer.textItem.contents = lay['char']

            # Color replace
            if lay.get('color'):
                current_layer.textItem.color = psd.get_color(lay['color'])

            # Stroke
            if lay.get('stroke'):
                psd.apply_fx(current_layer, [psd.format_symbol_fx_stroke(lay['stroke'])])

            # Apply background fill
            if lay.get('rarity') and lay.get('fill') == 'rarity':
                # Apply fill before rarity
                psd.rasterize_layer_style(current_layer)
                fill_layer = apply_fill(current_layer, psd.rgb_black())
                fill_layer = apply_rarity(fill_layer)
                current_layer = psd.merge_layers([current_layer, fill_layer])
            else:
                # Apply fill after rarity
                if lay.get('rarity'):
                    current_layer = apply_rarity(current_layer)
                psd.rasterize_layer_style(current_layer)
                if lay.get('fill'):
                    fill_layer = apply_fill(current_layer, psd.get_color(lay['fill']))
                    current_layer = psd.merge_layers([current_layer, fill_layer])

            # Scale factor
            if lay.get('scale', 1) != 1:
                current_layer.resize(lay['factor']*100, lay['scale']*100, self.expansion_symbol_anchor)

    def create_expansion_symbol_svg(self, group: LayerSet) -> None:
        """
        Creates an expansion symbol using SVG library. Falls back on default mode if SVG not available.
        @param group: The LayerSet to add generated layers to.
        """
        # Check if the SVG exists
        expansion = cfg.symbol_default if cfg.symbol_force_default else self.layout.set
        expansion = f"{expansion}F" if expansion.lower() == 'con' else expansion  # Conflux case
        svg_path = osp.join(con.path_img, f'symbols/{expansion}/{self.layout.rarity.upper()[0]}.svg')
        if not osp.exists(svg_path):
            self.create_expansion_symbol(group)

        # Import the SVG and place it correctly
        svg = psd.import_svg(svg_path)
        svg.move(group, ElementPlacement.PlaceInside)

    def create_watermark(self) -> None:
        """
        Builds the watermark.
        """
        # Is the watermark from Scryfall supported?
        wm_path = osp.join(con.path_img, f"watermarks/{self.layout.watermark}.svg")
        if not self.layout.watermark or not osp.exists(wm_path):
            return

        # Decide what colors to use
        colors = []
        if len(self.pinlines) == 2:
            colors.extend([con.watermark_colors[c] for c in self.pinlines if c in con.watermark_colors])
        elif self.pinlines in con.watermark_colors:
            colors.append(con.watermark_colors[self.pinlines])

        # Check for valid reference, valid colors, valid text layers group for placement
        if not self.textbox_reference or not colors or not self.text_layers:
            return

        # Get watermark custom settings if available
        wm_details = con.watermarks.get(self.layout.watermark, {})

        # Generate the watermark
        wm = psd.import_svg(wm_path)
        psd.frame_layer(wm, self.textbox_reference, True)
        wm.resize(
            wm_details.get('scale', 80),
            wm_details.get('scale', 80),
            AnchorPosition.MiddleCenter)
        wm.move(self.text_layers, ElementPlacement.PlaceAfter)
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

    def load_template(self) -> None:
        """
        Opens the template's PSD file in Photoshop.
        """
        # Create our full path and load it, set our document reference
        self.app.load(self.layout.template_file)

    def load_artwork(self) -> None:
        """
        Loads the specified art file into the specified layer.
        """
        # Choose image for dev_mode
        if cfg.test_mode:
            # Check for Fullart test image
            dims = psd.get_layer_dimensions(self.art_reference_layer)
            if (dims['width'] * 1.2) < dims['height']:
                # Use fullart test image
                self.layout.filename = osp.join(con.path_img, "test-fa.png")

        # Paste the file into the art
        self.active_layer = self.art_layer
        if self.art_action:
            psd.paste_file(self.art_layer, self.layout.filename, self.art_action, self.art_action_args)
        else:
            psd.import_art(self.art_layer, self.layout.filename)

        # Frame the artwork
        psd.frame_layer(self.active_layer, self.art_reference_layer)

    def paste_scryfall_scan(
        self, reference_layer: Optional[ArtLayer] = None, rotate: bool = False, visible: bool = False
    ) -> Optional[ArtLayer]:
        """
        Downloads the card's scryfall scan, pastes it into the document next to the active layer,
        and frames it to fill the given reference layer.
        @param reference_layer: Reference to frame the scan within.
        @param rotate: Will rotate the card horizontally if True, useful for Planar cards.
        @param visible: Whether to leave the layer visible or hide it.
        """
        # Check for a valid reference layer
        if not reference_layer:
            reference_layer = psd.getLayer(LAYERS.SCRYFALL_SCAN_FRAME)

        # Try to grab the scan from Scryfall
        scryfall_scan = card_scan(self.layout.scryfall_scan)
        if not scryfall_scan:
            return

        # Try to paste the scan into a new layer
        if layer := psd.import_art_into_new_layer(scryfall_scan, "Scryfall Reference"):
            # Should we rotate the layer?
            if rotate:
                layer.rotate(90)
            # Frame the layer and position it above the art layer
            psd.frame_layer(layer, reference_layer)
            layer.move(self.art_layer, ElementPlacement.PlaceBefore)
            # Should we hide the layer?
            if not visible:
                layer.visible = False
            return layer
        return

    def basic_text_layers(self) -> None:
        """
        Set up the card's mana cost, name (scaled to not overlap with mana cost), expansion symbol, and type line
        (scaled to not overlap with the expansion symbol).
        """
        pass

    def rules_text_and_pt_layers(self) -> None:
        """
        Set up the card's rules text and power/toughness according to whether or not the card is a creature.
        You're encouraged to override this method if a template extending this one doesn't have the option for
        creating creature cards (e.g. miracles).
        """
        pass

    def enable_frame_layers(self) -> None:
        """
        Enable the correct layers for this card's frame.
        """
        pass

    def post_text_layers(self) -> None:
        """
        Write code that will be processed after text layers are executed.
        """
        pass

    def post_execute(self) -> None:
        """
        Write code that will be processed after execute completes.
        """
        pass

    def reset(self, document: bool = True) -> None:
        """
        Reset the document, purge the cache, end await.
        @param document: Whether the document is currently open.
        """
        if document:
            psd.reset_document()
            self.app.purge(4)
        console.end_await()

    def run_tasks(
        self,
        funcs: list[Callable],
        message: str,
        warning: bool = False,
        document: bool = True,
        args: Optional[tuple[Any]] = None
    ) -> tuple[bool, bool]:
        """
        Run a list of functions, checking for thread cancellation and exceptions on each.
        @param funcs: List of functions to perform.
        @param message: Error message to raise if exception occurs.
        @param warning: Warn the user if True, otherwise raise error.
        @param document: Whether the document has been opened.
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
                    return False, self.raise_error(message=message, error=e, document=document)
                console.log_exception(e)
                self.raise_warning(message)
        return True, True

    def raise_error(self, message: str, error: Optional[Exception] = None, document: bool = True) -> bool:
        """
        Raise an error on the console display.
        @param message: Message to be displayed
        @param error: Exception object
        @param document: Whether the document is currently open.
        @return: True if continuing, False if cancelling.
        """
        result = console.log_error(
            self.event, self.layout.name, self.layout.template_file,
            f"{msg_error(message)}\nCheck [b]/logs/error.txt[/b] for details.",
            error
        )
        self.reset(document)
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

    def color_border(self) -> None:
        """
        Color this card's border based on given setting.
        """
        # Change to a recognized color that isn't the default
        if self.border_color != 'black' and self.border_group:
            try:
                border = self.docref.layers.getByName('Border')
                psd.apply_fx(border, [{
                    'type': 'color-overlay',
                    'color': psd.get_color(self.border_color)
                }])
            except PS_EXCEPTIONS:
                pass

    """
    HOOKS
    """

    def hook_creature(self) -> None:
        """
        Run this if creature.
        """
        pass

    """
    Execution Sequence
    """

    def execute(self) -> bool:
        """
        Perform actions to populate this template. Load and frame artwork, enable frame layers,
        and execute all text layers. Returns the file name of the image w/ the template's suffix if it
        specified one. Don't override this method!
        """
        # Ensure maximum urgency
        self.docref.info.urgency = Urgency.High

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
        if cfg.enable_watermark:
            check = self.run_tasks([self.create_watermark], "Unable to generate watermark!")
            if not all(check):
                return check[1]

        # Select text layers
        check = self.run_tasks(
            [self.basic_text_layers, self.rules_text_and_pt_layers],
            "Selecting text layers failed!"
        )
        if not all(check):
            return check[1]

        # Enable layers to build our frame
        check = self.run_tasks(
            [self.enable_frame_layers, self.color_border],
            "Enabling layers failed!"
        )
        if not all(check):
            return check[1]

        # Input and format each text layer
        check = self.run_tasks(
            [layer.execute for layer in self.text],
            "Formatting text failed!"
        )
        if not all(check):
            return check[1]

        # Specific hooks
        check = self.run_tasks(
            self.hooks,
            "Encountered an error during triggered hooks step!"
        )
        if not all(check):
            return check[1]

        # Reload the symbol color map before text execution
        check = self.run_tasks(
            [ft.symbol_map.load],
            "Failed to load the symbol color map!"
        )
        if not all(check):
            return check[1]

        # Post text layer execution
        check = self.run_tasks(
            [self.post_text_layers],
            "Post text formatting execution failed!"
        )
        if not all(check):
            return check[1]

        # Manual edit step?
        if cfg.exit_early and not cfg.test_mode:
            console.await_choice(self.event)

        # Save the document
        check = self.run_tasks(
            [self.save_modes.get(cfg.output_filetype, psd.save_document_jpeg)],
            "Error during file save process!",
            args=(self.output_file_name,)
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
    A BaseTemplate with basic text layers added. In most cases this is the class you'll extend to
    when doing more complicated templates which require replacing most of the NormalTemplate functionality.
    """

    """
    HOOKS
    """

    def hook_creature(self) -> None:
        check = ["+", "*"]
        if all(sub in self.layout.power for sub in check) and all(sub in self.layout.toughness for sub in check):
            # Resize the PT text for cards like Gaea's Avenger
            factor = psd.get_text_scale_factor(self.text_layer_pt)
            self.text_layer_pt.textItem.size = (factor * self.text_layer_pt.textItem.size) * .7
            self.text_layer_pt.textItem.baselineShift = 1

    """
    METHODS
    """

    def basic_text_layers(self) -> None:
        """
        Add text layers.
        """
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_mana,
                contents = self.layout.mana_cost
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_name,
                contents = self.layout.name,
                reference = self.text_layer_mana
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line,
                reference = self.expansion_symbol_layer
            )
        ])

    """
    UTILITY METHODS
    """

    def create_dual_layer(self, colors: str, group: LayerSet, mask: Optional[ArtLayer] = None):
        """
        Create a dual color layer using a gradient mask.
        @param colors: Colors to use.
        @param group: Group to look for the layers within.
        @param mask: Layer containing the gradient mask.
        """
        # Was mask provided?
        if not mask or not isinstance(mask, ArtLayer):
            mask = self.docref.artLayers.getByName("Mask")

        # Change layer visibility
        top = psd.getLayer(colors[0], group)
        bottom = psd.getLayer(colors[1], group)
        bottom.move(top, ElementPlacement.PlaceAfter)
        top.visible = True
        bottom.visible = True

        # add the mask
        psd.copy_layer_mask(mask, top)


class NormalTemplate (StarterTemplate):
    """
    Normal M15-style template.
    Extend this for most normal card templates that have typical MTG card layer setu
    """

    @property
    def art_reference(self) -> str:
        # If colorless, use "Full Art Frame"
        if self.is_colorless:
            return LAYERS.FULL_ART_FRAME
        return LAYERS.ART_FRAME

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:

        if self.is_creature:
            # Creature Rules Text + PT
            self.text.extend([
                text_classes.TextField(
                    layer = self.text_layer_pt,
                    contents = f"{self.layout.power}/{self.layout.toughness}"
                ),
                text_classes.CreatureFormattedTextArea(
                    layer = self.text_layer_rules,
                    contents = self.layout.oracle_text,
                    flavor = self.layout.flavor_text,
                    reference = self.textbox_reference,
                    divider = self.divider_layer,
                    pt_reference = psd.getLayer(LAYERS.PT_REFERENCE, self.text_layers),
                    pt_top_reference = psd.getLayer(LAYERS.PT_TOP_REFERENCE, self.text_layers),
                    centered = self.is_centered
                )
            ])

        else:
            # Noncreature Rules Text
            self.text.append(
                text_classes.FormattedTextArea(
                    layer = self.text_layer_rules,
                    contents = self.layout.oracle_text,
                    flavor = self.layout.flavor_text,
                    reference = self.textbox_reference,
                    divider = self.divider_layer,
                    centered = self.is_centered
                )
            )

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
        if self.type_line_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

        # Background
        if self.background_layer:
            self.background_layer.visible = True

        # Legendary crown
        if self.is_legendary and self.crown_layer:
            self.enable_crown()

    def enable_crown(self) -> None:
        """
        Enable the Legendary crown
        """
        self.crown_layer.visible = True
        psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
        psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True

        # Nyx/Companion: Enable the hollow crown shadow and layer mask on crown, pinlines, and shadows
        if self.is_nyx or self.is_companion:
            self.enable_hollow_crown()

            # Enable companion texture
            if self.is_companion and self.companion_layer:
                self.companion_layer.visible = True

    def enable_hollow_crown(self, shadows: Optional[ArtLayer] = None) -> None:
        """
        Enable the hollow legendary crown for this card given layer groups for the crown and pinlines.
        """
        if not shadows:
            shadows = psd.getLayer(LAYERS.SHADOWS)
        psd.enable_mask(self.crown_layer.parent)
        psd.enable_mask(self.pinlines_layer.parent)
        psd.enable_mask(shadows)
        psd.getLayer(LAYERS.HOLLOW_CROWN_SHADOW).visible = True


class NormalClassicTemplate (StarterTemplate):
    """
    A template for 7th Edition frame. Lacks many of the Normal Template features.
    """

    def __init__(self, layout: CardLayout):
        cfg.real_collector = False
        super().__init__(layout)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_layers)

    @property
    def type_line_shifted(self) -> bool:
        return False

    @property
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
    def textbox_reference(self) -> Optional[ArtLayer]:
        return psd.getLayer(
            LAYERS.TEXTBOX_REFERENCE_LAND if self.is_land
            else LAYERS.TEXTBOX_REFERENCE,
            self.text_layers
        )

    def rules_text_and_pt_layers(self):
        # Move mana layer down for hybrid mana
        if len(self.background) == 2:
            self.text_layer_mana.translate(0, -5)

        # Add rules text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_rules,
                contents = self.layout.oracle_text,
                flavor = self.layout.flavor_text,
                centered = self.is_centered,
                reference = self.textbox_reference,
                divider = psd.getLayer(LAYERS.DIVIDER, self.text_layers)
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
            self.expansion_symbol_layer.translate(0, 4)

        # Simple one image background, Land or Nonland
        psd.getLayer(
            self.pinlines,
            LAYERS.LAND if self.is_land else LAYERS.NONLAND
        ).visible = True

        # Add the promo star
        if self.promo_star:
            psd.getLayerSet("Promo Star", LAYERS.TEXT_AND_ICONS).visible = True

    def collector_info(self) -> None:
        """
        Doesn't support authentic collector info.
        """
        # Ignore this step if legal layer not present
        if not self.legal_group:
            return

        # If creator is specified add the text
        if self.layout.creator and self.text_layer_creator:
            self.text_layer_creator.textItem.contents = self.layout.creator

        # Layers we need
        set_layer = psd.getLayer("Set", self.legal_group)
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)

        # Fill in language if needed
        if self.layout.lang != "en":
            psd.replace_text(set_layer, "EN", self.layout.lang.upper())

        # Fill set info / artist info
        set_layer.textItem.contents = self.layout.set + set_layer.textItem.contents
        psd.replace_text(artist_layer, "Artist", self.layout.artist)


"""
Templates similar to NormalTemplate but with aesthetic differences
"""


class NormalExtendedTemplate (NormalTemplate):
    """
    An extended-art version of the normal template. The layer structure of this template and
    NormalTemplate are identical.
    """
    template_suffix = "Extended"


class NormalFullartTemplate (NormalTemplate):
    """
    Normal full art template (Also called "Universes Beyond")
    """
    template_suffix = "Fullart"


class WomensDayTemplate (NormalTemplate):
    """
    The showcase template first used on the Women's Day Secret Lair. Doesn't have any background layers, needs a
    layer mask on the pinlines group when card is legendary, and doesn't support companions.
    """
    template_suffix = "Showcase"

    @cached_property
    def art_reference_layer(self) -> ArtLayer:
        return psd.getLayer(LAYERS.FULL_ART_FRAME)

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    @cached_property
    def crown_layer(self) -> Optional[ArtLayer]:
        # On first access, enable pinlines mask
        psd.enable_mask(self.pinlines_layer.parent)
        return psd.getLayer(self.pinlines, LAYERS.LEGENDARY_CROWN)


class StargazingTemplate (NormalTemplate):
    """
    Stargazing template from Theros: Beyond Death showcase cards. The layer structure of this template and
    NormalTemplate are largely identical, but this template only has Nyx backgrounds and no companion layers.
    """
    template_suffix = "Stargazing"

    @property
    def is_nyx(self) -> bool:
        return True

    @property
    def is_companion(self) -> bool:
        return False

    @property
    def is_land(self) -> bool:
        return False


class InventionTemplate (NormalTemplate):
    """
    Kaladesh Invention template. No special layers for lands, colorless, companion, or nyx.
    """
    template_suffix = "Masterpiece"

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

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_colorless(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @property
    def is_land(self) -> bool:
        return False


class ExpeditionTemplate (NormalTemplate):
    """
    Zendikar Rising Expedition template. Masks pinlines for legendary cards, has a single static background layer,
    doesn't support color indicator, companion, or nyx layers.
    """
    template_suffix = "Expedition"

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_layers)

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def is_land(self) -> bool:
        return False

    def enable_crown(self):
        # legendary crown
        psd.enable_mask(self.pinlines_layer.parent)
        self.crown_layer.visible = True
        psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
        psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True


class SnowTemplate (NormalTemplate):
    """
    A snow template with textures from Kaldheim's snow cards.
    Doesn't support Nyx or Companion layers.
    """
    template_suffix = "Snow"

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False


class MiracleTemplate (NormalTemplate):
    """
    A template for miracle cards. Doesn't support creatures, Nyx, or Companion.
    """

    @property
    def is_creature(self) -> bool:
        return False

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_legendary(self) -> bool:
        return False


"""
Double faced card templates
"""


class TransformTemplate (NormalTemplate):
    """
    Template for the back faces of transform cards.
    """

    @cached_property
    def has_flipside_pt(self) -> bool:
        # Should we make room for displaying flipside PT?
        return bool(self.is_front and self.other_face_is_creature)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # Does it have flipside PT cutout?
        if self.has_flipside_pt:
            if self.is_creature:
                return psd.getLayer(LAYERS.RULES_TEXT_CREATURE_FLIP, self.text_layers)
            # Disable PT
            if self.text_layer_pt:
                self.text_layer_pt.visible = False
            return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE_FLIP, self.text_layers)
        return super().text_layer_rules

    def enable_frame_layers(self):
        # set transform icon
        if self.transform_icon:
            self.transform_icon.visible = True
        super().enable_frame_layers()

    def basic_text_layers(self):
        # For eldrazi card, set the color of the rules text, type line, and power/toughness to black
        if self.layout.transform_icon == LAYERS.DFC_MOONELDRAZI:
            self.text_layer_name.textItem.color = psd.rgb_black()
            self.text_layer_type.textItem.color = psd.rgb_black()
            self.text_layer_pt.textItem.color = psd.rgb_black()
        super().basic_text_layers()

    def rules_text_and_pt_layers(self):
        # If flipside is creature, set flipside power/toughness
        if self.has_flipside_pt:
            self.text.append(
                text_classes.TextField(
                    layer=psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_layers),
                    contents=str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness)
                )
            )
        super().rules_text_and_pt_layers()


class IxalanTemplate (NormalTemplate):
    """
    Template for the back faces of transforming cards from Ixalan block.
    Typeline doesn't scale, no mana cost layer, doesn't support creatures, frame only has background.
    Expansion symbol is centered on this template.
    """

    @property
    def is_creature(self) -> bool:
        # Only lands for this one
        return False

    @property
    def name_shifted(self) -> bool:
        # Since transform icon is present, need to disable name_shifted
        return False

    @cached_property
    def expansion_symbol_anchor(self) -> AnchorPosition:
        return AnchorPosition.MiddleCenter

    @cached_property
    def expansion_symbol_alignments(self) -> list[Alignment]:
        return [Alignment.CenterVertical, Alignment.CenterHorizontal]

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, LAYERS.BACKGROUND)

    def basic_text_layers(self):

        # Add to text layers
        self.text.extend([
            text_classes.TextField(
                layer = self.text_layer_name,
                contents = self.layout.name
            ),
            text_classes.TextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line
            )
        ])

    def enable_frame_layers(self):
        self.background_layer.visible = True


class MDFCTemplate (NormalTemplate):
    """
    Template for Modal Double Faced cards.
    """

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.LEFT, self.dfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RIGHT, self.dfc_group)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add mdfc text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_mdfc_right,
                contents = self.layout.other_face_right
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_mdfc_left,
                contents = self.layout.other_face_left,
                reference = self.text_layer_mdfc_right,
            )
        ])

    def enable_frame_layers(self):
        # MDFC elements at the top and bottom of the card
        psd.getLayer(
            self.twins,
            psd.getLayerSet(LAYERS.TOP, self.dfc_group)
        ).visible = True
        psd.getLayer(
            self.layout.other_face_twins,
            psd.getLayerSet(LAYERS.BOTTOM, self.dfc_group)
        ).visible = True
        super().enable_frame_layers()


"""
Templates similar to NormalTemplate with new features
"""


class MutateTemplate (NormalTemplate):
    """
    A template for Ikoria's mutate cards.  The layer structure of this template and NormalTemplate are
    close to identical, but this template has a couple more text and reference layers for the top half of
    the textbox. It also doesn't include layers for Nyx backgrounds or Companion crowns, but no mutate
    cards exist that would require these layers.
    """

    @cached_property
    def mutate_text(self) -> str:
        split_rules_text = self.layout.oracle_text.split("\n")
        self.layout.oracle_text = "\n".join(split_rules_text[1:])
        return split_rules_text[0]

    @cached_property
    def text_layer_mutate(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.MUTATE, self.text_layers)

    def basic_text_layers(self):

        # Add mutate text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_mutate,
                contents = self.mutate_text,
                flavor = self.layout.flavor_text,
                reference = psd.getLayer(LAYERS.MUTATE_REFERENCE, self.text_layers),
            )
        )

        # Continue with text
        super().basic_text_layers()


class PrototypeTemplate (NormalTemplate):
    """
    A template for Prototype cards introduced in The Brothers' War. This template has a couple
    of additional text layers for prototype text, mana cost, and power/toughness.
    Doesn't support Nyx backgrounds or Companion crowns.
    """

    def __init__(self, layout: CardLayout):

        # Split self.oracle_text between prototype text and rules text
        split_rules_text = layout.oracle_text.split("\n")
        layout.oracle_text = "\n".join(split_rules_text[1:])

        # Set up the prototype elements
        match = Reg.PROTOTYPE.match(split_rules_text[0])
        self.proto_mana_cost, self.proto_pt = match[1], match[2]
        super().__init__(layout)

    @cached_property
    def proto_color(self) -> Optional[str]:
        for c in ['W', 'U', 'B', 'R', 'G']:
            if c in self.proto_mana_cost:
                return c
        return

    @cached_property
    def proto_textbox(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.proto_color, LAYERS.PROTO_TEXTBOX)

    @cached_property
    def proto_manabox(self) -> Optional[ArtLayer]:
        if self.proto_mana_cost.count('{') == 2:
            manabox_group = psd.getLayerSet(LAYERS.PROTO_MANABOX_SMALL)
        else:
            manabox_group = psd.getLayerSet(LAYERS.PROTO_MANABOX_MEDIUM)
        manabox_group.visible = True
        return psd.getLayer(self.proto_color, manabox_group)

    @cached_property
    def proto_ptbox(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.proto_color, LAYERS.PROTO_PTBOX)

    @cached_property
    def text_layer_proto(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_RULES, self.text_layers)

    @cached_property
    def text_layer_proto_mana(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_MANA_COST, self.text_layers)

    @cached_property
    def text_layer_proto_pt(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.PROTO_PT, self.text_layers)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add prototype PT and Mana Cost
        self.text.extend([
            text_classes.FormattedTextField(
                layer = self.text_layer_proto_mana,
                contents = self.proto_mana_cost
            ),
            text_classes.TextField(
                layer = self.text_layer_proto_pt,
                contents = self.proto_pt
            )
        ])

        # Remove reminder text if necessary
        if cfg.remove_reminder:
            self.text_layer_proto.textItem.size = psd.get_text_scale_factor(
                self.text_layer_proto) * 8.93
            self.text.append(
                text_classes.FormattedTextArea(
                    layer = self.text_layer_proto,
                    contents = 'Prototype',
                    reference = self.proto_textbox
                )
            )

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add prototype layers
        if self.proto_textbox:
            self.proto_textbox.visible = True
        if self.proto_manabox:
            self.proto_manabox.visible = True
        if self.proto_ptbox:
            self.proto_ptbox.visible = True


class AdventureTemplate (NormalTemplate):
    """
    A template for Eldraine adventure cards. The layer structure of this template and NormalTemplate
    are close to identical,but this template has a couple more text and reference layers for the left
    half of the textbox.It also doesn't include layers for Nyx backgrounds or Companion crowns, but
    no adventure cards exist that would require these layers.
    """

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add adventure text layers
        mana_cost = psd.getLayer(LAYERS.MANA_COST_ADVENTURE, self.text_layers)
        self.text.extend([
            text_classes.FormattedTextField(
                layer = mana_cost,
                contents = self.layout.adventure['mana_cost']
            ),
            text_classes.ScaledTextField(
                layer = psd.getLayer(LAYERS.NAME_ADVENTURE, self.text_layers),
                contents = self.layout.adventure['name'],
                reference = mana_cost,
            ),
            text_classes.FormattedTextArea(
                layer = psd.getLayer(LAYERS.RULES_TEXT_ADVENTURE, self.text_layers),
                contents = self.layout.adventure['oracle_text'],
                flavor = "",
                centered = False,
                reference = psd.getLayer(LAYERS.TEXTBOX_REFERENCE_ADVENTURE, self.text_layers),
            ),
            text_classes.TextField(
                layer = psd.getLayer(LAYERS.TYPE_LINE_ADVENTURE, self.text_layers),
                contents = self.layout.adventure['type_line']
            )
        ])


class LevelerTemplate (NormalTemplate):
    """
    Leveler template. No layers are scaled or positioned vertically so manual intervention is required.
    Doesn't support companion, nyx, or lands.
    """

    def __init__(self, layout: CardLayout):
        cfg.exit_early = True
        super().__init__(layout)

    def rules_text_and_pt_layers(self):

        # Overwrite to add level abilities
        leveler_text_group = psd.getLayerSet("Leveler Text", self.text_layers)
        self.text.extend([
            text_classes.FormattedTextField(
                layer = psd.getLayer("Rules Text - Level Up", leveler_text_group),
                contents = self.layout.level_up_text
            ),
            text_classes.TextField(
                layer = psd.getLayer("Top Power / Toughness", leveler_text_group),
                contents = str(self.layout.power) + "/" + str(self.layout.toughness)
            ),
            text_classes.TextField(
                layer = psd.getLayer("Middle Level", leveler_text_group),
                contents = self.layout.middle_level
            ),
            text_classes.TextField(
                layer = psd.getLayer("Middle Power / Toughness", leveler_text_group),
                contents = self.layout.middle_power_toughness
            ),
            text_classes.FormattedTextField(
                layer = psd.getLayer("Rules Text - Levels X-Y", leveler_text_group),
                contents = self.layout.levels_x_y_text
            ),
            text_classes.TextField(
                layer = psd.getLayer("Bottom Level", leveler_text_group),
                contents = self.layout.bottom_level
            ),
            text_classes.TextField(
                layer = psd.getLayer("Bottom Power / Toughness", leveler_text_group),
                contents = self.layout.bottom_power_toughness
            ),
            text_classes.FormattedTextField(
                layer = psd.getLayer("Rules Text - Levels Z+", leveler_text_group),
                contents = self.layout.levels_z_plus_text
            )
        ])

    @property
    def is_land(self) -> bool:
        return False

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.twins, LAYERS.PT_AND_LEVEL_BOXES)


class SagaTemplate (NormalTemplate):
    """
    Saga template. No layers are scaled or positioned vertically so manual intervention is required.
    Doesn't support legendary crown, creatures, nyx, or companion.
    """

    def __init__(self, layout: CardLayout):
        self._abilities = []
        self._icons = []
        super().__init__(layout)

    """
    BOOL PROPERTIES
    """

    @property
    def is_legendary(self) -> bool:
        return False

    @property
    def is_creature(self) -> bool:
        return False

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    """
    LAYER PROPERTIES
    """

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.background, LAYERS.TEXTBOX)

    @property
    def ability_layers(self) -> list[ArtLayer]:
        return self._abilities

    @ability_layers.setter
    def ability_layers(self, value):
        self._abilities = value

    @property
    def icon_layers(self) -> list[list[ArtLayer]]:
        return self._icons

    @icon_layers.setter
    def icon_layers(self, value):
        self._icons = value

    @cached_property
    def saga_group(self):
        return psd.getLayerSet("Saga", self.text_layers)

    @cached_property
    def ability_divider(self) -> ArtLayer:
        return psd.getLayer(LAYERS.DIVIDER, self.saga_group)

    """
    TRANSFORM PROPERTIES
    """

    @cached_property
    def transform_icon(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.transform_icon, [self.text_layers, 'tf-front'])

    """
    METHODS
    """

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Saga stripe
        psd.getLayer(self.pinlines, LAYERS.PINLINES_AND_SAGA_STRIPE).visible = True

        # Is this transform?
        if self.layout.other_face:
            # Icon
            psd.getLayerSet('Circle', self.text_layers).visible = True
            self.transform_icon.visible = True

            # Nameplate
            psd.enable_mask(self.twins_layer.parent)
            psd.getLayer(self.background, 'TF Twins').visible = True

    def rules_text_and_pt_layers(self):

        # Add description text with reminder
        self.text.append(
            text_classes.FormattedTextArea(
                layer=psd.getLayer("Reminder Text", self.saga_group),
                contents=self.layout.saga_description,
                reference=psd.getLayer("Description Reference", self.text_layers)
            )
        )

        # Iterate through each saga stage and add line to text layers
        for line in self.layout.saga_lines:
            layer = psd.getLayer(LAYERS.TEXT, self.saga_group).duplicate()
            self.ability_layers.append(layer)
            self.icon_layers.append([psd.getLayer(n, self.saga_group).duplicate() for n in line['icons']])
            self.text.append(
                text_classes.FormattedTextField(
                    layer = layer,
                    contents = line['text']
                )
            )

    def post_text_layers(self) -> None:

        # Core vars
        spacing = 80 * self.app.activeDocument.width / 3264
        spaces = len(self.ability_layers) - 1
        spacing_total = (spaces * 1.5) + 2
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        total_height = ref_height - (((spacing * 1.5) * spaces) + (spacing * 2))

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.ability_layers])
        gap = (ref_height - layer_heights) * (1 / spacing_total)
        inside_gap = (ref_height - layer_heights) * (1.5 / spacing_total)

        # Space Saga lines evenly apart
        psd.spread_layers_over_reference(self.ability_layers, self.textbox_reference, gap, inside_gap)

        # Align icons to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):
            # Skip if this is a passive ability
            icons = self.icon_layers[i]
            if len(icons) > 1:
                psd.space_layers_apart(icons, spacing/3)
                icon_layer = psd.merge_layers(icons)
            else:
                icon_layer = icons[0]
            self.docref.selection.select([
                [0, ref_layer.bounds[1]],
                [ref_layer.bounds[0], ref_layer.bounds[1]],
                [ref_layer.bounds[0], ref_layer.bounds[3]],
                [0, ref_layer.bounds[3]]
            ])
            psd.align_vertical(icon_layer)
            psd.clear_selection()

        # Position divider lines
        self.position_divider_lines()

    def position_divider_lines(self):

        # Position a line between each ability layer
        for i in range(len(self.ability_layers) - 1):
            divider = self.ability_divider.duplicate()
            psd.position_between_layers(divider, self.ability_layers[i], self.ability_layers[i + 1])


class ClassTemplate (NormalTemplate):
    """
    Template for Class cards introduced in AFR.
    """

    def __init__(self, layout: CardLayout):
        self._line_layers: list[ArtLayer] = []
        self._stage_layers: list[LayerSet] = []
        super().__init__(layout)

    """
    BOOL PROPERTIES
    """

    @property
    def is_legendary(self) -> bool:
        return False

    @property
    def is_land(self) -> bool:
        return False

    @property
    def is_creature(self) -> bool:
        return False

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    """
    LAYERS
    """

    @cached_property
    def class_group(self) -> LayerSet:
        return psd.getLayerSet("Class", LAYERS.TEXT_AND_ICONS)

    @cached_property
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet("Stage", self.class_group)

    @property
    def line_layers(self) -> list[ArtLayer]:
        return self._line_layers

    @line_layers.setter
    def line_layers(self, value):
        self._line_layers = value

    @property
    def stage_layers(self) -> list[LayerSet]:
        return self._stage_layers

    @stage_layers.setter
    def stage_layers(self, value):
        self._stage_layers = value

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:

        # Add first static line
        level_1 = psd.getLayer(LAYERS.TEXT, self.class_group)
        self.line_layers.append(level_1)
        self.text.append(
            text_classes.FormattedTextField(
                layer=level_1,
                contents=self.layout.class_lines[0]['text']
            )
        )

        # Add text fields for each line and class stage
        for i, line in enumerate(self.layout.class_lines[1:]):
            line_layer = level_1.duplicate()
            self.active_layer = self.stage_group
            stage = psd.duplicate_group(f"{self.stage_group.name} {i + 1}")
            self.line_layers.append(line_layer)
            self.stage_layers.append(stage)
            self.text.extend([
                text_classes.FormattedTextField(
                    layer=line_layer,
                    contents=line['text']
                ),
                text_classes.FormattedTextField(
                    layer=psd.getLayer("Cost", stage),
                    contents=f"{line['cost']}:"
                ),
                text_classes.TextField(
                    layer=psd.getLayer("Level", stage),
                    contents=f"Level {line['level']}"
                )
            ])
        self.stage_group.visible = False

    def post_text_layers(self) -> None:

        # Core vars
        spacing = 80 * self.app.activeDocument.width / 3264
        spaces = len(self.line_layers) - 1
        divider_height = psd.get_layer_dimensions(self.stage_layers[0])['height']
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.line_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * ((spacing + divider_height) / spacing_total)

        # Space Class lines evenly apart
        psd.spread_layers_over_reference(self.line_layers, self.textbox_reference, gap, inside_gap)

        # Position divider lines
        self.position_divider_lines()

    def position_divider_lines(self):

        # Position a line between each ability layer
        for i in range(len(self.line_layers) - 1):
            psd.position_between_layers(self.stage_layers[i], self.line_layers[i], self.line_layers[i + 1])


"""
Planeswalker templates
"""


class PlaneswalkerTemplate (StarterTemplate):
    """
    Planeswalker template - 3 or 4 loyalty abilities.
    """

    def __init__(self, layout: CardLayout):

        # Settable Properties
        self._ability_layers = []
        self._shields = []
        self._colons = []
        super().__init__(layout)

    """
    PROPERTIES
    """

    @cached_property
    def abilities(self) -> list:
        # Fix abilities that include a newline
        return Reg.PLANESWALKER.findall(self.layout.oracle_text)

    @property
    def art_reference(self):
        # Name of art reference layer
        if self.is_colorless:
            return LAYERS.FULL_ART_FRAME
        return LAYERS.PLANESWALKER_ART_FRAME

    """
    GROUPS
    """

    @cached_property
    def group(self) -> LayerSet:
        # Get the main layer group based on ability box size
        if self.layout.name in ("Gideon Blackblade", "Comet, Stellar Pup"):
            group = psd.getLayerSet("pw-4")
        elif len(self.abilities) <= 3:
            group = psd.getLayerSet("pw-3")
        else:
            group = psd.getLayerSet("pw-4")
        group.visible = True
        return group

    @cached_property
    def loyalty_group(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.LOYALTY_GRAPHICS)

    @cached_property
    def border_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(LAYERS.BORDER, self.group)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layers(self) -> LayerSet:
        return psd.getLayerSet(LAYERS.TEXT_AND_ICONS, self.group)

    @cached_property
    def top_ref(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PW_TOP_REFERENCE, self.text_layers)

    @cached_property
    def adj_ref(self) -> ArtLayer:
        return psd.getLayer(LAYERS.PW_ADJUSTMENT_REFERENCE, self.text_layers)

    @cached_property
    def loyalty_text(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TEXT, [self.loyalty_group, LAYERS.STARTING_LOYALTY])

    """
    SETTABLE LAYERS
    """

    @property
    def ability_layers(self) -> list[ArtLayer]:
        return self._ability_layers

    @ability_layers.setter
    def ability_layers(self, value):
        self._ability_layers = value

    @property
    def colons(self) -> list:
        return self._colons

    @colons.setter
    def colons(self, value):
        self._colons = value

    @property
    def shields(self) -> list:
        return self._shields

    @shields.setter
    def shields(self, value):
        self._shields = value

    """
    FRAME LAYERS
    """

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.twins, psd.getLayerSet(LAYERS.TWINS, self.group))

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, psd.getLayerSet(LAYERS.PINLINES, self.group))

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.background, psd.getLayerSet(LAYERS.BACKGROUND, self.group))

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, [self.group, LAYERS.COLOR_INDICATOR])

    @cached_property
    def crown_layer(self) -> Optional[ArtLayer]:
        # Crown never included
        return

    """
    METHODS
    """

    def basic_text_layers(self):

        # Iterate through abilities to add text layers
        for i, ability in enumerate(self.abilities):

            # Get the colon index, determine if this is static or activated ability
            colon_index = ability.find(": ")
            if 5 > colon_index > 0:

                # Determine which loyalty group to enable, and set the loyalty symbol's text
                loyalty_graphic = psd.getLayerSet(ability[0], self.loyalty_group)
                psd.getLayer(LAYERS.COST, loyalty_graphic).textItem.contents = ability[0:int(colon_index)]
                ability_layer = psd.getLayer(LAYERS.ABILITY_TEXT, self.loyalty_group).duplicate()

                # Add text layer, shields, and colons to list
                self.ability_layers.append(ability_layer)
                self.shields.append(loyalty_graphic.duplicate())
                self.colons.append(psd.getLayer(LAYERS.COLON, self.loyalty_group).duplicate())
                ability = ability[colon_index + 2:]

            else:

                # Hide default ability, switch to static
                ability_layer = psd.getLayer(LAYERS.STATIC_TEXT, self.loyalty_group).duplicate()
                self.ability_layers.append(ability_layer)
                self.shields.append(None)
                self.colons.append(None)

                # Is this a double line ability?
                if "\n" in ability:
                    self.active_layer = ability_layer
                    ft.space_after_paragraph(2)

            # Add ability text
            self.text.append(
                text_classes.FormattedTextField(
                    layer=ability_layer,
                    contents=ability
                )
            )

        # Starting loyalty
        if self.layout.loyalty:
            self.loyalty_text.textItem.contents = self.layout.loyalty
        else:
            self.loyalty_text.parent.visible = False

        # Call to super for name, type, etc
        super().basic_text_layers()

    def enable_frame_layers(self):

        # Enable twins, pinlines, background, color indicator
        if self.twins_layer:
            self.twins_layer.visible = True
        if self.pinlines_layer:
            self.pinlines_layer.visible = True
        if self.background_layer:
            self.background_layer.visible = True
        if self.type_line_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

    def post_text_layers(self):
        """
        Auto-position the ability text, colons, and shields.
        """
        # Core vars
        spacing = 64 * (self.app.activeDocument.width / 3264)
        spaces = len(self.ability_layers) + 1
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        total_height = ref_height - (spacing * spaces)

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Space abilities evenly apart
        uniform_gap = True if len(self.ability_layers) < 3 or not self.layout.loyalty else False
        psd.spread_layers_over_reference(
            self.ability_layers,
            self.textbox_reference,
            spacing if not uniform_gap else None
        )

        # Adjust text to avoid loyalty badge
        if self.layout.loyalty:
            ft.vertically_nudge_pw_text(
                self.ability_layers,
                self.textbox_reference,
                self.adj_ref,
                self.top_ref,
                spacing,
                uniform_gap=uniform_gap
            )

        # Align colons and shields to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):
            # Break if we encounter a length mismatch
            if len(self.shields) < (i + 1) or len(self.colons) < (i + 1):
                self.raise_warning("Encountered bizarre Planeswalker data!")
                break
            # Skip if this is a passive ability
            if self.shields[i] and self.colons[i]:
                before = self.colons[i].bounds[1]
                psd.align_vertical(self.colons[i], reference=ref_layer)
                psd.clear_selection()
                difference = self.colons[i].bounds[1] - before
                self.shields[i].translate(0, difference)

        # Add the ability layer mask
        self.pw_ability_mask()

    def pw_ability_mask(self):
        """
        Position the ragged edge ability mask.
        """

        # Ragged line layers
        lines = psd.getLayerSet("Ragged Lines", [self.group, LAYERS.TEXTBOX, "Ability Dividers"])
        line1_top = psd.getLayer("Line 1 Top", lines)
        line1_bottom = psd.getLayer("Line 1 Bottom", lines)
        line1_top_ref = psd.getLayer("Line 1 Top Reference", lines)
        line1_bottom_ref = psd.getLayer("Line 1 Bottom Reference", lines)
        line1_top.visible = True
        line1_bottom.visible = True

        # Additional for 4 Abilities
        if len(self.ability_layers) == 4:
            line2_top = psd.getLayer("Line 2 Top", lines)
            line2_bottom = psd.getLayer("Line 2 Bottom", lines)
            line2_ref = psd.getLayer("Line 2 Reference", lines)
            line2_top.visible = True
            line2_bottom.visible = True
        else:
            line2_top, line2_bottom, line2_ref = None, None, None

        # Position needed ragged lines
        if len(self.ability_layers) > 2:
            # 3+ Ability Planeswalker
            self.position_divider_line([self.ability_layers[0], self.ability_layers[1]], line1_top, line1_top_ref)
            self.position_divider_line([self.ability_layers[1], self.ability_layers[2]], line1_bottom, line1_bottom_ref)
        else:
            # 2 Ability Planeswalker
            self.position_divider_line([self.ability_layers[0], self.ability_layers[1]], line1_top, line1_top_ref)
        if line2_top and line2_ref:
            # 4 Ability Planeswalker
            self.position_divider_line([self.ability_layers[2], self.ability_layers[3]], line2_top, line2_ref)

        # Fill between the ragged lines
        if len(self.ability_layers) > 2:
            # 3+ Ability Planeswalker
            self.fill_between_dividers(line1_top, line1_bottom)
        else:
            # 2 Ability Planeswalker
            line1_bottom.translate(0, 1000)
            self.fill_between_dividers(line1_top, line1_bottom)
        if line2_top and line2_bottom:
            # 4 Ability Planeswalker
            self.fill_between_dividers(line2_top, line2_bottom)

    @staticmethod
    def position_divider_line(layers: list[ArtLayer], line: ArtLayer, line_ref: ArtLayer):
        """
        Positions a ragged divider line correctly.
        @param layers: Two layers to position the line between.
        @param line: Line layer to be positioned.
        @param line_ref: Reference line layer to help position the ragged line.
        """
        dif = (layers[1].bounds[1] - layers[0].bounds[3]) / 2
        ref_pos = (line_ref.bounds[3] + line_ref.bounds[1]) / 2
        targ_pos = dif + layers[0].bounds[3]
        line.translate(0, (targ_pos - ref_pos))

    def fill_between_dividers(self, line1: ArtLayer, line2: ArtLayer):
        """
        Fill area between two ragged lines.
        @param line1: The top ragged line layer.
        @param line2: The bottom ragged line layer.
        """
        self.active_layer = self.docref.artLayers.add()
        self.active_layer.move(line1, ElementPlacement.PlaceAfter)
        self.docref.selection.select([
            [line1.bounds[0] - 200, line1.bounds[3]],
            [line1.bounds[2] + 200, line1.bounds[3]],
            [line1.bounds[2] + 200, line2.bounds[1]],
            [line1.bounds[0] - 200, line2.bounds[1]]
        ])
        fill_color = psd.rgb_black()
        self.docref.selection.expand(1)
        self.docref.selection.fill(
            fill_color, ColorBlendMode.NormalBlendColor, 100, False
        )
        psd.clear_selection()


class PlaneswalkerExtendedTemplate (PlaneswalkerTemplate):
    """
    An extended version of PlaneswalkerTemplate. Functionally identical except for the lack of background textures.
    No background, fill empty area for art layer.
    """
    template_suffix = "Extended"

    @property
    def art_reference(self) -> str:
        return LAYERS.PLANESWALKER_ART_FRAME

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


class PlaneswalkerMDFCTemplate (PlaneswalkerTemplate):
    """
    Template for modal double faced Planeswalker cards.
    Need to enable MDFC layers and add MDFC text.
    """

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.LEFT, self.dfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.RIGHT, self.dfc_group)

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.NAME, self.text_layers)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add mdfc text layers
        self.text.extend([
            text_classes.FormattedTextField(
                layer=self.text_layer_mdfc_right,
                contents=self.layout.other_face_right
            ),
            text_classes.ScaledTextField(
                layer=self.text_layer_mdfc_left,
                contents=self.layout.other_face_left,
                reference=self.text_layer_mdfc_right,
            )
        ])

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add special MDFC layers
        psd.getLayer(self.twins,
                     psd.getLayerSet(LAYERS.TOP, self.dfc_group)).visible = True
        psd.getLayer(self.layout.other_face_twins,
                     psd.getLayerSet(LAYERS.BOTTOM, self.dfc_group)).visible = True


class PlaneswalkerMDFCExtendedTemplate (PlaneswalkerMDFCTemplate):
    """
    An extended version of Planeswalker MDFC template.
    No background, fill empty area for art layer.
    """
    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


class PlaneswalkerTransformTemplate (PlaneswalkerTemplate):
    """
    Template for the back faces of transform cards.
    """
    template_file_name = "pw-tf-back"

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.NAME, self.text_layers)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(LAYERS.TYPE_LINE, self.text_layers)

    @cached_property
    def transform_icon(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.transform_icon, self.dfc_group)

    def enable_frame_layers(self):
        # Add the transform icon
        super().enable_frame_layers()
        self.transform_icon.visible = True


class PlaneswalkerTransformExtendedTemplate (PlaneswalkerTransformTemplate):
    """
    An extended version of Planeswalker MDFC Back template.
    No background, fill empty area for art layer.
    """
    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


"""
Misc. Templates
"""


class PlanarTemplate (StarterTemplate):
    """
    Planar template for Planar/Phenomenon cards
    """

    def __init__(self, layout: CardLayout):
        cfg.exit_early = True
        super().__init__(layout)

    @cached_property
    def text_layer_static_ability(self) -> ArtLayer:
        return psd.getLayer(LAYERS.STATIC_ABILITY, self.text_layers)

    @cached_property
    def text_layer_chaos_ability(self) -> ArtLayer:
        return psd.getLayer(LAYERS.CHAOS_ABILITY, self.text_layers)

    def basic_text_layers(self):

        # Add text layers
        self.text.extend([
            text_classes.TextField(
                layer = self.text_layer_name,
                contents = self.layout.name
            ),
            text_classes.ScaledTextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line,
                reference = self.expansion_symbol_layer
            )
        ])

    def rules_text_and_pt_layers(self):

        # Phenomenon card?
        if self.layout.type_line == LAYERS.PHENOMENON:

            # Insert oracle text into static ability layer and disable chaos ability & layer mask on textbox
            self.text.append(
                text_classes.FormattedTextField(
                    layer = self.text_layer_static_ability,
                    contents = self.layout.oracle_text
                )
            )
            psd.enable_mask(psd.getLayerSet(LAYERS.TEXTBOX))
            psd.getLayer(LAYERS.CHAOS_SYMBOL, self.text_layers).visible = False
            self.text_layer_chaos_ability.visible = False

        else:

            # Split oracle text on last line break, insert everything before into static, the rest into chaos
            linebreak_index = self.layout.oracle_text.rindex("\n")
            self.text.extend([
                text_classes.FormattedTextField(
                    layer = self.text_layer_static_ability,
                    contents = self.layout.oracle_text[0:linebreak_index]
                ),
                text_classes.FormattedTextField(
                    layer = self.text_layer_chaos_ability,
                    contents = self.layout.oracle_text[linebreak_index+1:]
                ),
            ])

    def paste_scryfall_scan(
            self, reference_layer: Optional[ArtLayer] = None, rotate: bool = False, visible: bool = False
    ) -> Optional[ArtLayer]:
        # Rotate the scan
        return super().paste_scryfall_scan(reference_layer, True, visible)


"""
Basic land Templates
"""


class BasicLandTemplate (BaseTemplate):
    """
    Basic land template - no text and icons (aside from legal), just a layer for each of the eleven basic lands.
    """

    def __init__(self, layout: CardLayout):
        cfg.save_artist_name = True
        cfg.real_collector = False
        super().__init__(layout)

    @property
    def art_reference(self) -> str:
        return LAYERS.BASIC_ART_FRAME

    @cached_property
    def text_layers(self) -> Optional[LayerSet]:
        return self.docref

    def enable_frame_layers(self):
        psd.getLayer(self.layout.name).visible = True


class BasicLandUnstableTemplate (BasicLandTemplate):
    """
    Basic land template for the borderless basics from Unstable.
    Doesn't have expansion symbol.
    """
    template_suffix = "Unstable"

    def expansion_symbol(self):
        pass

    def basic_text_layers(self):
        pass


class BasicLandTherosTemplate (BasicLandTemplate):
    """
    Basic land template for the full-art Nyx basics from Theros: Beyond Death.
    """
    template_suffix = "Theros"


class BasicLandClassicTemplate (BasicLandTemplate):
    """
    Basic land template for 7th Edition basics.
    """

    @cached_property
    def template_suffix(self) -> str:
        if self.promo_star:
            return "Promo Classic"
        return "Classic"

    @property
    def promo_star(self) -> str:
        return cfg.get_setting(
            section="FRAME",
            key="Promo.Star",
            default=False
        )

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add the promo star
        if self.promo_star:
            psd.getLayerSet("Promo Star").visible = True


"""
TOKEN TEMPLATES
"""


class TokenTemplate(StarterTemplate):
    """
    Core template class for Tokens.
    """

    """
    LAYERS
    """

    @property
    def art_reference_layer(self) -> ArtLayer:
        return psd.getLayer(LAYERS.ART_FRAME)

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.pinlines, [
            LAYERS.FRAME,
            LAYERS.LEGENDARY if self.is_legendary else LAYERS.NON_LEGENDARY,
            LAYERS.CREATURE if self.is_creature else LAYERS.NON_CREATURE
        ])

    @cached_property
    def textbox_group(self) -> LayerSet:
        # No Rules Text
        if not self.layout.oracle_text and not self.layout.flavor_text:
            group = LAYERS.NONE
        # One Line Rules Text
        elif not any(is_multiline([self.layout.oracle_text, self.layout.flavor_text])) and (
            not self.layout.oracle_text or not self.layout.flavor_text
        ):
            group = LAYERS.ONE_LINE
        # Full Sized Rules Text
        else:
            group = LAYERS.FULL
        group = psd.getLayerSet(group, LAYERS.TEXTBOX)
        group.visible = True
        return group

    """
    REFERENCES
    """

    @cached_property
    def type_line_reference(self) -> ArtLayer:
        # Reference to scale the Type Line
        return psd.getLayer(LAYERS.TYPE_LINE_REFERENCE, self.textbox_group)

    @cached_property
    def name_reference(self) -> ArtLayer:
        # Reference to scale the Type Line
        if self.is_legendary:
            return psd.getLayer(LAYERS.NAME_REFERENCE_LEGENDARY, self.text_layers)
        return psd.getLayer(LAYERS.NAME_REFERENCE_NON_LEGENDARY, self.text_layers)

    @cached_property
    def rules_reference(self) -> Optional[ArtLayer]:
        # Reference to scale the rules text
        return psd.getLayer(LAYERS.TEXTBOX_REFERENCE, self.textbox_group)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_type(self) -> ArtLayer:
        return psd.getLayer(LAYERS.TYPE_LINE, self.textbox_group)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        if self.textbox_group.name == LAYERS.FULL and self.is_creature:
            return psd.getLayer(LAYERS.RULES_TEXT_CREATURE, self.textbox_group)
        if self.textbox_group.name == LAYERS.FULL:
            return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.textbox_group)
        return psd.getLayer(LAYERS.RULES_TEXT, self.textbox_group)

    """
    METHODS
    """

    def expansion_symbol(self) -> None:
        pass

    def enable_frame_layers(self) -> None:
        if self.background_layer:
            self.background_layer.visible = True

    def basic_text_layers(self) -> None:
        self.text.extend([
            text_classes.ScaledWidthTextField(
                layer = self.text_layer_name,
                contents = self.layout.name,
                reference = self.name_reference
            ),
            text_classes.ScaledWidthTextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line,
                reference = self.type_line_reference
            )
        ])

    def rules_text_and_pt_layers(self) -> None:
        # Adjust the default linebreak lead
        con.line_break_lead = 3

        # Rules Text
        if self.textbox_group.name == LAYERS.ONE_LINE:
            self.text.append(
                text_classes.FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    color=psd.rgb_white(),
                    flavor=self.layout.flavor_text,
                    reference=self.rules_reference,
                    scale_height=False,
                    scale_width=True
                )
            )
        if self.textbox_group.name == LAYERS.FULL:
            self.text.append(
                text_classes.FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    color=psd.rgb_white(),
                    flavor=self.layout.flavor_text,
                    reference=self.rules_reference
                )
            )
        # PT Layer
        if self.is_creature:
            # Enable cutout
            psd.enable_vector_mask(self.textbox_group.parent)
            self.text.append(
                text_classes.TextField(
                    layer=self.text_layer_pt,
                    contents=f"{self.layout.power}/{self.layout.toughness}"
                )
            )
        else:
            self.text_layer_pt.visible = False

    def post_text_layers(self) -> None:
        # Need to vertically center the name after it's been scaled
        psd.align_vertical(self.text_layer_name, self.name_reference)


"""
[EXPERIMENTAL TEMPLATES]
*   These are templates which use a layer structure that substantially diverges from the typical Proxyshop workflow.

*   I have been experimenting with using vector shapes to create the frame elements and clipping layers to apply 
colors and textures to the shapes.

*   This methodology was popularized by Silvan MTG and Chilli, its often the basis of a master template that later 
becomes rasterized to make the automation workflow quicker. However, leaving the vector shapes in-tact can improve 
overall quality and maintainability over time, and can allow the same template to be used for a variety of card types.

*   Having the textures applied as a list of clipping masks can cut down on layers and document size, instead we 
generate dual colors by automating the combination of these layers with a blended gradient.

*   Right now these documents have incredible quality, but automated execution time takes a couple seconds longer.
"""


class UniversesBeyondTemplate (NormalTemplate):
    """
    Template used for crossover sets like WH40K, Transformers, Street Fighter, etc.
    This template is built using the Silvan style of creating vector shapes and applying the colors
    and textures in the form of clipping masks. It's a little more involved, but it demonstrates
    an alternative way to build a highly complex template which can work for multiple card types.
    Credit to Kyle of Card Conjurer, WarpDandy, SilvanMTG, Chilli and MrTeferi.
    """
    template_suffix = "Universes Beyond"

    @property
    def is_nyx(self) -> bool:
        # Disable Nyx
        return False

    """
    LAYERS
    """

    @cached_property
    def mask_layer(self) -> ArtLayer:
        # This layer contains the gradient mask for creating dual colors
        return self.docref.artLayers.getByName("Mask")

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return self.pinlines_group.artLayers.getByName(self.pinlines)

    @cached_property
    def textbox_layer(self) -> Optional[ArtLayer]:
        return self.textbox_group.artLayers.getByName(self.pinlines)

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Support Vehicle, regular layers, and back side darkened layers
        if self.background == 'Vehicle':
            return psd.getLayer(self.background, LAYERS.PT_BOX)
        if self.is_front:
            return psd.getLayer(self.twins, LAYERS.PT_BOX)
        return psd.getLayer(f'{self.twins} Back', LAYERS.PT_BOX)

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # Is this a creature?
        if self.is_creature:
            # Flipside P/T?
            if self.other_face_is_creature and self.layout.transform_icon:
                return psd.getLayer(LAYERS.RULES_TEXT_CREATURE_FLIP, self.text_layers)
            return psd.getLayer(LAYERS.RULES_TEXT_CREATURE, self.text_layers)
        self.text_layer_pt.visible = False

        # Not a creature, Flipside P/T?
        if self.other_face_is_creature and self.layout.transform_icon:
            return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE_FLIP, self.text_layers)
        return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE, self.text_layers)

    """
    GROUPS
    """

    @cached_property
    def twins_group(self) -> LayerSet:
        return self.docref.layerSets.getByName(LAYERS.TWINS)

    @cached_property
    def pinlines_group(self) -> LayerSet:
        return self.docref.layerSets.getByName(LAYERS.PINLINES)

    @cached_property
    def textbox_group(self) -> LayerSet:
        return self.docref.layerSets.getByName(LAYERS.TEXTBOX)

    @cached_property
    def background_group(self) -> LayerSet:
        return self.docref.layerSets.getByName(LAYERS.BACKGROUND)

    @cached_property
    def crown_group(self) -> LayerSet:
        return self.docref.layerSets.getByName(LAYERS.LEGENDARY_CROWN)

    """
    SHAPES
    """

    @cached_property
    def pinlines_shape_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet("Shape", self.pinlines_group)

    @cached_property
    def textbox_shape_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet("Shape", self.textbox_group)

    @cached_property
    def twins_shape_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet("Shape", self.twins_group)

    """
    METHODS
    """

    def enable_frame_layers(self) -> None:

        # Twins
        if self.twins_layer:
            self.twins_layer.visible = True
            if self.twins == "Colorless":
                psd.set_fill_opacity(60, self.twins_group)

        # PT Box
        if self.is_creature and self.pt_layer:
            self.pt_layer.parent.visible = True
            self.pt_layer.visible = True

        # Color Indicator
        if self.type_line_shifted and self.color_indicator_layer:
            self.color_indicator_layer.visible = True

        # Pinlines
        if len(self.pinlines) != 2 and self.pinlines_layer and self.textbox_layer:
            self.textbox_layer.visible = True
            self.pinlines_layer.visible = True
            if self.pinlines == "Colorless":
                psd.set_fill_opacity(60, self.textbox_group)
        else:
            # Generate dual color layers
            self.create_dual_layer(self.pinlines, self.pinlines_group, self.mask_layer)
            self.create_dual_layer(self.pinlines, self.textbox_group, self.mask_layer)

        # Background layer
        if len(self.background) != 2 and self.background_layer:
            self.background_layer.visible = True
        else:
            # Generate dual color layer
            self.create_dual_layer(self.background, self.background_group, self.mask_layer)

        # Legendary crown
        if self.is_legendary:
            self.enable_crown()

        # Transform alterations
        if self.is_transform:
            self.enable_transform_layers()
        else:
            # Add normal mask to Pinlines
            psd.copy_layer_mask(psd.getLayer('Normal Mask', self.pinlines_group), self.pinlines_group)

    def enable_transform_layers(self):
        """
        Make any changes that are required by Transform cards.
        """
        # Enable transform icon
        psd.getLayerSet('Circle', self.text_layers).visible = True
        self.transform_icon.visible = True

        # Add transform mask to Textbox
        if self.is_front:
            # Use TF Front mask, TF Front/Transform shapes
            psd.copy_layer_mask(self.pinlines_group.layers.getByName('TF Front Mask'), self.pinlines_group)
            self.pinlines_shape_group.layers.getByName('TF Front').visible = True
            self.textbox_shape_group.layers.getByName('TF Front').visible = True
            self.twins_shape_group.layers.getByName('Transform').visible = True
            self.pinlines_shape_group.layers.getByName('Normal').visible = False
            self.textbox_shape_group.layers.getByName('Normal').visible = False
            self.twins_shape_group.layers.getByName('Normal').visible = False

            # Add flipside PT if needed
            if self.other_face_is_creature:
                self.text.append(
                    text_classes.TextField(
                        layer=psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_layers),
                        contents=str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness)
                    )
                )
        else:
            # Use Normal mask, TF Back/Transform shapes, and back side darker colors
            psd.copy_layer_mask(self.pinlines_group.layers.getByName('Normal Mask'), self.pinlines_group)
            self.pinlines_shape_group.layers.getByName('TF Back').visible = True
            self.twins_shape_group.layers.getByName('Transform').visible = True
            self.pinlines_shape_group.layers.getByName('Normal').visible = False
            self.twins_shape_group.layers.getByName('Normal').visible = False

            # Change Name, Type, and PT to white with shadow for non-Eldrazi backs
            if self.layout.transform_icon != LAYERS.DFC_MOONELDRAZI:
                psd.enable_layer_fx(self.text_layer_name)
                psd.enable_layer_fx(self.text_layer_type)
                psd.enable_layer_fx(self.text_layer_pt)
                self.text_layer_name.textItem.color = psd.rgb_white()
                self.text_layer_type.textItem.color = psd.rgb_white()
                self.text_layer_pt.textItem.color = psd.rgb_white()
                psd.getLayerSet('Back', self.twins_group).visible = True
                psd.getLayer('Back', self.textbox_group).visible = True

    def enable_crown(self) -> None:
        # Enable Legendary Crown group
        self.crown_group.visible = True

        # Crown layer
        if len(self.pinlines) != 2 and self.crown_layer:
            self.crown_layer.visible = True
        else:
            # Generate dual color layer
            self.create_dual_layer(self.pinlines, self.crown_group, self.mask_layer)

        # Change border
        psd.getLayer(LAYERS.NORMAL_BORDER, self.border_group).visible = False
        psd.getLayer(LAYERS.LEGENDARY_BORDER, self.border_group).visible = True

        # Enable Legendary pinline connector
        psd.getLayer("Legendary Pinlines", self.pinlines_shape_group).visible = True
