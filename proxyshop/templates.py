"""
CORE TEMPLATES
"""
import os
import re
from functools import cached_property
from typing import Optional, Callable

from PIL import Image
from photoshop.api.application import ArtLayer, Photoshop
from photoshop.api._layerSet import LayerSet

from proxyshop.frame_logic import format_expansion_symbol_info
import proxyshop.text_layers as text_classes
import proxyshop.format_text as ft
from proxyshop.constants import con
from proxyshop.settings import cfg
import proxyshop.helpers as psd
from photoshop import api as ps
from proxyshop.__console__ import console


class BaseTemplate:
    """
    Set up variables for things which are common to all templates, extend this at bare minimum.
    """
    template_file_name = ""
    template_suffix = ""

    def __init__(self, layout):

        # Setup manual properties
        self.layout = layout
        self.tx_layers = []
        self.exp_sym = None

        # Load PSD file
        try:
            self.load_template()
        except Exception as e:
            console.log_error(
                "PSD failed to load!",
                self.layout.name,
                self.template_file,
                e
            )

        # Remove flavor or reminder text
        if cfg.remove_flavor:
            self.layout.flavor_text = ""
        if cfg.remove_reminder:
            self.layout.oracle_text = ft.strip_reminder_text(layout.oracle_text)

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
    def name_shifted(self) -> bool:
        # Use right shifted name?
        return bool(self.layout.transform_icon)

    @property
    def type_line_shifted(self) -> bool:
        # Use right shifted typeline? Also governs color indicator input
        return bool(self.layout.color_indicator)

    @cached_property
    def is_centered(self) -> bool:
        # Center the rules text
        return bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
        )

    @cached_property
    def other_face_is_creature(self) -> bool:
        # Governs transform cards other side creature P/T
        return self.layout.other_face_power and self.layout.other_face_toughness

    """
    DOCUMENT PROPERTIES
    """

    @cached_property
    def app(self) -> Photoshop:
        return ps.Application()

    @cached_property
    def template_file(self) -> str:
        # Get from callable
        if callable(self.template_file_name):
            fn = self.template_file_name()
            if fn[-4:] not in (".psd", ".psb"):
                return f"{fn}.psd"
            return fn
        # Get from attribute
        fn = self.template_file_name
        if fn[-4:] not in (".psd", ".psb"):
            return f"{fn}.psd"
        return fn

    @cached_property
    def docref(self):
        # The current template document
        return self.app.activeDocument

    @property
    def active_layer(self):
        # Current active layer
        return self.docref.activeLayer

    @active_layer.setter
    def active_layer(self, value):
        # Set the active layer
        self.docref.activeLayer = value

    @property
    def art_layer(self) -> ArtLayer:
        # The MTG art layer
        return psd.getLayer(con.default_layer)

    @property
    def art_action(self) -> Optional[Callable]:
        return None

    @property
    def art_action_args(self) -> Optional[dict]:
        return None

    @property
    def art_reference(self) -> str:
        return con.layers.ART_FRAME

    @cached_property
    def art_reference_layer(self) -> ArtLayer:
        # Select a main reference layer
        if isinstance(self.art_reference, ArtLayer):
            # Art reference given as a layer
            layer = self.art_reference
        else:
            # Art reference given as a string
            layer = psd.getLayer(self.art_reference)
            if not layer:
                psd.getLayer(con.layers.ART_FRAME)

        # Check if we can change to fullart reference
        if not any(map(str(layer.name).__contains__, ["Full Art", "Fullart"])):
            # Auto detect full art image
            with Image.open(self.layout.filename) as image:
                width, height = image.size
            if height > (width * 1.2):
                fa_frame = psd.getLayer(con.layers.FULL_ART_FRAME)
                if fa_frame:
                    return fa_frame
        return layer

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
    TEXT LAYERS
    """

    @cached_property
    def legal_layer(self) -> Optional[LayerSet]:
        # Legal group
        return psd.getLayerSet(con.layers.LEGAL)

    @cached_property
    def creator_layer(self) -> Optional[ArtLayer]:
        # Creator name layer
        return psd.getLayer("Creator", self.legal_layer)

    @cached_property
    def text_layers(self) -> Optional[LayerSet]:
        # Text and icon group
        return psd.getLayerSet(con.layers.TEXT_AND_ICONS)

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # CARD NAME
        if self.name_shifted:
            psd.getLayer(con.layers.NAME, self.text_layers).visible = False
            name = psd.getLayer(con.layers.NAME_SHIFT, self.text_layers)
            name.visible = True
            return name
        return psd.getLayer(con.layers.NAME, self.text_layers)

    @cached_property
    def text_layer_mana(self) -> Optional[ArtLayer]:
        # CARD MANA COST
        return psd.getLayer(con.layers.MANA_COST, self.text_layers)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # CARD TYPELINE
        if self.type_line_shifted:
            psd.getLayer(con.layers.TYPE_LINE, self.text_layers).visible = False
            typeline = psd.getLayer(con.layers.TYPE_LINE_SHIFT, self.text_layers)
            typeline.visible = True
            return typeline
        return psd.getLayer(con.layers.TYPE_LINE, self.text_layers)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # CARD RULES TEXT
        if self.is_creature:
            rules_text = psd.getLayer(con.layers.RULES_TEXT_CREATURE, self.text_layers)
            rules_text.visible = True
            return rules_text
        # Noncreature card - use the normal rules text layer and disable the p/t layer
        if self.text_layer_pt:
            self.text_layer_pt.visible = False
        return psd.getLayer(con.layers.RULES_TEXT_NONCREATURE, self.text_layers)

    @cached_property
    def text_layer_pt(self) -> Optional[ArtLayer]:
        # CARD POWER/TOUGHNESS
        return psd.getLayer(con.layers.POWER_TOUGHNESS, self.text_layers)

    """
    FRAME LAYERS
    """

    @cached_property
    def symbol(self) -> str:
        # Expansion symbol
        return self.layout.symbol

    @cached_property
    def twins(self) -> str:
        # Name of the Twins layer
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
    def twins_layer(self) -> Optional[ArtLayer]:
        # Twins
        return psd.getLayer(self.twins, con.layers.TWINS)

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Pinlines
        if self.is_land:
            return psd.getLayer(self.pinlines, con.layers.LAND_PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, con.layers.PINLINES_TEXTBOX)

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        # Background
        if self.is_nyx:
            return psd.getLayer(self.background, con.layers.NYX)
        return psd.getLayer(self.background, con.layers.BACKGROUND)

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        # Color Indicator
        return psd.getLayer(self.pinlines, con.layers.COLOR_INDICATOR)

    @cached_property
    def crown_layer(self) -> Optional[ArtLayer]:
        # Legendary Crown
        return psd.getLayer(self.pinlines, con.layers.LEGENDARY_CROWN)

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Power/Toughness box
        return psd.getLayer(self.twins, con.layers.PT_BOX)

    @cached_property
    def companion_layer(self) -> Optional[ArtLayer]:
        # Companion inner crown
        return psd.getLayer(self.pinlines, con.layers.COMPANION)

    @property
    def expansion_symbol(self) -> Optional[ArtLayer]:
        # CARD EXPANSION SYMBOL
        return self.exp_sym

    @expansion_symbol.setter
    def expansion_symbol(self, value):
        self.exp_sym = value

    """
    METHODS
    """

    def collector_info(self) -> None:
        """
        Format and add the collector info at the bottom.
        """
        # Ignore this step if legal layer not present
        if not self.legal_layer:
            return

        # If creator is specified add the text
        if self.layout.creator and self.creator_layer:
            self.creator_layer.textItem.contents = self.layout.creator

        # Use realistic collector information?
        if all([self.layout.collector_number, self.layout.rarity, cfg.real_collector]):

            # Reveal collector group, hide old layers
            collector_layer = psd.getLayerSet(con.layers.COLLECTOR, con.layers.LEGAL)
            collector_layer.visible = True
            psd.getLayer("Artist", self.legal_layer).visible = False
            psd.getLayer("Set", self.legal_layer).visible = False
            try:
                psd.getLayer("Pen", self.legal_layer).visible = False
            except AttributeError:
                pass

            # Get the collector layers
            collector_top = psd.getLayer(con.layers.TOP_LINE, collector_layer).textItem
            collector_bottom = psd.getLayer(con.layers.BOTTOM_LINE, collector_layer)

            # Fill in language if needed
            if self.layout.lang != "en":
                psd.replace_text(collector_bottom, "EN", self.layout.lang.upper())

            # Apply the collector info
            if self.layout.card_count:
                collector_top.contents = \
                    f"{self.layout.collector_number}/{self.layout.card_count} {self.layout.rarity_letter}"
            else:
                collector_top.contents = \
                    f"{self.layout.collector_number} {self.layout.rarity_letter}"
            psd.replace_text(collector_bottom, "SET", self.layout.set)
            psd.replace_text(collector_bottom, "Artist", self.layout.artist)

        else:

            # Layers we need
            set_layer = psd.getLayer("Set", self.legal_layer)
            artist_layer = psd.getLayer(con.layers.ARTIST, self.legal_layer)

            # Fill in language if needed
            if self.layout.lang != "en":
                psd.replace_text(set_layer, "EN", self.layout.lang.upper())

            # Fill set info / artist info
            set_layer.textItem.contents = self.layout.set + set_layer.textItem.contents
            psd.replace_text(artist_layer, "Artist", self.layout.artist)

        # Generate the expansion symbol
        self.create_expansion_symbol()

    @property
    def expansion_symbol_anchor(self) -> ps.AnchorPosition:
        return ps.AnchorPosition.MiddleRight

    def create_expansion_symbol(self, centered=False) -> None:
        """
        Builds the expansion symbol
        @param centered: Center the symbol within its reference.
        """
        # Colors to use for given settings
        colors = {
            "black": psd.rgb_black(),
            "white": psd.rgb_white(),
            "rarity": psd.rgb_black(),
        }

        # Starting rarity layer
        rarity = self.layout.rarity
        if self.layout.rarity in (con.rarity_bonus, con.rarity_special):
            rarity = con.rarity_mythic

        # Starting symbol, reference, and rarity layers
        symbol_layer = psd.getLayer(con.layers.EXPANSION_SYMBOL, self.text_layers)
        ref_layer = psd.getLayer(con.layers.EXPANSION_REFERENCE, self.text_layers)
        rarity_layer = psd.getLayer(rarity, self.text_layers)
        current_layer = symbol_layer

        # Put everything in a group
        group = self.app.activeDocument.layerSets.add()
        group.move(current_layer, ps.ElementPlacement.PlaceAfter)
        symbol_layer.move(group, ps.ElementPlacement.PlaceInside)

        # Set the starting character and format our layer array
        symbol_layer.textItem.contents, symbols = format_expansion_symbol_info(self.layout.symbol)

        # Size to fit reference?
        if cfg.auto_symbol_size:
            psd.frame_layer(symbol_layer, ref_layer, self.expansion_symbol_anchor, True, centered)

        def apply_rarity(layer) -> ArtLayer:
            # Apply rarity gradient to this layer
            mask_layer = rarity_layer.duplicate(layer, ps.ElementPlacement.PlaceBefore)
            mask_layer.grouped = True
            mask_layer.visible = True
            psd.select_layer_bounds(layer)
            self.app.activeDocument.activeLayer = mask_layer
            psd.align_horizontal()
            psd.align_vertical()
            psd.clear_selection()
            layer = psd.merge_layers([mask_layer, layer])
            return layer

        def apply_fill(layer, color=psd.rgb_black()):
            # Make active and fill background
            self.app.activeDocument.activeLayer = layer
            return psd.fill_expansion_symbol(ref_layer, color)

        def get_color_choice(color):
            # Figure out what color to use
            if isinstance(color, str) and color in colors:
                return colors[color]
            if isinstance(color, list) and len(color) == 3:
                return psd.get_rgb(color[0], color[1], color[2])
            if isinstance(color, list) and len(color) == 4:
                return psd.get_cmyk(color[0], color[1], color[2], color[3])
            return colors['black']

        # Create each symbol layer
        for i, lay in enumerate(symbols):
            # Establish new current layer
            current_layer = symbol_layer.duplicate(current_layer, ps.ElementPlacement.PlaceAfter)
            current_layer.textItem.contents = lay['char']

            # Non-common or Common traits
            if rarity != con.rarity_common:
                # Color replace
                if lay['color']:
                    current_layer.textItem.color = get_color_choice(lay['color'])

                # Stroke
                if lay['stroke']:
                    psd.apply_stroke(current_layer, lay['stroke'][1], get_color_choice(lay['stroke'][0]))
                else:
                    psd.clear_layer_style(current_layer)

                # Apply background fill
                if lay['fill'] == 'rarity':
                    # Apply fill before rarity
                    psd.rasterize_layer_style(current_layer)
                    fill_layer = apply_fill(current_layer, get_color_choice(lay['fill']))
                    fill_layer = apply_rarity(fill_layer)
                    current_layer = psd.merge_layers([current_layer, fill_layer])
                else:
                    # Apply fill after rarity
                    if lay['rarity']:
                        current_layer = apply_rarity(current_layer)
                    psd.rasterize_layer_style(current_layer)
                    if lay['fill']:
                        fill_layer = apply_fill(current_layer, get_color_choice(lay['fill']))
                        current_layer = psd.merge_layers([current_layer, fill_layer])

            else:
                # Common color
                if lay['common-color']:
                    current_layer.textItem.color = get_color_choice(lay['common-color'])

                # Common stroke
                if lay['common-stroke']:
                    psd.apply_stroke(current_layer, lay['common-stroke'][1], get_color_choice(lay['common-stroke'][0]))
                else:
                    psd.clear_layer_style(current_layer)

                # Common fill
                psd.rasterize_layer_style(current_layer)
                if lay['common-fill']:
                    fill_layer = apply_fill(current_layer, get_color_choice(lay['common-fill']))
                    current_layer = psd.merge_layers([current_layer, fill_layer])

            # Scale factor
            if lay['scale-factor'] != 1:
                current_layer.resize(lay['scale-factor']*100, lay['scale-factor']*100, ps.AnchorPosition.MiddleRight)

        # Merge all
        symbol_layer.move(group, ps.ElementPlacement.PlaceBefore)
        symbol_layer.name = "Expansion Symbol Old"
        symbol_layer.opacity = 0
        self.expansion_symbol = group.merge()
        self.expansion_symbol.name = "Expansion Symbol"

    def load_template(self) -> None:
        """
        Opens the template's PSD file in Photoshop.
        """
        # Create our full path and load it, set our document reference
        self.app.load(os.path.join(con.cwd, f"templates\\{self.template_file}"))

    def load_artwork(self) -> None:
        """
        Loads the specified art file into the specified layer.
        """
        # Choose image for dev_mode
        if cfg.dev_mode:
            # Check for Fullart test image
            dims = psd.get_layer_dimensions(self.art_reference_layer)
            if (dims['width'] * 1.2) < dims['height']:
                # Use fullart test image
                self.layout.filename = os.path.join(os.getcwd(), "proxyshop/img/test-fa.png")

        # Paste the file into the art
        self.active_layer = self.art_layer
        if self.art_action:
            psd.paste_file(self.art_layer, self.layout.filename, self.art_action, self.art_action_args)
        else:
            psd.import_art(self.art_layer, self.layout.filename)

        # Frame the artwork
        psd.frame_layer(self.active_layer, self.art_reference_layer)

    def get_file_name(self) -> str:
        """
        Format the output filename.
        Overwrite this function if your template has specific demands.
        """
        # Establish the name
        suffix = self.template_suffix
        if cfg.save_artist_name:
            suffix = f"{suffix} {self.layout.artist}" if suffix else self.layout.artist
        name = f"{self.layout.name_raw} ({suffix})" if suffix else self.layout.name_raw

        # Check if name already exists
        if not cfg.overwrite_duplicate:
            num = 0
            while os.path.exists(os.path.join(con.cwd, f"out/{name}.{cfg.output_filetype}")):
                num += 1
                if ")" not in name:
                    name = f'{name} (1)'
                elif ")" in name and num == 1:
                    name = name.replace(f'({suffix})', f'({suffix} 1)')
                else:
                    name = name.replace(f'{num - 1})', f'{num})')
        return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", name)

    def paste_scryfall_scan(
        self, reference_layer: ArtLayer, rotate: bool = False, visible: bool = True
    ) -> Optional[ArtLayer]:
        """
        Downloads the card's scryfall scan, pastes it into the document next to the active layer,
        and frames it to fill the given reference layer. Can optionally rotate the layer by 90 degrees
        (useful for planar cards).
        """
        layer = psd.insert_scryfall_scan(self.layout.scryfall_scan)
        if layer:
            if rotate:
                layer.rotate(90)
            psd.frame_layer(layer, reference_layer)
            if not visible:
                layer.visible = False
        return layer

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

    def reset(self) -> None:
        """
        Reset the document, purge the cache, end await.
        """
        psd.reset_document(self.template_file)
        self.app.purge(4)
        console.end_await()

    def raise_error(self, message: str, error: Exception) -> bool:
        """
        Raise an error on the console display.
        @param message: Message to be displayed
        @param error: Exception object
        @return:
        """
        result = console.log_error(
            f"{message}\nCheck [b]/tmp/error.txt[/b] for details.",
            self.layout.name, self.template_file, error
        )
        self.reset()
        return result

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
        self.docref.info.urgency = ps.Urgency.High

        # Load in artwork and frame it
        try:
            self.load_artwork()
        except Exception as e:
            return self.raise_error("Unable to load artwork!", e)

        # Add collector info
        try:
            self.collector_info()
        except Exception as e:
            return self.raise_error("Unable to insert collector info!", e)

        # Add text layers
        try:
            self.basic_text_layers()
            self.rules_text_and_pt_layers()
        except Exception as e:
            return self.raise_error("Selecting text layers failed!", e)

        # Enable the layers we need
        try:
            self.enable_frame_layers()
        except Exception as e:
            return self.raise_error("Enabling layers failed!", e)

        # Input and format each text layer
        try:
            for this_layer in self.tx_layers:
                this_layer.execute()
        except Exception as e:
            return self.raise_error("Formatting text failed!", e)

        # Specific hooks
        try:
            if self.is_creature:
                self.hook_creature()
        except Exception as e:
            return self.raise_error("Encountered an error during triggered hooks step!", e)

        # Post text layer execution
        try:
            self.post_text_layers()
        except Exception as e:
            return self.raise_error("Post text formatting execution failed!", e)

        # Format file name
        file_name = self.get_file_name()

        # Manual edit step?
        if cfg.exit_early and not cfg.dev_mode:
            console.wait("Manual editing enabled!\nWhen you're ready to save, click continue...")
            console.update("Saving document...\n")

        # Save the document
        try:
            if cfg.output_filetype == "png":
                psd.save_document_png(file_name)
            elif cfg.output_filetype == "psd":
                psd.save_document_psd(file_name)
            else:
                psd.save_document_jpeg(file_name)
            if not cfg.dev_mode:
                console.update(f"[b]{file_name}[/b] rendered successfully!")
        except Exception as e:
            if not cfg.dev_mode:
                console.update(
                    f"Error during save process!\nMake sure the file was successfully saved.", e
                )

        # Post execution code
        try:
            self.post_execute()
        except Exception as e:
            return self.raise_error(
                "Post execution step failed! Image saved but other issues may have occurred.", e
            )

        # Reset document, return success
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
                reference = self.expansion_symbol
            )
        ])


class NormalTemplate (StarterTemplate):
    """
    Normal M15-style template.
    Extend this for most normal card templates that have typical MTG card layer setups.
    """
    template_file_name = "normal"

    @property
    def art_reference(self) -> str:
        # If colorless, use "Full Art Frame"
        if self.is_colorless:
            return con.layers.FULL_ART_FRAME
        return con.layers.ART_FRAME

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
                    reference = psd.getLayer(con.layers.TEXTBOX_REFERENCE, self.text_layers),
                    divider = psd.getLayer(con.layers.DIVIDER, self.text_layers),
                    pt_reference = psd.getLayer(con.layers.PT_REFERENCE, self.text_layers),
                    pt_top_reference = psd.getLayer(con.layers.PT_TOP_REFERENCE, self.text_layers),
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
                    reference = psd.getLayer(con.layers.TEXTBOX_REFERENCE, self.text_layers),
                    divider = psd.getLayer(con.layers.DIVIDER, self.text_layers),
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
        psd.getLayer(con.layers.NORMAL_BORDER, con.layers.BORDER).visible = False
        psd.getLayer(con.layers.LEGENDARY_BORDER, con.layers.BORDER).visible = True

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
            shadows = psd.getLayer(con.layers.SHADOWS)
        psd.enable_mask(self.crown_layer.parent)
        psd.enable_mask(self.pinlines_layer.parent)
        psd.enable_mask(shadows)
        psd.getLayer(con.layers.HOLLOW_CROWN_SHADOW).visible = True


class NormalClassicTemplate (StarterTemplate):
    """
    A template for 7th Edition frame. Lacks many of the Normal Template features.
    """
    template_file_name = "normal-classic"

    def __init__(self, layout):
        cfg.real_collector = False
        super().__init__(layout)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.RULES_TEXT, self.text_layers)

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

    def rules_text_and_pt_layers(self):
        # Move mana layer down for hybrid mana
        if len(self.background) == 2:
            self.text_layer_mana.translate(0, -5)

        # Text reference and rules text
        reference_layer = psd.getLayer(
            con.layers.TEXTBOX_REFERENCE_LAND if self.is_land
            else con.layers.TEXTBOX_REFERENCE,
            self.text_layers
        )

        # Add rules text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_rules,
                contents = self.layout.oracle_text,
                flavor = self.layout.flavor_text,
                centered = self.is_centered,
                reference = reference_layer,
                divider = psd.getLayer(con.layers.DIVIDER, self.text_layers)
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
        # Simple one image background, Land or Nonland
        psd.getLayer(
            self.pinlines,
            con.layers.LAND if self.is_land else con.layers.NONLAND
        ).visible = True

        # Add the promo star
        if self.promo_star:
            psd.getLayer("Promo Star", con.layers.TEXT_AND_ICONS).visible = True


"""
Templates similar to NormalTemplate but with aesthetic differences
"""


class NormalExtendedTemplate (NormalTemplate):
    """
     An extended-art version of the normal template. The layer structure of this template and
     NormalTemplate are identical.
    """
    template_file_name = "normal-extended"
    template_suffix = "Extended"


class NormalFullartTemplate (NormalTemplate):
    """
    Normal full art template (Also called "Universes Beyond")
    """
    template_file_name = "normal-fullart"
    template_suffix = "Fullart"


class WomensDayTemplate (NormalTemplate):
    """
    The showcase template first used on the Women's Day Secret Lair. Doesn't have any background layers, needs a
    layer mask on the pinlines group when card is legendary, and doesn't support companions.
    """
    template_file_name = "womensday"
    template_suffix = "Showcase"

    @cached_property
    def art_reference_layer(self) -> ArtLayer:
        return psd.getLayer(con.layers.FULL_ART_FRAME)

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
        return psd.getLayer(self.pinlines, con.layers.LEGENDARY_CROWN)


class StargazingTemplate (NormalTemplate):
    """
    Stargazing template from Theros: Beyond Death showcase cards. The layer structure of this template and
    NormalTemplate are largely identical, but this template only has Nyx backgrounds and no companion layers.
    """
    template_file_name = "stargazing.psd"
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
    template_file_name = "masterpiece.psd"
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
    template_file_name = "znrexp.psd"
    template_suffix = "Expedition"

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.RULES_TEXT_NONCREATURE, self.text_layers)

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
        psd.getLayer(con.layers.NORMAL_BORDER, con.layers.BORDER).visible = False
        psd.getLayer(con.layers.LEGENDARY_BORDER, con.layers.BORDER).visible = True


class SnowTemplate (NormalTemplate):
    """
    A snow template with textures from Kaldheim's snow cards.
    Doesn't support Nyx or Companion layers.
    """
    template_file_name = "snow.psd"
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
    template_file_name = "miracle.psd"

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


class TransformBackTemplate (NormalTemplate):
    """
    Template for the back faces of transform cards.
    """
    template_file_name = "tf-back"
    dfc_layer_group = con.layers.TF_BACK

    @cached_property
    def transform_icon(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.transform_icon, psd.getLayerSet(
            self.dfc_layer_group, self.text_layers)
        )

    def enable_frame_layers(self):
        # set transform icon
        self.transform_icon.visible = True
        super().enable_frame_layers()

    def basic_text_layers(self):
        # For eldrazi card, set the color of the rules text, type line, and power/toughness to black
        if self.layout.transform_icon == con.layers.MOON_ELDRAZI_DFC:
            self.text_layer_name.textItem.color = psd.rgb_black()
            self.text_layer_type.textItem.color = psd.rgb_black()
            self.text_layer_pt.textItem.color = psd.rgb_black()
        super().basic_text_layers()


class TransformFrontTemplate (TransformBackTemplate):
    """
    Template for the front faces of transform cards.
    """
    template_file_name = "tf-front.psd"
    dfc_layer_group = con.layers.TF_FRONT

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        if self.is_creature:
            if self.other_face_is_creature:
                return psd.getLayer(con.layers.RULES_TEXT_CREATURE_FLIP, self.text_layers)
            return psd.getLayer(con.layers.RULES_TEXT_CREATURE, self.text_layers)
        self.text_layer_pt.visible = False
        if self.other_face_is_creature:
            return psd.getLayer(con.layers.RULES_TEXT_NONCREATURE_FLIP, self.text_layers)
        return psd.getLayer(con.layers.RULES_TEXT_NONCREATURE, self.text_layers)

    def rules_text_and_pt_layers(self):

        # If flipside is creature, set flipside power/toughness
        if self.other_face_is_creature:
            self.text.append(
                text_classes.TextField(
                    layer=psd.getLayer(con.layers.FLIPSIDE_POWER_TOUGHNESS, self.text_layers),
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
    template_file_name = "ixalan"

    @property
    def is_creature(self) -> bool:
        return False

    @property
    def name_shifted(self) -> bool:
        # Since transform icon is present, need to disable name_shifted
        return False

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

    def create_expansion_symbol(self, centered=False):
        super().create_expansion_symbol(True)


class MDFCBackTemplate (NormalTemplate):
    """
    Template for the back faces of modal double faced cards.
    """
    template_file_name = "mdfc-back"
    dfc_layer_group = con.layers.MDFC_BACK

    @cached_property
    def mdfc_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(self.dfc_layer_group, self.text_layers)

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.LEFT, self.mdfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.RIGHT, self.mdfc_group)

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
        psd.getLayer(self.twins,
                     psd.getLayerSet(con.layers.TOP, self.mdfc_group)).visible = True
        psd.getLayer(self.layout.other_face_twins,
                     psd.getLayerSet(con.layers.BOTTOM, self.mdfc_group)).visible = True
        super().enable_frame_layers()


class MDFCFrontTemplate (MDFCBackTemplate):
    """
    Template for the front faces of modal double faced cards.
    """
    template_file_name = "mdfc-front"
    dfc_layer_group = con.layers.MDFC_FRONT


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
    template_file_name = "mutate.psd"

    def __init__(self, layout):

        # Split self.oracle_text between mutate text and actual text before calling super()
        split_rules_text = layout.oracle_text.split("\n")
        layout.mutate_text = split_rules_text[0]
        layout.oracle_text = "\n".join(split_rules_text[1:])
        super().__init__(layout)

    @cached_property
    def text_layer_mutate(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.MUTATE, self.text_layers)

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add mutate text
        self.text.append(
            text_classes.FormattedTextArea(
                layer = self.text_layer_mutate,
                contents = self.layout.mutate_text,
                flavor = self.layout.flavor_text,
                reference = psd.getLayer(con.layers.MUTATE_REFERENCE, self.text_layers),
            )
        )


class PrototypeTemplate (NormalTemplate):
    """
    A template for Prototype cards introduced in The Brothers' War. This template has a couple
    of additional text layers for prototype text, mana cost, and power/toughness.
    Doesn't support Nyx backgrounds or Companion crowns.
    """
    template_file_name = "prototype.psd"

    def __init__(self, layout):

        # Split self.oracle_text between prototype text and rules text
        split_rules_text = layout.oracle_text.split("\n")
        layout.oracle_text = "\n".join(split_rules_text[1:])

        # Set up the prototype elements
        reg = r"Prototype (.+) [\—\-] ([0-9]{0,2}/[0-9]{0,2}) \((.+)\)"
        match = re.match(reg, split_rules_text[0])
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
        return psd.getLayer(self.proto_color, con.layers.PROTO_TEXTBOX)

    @cached_property
    def proto_manabox(self) -> Optional[ArtLayer]:
        if self.proto_mana_cost.count('{') == 2:
            manabox_group = psd.getLayerSet(con.layers.PROTO_MANABOX_SMALL)
        else:
            manabox_group = psd.getLayerSet(con.layers.PROTO_MANABOX_MEDIUM)
        manabox_group.visible = True
        return psd.getLayer(self.proto_color, manabox_group)

    @cached_property
    def proto_ptbox(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.proto_color, con.layers.PROTO_PTBOX)

    @cached_property
    def text_layer_proto(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.PROTO_RULES, self.text_layers)

    @cached_property
    def text_layer_proto_mana(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.PROTO_MANA_COST, self.text_layers)

    @cached_property
    def text_layer_proto_pt(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.PROTO_PT, self.text_layers)

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
    template_file_name = "adventure"

    def basic_text_layers(self):
        super().basic_text_layers()

        # Add adventure text layers
        mana_cost = psd.getLayer(con.layers.MANA_COST_ADVENTURE, self.text_layers)
        self.text.extend([
            text_classes.FormattedTextField(
                layer = mana_cost,
                contents = self.layout.adventure['mana_cost']
            ),
            text_classes.ScaledTextField(
                layer = psd.getLayer(con.layers.NAME_ADVENTURE, self.text_layers),
                contents = self.layout.adventure['name'],
                reference = mana_cost,
            ),
            text_classes.FormattedTextArea(
                layer = psd.getLayer(con.layers.RULES_TEXT_ADVENTURE, self.text_layers),
                contents = self.layout.adventure['oracle_text'],
                flavor = "",
                centered = False,
                reference = psd.getLayer(con.layers.TEXTBOX_REFERENCE_ADVENTURE, self.text_layers),
            ),
            text_classes.TextField(
                layer = psd.getLayer(con.layers.TYPE_LINE_ADVENTURE, self.text_layers),
                contents = self.layout.adventure['type_line']
            )
        ])


class LevelerTemplate (NormalTemplate):
    """
    Leveler template. No layers are scaled or positioned vertically so manual intervention is required.
    Doesn't support companion, nyx, or lands.
    """
    template_file_name = "leveler"

    def __init__(self, layout):
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
        return psd.getLayer(self.twins, con.layers.PT_AND_LEVEL_BOXES)


class SagaTemplate (NormalTemplate):
    """
    Saga template. No layers are scaled or positioned vertically so manual intervention is required.
    Doesn't support legendary crown, creatures, nyx, or companion.
    """
    template_file_name = "saga"

    def __init__(self, layout):
        self._abilities = []
        self._icons = []
        super().__init__(layout)

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

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.background, con.layers.TEXTBOX)

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
    def ref(self):
        return psd.getLayer(con.layers.TEXTBOX_REFERENCE, self.text_layers)

    @cached_property
    def ability_divider(self) -> ArtLayer:
        return psd.getLayer(con.layers.DIVIDER, self.saga_group)

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Paste scryfall scan
        self.active_layer = psd.getLayerSet(con.layers.TWINS)
        self.paste_scryfall_scan(psd.getLayer(con.layers.SCRYFALL_SCAN_FRAME), False, False)

        # Saga stripe
        psd.getLayer(self.pinlines, con.layers.PINLINES_AND_SAGA_STRIPE).visible = True

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
            layer = psd.getLayer(con.layers.TEXT, self.saga_group).duplicate()
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
        ref_height = psd.get_layer_dimensions(self.ref)['height']
        total_height = ref_height - (((spacing * 1.5) * spaces) + (spacing * 2))

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.ability_layers])
        gap = (ref_height - layer_heights) * (1 / spacing_total)
        inside_gap = (ref_height - layer_heights) * (1.5 / spacing_total)

        # Space Saga lines evenly apart
        psd.spread_layers_over_reference(self.ability_layers, self.ref, gap, inside_gap)

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
    template_file_name = "class"

    def __init__(self, layout):
        self._line_layers: list[ArtLayer] = []
        self._stage_layers: list[LayerSet] = []
        super().__init__(layout)

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
    def ref(self):
        return psd.getLayer(con.layers.TEXTBOX_REFERENCE, self.text_layers)

    @cached_property
    def class_group(self) -> LayerSet:
        return psd.getLayerSet("Class", con.layers.TEXT_AND_ICONS)

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
        level_1 = psd.getLayer(con.layers.TEXT, self.class_group)
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
        ref_height = psd.get_layer_dimensions(self.ref)['height']
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.line_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * ((spacing + divider_height) / spacing_total)

        # Space Class lines evenly apart
        psd.spread_layers_over_reference(self.line_layers, self.ref, gap, inside_gap)

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
    template_file_name = "pw.psd"

    def __init__(self, layout):

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
        return re.findall(r"(^[^:]*$|^.*:.*$)", self.layout.oracle_text, re.MULTILINE)

    @property
    def art_reference(self):
        # Name of art reference layer
        if self.is_colorless:
            return con.layers.FULL_ART_FRAME
        return con.layers.PLANESWALKER_ART_FRAME

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layers(self) -> LayerSet:
        return psd.getLayerSet(con.layers.TEXT_AND_ICONS, self.group)

    @cached_property
    def ref(self) -> ArtLayer:
        return psd.getLayer(con.layers.TEXTBOX_REFERENCE, self.text_layers)

    @cached_property
    def top_ref(self) -> ArtLayer:
        return psd.getLayer(con.layers.PW_TOP_REFERENCE, self.text_layers)

    @cached_property
    def adj_ref(self) -> ArtLayer:
        return psd.getLayer(con.layers.PW_ADJUSTMENT_REFERENCE, self.text_layers)

    """
    LAYERS
    """

    @cached_property
    def group(self) -> LayerSet:
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
        return psd.getLayerSet(con.layers.LOYALTY_GRAPHICS)

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

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.twins, psd.getLayerSet(con.layers.TWINS, self.group))

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, psd.getLayerSet(con.layers.PINLINES, self.group))

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.background, psd.getLayerSet(con.layers.BACKGROUND, self.group))

    @cached_property
    def color_indicator_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, [self.group, con.layers.COLOR_INDICATOR])

    def basic_text_layers(self):

        # Iterate through abilities to add text layers
        for i, ability in enumerate(self.abilities):

            # Get the colon index, determine if this is static or activated ability
            colon_index = ability.find(": ")
            if 5 > colon_index > 0:

                # Determine which loyalty group to enable, and set the loyalty symbol's text
                loyalty_graphic = psd.getLayerSet(ability[0], self.loyalty_group)
                psd.getLayer(con.layers.COST, loyalty_graphic).textItem.contents = ability[0:int(colon_index)]
                ability_layer = psd.getLayer(con.layers.ABILITY_TEXT, self.loyalty_group).duplicate()

                # Add text layer, shields, and colons to list
                self.ability_layers.append(ability_layer)
                self.shields.append(loyalty_graphic.duplicate())
                self.colons.append(psd.getLayer(con.layers.COLON, self.loyalty_group).duplicate())
                ability = ability[colon_index + 2:]

            else:

                # Hide default ability, switch to static
                ability_layer = psd.getLayer(con.layers.STATIC_TEXT, self.loyalty_group).duplicate()
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
        psd.getLayer(
            con.layers.TEXT, [self.loyalty_group, con.layers.STARTING_LOYALTY]
        ).textItem.contents = self.layout.loyalty

        # Call to super for name, type, etc
        super().basic_text_layers()

    def enable_frame_layers(self):
        # Paste scryfall scan
        self.active_layer = psd.getLayerSet(con.layers.TEXTBOX, self.group)
        self.paste_scryfall_scan(psd.getLayer(con.layers.SCRYFALL_SCAN_FRAME), False, False)
        self.active_layer = self.art_layer

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
        spacing = 80 * self.app.activeDocument.width / 3264
        spaces = len(self.ability_layers) + 1
        ref_height = psd.get_layer_dimensions(self.ref)['height']
        total_height = ref_height - (spacing * spaces)

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(layer)["height"] for layer in self.ability_layers])
        gap = (ref_height - layer_heights) / spaces

        # Space Planeswalker text evenly apart
        psd.spread_layers_over_reference(self.ability_layers, self.ref, gap)

        # Check the top reference of loyalty badge
        ft.vertically_nudge_pw_text(self.ability_layers, spacing, gap, self.ref, self.adj_ref, self.top_ref)

        # Align colons and shields to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):
            # Skip if this is a passive ability
            if self.shields[i] and self.colons[i]:
                c_pos = self.colons[i].bounds[1]
                self.docref.selection.select([
                    [0, ref_layer.bounds[1]],
                    [ref_layer.bounds[0], ref_layer.bounds[1]],
                    [ref_layer.bounds[0], ref_layer.bounds[3]],
                    [0, ref_layer.bounds[3]]
                ])
                psd.align_vertical(self.colons[i])
                psd.clear_selection()
                c_dif = self.colons[i].bounds[1] - c_pos
                self.shields[i].translate(0, c_dif)

        # Add the ability layer mask
        self.pw_ability_mask()

    def pw_ability_mask(self):
        """
        Position the ragged edge ability mask.
        """

        # Ragged line layers
        lines = psd.getLayerSet("Ragged Lines", [self.group, con.layers.TEXTBOX, "Ability Dividers"])
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
    def position_divider_line(layers: list, line, line_ref):
        """
        Positions the ragged line correctly.
        """
        dif = (layers[1].bounds[1] - layers[0].bounds[3]) / 2
        ref_pos = (line_ref.bounds[3] + line_ref.bounds[1]) / 2
        targ_pos = dif + layers[0].bounds[3]
        line.translate(0, (targ_pos - ref_pos))

    def fill_between_dividers(self, line1, line2):
        """
        Fill area between ragged lines.
        """
        self.active_layer = self.docref.artLayers.add()
        self.active_layer.move(line1, ps.ElementPlacement.PlaceAfter)
        self.docref.selection.select([
            [line1.bounds[0] - 200, line1.bounds[3]],
            [line1.bounds[2] + 200, line1.bounds[3]],
            [line1.bounds[2] + 200, line2.bounds[1]],
            [line1.bounds[0] - 200, line2.bounds[1]]
        ])
        fill_color = psd.rgb_black()
        self.docref.selection.expand(1)
        self.docref.selection.fill(
            fill_color, ps.ColorBlendMode.NormalBlendColor, 100, False
        )
        psd.clear_selection()


class PlaneswalkerExtendedTemplate (PlaneswalkerTemplate):
    """
    An extended version of PlaneswalkerTemplate. Functionally identical except for the lack of background textures.
    No background, fill empty area for art layer.
    """
    template_file_name = "pw-extended"
    template_suffix = "Extended"

    @property
    def art_reference(self) -> str:
        return con.layers.PLANESWALKER_ART_FRAME

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


class PlaneswalkerMDFCBackTemplate (PlaneswalkerTemplate):
    """
    Template for the back faces of modal double faced Planeswalker cards.
    Need to enable MDFC layers and add MDFC text.
    """
    template_file_name = "pw-mdfc-back"
    dfc_layer_group = con.layers.MDFC_BACK

    @cached_property
    def mdfc_group(self) -> Optional[LayerSet]:
        return psd.getLayerSet(self.dfc_layer_group, self.text_layers)

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.LEFT, self.mdfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        return psd.getLayer(con.layers.RIGHT, self.mdfc_group)

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(con.layers.NAME, self.text_layers)

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
                     psd.getLayerSet(con.layers.TOP, self.mdfc_group)).visible = True
        psd.getLayer(self.layout.other_face_twins,
                     psd.getLayerSet(con.layers.BOTTOM, self.mdfc_group)).visible = True


class PlaneswalkerMDFCFrontTemplate (PlaneswalkerMDFCBackTemplate):
    """
    Template for the front faces of modal double faced Planeswalker cards.
    """
    template_file_name = "pw-mdfc-front"
    dfc_layer_group = con.layers.MDFC_FRONT


class PlaneswalkerMDFCBackExtendedTemplate (PlaneswalkerMDFCBackTemplate):
    """
    An extended version of Planeswalker MDFC Back template.
    No background, fill empty area for art layer.
    """
    template_file_name = "pw-mdfc-back-extended.psd"
    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


class PlaneswalkerMDFCFrontExtendedTemplate (PlaneswalkerMDFCFrontTemplate):
    """
    An extended version of Planeswalker MDFC Front template.
    No background, fill empty area for art layer.
    """
    template_file_name = "pw-mdfc-front-extended.psd"
    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


class PlaneswalkerTransformBackTemplate (PlaneswalkerTemplate):
    """
    Template for the back faces of transform cards.
    """
    template_file_name = "pw-tf-back"
    dfc_layer_group = con.layers.TF_BACK

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(con.layers.NAME, self.text_layers)

    @cached_property
    def text_layer_type(self) -> Optional[ArtLayer]:
        # Name is always shifted
        return psd.getLayer(con.layers.TYPE_LINE, self.text_layers)

    @cached_property
    def transform_icon(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.transform_icon, [self.text_layers, self.dfc_layer_group])

    def enable_frame_layers(self):
        # Add the transform icon
        super().enable_frame_layers()
        self.transform_icon.visible = True


class PlaneswalkerTransformFrontTemplate (PlaneswalkerTransformBackTemplate):
    """
    Template for the back faces of transform cards.
    """
    template_file_name = "pw-tf-front"
    dfc_layer_group = con.layers.TF_FRONT


class PlaneswalkerTransformBackExtendedTemplate (PlaneswalkerTransformBackTemplate):
    """
    An extended version of Planeswalker MDFC Back template.
    No background, fill empty area for art layer.
    """
    template_file_name = "pw-tf-back-extended"
    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()
        psd.content_fill_empty_area(self.art_layer)


class PlaneswalkerTransformFrontExtendedTemplate (PlaneswalkerTransformFrontTemplate):
    """
    An extended version of Planeswalker MDFC Front template.
    No background, fill empty area for art layer.
    """
    template_file_name = "pw-tf-front-extended"
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
    template_file_name = "planar"

    def __init__(self, layout):
        cfg.exit_early = True
        super().__init__(layout)

    @cached_property
    def text_layer_static_ability(self) -> ArtLayer:
        return psd.getLayer(con.layers.STATIC_ABILITY, self.text_layers)

    @cached_property
    def text_layer_chaos_ability(self) -> ArtLayer:
        return psd.getLayer(con.layers.CHAOS_ABILITY, self.text_layers)

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
                reference = self.expansion_symbol
            )
        ])

    def rules_text_and_pt_layers(self):

        # Phenomenon card?
        if self.layout.type_line == con.layers.PHENOMENON:

            # Insert oracle text into static ability layer and disable chaos ability & layer mask on textbox
            self.text.append(
                text_classes.FormattedTextField(
                    layer = self.text_layer_static_ability,
                    contents = self.layout.oracle_text
                )
            )
            psd.enable_mask(psd.getLayerSet(con.layers.TEXTBOX))
            psd.getLayer(con.layers.CHAOS_SYMBOL, self.text_layers).visible = False
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

    def enable_frame_layers(self):

        # Paste scryfall scan
        self.active_layer = psd.getLayerSet(con.layers.TEXTBOX)
        self.paste_scryfall_scan(psd.getLayer(con.layers.SCRYFALL_SCAN_FRAME), True)


"""
Basic land Templates
"""


class BasicLandTemplate (BaseTemplate):
    """
    Basic land template - no text and icons (aside from legal), just a layer for each of the eleven basic lands.
    """
    template_file_name = "basic"

    def __init__(self, layout):
        cfg.save_artist_name = True
        cfg.real_collector = False
        super().__init__(layout)

    @property
    def art_reference(self) -> str:
        return con.layers.BASIC_ART_FRAME

    @cached_property
    def text_layers(self) -> Optional[LayerSet]:
        return self.app.activeDocument

    def enable_frame_layers(self):
        psd.getLayer(self.layout.name).visible = True


class BasicLandUnstableTemplate (BasicLandTemplate):
    """
    Basic land template for the borderless basics from Unstable.
    Doesn't have expansion symbol.
    """
    template_file_name = "basic-unstable"
    template_suffix = "Unstable"

    def create_expansion_symbol(self, centered=False):
        pass

    def basic_text_layers(self):
        pass


class BasicLandTherosTemplate (BasicLandTemplate):
    """
    Basic land template for the full-art Nyx basics from Theros: Beyond Death.
    """
    template_file_name = "basic-theros"
    template_suffix = "Theros"


class BasicLandClassicTemplate (BasicLandTemplate):
    """
    Basic land template for 7th Edition basics.
    """
    template_file_name = "basic-classic"

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
            psd.getLayer("Promo Star").visible = True
