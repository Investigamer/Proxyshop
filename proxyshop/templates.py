"""
CORE TEMPLATES
"""
import os
import proxyshop.text_layers as txt_layers
from proxyshop import format_text, gui
from proxyshop.constants import con
from proxyshop.settings import cfg
import proxyshop.helpers as psd
from photoshop import api as ps
app = ps.Application()
console = gui.console_handler

# Ensure scaling with pixels, font size with points
app.preferences.rulerUnits = ps.Units.Pixels
app.preferences.typeUnits = ps.Units.Points


# MUST EXTEND THIS AT BARE MINIMUM
class BaseTemplate:
    """
    Set up variables for things which are common to all templates (artwork and artist credit).
    Classes extending this base class are expected to populate the following properties at minimum: self.art_reference
    """
    def __init__(self, layout, file):
        # Setup inherited info, tx_layers, template PSD
        self.failed = False
        self.layout = layout
        self.file = file
        self.tx_layers = []
        try: self.file_path = self.load_template()
        except Exception as e:
            console.log_error(
                "PSD not found! Make sure to download the photoshop templates!",
                self.layout.name,
                self.template_file_name(),
                e
            )

        # Basic layers
        self.art_layer = psd.getLayer(con.default_layer)
        self.legal_layer = psd.getLayerSet(con.layers['LEGAL'])

        # Flavor/reminder text
        if cfg.remove_flavor: self.layout.flavor_text = ""
        try:
            # Full art basic lands have no oracle_text. Check for existence of attribute first.
            if hasattr(self.layout, 'oracle_text') and self.layout.oracle_text and cfg.remove_reminder:
                self.layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        finally: pass

        # Add collector info
        self.collector_info()

    def collector_info(self):
        """
        Format and add the collector info at the bottom.
        """
        # If creator is specified add the text
        if self.layout.creator:
            try: psd.getLayer("Creator", self.legal_layer).textItem.contents = self.layout.creator
            except Exception as e:
                console.update("Creator text layer not found, skipping that step.", e)

        # Use realistic collector information?
        if (
            self.layout.collector_number
            and self.layout.rarity
            and self.layout.card_count
            and cfg.real_collector
        ):

            # Reveal collector group, hide old layers
            collector_layer = psd.getLayerSet(con.layers['COLLECTOR'], con.layers['LEGAL'])
            collector_layer.visible = True
            psd.getLayer("Artist", self.legal_layer).visible = False
            psd.getLayer("Set", self.legal_layer).visible = False
            try: psd.getLayer("Pen", self.legal_layer).visible = False
            except AttributeError: pass

            # Get the collector layers
            collector_top = psd.getLayer(con.layers['TOP_LINE'], collector_layer).textItem
            collector_bottom = psd.getLayer(con.layers['BOTTOM_LINE'], collector_layer)

            # Apply the collector info
            collector_top.contents = \
                f"{self.layout.collector_number}/{self.layout.card_count} {self.layout.rarity_letter}"
            psd.replace_text(collector_bottom, "SET", self.layout.set)
            psd.replace_text(collector_bottom, "Artist", self.layout.artist)

        else:

            # Layers we need
            set_layer = psd.getLayer("Set", self.legal_layer)
            artist_layer = psd.getLayer(con.layers['ARTIST'], self.legal_layer)

            # Fill set info / artist info
            set_layer.textItem.contents = self.layout.set + set_layer.textItem.contents
            psd.replace_text(artist_layer, "Artist", self.layout.artist)

    def load_template(self):
        """
        Opens the template's PSD file in Photoshop.
        """
        file_path = os.path.join(con.cwd, f"templates\\{self.template_file_name()}{cfg.file_ext}")
        app.load(file_path)
        return file_path

    def load_artwork(self):
        """
        Loads the specified art file into the specified layer.
        """
        psd.paste_file(self.art_layer, self.file)

    def template_file_name(self):
        """
        Return the file name (no extension) for the template .psd file in the /templates folder.
        """
        print("Template name not specified!")

    def template_suffix(self):
        """
        Templates can optionally specify a string to append to the end of the output filename.
        For example, "extended" on the card Brainstorm will be appended as "Brainstorm (Extended).jpg"
        """
        return None

    def enable_frame_layers(self):
        """
        Enable the correct layers for this card's frame.
        """
        return None

    def post_execute(self):
        """
        Write code that will be processed after execute completes.
        """
        pass

    def execute(self):
        """
        Perform actions to populate this template. Load and frame artwork, enable frame layers,
        and execute all text layers. Returns the file name of the image w/ the template's suffix if it
        specified one. Don't override this method!
        """
        # Load in artwork and frame it
        self.load_artwork()
        psd.frame_layer(self.art_layer, self.art_reference)

        # Enable the layers we need
        try:
            console.update("Enabling frame layers...")
            self.enable_frame_layers()
        except Exception as e:
            result = console.log_error(
                "This card is incompatible with this Template!",
                self.layout.name,
                self.template_file_name(),
                e
            )
            return result

        # Input and format each text layer
        try:
            console.update("Formatting text...")
            for this_layer in self.tx_layers:
                this_layer.execute()
        except Exception as e:
            result = console.log_error(
                "This card is incompatible with this Template!",
                self.layout.name,
                self.template_file_name(),
                e
            )
            return result

        # Format file name
        suffix = self.template_suffix()
        if cfg.save_artist_name:
            if suffix: suffix = f"{suffix} {self.layout.artist}"
            else: suffix = self.layout.artist
        if suffix: file_name = f"{self.layout.name} ({suffix})"
        else: file_name = self.layout.name

        # Manual edit step?
        if cfg.exit_early:
            console.wait("Manual editing enabled! When you're ready to save, click continue...")
            console.update("Saving document...\n")

        # Save the document
        try:
            if cfg.save_jpeg: psd.save_document_jpeg(file_name)
            else: psd.save_document_png(file_name)
            console.update(f"[b]{file_name}[/b] rendered successfully!")

            # Post execution code, then reset document
            self.post_execute()
            psd.reset_document(os.path.basename(self.file_path))
        except Exception as e: console.update(f"Error during save process!\nMake sure the file saved.", e)

        # Return for next assignment
        console.end_await()
        return True


# EXTEND THIS FOR MOST CORE FUNCTIONALITY
class StarterTemplate (BaseTemplate):
    """
    A BaseTemplate with a few extra features. In most cases this will be your starter template
    you want to extend for the most important functionality.
    """
    def __init__(self, layout, file):
        super().__init__(layout, file)
        try: self.is_creature = bool(self.layout.power and self.layout.toughness)
        except AttributeError: self.is_creature = False
        try: self.is_legendary = bool(self.layout.type_line.find("Legendary") >= 0)
        except AttributeError: self.is_legendary = False
        try: self.is_land = bool(self.layout.type_line.find("Land") >= 0)
        except AttributeError: self.is_land = False
        try: self.is_companion = bool("companion" in self.layout.frame_effects)
        except AttributeError: self.is_companion = False

    def basic_text_layers(self, text_and_icons):
        """
        Set up the card's mana cost, name (scaled to not overlap with mana cost), expansion symbol, and type line
        (scaled to not overlap with the expansion symbol).
        """
        # Shift name if necessary (hiding the unused layer)
        name = psd.getLayer(con.layers['NAME'], text_and_icons)
        name_selected = name
        try:
            if self.name_shifted:
                name_selected = psd.getLayer(con.layers['NAME_SHIFT'], text_and_icons)
                name.visible, name_selected.visible = False, True
        except AttributeError: pass

        # Shift typeline if necessary
        type_line = psd.getLayer(con.layers['TYPE_LINE'], text_and_icons)
        type_line_selected = type_line
        try:
            # Handle error if type line shift / color indicator doesn't exist
            if self.type_line_shifted:
                type_line_selected = psd.getLayer(con.layers['TYPE_LINE_SHIFT'], text_and_icons)
                psd.getLayer(self.layout.pinlines, con.layers['COLOR_INDICATOR']).visible = True
                type_line.visible, type_line_selected.visible = False, True
        except AttributeError: pass

        # Mana, expansion
        mana_cost = psd.getLayer(con.layers['MANA_COST'], text_and_icons)
        expansion_symbol = psd.getLayer(con.layers['EXPANSION_SYMBOL'], text_and_icons)
        expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'], text_and_icons)

        # Add text layers
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer=mana_cost,
                text_contents=self.layout.mana_cost,
                text_color=psd.rgb_black()
            ),
            txt_layers.ScaledTextField(
                layer=name_selected,
                text_contents=self.layout.name,
                text_color=psd.get_text_layer_color(name_selected),
                reference_layer=mana_cost
            ),
            txt_layers.ExpansionSymbolField(
                layer=expansion_symbol,
                text_contents=self.layout.symbol,
                rarity=self.layout.rarity,
                reference=expansion_reference
            ),
            txt_layers.ScaledTextField(
                layer=type_line_selected,
                text_contents=self.layout.type_line,
                text_color=psd.get_text_layer_color(type_line_selected),
                reference_layer=expansion_symbol
            ),
        ])

    @staticmethod
    def enable_hollow_crown(crown, pinlines):
        """
         * Enable the hollow legendary crown for this card given layer groups for the crown and pinlines.
        """
        docref = app.activeDocument
        docref.activeLayer = crown
        psd.enable_active_layer_mask()
        docref.activeLayer = pinlines
        psd.enable_active_layer_mask()
        docref.activeLayer = psd.getLayer(con.layers['SHADOWS'])
        psd.enable_active_layer_mask()
        psd.getLayer(con.layers['HOLLOW_CROWN_SHADOW']).visible = True

    def paste_scryfall_scan(self, reference_layer, rotate=False):
        """
        Downloads the card's scryfall scan, pastes it into the document next to the active layer,
        and frames it to fill the given reference layer. Can optionally rotate the layer by 90 degrees
        (useful for planar cards).
        """
        layer = psd.insert_scryfall_scan(self.layout.scryfall_scan)
        if layer:
            if rotate: layer.rotate(90)
            psd.frame_layer(layer, reference_layer)


# EXTEND THIS FOR MOST NORMAL M15-STYLE TEMPLATES
class NormalTemplate (StarterTemplate):
    """
     * Normal M15-style template.
    """
    def template_file_name(self):
        return "normal"

    def __init__(self, layout, file):
        super().__init__(layout, file)

        # If colorless, use fullart
        if self.layout.is_colorless: self.art_reference = psd.getLayer(con.layers['FULL_ART_FRAME'])
        else: self.art_reference = psd.getLayer(con.layers['ART_FRAME'])

        # Name/typeline shifted?
        try: self.name_shifted = bool(self.layout.transform_icon)
        except AttributeError: self.name_shifted = False
        try: self.type_line_shifted = bool(self.layout.color_indicator)
        except AttributeError: self.type_line_shifted = False

        # Do text layers
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        self.basic_text_layers(text_and_icons)
        self.rules_text_and_pt_layers(text_and_icons)

    def rules_text_and_pt_layers(self, text_and_icons):
        """
         * Set up the card's rules text and power/toughness according to whether or not the card is a creature.
         * You're encouraged to override this method if a template extending this one doesn't have the option for
         * creating creature cards (e.g. miracles).
        """
        # Center the rules text if the card has no flavor text, text all in one line, and that line is fairly short
        is_centered = bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" not in self.layout.oracle_text
        )

        if self.is_creature:
            # Creature card - set up creature layer for rules text and insert p/t
            power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
            rules_text = psd.getLayer(con.layers['RULES_TEXT_CREATURE'], text_and_icons)
            rules_text.visible = True

            # Add text layers
            self.tx_layers.extend([
                txt_layers.TextField(
                    layer = power_toughness,
                    text_contents = str(self.layout.power) + "/" + str(self.layout.toughness),
                    text_color = psd.get_text_layer_color(power_toughness)
                ),
                txt_layers.CreatureFormattedTextArea(
                    layer = rules_text,
                    text_contents = self.layout.oracle_text,
                    text_color = psd.get_text_layer_color(rules_text),
                    flavor_text = self.layout.flavor_text,
                    reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
                    pt_reference_layer = psd.getLayer(con.layers['PT_REFERENCE'], text_and_icons),
                    pt_top_reference_layer = psd.getLayer(con.layers['PT_TOP_REFERENCE'], text_and_icons),
                    is_centered = is_centered
                )
            ])
        else:
            # Noncreature card - use the normal rules text layer and disable the p/t layer
            psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons).visible = False
            rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)

            # Add text layers
            self.tx_layers.append(
                txt_layers.FormattedTextArea(
                    layer = rules_text,
                    text_contents = self.layout.oracle_text,
                    text_color = psd.get_text_layer_color(rules_text),
                    flavor_text = self.layout.flavor_text,
                    reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
                    is_centered = is_centered
                )
            )

    def enable_frame_layers(self):

        # Twins and p/t box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines
        if self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # Background
        if self.layout.is_nyx: psd.getLayer(self.layout.background, con.layers['NYX']).visible = True
        else: psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True

        if self.is_legendary:
            # Legendary crown
            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            psd.getLayer(self.layout.pinlines, crown).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True

            # Hollow for Nyx or Companion
            if self.layout.is_nyx or self.is_companion:
                # Enable the hollow crown shadow and layer mask on crown, pinlines, and shadows
                self.enable_hollow_crown(crown, pinlines)

        if self.is_companion:
            # Enable companion texture
            psd.getLayer(self.layout.pinlines, con.layers['COMPANION']).visible = True


class NormalClassicTemplate (StarterTemplate):
    """
     * A template for 7th Edition frame. Each frame is flattened into its own singular layer.
    """
    def template_file_name(self): return "normal-classic"
    def template_suffix(self): return "Classic"

    def __init__(self, layout, file):
        # No collector info for Classic
        cfg.real_collector = False
        if layout.background == con.layers['COLORLESS']: layout.background = con.layers['ARTIFACT']
        super().__init__(layout, file)
        self.art_reference = psd.getLayer(con.layers['ART_FRAME'])

        # Basic text
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        super().basic_text_layers(text_and_icons)

        # Text reference and rules text
        if self.is_land: reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE_LAND'], text_and_icons)
        else: reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons)
        rules_text = psd.getLayer(con.layers['RULES_TEXT'], text_and_icons)
        is_centered = bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and self.layout.oracle_text.find("\n") < 0
        )

        # Add to text layers
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer=rules_text,
                text_contents=self.layout.oracle_text,
                text_color=psd.get_text_layer_color(rules_text),
                flavor_text=self.layout.flavor_text,
                is_centered=is_centered,
                reference_layer=reference_layer,
                fix_length=False
            )
        )

        # Add creature text layers
        power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
        if self.is_creature:
            self.tx_layers.append(
                txt_layers.TextField(
                    layer=power_toughness,
                    text_contents=str(self.layout.power) + "/" + str(self.layout.toughness),
                    text_color=psd.get_text_layer_color(power_toughness)
                )
            )
        else: power_toughness.visible = False

    def enable_frame_layers(self):
        # Simple one image background, Land or Nonland
        if self.is_land: psd.getLayer(self.layout.pinlines, con.layers['LAND']).visible = True
        else: psd.getLayer(self.layout.background, con.layers['NONLAND']).visible = True


"""
Templates similar to NormalTemplate but with aesthetic differences
"""


class NormalExtendedTemplate (NormalTemplate):
    """
     An extended-art version of the normal template. The layer structure of this template and
     NormalTemplate are identical.
    """
    def template_file_name(self): return "normal-extended"
    def template_suffix(self): return "Extended"

    def __init__(self, layout, file):
        # Strip out reminder text for extended
        cfg.remove_reminder = True
        super().__init__(layout, file)


class NormalFullartTemplate (NormalTemplate):
    """
    Normal full art template (Also called "Universes Beyond")
    """
    def template_file_name(self): return "normal-fullart"
    def template_suffix(self): return "Fullart"


class WomensDayTemplate (NormalTemplate):
    """
    The showcase template first used on the Women's Day Secret Lair. The layer structure of this template
    and NormalTemplate are similar, but this template doesn't have any background layers, and a layer mask
    on the pinlines group needs to be enabled when the card is legendary.
    """
    def template_file_name(self): return "womensday"
    def template_suffix(self): return "Showcase"

    def __init__(self, layout, file):
        # Strip out reminder text for fullart
        cfg.remove_reminder = True
        super().__init__(layout, file)

    def enable_frame_layers(self):

        # Twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature:
            psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines
        pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        if self.is_land:
            pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # legendary crown
        if self.is_legendary:
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            app.activeDocument.activeLayer = pinlines
            psd.enable_active_layer_mask()


class StargazingTemplate (NormalTemplate):
    """
    Stargazing template from Theros: Beyond Death showcase cards. The layer structure of this template and
    NormalTemplate are largely identical, but this template doesn't have normal background textures,
    only the Nyxtouched ones.
    """
    def template_file_name(self): return "stargazing"
    def template_suffix(self): return "Stargazing"

    def __init__(self, layout, file):
        # Strip out reminder text
        cfg.remove_reminder = True
        layout.is_nyx = True
        super().__init__(layout, file)


class InventionTemplate (NormalTemplate):
    """
     Kaladesh Invention template. This template has stripped-down layers compared to NormalTemplate
     but is otherwise similar.
    """
    def template_file_name(self): return "masterpiece"
    def template_suffix(self): return "Masterpiece"

    def __init__(self, layout, file):
        # Strip reminder text
        cfg.remove_reminder = True
        self.is_colorless = False
        layout.is_nyx = False

        # Rendering as silver or no?
        if layout.twins != "Silver":
            layout.twins = "Bronze"
            layout.background = "Bronze"

        super().__init__(layout, file)

    def enable_frame_layers(self):

        # Twins and p/t box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines / background
        pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True

        # legendary crown
        if self.is_legendary:

            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            psd.getLayer(self.layout.pinlines, crown).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True
            super().enable_hollow_crown(crown, pinlines)


class InventionSilverTemplate (InventionTemplate):
    """
     * Kaladesh Invention template, Silver choice.
    """
    def __init__(self, layout, file):
        layout.twins = "Silver"
        layout.background = "Silver"
        super().__init__(layout, file)


class ExpeditionTemplate (NormalTemplate):
    """
     Zendikar Rising Expedition template. Doesn't have a mana cost layer, support creature cards, masks pinlines for
     legendary cards like WomensDayTemplate, and has a single static background layer.
    """
    def template_file_name(self): return "znrexp"
    def template_suffix(self): return "Expedition"

    def __init__(self, layout, file):
        # strip out reminder text
        if not cfg.remove_reminder:
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        super().__init__(layout, file)

    def rules_text_and_pt_layers(self, text_and_icons):

        if self.is_creature:
            # Creature card - set up creature layer for rules text and insert p/t
            power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
            self.tx_layers.append(
                txt_layers.TextField(
                    layer = power_toughness,
                    text_contents = str(self.layout.power) + "/" + str(self.layout.toughness),
                    text_color = psd.get_text_layer_color(power_toughness)
                )
            )

        # Expedition template doesn't need to use creature text positioning
        rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer = rules_text,
                text_contents = self.layout.oracle_text,
                text_color = psd.get_text_layer_color(rules_text),
                flavor_text = self.layout.flavor_text,
                reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
                is_centered = False
            ),
        )

    def enable_frame_layers(self):

        # twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # pinlines
        pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        if self.is_legendary:
            # legendary crown
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            app.activeDocument.activeLayer = pinlines
            psd.enable_active_layer_mask()
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True


class SnowTemplate (NormalTemplate):
    """
    A snow template with textures from Kaldheim's snow cards.
    Identical to NormalTemplate.
    """
    def template_file_name(self): return "snow"
    def template_suffix(self): return "Snow"


class MiracleTemplate (NormalTemplate):
    """
    A template for miracle cards. The layer structure of this template and NormalTemplate are
    close to identical, but this template is stripped down to only include mono-colored layers
    and no land layers or other special layers, but no miracle cards exist that require these layers.
    """
    def template_file_name(self): return "miracle"

    def rules_text_and_pt_layers(self, text_and_icons):
        # overriding this because the miracle template doesn't have power/toughness layers
        rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer = rules_text,
                text_contents = self.layout.oracle_text,
                text_color = psd.get_text_layer_color(rules_text),
                flavor_text = self.layout.flavor_text,
                reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
                is_centered = False
            ),
        )


"""
Double faced card templates
"""


class TransformBackTemplate (NormalTemplate):
    """
    Template for the back faces of transform cards.
    """
    def template_file_name(self): return "tf-back"

    def dfc_layer_group(self):
        """
        Layer group containing double face elements
        """
        return con.layers['TF_BACK']

    def __init__(self, layout, file):
        super().__init__(layout, file)
        # set transform icon
        transform_group = psd.getLayerSet(self.dfc_layer_group(), con.layers['TEXT_AND_ICONS'])
        psd.getLayer(self.layout.transform_icon, transform_group).visible = True

    def basic_text_layers(self, txt):
        # For eldrazi card, set the color of the rules text, type line, and power/toughness to black
        if self.layout.transform_icon == con.layers['MOON_ELDRAZI_DFC']:
            # Name
            if self.name_shifted: psd.getLayer(con.layers['NAME_SHIFT'], txt).color = psd.rgb_black()
            else: psd.getLayer(con.layers['NAME'], txt).color = psd.rgb_black()

            # Type line
            if self.type_line_shifted: psd.getLayer(con.layers['TYPE_LINE_SHIFT'], txt).color = psd.rgb_black()
            else: psd.getLayer(con.layers['TYPE_LINE'], txt).color = psd.rgb_black()

            # PT
            psd.getLayer(con.layers['POWER_TOUGHNESS'], txt).color = psd.rgb_black()

        super().basic_text_layers(txt)


class TransformFrontTemplate (TransformBackTemplate):
    """
    Template for the front faces of transform cards.
    """
    def template_file_name(self): return "tf-front"
    def dfc_layer_group(self): return con.layers['TF_FRONT']

    def __init__(self, layout, file):
        try: self.other_face_is_creature = bool(layout.other_face_power and layout.other_face_toughness)
        except AttributeError: self.other_face_is_creature = False
        super().__init__(layout, file)

        # if creature on back face, set flipside power/toughness
        if self.other_face_is_creature:
            flipside_pt = psd.getLayer(con.layers['FLIPSIDE_POWER_TOUGHNESS'], con.layers['TEXT_AND_ICONS'])
            self.tx_layers.append(
                txt_layers.TextField(
                    layer = flipside_pt,
                    text_contents = str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness),
                    text_color = psd.get_text_layer_color(flipside_pt),
                )
            )

    def rules_text_and_pt_layers(self, text_and_icons):
        # Overriding to select one of the four rules text layers

        is_centered = bool(
            len(self.layout.flavor_text) <= 1
            and len(self.layout.oracle_text) <= 70
            and "\n" in self.layout.oracle_text
        )

        power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
        if self.is_creature:

            # Include cutout for other-face PT?
            if self.other_face_is_creature:
                rules_text = psd.getLayer(con.layers['RULES_TEXT_CREATURE_FLIP'], text_and_icons)
            else: rules_text = psd.getLayer(con.layers['RULES_TEXT_CREATURE'], text_and_icons)

            self.tx_layers.extend([
                txt_layers.TextField(
                    layer = power_toughness,
                    text_contents = str(self.layout.power) + "/" + str(self.layout.toughness),
                    text_color = psd.get_text_layer_color(power_toughness),
                ),
                txt_layers.CreatureFormattedTextArea(
                    layer = rules_text,
                    text_contents = self.layout.oracle_text,
                    text_color = psd.get_text_layer_color(rules_text),
                    flavor_text = self.layout.flavor_text,
                    is_centered = is_centered,
                    reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
                    pt_reference_layer = psd.getLayer(con.layers['PT_REFERENCE'], text_and_icons),
                    pt_top_reference_layer = psd.getLayer(con.layers['PT_TOP_REFERENCE'], text_and_icons),
                )
            ])

        else:

            # Include cutout for other-face PT?
            if self.other_face_is_creature:
                rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE_FLIP'], text_and_icons)
            else: rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)

            self.tx_layers.append(
                txt_layers.FormattedTextArea(
                    layer = rules_text,
                    text_contents = self.layout.oracle_text,
                    text_color = psd.get_text_layer_color(rules_text),
                    flavor_text = self.layout.flavor_text,
                    is_centered = is_centered,
                    reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
                )
            )
            power_toughness.visible = False


class IxalanTemplate (NormalTemplate):
    """
    Template for the back faces of transforming cards from Ixalan block.
    """
    def template_file_name(self): return "ixalan"

    def basic_text_layers(self, text_and_icons):
        # typeline doesn't scale down with expansion symbol, and no mana cost layer
        name = psd.getLayer(con.layers['NAME'], text_and_icons)
        type_line = psd.getLayer(con.layers['TYPE_LINE'], text_and_icons)

        # Expansion symbol
        expansion_symbol = psd.getLayer(con.layers['EXPANSION_SYMBOL'], text_and_icons)
        expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'], text_and_icons)

        # Add to text layers
        self.tx_layers.extend([
            txt_layers.TextField(
                layer = name,
                text_contents = self.layout.name,
                text_color = psd.get_text_layer_color(name),
            ),
            txt_layers.ExpansionSymbolField(
                layer = expansion_symbol,
                text_contents = self.layout.symbol,
                rarity = self.layout.rarity,
                reference = expansion_reference,
                centered = True,
            ),
            txt_layers.TextField(
                layer = type_line,
                text_contents = self.layout.type_line,
                text_color = psd.get_text_layer_color(type_line),
            )
        ])

    def rules_text_and_pt_layers(self, text_and_icons):
        # Overriding this because the ixalan template doesn't have power/toughness layers
        rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer = rules_text,
                text_contents = self.layout.oracle_text,
                text_color = psd.get_text_layer_color(rules_text),
                flavor_text = self.layout.flavor_text,
                is_centered = False,
                reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
            )
        )

    def enable_frame_layers(self):
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True


class MDFCBackTemplate (NormalTemplate):
    """
    Template for the back faces of modal double faced cards.
    """
    def template_file_name(self): return "mdfc-back"
    def dfc_layer_group(self): return con.layers['MDFC_BACK']

    def __init__(self, layout, file):
        super().__init__(layout, file)

        # set visibility of top & bottom mdfc elements and set text of left & right text
        mdfc_group = psd.getLayerSet(self.dfc_layer_group(), con.layers['TEXT_AND_ICONS'])
        mdfc_group_top = psd.getLayerSet(con.layers['TOP'], mdfc_group)
        mdfc_group_bottom = psd.getLayerSet(con.layers['BOTTOM'], mdfc_group)
        psd.getLayer(self.layout.twins, mdfc_group_top).visible = True
        psd.getLayer(self.layout.other_face_twins, mdfc_group_bottom).visible = True
        left = psd.getLayer(con.layers['LEFT'], mdfc_group)
        right = psd.getLayer(con.layers['RIGHT'], mdfc_group)
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer = right,
                text_contents = self.layout.other_face_right,
                text_color = psd.get_text_layer_color(right),
            ),
            txt_layers.ScaledTextField(
                layer = left,
                text_contents = self.layout.other_face_left,
                text_color = psd.get_text_layer_color(left),
                reference_layer = right,
            )
        ])


class MDFCFrontTemplate (MDFCBackTemplate):
    """
    Template for the front faces of modal double faced cards.
    """
    def template_file_name(self): return "mdfc-front"
    def dfc_layer_group(self): return con.layers['MDFC_FRONT']


"""
Templates similar to NormalTemplate with new features
"""


class MutateTemplate (NormalTemplate):
    """
     * A template for Ikoria's mutate cards.  The layer structure of this template and NormalTemplate are
     close to identical, but this template has a couple more text and reference layers for the top half of
     the textbox. It also doesn't include layers for Nyx backgrounds or Companion crowns, but no mutate
     cards exist that would require these layers.
    """
    def template_file_name(self): return "mutate"

    def __init__(self, layout, file):

        # Split self.oracle_text between mutate text and actual text before calling super()
        split_rules_text = layout.oracle_text.split("\n")
        layout.mutate_text = split_rules_text[0]
        layout.oracle_text = "\n".join(split_rules_text[1:len(split_rules_text)])

        super().__init__(layout, file)

        # Add mutate text
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        mutate = psd.getLayer(con.layers['MUTATE'], text_and_icons)
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer = mutate,
                text_contents = self.layout.mutate_text,
                text_color = psd.get_text_layer_color(mutate),
                flavor_text = self.layout.flavor_text,
                is_centered = False,
                reference_layer = psd.getLayer(con.layers['MUTATE_REFERENCE'], text_and_icons),
            )
        )


class AdventureTemplate (NormalTemplate):
    """
    A template for Eldraine adventure cards. The layer structure of this template and NormalTemplate
    are close to identical,but this template has a couple more text and reference layers for the left
    half of the textbox.It also doesn't include layers for Nyx backgrounds or Companion crowns, but
    no adventure cards exist that would require these layers.
    """
    def template_file_name(self): return "adventure"

    def __init__(self, layout, file):
        super().__init__(layout, file)

        # Add adventure name, mana cost, type line, and rules text fields to self.tx_layers
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        name = psd.getLayer(con.layers['NAME_ADVENTURE'], text_and_icons)
        mana_cost = psd.getLayer(con.layers['MANA_COST_ADVENTURE'], text_and_icons)
        rules_text = psd.getLayer(con.layers['RULES_TEXT_ADVENTURE'], text_and_icons)
        type_line = psd.getLayer(con.layers['TYPE_LINE_ADVENTURE'], text_and_icons)

        # Add adventure text layers
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer = mana_cost,
                text_contents = self.layout.adventure['mana_cost'],
                text_color = psd.rgb_black(),
            ),
            txt_layers.ScaledTextField(
                layer = name,
                text_contents = self.layout.adventure['name'],
                text_color = psd.get_text_layer_color(name),
                reference_layer = mana_cost,
            ),
            txt_layers.FormattedTextArea(
                layer = rules_text,
                text_contents = self.layout.adventure['oracle_text'],
                text_color = psd.get_text_layer_color(rules_text),
                flavor_text = "",
                is_centered = False,
                reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE_ADVENTURE'], text_and_icons),
            ),
            txt_layers.TextField(
                layer = type_line,
                text_contents = self.layout.adventure['type_line'],
                text_color = psd.get_text_layer_color(type_line),
            )
        ])


class LevelerTemplate (NormalTemplate):
    """
    Leveler template. No layers are scaled or positioned vertically so manual intervention is required.
    """
    def template_file_name(self): return "leveler"

    def __init__(self, layout, file):
        cfg.exit_early = True
        super().__init__(layout, file)

    def rules_text_and_pt_layers(self, text_and_icons):
        # Overwrite to add level abilities
        leveler_text_group = psd.getLayerSet("Leveler Text", text_and_icons)
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer = psd.getLayer("Rules Text - Level Up", leveler_text_group),
                text_contents = self.layout.level_up_text,
                text_color = psd.rgb_black(),
            ),
            txt_layers.TextField(
                layer = psd.getLayer("Top Power / Toughness", leveler_text_group),
                text_contents = str(self.layout.power) + "/" + str(self.layout.toughness),
                text_color = psd.rgb_black(),
            ),
            txt_layers.TextField(
                layer = psd.getLayer("Middle Level", leveler_text_group),
                text_contents = self.layout.middle_level,
                text_color = psd.rgb_black(),
            ),
            txt_layers.TextField(
                layer = psd.getLayer("Middle Power / Toughness", leveler_text_group),
                text_contents = self.layout.middle_power_toughness,
                text_color = psd.rgb_black(),
            ),
            txt_layers.BasicFormattedTextField(
                layer = psd.getLayer("Rules Text - Levels X-Y", leveler_text_group),
                text_contents = self.layout.levels_x_y_text,
                text_color = psd.rgb_black(),
            ),
            txt_layers.TextField(
                layer = psd.getLayer("Bottom Level", leveler_text_group),
                text_contents = self.layout.bottom_level,
                text_color = psd.rgb_black(),
            ),
            txt_layers.TextField(
                layer = psd.getLayer("Bottom Power / Toughness", leveler_text_group),
                text_contents = self.layout.bottom_power_toughness,
                text_color = psd.rgb_black(),
            ),
            txt_layers.BasicFormattedTextField(
                layer = psd.getLayer("Rules Text - Levels Z+", leveler_text_group),
                text_contents = self.layout.levels_z_plus_text,
                text_color = psd.rgb_black(),
            )
        ])

    def enable_frame_layers(self):

        # Twins and PT box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        psd.getLayer(self.layout.twins, con.layers['PT_AND_LEVEL_BOXES']).visible = True

        # Pinlines and background
        psd.getLayer(self.layout.pinlines, con.layers['PINLINES_TEXTBOX']).visible = True
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True


class SagaTemplate (NormalTemplate):
    """
     * Saga template. No layers are scaled or positioned vertically so manual intervention is required.
    """
    def template_file_name(self): return "saga"

    def __init__(self, layout, file):
        cfg.exit_early = True
        super().__init__(layout, file)

        # Paste scryfall scan
        app.activeDocument.activeLayer = psd.getLayerSet(con.layers['TWINS'])
        self.paste_scryfall_scan(psd.getLayer(con.layers['SCRYFALL_SCAN_FRAME']))

    def rules_text_and_pt_layers(self, text_and_icons):

        # Iterate through each saga stage and add line to text layers
        saga_text_group = psd.getLayerSet("Saga", text_and_icons)
        stages = ["I", "II", "III", "IV"]

        for i, line in enumerate(self.layout.saga_lines):
            stage_group = psd.getLayerSet(stages[i], saga_text_group)
            stage_group.visible = True
            self.tx_layers.append(
                txt_layers.BasicFormattedTextField(
                    layer = psd.getLayer("Text", stage_group),
                    text_contents = line,
                    text_color = psd.rgb_black()
                )
            )

    def enable_frame_layers(self):
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        psd.getLayer(self.layout.pinlines, con.layers['PINLINES_AND_SAGA_STRIPE']).visible = True
        psd.getLayer(self.layout.background, con.layers['TEXTBOX']).visible = True
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True


"""
Planeswalker templates
"""


class PlaneswalkerTemplate (StarterTemplate):
    """
    Planeswalker template - 3 or 4 loyalty abilities.
    """
    def template_file_name(self): return "pw"

    def __init__(self, layout, file):
        cfg.exit_early = True
        super().__init__(layout, file)

        # Which art frame?
        if self.layout.is_colorless: self.art_reference = psd.getLayer(con.layers['FULL_ART_FRAME'])
        else: self.art_reference = psd.getLayer(con.layers['PLANESWALKER_ART_FRAME'])

        # Docref group for everything but legal and art reference is based on number of abilities
        ability_array = self.layout.oracle_text.split("\n")
        if len(ability_array) > 3: self.docref = psd.getLayerSet("pw-4")
        else: self.docref = psd.getLayerSet("pw-3")
        self.docref.visible = True

        # Basic text layers
        self.basic_text_layers(psd.getLayerSet(con.layers['TEXT_AND_ICONS'], self.docref))

        # Planeswalker ability layers
        group_names = [
            con.layers['FIRST_ABILITY'],
            con.layers['SECOND_ABILITY'],
            con.layers['THIRD_ABILITY'],
            con.layers['FOURTH_ABILITY']
        ]
        loyalty_group = psd.getLayerSet(con.layers['LOYALTY_GRAPHICS'], self.docref)

        # Iterate through abilities to add text layers
        for i, ability in enumerate(ability_array):
            if i == 4: break

            # Ability group, default ability layer (nonstatic)
            ability_group = psd.getLayerSet(group_names[i], loyalty_group)
            ability_layer = psd.getLayer(con.layers['ABILITY_TEXT'], ability_group)
            colon_index = ability.find(": ")

            # determine if this is a static or activated ability by the presence of ":" in the start of the ability
            if colon_index > 0 < 5:

                # Determine which loyalty group to enable, and set the loyalty symbol's text
                loyalty_graphic = psd.getLayerSet(ability[0], ability_group)
                loyalty_graphic.visible = True

                # Add loyalty cost
                self.tx_layers.append(
                    txt_layers.TextField(
                        layer = psd.getLayer(con.layers['COST'], loyalty_graphic),
                        text_contents = ability[0:int(colon_index)],
                        text_color = psd.rgb_white(),
                    )
                )
                ability = ability[int(colon_index)+2:]

            else:

                # Hide default ability, switch to static
                ability_layer.visible = False
                ability_layer = psd.getLayer(con.layers['STATIC_TEXT'], ability_group)
                ability_layer.visible = True
                psd.getLayer("Colon", ability_group).visible = False

            # Add ability text
            self.tx_layers.append(
                txt_layers.BasicFormattedTextField(
                    layer = ability_layer,
                    text_contents = ability,
                    text_color = psd.get_text_layer_color(ability_layer),
                )
            )

        # starting loyalty
        self.tx_layers.append(
            txt_layers.TextField(
                layer = psd.getLayer(
                    con.layers['TEXT'], psd.getLayerSet(con.layers['STARTING_LOYALTY'], loyalty_group)
                ),
                text_contents = self.layout.loyalty,
                text_color = psd.rgb_white(),
            )
        )

        # Paste scryfall scan
        app.activeDocument.activeLayer = psd.getLayerSet(con.layers['TEXTBOX'], self.docref)
        self.paste_scryfall_scan(psd.getLayer(con.layers['SCRYFALL_SCAN_FRAME']))

    def enable_frame_layers(self):
        # Twins, pinlines, background
        psd.getLayer(self.layout.twins, psd.getLayerSet(con.layers['TWINS'], self.docref)).visible = True
        psd.getLayer(self.layout.pinlines, psd.getLayerSet(con.layers['PINLINES'], self.docref)).visible = True
        self.enable_background()

    def enable_background(self):
        """
        Enable card background
        """
        psd.getLayer(self.layout.background, psd.getLayerSet(con.layers['BACKGROUND'], self.docref)).visible = True


class PlaneswalkerExtendedTemplate (PlaneswalkerTemplate):
    """
    An extended version of PlaneswalkerTemplate. Functionally identical except for the lack of background textures.
    """
    def template_file_name(self): return "pw-extended"
    def template_suffix(self): return "Extended"
    def enable_background(self): pass


class PlaneswalkerMDFCBackTemplate (PlaneswalkerTemplate):
    """
    Template for the back faces of modal double faced Planeswalker cards.
    """
    def template_file_name(self): return "pw-mdfc-back"
    def dfc_layer_group(self): return con.layers['MDFC_BACK']

    def basic_text_layers(self, text_and_icons):
        super().basic_text_layers(text_and_icons)

        # set visibility of top & bottom mdfc elements and set text of left & right text
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'], self.docref)
        mdfc_group = psd.getLayerSet(self.dfc_layer_group(), text_and_icons)
        mdfc_group_top = psd.getLayerSet(con.layers['TOP'], mdfc_group)
        mdfc_group_bottom = psd.getLayerSet(con.layers['BOTTOM'], mdfc_group)
        psd.getLayer(self.layout.twins, mdfc_group_top).visible = True
        psd.getLayer(self.layout.other_face_twins, mdfc_group_bottom).visible = True
        left = psd.getLayer(con.layers['LEFT'], mdfc_group)
        right = psd.getLayer(con.layers['RIGHT'], mdfc_group)

        # Add MDFC text layers
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer = right,
                text_contents = self.layout.other_face_right,
                text_color = psd.get_text_layer_color(right),
            ),
            txt_layers.ScaledTextField(
                layer = left,
                text_contents = self.layout.other_face_left,
                text_color = psd.get_text_layer_color(left),
                reference_layer = right,
            )
        ])


class PlaneswalkerMDFCFrontTemplate (PlaneswalkerMDFCBackTemplate):
    """
    Template for the front faces of modal double faced Planeswalker cards.
    """
    def template_file_name(self): return "pw-mdfc-front"
    def dfc_layer_group(self): return con.layers['MDFC_FRONT']


class PlaneswalkerMDFCBackExtendedTemplate (PlaneswalkerMDFCBackTemplate):
    """
    An extended version of Planeswalker MDFC Back template.
    """
    def template_file_name(self): return "pw-mdfc-back-extended"
    def template_suffix(self): return "Extended"

    def enable_background(self):
        app.activeDocument.activeLayer = self.art_layer
        psd.content_fill_empty_area()


class PlaneswalkerMDFCFrontExtendedTemplate (PlaneswalkerMDFCFrontTemplate):
    """
    An extended version of Planeswalker MDFC Front template.
    """
    def template_file_name(self): return "pw-mdfc-front-extended"
    def template_suffix(self): return "Extended"

    def enable_background(self):
        app.activeDocument.activeLayer = self.art_layer
        psd.content_fill_empty_area()


class PlaneswalkerTransformBackTemplate (PlaneswalkerTemplate):
    """
    Template for the back faces of transform cards.
    """
    def template_file_name(self): return "pw-tf-back"
    @staticmethod
    def dfc_layer_group(): return con.layers['TF_BACK']

    def basic_text_layers(self, text_and_icons):
        # Enable transform stuff
        transform_group = psd.getLayerSet(self.dfc_layer_group(), text_and_icons)
        color_indicator = psd.getLayerSet(con.layers['COLOR_INDICATOR'], self.docref)
        psd.getLayer(self.layout.transform_icon, transform_group).visible = True
        psd.getLayer(self.layout.pinlines, color_indicator).visible = True
        super().basic_text_layers(text_and_icons)


class PlaneswalkerTransformFrontTemplate (PlaneswalkerTemplate):
    """
    Template for the back faces of transform cards.
    """
    def template_file_name(self): return "pw-tf-front"
    @staticmethod
    def dfc_layer_group(): return con.layers['TF_FRONT']

    def basic_text_layers(self, text_and_icons):
        # Add transform elements
        transform_group = psd.getLayerSet(self.dfc_layer_group(), text_and_icons)
        psd.getLayer(self.layout.transform_icon, transform_group).visible = True
        super().basic_text_layers(text_and_icons)


class PlaneswalkerTransformBackExtendedTemplate (PlaneswalkerTransformBackTemplate):
    """
    An extended version of Planeswalker MDFC Back template.
    """
    def template_file_name(self): return "pw-tf-back-extended"
    def template_suffix(self): return "Extended"

    def enable_background(self):
        app.activeDocument.activeLayer = self.art_layer
        psd.content_fill_empty_area()


class PlaneswalkerTransformFrontExtendedTemplate (PlaneswalkerTransformFrontTemplate):
    """
    An extended version of Planeswalker MDFC Front template.
    """
    def template_file_name(self): return "pw-tf-front-extended"
    def template_suffix(self): return "Extended"

    def enable_background(self):
        app.activeDocument.activeLayer = self.art_layer
        psd.content_fill_empty_area()


"""
Misc. Templates
"""


class PlanarTemplate (StarterTemplate):
    """
    Planar template for Planar/Phenomenon cards
    """
    def template_file_name(self): return "planar"

    def __init__(self, layout, file):
        cfg.exit_early = True
        super().__init__(layout, file)
        self.art_reference = psd.getLayer(con.layers['ART_FRAME'])

        # Card name, type line, expansion symbol
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        name = psd.getLayer(con.layers['NAME'], text_and_icons)
        type_line = psd.getLayer(con.layers['TYPE_LINE'], text_and_icons)
        expansion_symbol = psd.getLayer(con.layers['EXPANSION_SYMBOL'], text_and_icons)
        expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'], text_and_icons)

        # Overwrite self.tx_layers
        self.tx_layers = [
            txt_layers.TextField(
                layer = name,
                text_contents = self.layout.name,
                text_color = psd.get_text_layer_color(name),
            ),
            txt_layers.ScaledTextField(
                layer = type_line,
                text_contents = self.layout.type_line,
                text_color = psd.get_text_layer_color(type_line),
                reference_layer = expansion_symbol,
            ),
            txt_layers.ExpansionSymbolField(
                layer = expansion_symbol,
                text_contents = self.layout.symbol,
                rarity = self.layout.rarity,
                reference = expansion_reference
            )
        ]

        # Abilities
        static_ability = psd.getLayer(con.layers['STATIC_ABILITY'], text_and_icons)
        chaos_ability = psd.getLayer(con.layers['CHAOS_ABILITY'], text_and_icons)

        # Phenomenon card?
        if self.layout.type_line == con.layers['PHENOMENON']:

            # Insert oracle text into static ability layer and disable chaos ability & layer mask on textbox
            self.tx_layers.append(
                txt_layers.BasicFormattedTextField(
                    layer = static_ability,
                    text_contents = self.layout.oracle_text,
                    text_color = psd.get_text_layer_color(static_ability),
                )
            )

            app.activeDocument.activeLayer = psd.getLayerSet(con.layers['TEXTBOX'])
            psd.disable_active_layer_mask()
            psd.getLayer(con.layers['CHAOS_SYMBOL'], text_and_icons).visible = False
            chaos_ability.visible = False

        else:

            # Split oracle text on last line break, insert everything before into static, the rest into chaos
            linebreak_index = self.layout.oracle_text.rindex("\n")
            self.tx_layers.extend([
                txt_layers.BasicFormattedTextField(
                    layer = static_ability,
                    text_contents = self.layout.oracle_text[0:linebreak_index],
                    text_color = psd.get_text_layer_color(static_ability),
                ),
                txt_layers.BasicFormattedTextField(
                    layer = chaos_ability,
                    text_contents = self.layout.oracle_text[linebreak_index+1:],
                    text_color = psd.get_text_layer_color(chaos_ability),
                ),
            ])

        # Paste scryfall scan
        app.activeDocument.activeLayer = psd.getLayerSet(con.layers['TEXTBOX'])
        self.paste_scryfall_scan(psd.getLayer(con.layers['SCRYFALL_SCAN_FRAME']), True)

    def enable_frame_layers(self):
        # No need to enable layers
        pass


"""
Basic land Templates
"""


class BasicLandTemplate (BaseTemplate):
    """
    Basic land template - no text and icons (aside from legal), just a layer for each of the eleven basic lands.
    """
    def template_file_name(self): return "basic"

    def __init__(self, layout, file):
        cfg.save_artist_name = True
        cfg.real_collector = False
        super().__init__(layout, file)
        self.art_reference = psd.getLayer(con.layers['BASIC_ART_FRAME'])

    def enable_frame_layers(self):
        psd.getLayer(self.layout.name).visible = True
        self.tx_layers.append(
            txt_layers.ExpansionSymbolField(
                layer = psd.getLayer("Expansion Symbol"),
                text_contents = self.layout.symbol,
                rarity = "common",
                reference = psd.getLayer(con.layers['EXPANSION_REFERENCE']),
            )
        )


class BasicLandUnstableTemplate (BasicLandTemplate):
    """
    Basic land template for the borderless basics from Unstable.
    """
    def template_file_name(self): return "basic-unstable"
    def template_suffix(self): return "Unstable"

    def enable_frame_layers(self):
        # Overwrite to ignore expansion symbol
        psd.getLayer(self.layout.name).visible = True


class BasicLandTherosTemplate (BasicLandTemplate):
    """
    Basic land template for the full-art Nyx basics from Theros: Beyond Death.
    """
    def template_file_name(self): return "basic-theros"
    def template_suffix(self): return "Theros"


class BasicLandClassicTemplate (BasicLandTemplate):
    """
    Basic land template for 7th Edition basics.
    """
    def template_file_name(self): return "basic-classic"
    def template_suffix(self): return f"Classic - {self.layout.artist}"
