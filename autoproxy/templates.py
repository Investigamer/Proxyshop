"""
CORE TEMPLATES
"""
import os
import autoproxy.frame_logic as frame_logic
import autoproxy.format_text as format_text
import autoproxy.text_layers as txt_layers
import autoproxy.constants as con
import autoproxy.settings as cfg
import autoproxy.helpers as psd
import photoshop.api as ps
app = ps.Application()

"""
Template boilerplate class
Your entrypoint to customising this project for automating your own templates. You should write classes that extend BaseTemplate for your 
templates, and:
* Override the method template_file_name() to return your template's file name (without extension). It should be located in the
  directory /scripts for the project to find it correctly.

* Extend the constructor (make sure you call self.super() in the constructor). Define the text fields you need to populate in your
  template. Do this by creating new instances of the project's text field classes (see my templates for examples) and append them
  to the array self.tx_layers. The constructor also needs to set the property self.art_reference to a layer in your template, and
  your card art will be scaled to match the size of this layer.

* Override the method enable_frame_layers. This method should use information about the card's layout to determine which layers to
  turn on in your template to complete the card's frame. self.layout contains information about the card's twins color (name and title 
  boxes), pinlines and textbox color(s), and background color(s), so you'll be mainly using self. You also know if the card is colorless
  (as in full-art like Eldrazi cards) and whether or not the card is nyx-touched (uses the nyx background).

You should also add your template to the class_template_map in constants.py

class Template = Class(BaseTemplate):    
    def __init__ (self, layout, file):
        super().__init__(layout, file)
        # do stuff, including setting self.art_reference
        # add text layers to the array self.tx_layers (will be executed automatically)
    
    def template_file_name (self):
        return "psd_file_name"

    def enable_frame_layers (self):
        # do stuff

"""

class BaseTemplate(object):
    def __init__ (self, layout, file):
        """
         * Set up variables for things which are common to all templates (artwork and artist credit).
         * Classes extending this base class are expected to populate the following properties at minimum: self.art_reference
        """
        # Setup inherited info, tx_layers, template PSD
        self.layout = layout
        self.file = file
        self.tx_layers = []
        self.load_template()

        # Flavor/reminder text
        if cfg.remove_flavor: self.layout.flavor_text = ""
        try:
            if self.layout.oracle_text and cfg.remove_reminder: 
                self.layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        except: pass

        # Basic layers
        self.art_layer = psd.getLayer(con.default_layer)
        self.legal_layer = psd.getLayerSet(con.layers['LEGAL'])
        try: self.layout.no_collector
        except: self.layout.no_collector = False
        
        # Remove the P for promo sets
        if len(self.layout.set) > 3: self.layout.set = self.layout.set[1:]
        
        # Automatic set symbol enabled?
        if cfg.auto_symbol == True: 
            if self.layout.set in con.set_symbol_library: 
                self.symbol_char = con.set_symbol_library[self.layout.set]
            else: self.symbol_char = cfg.symbol_char
        else: self.symbol_char = cfg.symbol_char
        
        # If creator is specified add the text
        if self.layout.creator:
            try: psd.getLayer("Creator", self.legal_layer).textItem.contents = self.layout.creator
            except: pass
        
        # Use realistic collector information? Is the necessary info available?
        if ( self.layout.collector_number 
            and self.layout.rarity 
            and self.layout.card_count 
            and cfg.real_collector 
            and not self.layout.no_collector 
        ):

            # Reveal collector group, hide old layers
            self.collector_layer = psd.getLayerSet(con.layers['COLLECTOR'], con.layers['LEGAL'])
            self.collector_layer.visible = True
            psd.getLayer("Artist", self.legal_layer).visible = False
            psd.getLayer("Set", self.legal_layer).visible = False
            psd.getLayer("Pen", self.legal_layer).visible = False

            # Get the collector layers
            self.collector_top = psd.getLayer(con.layers['TOP_LINE'], self.collector_layer)
            self.collector_bottom = psd.getLayer(con.layers['BOTTOM_LINE'], self.collector_layer)

            # Prepare rarity letter + collector number
            rarity_letter = self.layout.rarity[0:1].upper()
            if len(self.layout.collector_number) == 2: 
                self.layout.collector_number = "0" + str(self.layout.collector_number)
            elif len(self.layout.collector_number) == 1: 
                self.layout.collector_number = "00" + str(self.layout.collector_number)
            else: self.layout.collector_number = str(self.layout.collector_number)
            
            # Prepare card count
            if len(str(self.layout.card_count)) == 2:
                self.layout.card_count = "0" + str(self.layout.card_count)
            elif len(str(self.layout.card_count)) == 1:
                self.layout.card_count = "00" + str(self.layout.card_count)
            else: self.layout.card_count = str(self.layout.card_count)

            # Apply the collector info
            self.collector_top.textItem.contents = self.layout.collector_number + "/" + self.layout.card_count + " " + rarity_letter
            psd.replace_text(self.collector_bottom, "SET", self.layout.set)
            psd.replace_text(self.collector_bottom, "Artist", self.layout.artist)

        else: 

            # Layers we need
            self.set_layer = psd.getLayer("Set", con.layers['LEGAL'])
            self.artist_layer = psd.getLayer(con.layers['ARTIST'], con.layers['LEGAL'])

            # Fill set info / artist info
            self.set_layer.textItem.contents = self.layout.set + self.set_layer.textItem.contents
            psd.replace_text(psd.getLayer(con.layers['ARTIST'], con.layers['LEGAL']), "Artist", self.layout.artist)

    def template_file_name (self):
        """
         * Return the file name (no extension) for the template .psd file in the /templates folder.
        """
        print("Template name not specified!")
    
    def template_suffix (self):
        """
         * Templates can optionally specify strings to append to the end of cards created by them.
         * For example, extended templates can be set up to automatically append " (Extended)" to the end of 
         * image file names by setting the return value of this method to "Extended"
        """
        return None
    
    def load_template (self):
        """
         * Opens the template's PSD file in Photoshop.
        """
        tmp_file_name = self.template_file_name()
        template_path = os.path.join(con.cwd, f"templates\\{tmp_file_name}{cfg.file_ext}")
        app.load(template_path)
        # TODO: if that's the file that's currently open, reset instead of opening?
    
    def enable_frame_layers (self):
        """
         * Enable the correct layers for this card's frame.
        """
        print("Frame layers not specified!")
    
    def load_artwork (self):
        """
         * Loads the specified art file into the specified layer.
        """
        psd.paste_file(self.art_layer, self.file)
    
    def execute (self):
        """
         * Perform actions to populate this template. Load and frame artwork, enable frame layers, and execute all text layers.
         * Returns the file name of the image w/ the template's suffix if it specified one.
         * Don't override this method! You should be able to specify the full behaviour of the template in the constructor (making 
         * sure to call self.super()) and enable_frame_layers().
        """
        # Load in artwork and frame it
        self.load_artwork()
        psd.frame_layer(self.art_layer, self.art_reference)

        # Enable the layers we need
        self.enable_frame_layers()

        # Input and format each text layer
        for this_layer in self.tx_layers:
            this_layer.execute()

        # Exit early?
        try:
            if self.exit_early:
                print("Time to manually edit!")
                os._exit(0)
            elif cfg.exit_early: 
                print("Time to manually edit!")
                os._exit(0)
        except: 
            if cfg.exit_early: 
                print("Time to manually edit!")
                os._exit(0)

        # Format file name, return it for saving
        file_name = self.layout.name
        suffix = self.template_suffix()
        if suffix: file_name = f"{file_name} ({suffix})"
        return file_name

# Class definitions for Starter template #

class StarterTemplate (BaseTemplate):
    """
     * A BaseTemplate with a few extra features. In most cases this will be your starter template
     * you want to extend for the most important functionality.
    """
    # TODO: add code for transform and mdfc stuff here (since both normal and planeswalker templates need to inherit them)
    def __init__ (self, layout, file):
        super().__init__(layout, file)
        self.is_creature = bool(self.layout.power and self.layout.toughness)
        self.is_legendary = bool(self.layout.type_line.find("Legendary") >= 0)
        self.is_land = bool(self.layout.type_line.find("Land") >= 0)
        try: self.is_companion = bool("companion" in self.layout.frame_effects)
        except: self.is_companion = False 
    
    def basic_text_layers (self, text_and_icons):
        """
         * Set up the card's mana cost, name (scaled to not overlap with mana cost), expansion symbol, and type line
         * (scaled to not overlap with the expansion symbol).
        """
        # Shift name if necessary (hiding the unused layer)
        name = psd.getLayer(con.layers['NAME'], text_and_icons)
        name_selected = name
        try:
            # Handle errors when name_shift does not exist
            name_shift = psd.getLayer(con.layers['NAME_SHIFT'],text_and_icons)
            if self.name_shifted:
                name_selected = name_shift
                name.visible = False
                name_shift.visible = True
            else:
                name_shift.visible = False
                name.visible = True
        except: pass
        # Shift typeline if necessary
        type_line = psd.getLayer(con.layers['TYPE_LINE'],text_and_icons)
        type_line_selected = type_line
        try:
            # Handle errors when type_line_shift does not exist
            type_line_shift = psd.getLayer(con.layers['TYPE_LINE_SHIFT'], text_and_icons)
            if self.type_line_shifted:
                type_line_selected = type_line_shift
                type_line.visible = False
                type_line_shift.visible = True
                # enable color indicator dot
                psd.getLayer(self.layout.pinlines,con.layers['color_INDICATOR']).visible = True
            else:
                type_line_shift.visible = False
                type_line.visible = True
        except: pass

        mana_cost = psd.getLayer(con.layers['MANA_COST'], text_and_icons)
        expansion_symbol = psd.getLayer(con.layers['EXPANSION_SYMBOL'], text_and_icons)
        if cfg.auto_symbol_size: expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'], text_and_icons)
        else: expansion_reference = None
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer = mana_cost,
                text_contents = self.layout.mana_cost,
                text_color = psd.rgb_black()
            ),
            txt_layers.ScaledTextField(
                layer = name_selected,
                text_contents = self.layout.name,
                text_color = psd.get_text_layer_color(name_selected),
                reference_layer = mana_cost
            ),
            txt_layers.ExpansionSymbolField(
                layer = expansion_symbol,
                text_contents = self.symbol_char,
                rarity = self.layout.rarity,
                reference = expansion_reference
            ),
            txt_layers.ScaledTextField(
                layer = type_line_selected,
                text_contents = self.layout.type_line,
                text_color = psd.get_text_layer_color(type_line_selected),
                reference_layer = expansion_symbol
            ),
        ])
        
    def enable_hollow_crown (self, crown, pinlines):
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
    
    def paste_scryfall_scan (self, reference_layer, rotate=False):
        """
         * Downloads the card's scryfall scan, pastes it into the document next to the active layer, and frames it to fill
         * the given reference layer. Can optionally rotate the layer by 90 degrees (useful for planar cards).
        """
        layer = psd.insert_scryfall_scan(self.layout.scryfall_scan)
        if rotate: layer.rotate(90)
        psd.frame_layer(layer, reference_layer)

class NormalTemplate (StarterTemplate):
    """
     * Normal M15-style template.
    """
    def template_file_name (self):
        return "normal"
        
    def __init__ (self, layout, file):
        super().__init__(layout, file)

        # If colorless use full art
        if self.layout.is_colorless: self.art_reference = psd.getLayer(con.layers['FULL_ART_FRAME'])
        else: self.art_reference = psd.getLayer(con.layers['ART_FRAME'])

        # Name/typeline shifted?
        try: self.name_shifted = bool(self.layout.transform_icon)
        except: self.name_shifted = False
        try: self.type_line_shifted = bool(self.layout.color_indicator)
        except: self.type_line_shifted = False

        # Do text layers
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        try: self.basic_text_layers(text_and_icons)
        except: super().basic_text_layers(text_and_icons)
        self.rules_text_and_pt_layers(text_and_icons)
    
    def rules_text_and_pt_layers (self, text_and_icons):
        """
         * Set up the card's rules text and power/toughness according to whether or not the card is a creature.
         * You're encouraged to override this method if a template extending this one doesn't have the option for
         * creating creature cards (e.g. miracles).
        """
        # Center the rules text if the card has no flavor text, text all in one line, and that line is fairly short
        is_centered = bool(len(self.layout.flavor_text) <= 1 and len(self.layout.oracle_text) <= 70 and self.layout.oracle_text.find("\n") < 0)

        power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
        if self.is_creature:
            # Creature card - set up creature layer for rules text and insert p/t
            rules_text = psd.getLayer(con.layers['RULES_TEXT_CREATURE'], text_and_icons)
            rules_text.visible = True
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
            rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)
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
            power_toughness.visible = False
    
    def enable_frame_layers (self):

        # Twins and p/t box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines
        if self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # Background
        if self.layout.is_nyx: background = psd.getLayer(self.layout.background, con.layers['NYX'])
        else: background = psd.getLayer(self.layout.background, con.layers['BACKGROUND'])
        background.visible = True

        if self.is_legendary:
            # legendary crown
            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            psd.getLayer(self.layout.pinlines, crown).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True

        if self.is_companion:
            # enable companion texture
            psd.getLayer(self.layout.pinlines, LayerNames['COMPANION']).visible = True

        if (self.is_legendary and self.layout.is_nyx) or self.is_companion:
            # legendary crown on nyx background - enable the hollow crown shadow and layer mask on crown, pinlines, and shadows
            super().enable_hollow_crown(crown, pinlines)

# CLASSIC TEMPLATE, NORMAL
class NormalClassicTemplate (StarterTemplate):
    """
     * A template for 7th Edition frame. Each frame is flattened into its own singular layer.
    """
    def template_file_name (self):
        return "normal-classic"
    
    def template_suffix (self):
        return "Classic"
    
    def __init__ (self, layout, file):
        
        # No collector info for Classic
        layout.no_collector = True
        if layout.background == con.layers['COLORLESS']: layout.background = con.layers['ARTIFACT']
        super().__init__(layout, file)
        self.art_reference = psd.getLayer(con.layers['ART_FRAME'])

        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        super().basic_text_layers(text_and_icons)

        # rules text
        is_centered = bool(len(self.layout.flavor_text) <= 1 and len(self.layout.oracle_text) <= 70 and self.layout.oracle_text.find("\n") < 0)
        reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons)
        if self.is_land: reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE_LAND'], text_and_icons)
        
        rules_text = psd.getLayer(con.layers['RULES_TEXT'], text_and_icons)
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer = rules_text,
                text_contents = self.layout.oracle_text,
                text_color = psd.get_text_layer_color(rules_text),
                flavor_text = self.layout.flavor_text,
                is_centered = is_centered,
                reference_layer = reference_layer
            )
        )

        power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
        if self.is_creature:
            self.tx_layers.append(
                txt_layers.TextField(
                    layer = power_toughness,
                    text_contents = str(self.layout.power) + "/" + str(self.layout.toughness),
                    text_color = psd.get_text_layer_color(power_toughness)
                )
            )
        else: power_toughness.visible = False
    
    def enable_frame_layers (self):

        # Simple one image background, Land or Nonland
        layer_set = psd.getLayerSet(con.layers['NONLAND'])
        selected_layer = self.layout.background
        if self.is_land:
            layer_set = psd.getLayerSet(con.layers['LAND'])
            selected_layer = self.layout.pinlines
        psd.getLayer(selected_layer, layer_set).visible = True



# Templates similar to NormalTemplate but with aesthetic differences 
class NormalExtendedTemplate (NormalTemplate):
    """
     * An extended-art version of the normal template. The layer structure of this template and NormalTemplate are identical.
    """
    def template_file_name (self):
        return "normal-extended"
    
    def template_suffix (self):
        return "Extended"
    
    def __init__ (self, layout, file):
        # strip out reminder text for extended
        if not cfg.remove_reminder: 
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        super().__init__(layout, file)

class NormalFullartTemplate (NormalTemplate):
    """
     * Normal full art template (Also called "Universes Beyond")
    """
    def template_file_name (self):
        return "normal-fullart"
    
    def template_suffix (self):
        return "Fullart"
    
    def constructor (self, layout, file):
        super().__init__(layout, file)
        

class WomensDayTemplate (NormalTemplate):
    """
     * The showcase template first used on the Women's Day Secret Lair. The layer structure of this template and NormalTemplate are
     * similar, but this template doesn't have any background layers, and a layer mask on the pinlines group needs to be enabled when
     * the card is legendary.
    """
    def template_file_name (self):
        return "womensday"
    
    def template_suffix (self):
        return "Showcase"
    
    def __init__ (self, layout, file):
        # strip out reminder text for fullart
        if not cfg.remove_reminder: 
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        super().__init__(layout, file)
    
    def enable_frame_layers (self):

        # twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature:
            psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # pinlines
        pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        if self.is_land:
            pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        if self.is_legendary:
            # legendary crown
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            docref.activeLayer = pinlines
            psd.enable_active_layer_mask()


class StargazingTemplate (NormalTemplate):
    """
     * Stargazing template from Theros: Beyond Death showcase cards. The layer structure of this template and NormalTemplate are largely 
     * identical, but this template doesn't have normal background textures, only the Nyxtouched ones.
    """
    def template_file_name (self):
        return "stargazing"
    
    def template_suffix (self):
        return "Stargazing"
    
    def __init__ (self, layout, file):
        # strip out reminder text
        if not cfg.remove_reminder: 
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        layout.is_nyx = True
        super().__init__(layout, file)


class MasterpieceTemplate (NormalTemplate):
    """
     * Kaladesh Invention template. This template has stripped-down layers compared to NormalTemplate but is otherwise similar.
    """
    def template_file_name (self):
        return "masterpiece"
    
    def template_suffix (self):
        return "Masterpiece"
    
    def __init__ (self, layout, file):
        is_colorless = False
        
        # force to use bronze twins and background
        layout.twins = "Bronze"
        layout.background = "Bronze"

        # strip out reminder text
        if not cfg.remove_reminder: 
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)

        super().__init__(layout, file)
    
    def enable_frame_layers (self):
        super().enable_frame_layers()
        if self.is_legendary:
            # always enable hollow crown for legendary cards in this template
            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
            super.enable_hollow_crown(crown, pinlines)


class ExpeditionTemplate (NormalTemplate):
    """
     * Zendikar Rising Expedition template. Doesn't have a mana cost layer, support creature cards, masks pinlines for legendary
     * cards like WomensDayTemplate, and has a single static background layer.
    """
    def template_file_name (self):
        return "znrexp"
    
    def template_suffix (self):
        return "Expedition"
    
    def __init__ (self, layout, file):
        # strip out reminder text
        if not cfg.remove_reminder: 
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        super().__init__(layout, file)
    
    def basic_text_layers (self, text_and_icons):
        name = psd.getLayer(con.layers['NAME'], text_and_icons)
        type_line = psd.getLayer(con.layers['TYPE_LINE'], text_and_icons)

        # Expansion symbol
        expansion_symbol = psd.getLayer(con.layers['EXPANSION_SYMBOL'], text_and_icons)
        if cfg.auto_symbol_size: expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'], text_and_icons)
        else: expansion_reference = None
        self.tx_layers.extend([
            txt_layers.TextField(
                layer = name,
                text_contents = self.layout.name,
                text_color = psd.get_text_layer_color(name)
            ),
            txt_layers.ExpansionSymbolField(
                layer = expansion_symbol,
                text_contents = self.symbol_char,
                rarity = self.layout.rarity,
                reference = expansion_reference
            ),
            txt_layers.ScaledTextField(
                layer = type_line,
                text_contents = self.layout.type_line,
                text_color = psd.get_text_layer_color(type_line),
                reference_layer = expansion_symbol
            ),
        ])
    
    def rules_text_and_pt_layers (self, text_and_icons):
        # overriding this because the expedition template doesn't have power/toughness layers
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
    
    def enable_frame_layers (self):

        # twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True

        # pinlines
        pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        if self.is_legendary:
            # legendary crown
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            app.activeDocument.activeLayer = pinlines
            enable_active_layer_mask()
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True


class SnowTemplate (NormalTemplate):
    """
     * A snow template with textures from Kaldheim's snow cards. The layer structure of this template and NormalTemplate are identical.
    """
    def template_file_name (self):
        return "snow"

    def __init__ (self, layout, file):
        super().__init__(layout, file)


class MiracleTemplate (NormalTemplate):
    """
     * A template for miracle cards. The layer structure of this template and NormalTemplate are close to identical, but this
     * template is stripped down to only include mono-colored layers and no land layers or other special layers, but no miracle
     * cards exist that require these layers.
    """
    def template_file_name (self):
        return "miracle"

    def __init__ (self, layout, file):
        super().__init__(layout, file)
    
    def rules_text_and_pt_layers (self, text_and_icons):
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


# DOUBLE FACED CARD TEMPLATES

class TransformBackTemplate (NormalTemplate):
    """
     * Template for the back faces of transform cards.
    """
    def template_file_name (self):
        return "tf-back"
    
    def dfc_layer_group (self):
        return con.layers['TF_BACK']
    
    def __init__ (self, layout, file):
        super().__init__(layout, file)
        # set transform icon
        transform_group = psd.getLayerSet(self.dfc_layer_group(), con.layers['TEXT_AND_ICONS'])
        psd.getLayer(self.layout.transform_icon, transform_group).visible = True
    
    def basic_text_layers (self, text_and_icons):
        # if this is an eldrazi card, set the color of the rules text, type line, and power/toughness to black
        if self.layout.transform_icon == con.layers['MOON_ELDRAZI_DFC']:
            name = psd.getLayer(con.layers['NAME'], text_and_icons)
            if self.name_shifted: name = psd.getLayer(con.layers['NAME_SHIFT'], text_and_icons)
            type_line = psd.getLayer(con.layers['TYPE_LINE'], text_and_icons)
            if self.type_line_shifted: type_line = psd.getLayer(con.layers['TYPE_LINE_SHIFT'], text_and_icons)
            power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)

            name.textItem.color = psd.rgb_black()
            type_line.textItem.color = psd.rgb_black()
            power_toughness.textItem.color = psd.rgb_black()

        super().basic_text_layers(text_and_icons)


class TransformFrontTemplate (TransformBackTemplate):
    """
     * Template for the front faces of transform cards.
    """
    def template_file_name (self):
        return "tf-front"
    
    def dfc_layer_group (self):
        return con.layers['TF_FRONT']
    
    def __init__ (self, layout, file):
        try: self.other_face_is_creature = bool(layout.other_face_power and layout.other_face_toughness)
        except: self.other_face_is_creature = False
        super().__init__(layout, file)

        # if creature on back face, set flipside power/toughness
        if self.other_face_is_creature:
            flipside_power_toughness = psd.getLayer(con.layers['FLIPSIDE_POWER_TOUGHNESS'], con.layers['TEXT_AND_ICONS'])
            self.tx_layers.append(
                txt_layers.TextField(
                    layer = flipside_power_toughness,
                    text_contents = str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness),
                    text_color = psd.get_text_layer_color(flipside_power_toughness),
                )
            )

    def rules_text_and_pt_layers (self, text_and_icons):
        # overriding to select one of the four rules text layers

        # centre the rules text if the card has no flavor text, text is all on one line, and that line is fairly short
        is_centered = bool( len(self.layout.flavor_text) <= 1 and len(self.layout.oracle_text) <= 70 and self.layout.oracle_text.find("\n") < 0 )

        power_toughness = psd.getLayer(con.layers['POWER_TOUGHNESS'], text_and_icons)
        if self.is_creature:
            # creature card - set up creature layer for rules text and insert power & toughness
            rules_text = psd.getLayer(con.layers['RULES_TEXT_CREATURE'], text_and_icons)
            
            if self.other_face_is_creature:
                rules_text = psd.getLayer(con.layers['RULES_TEXT_CREATURE_FLIP'], text_and_icons)
            
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
            # noncreature card - use the normal rules text layer and disable the power/toughness layer
            rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)
            if self.other_face_is_creature:
                rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE_FLIP'], text_and_icons)
            
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
     * Template for the back faces of transforming cards from Ixalan block.
    """
    def template_file_name (self):
        return "ixalan"

    def __init__ (self, layout, file):
        super().__init__(layout, file)
    
    def basic_text_layers (self, text_and_icons):
        # typeline doesn't scale down with expansion symbol, and no mana cost layer
        name = psd.getLayer(con.layers['NAME'], text_and_icons)
        type_line = psd.getLayer(con.layers['TYPE_LINE'], text_and_icons)

        # Expansion symbol
        expansion_symbol = psd.getLayer(con.layers['EXPANSION_SYMBOL'], text_and_icons)
        if cfg.auto_symbol_size: expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'], text_and_icons)
        else: expansion_reference = None
        
        self.tx_layers.extend([
            txt_layers.TextField(
                layer = name,
                text_contents = self.layout.name,
                text_color = psd.get_text_layer_color(name),
            ),
            txt_layers.ExpansionSymbolField(
                layer = expansion_symbol,
                text_contents = self.symbol_char,
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
    
    def rules_text_and_pt_layers (self, text_and_icons):
        # overriding this because the ixalan template doesn't have power/toughness layers
        rules_text = psd.getLayer(con.layers['RULES_TEXT_NONCREATURE'], text_and_icons)
        self.tx_layers.append(
            txt_layers.FormattedTextArea(
                layer = rules_text,
                text_contents = self.layout.oracle_text,
                text_color = psd.get_text_layer_color(rules_text),
                flavor_text = self.layout.flavor_text,
                is_centered = False,
                reference_layer = psd.getLayer(con.layers['TEXTBOX_REFERENCE'], text_and_icons),
            ),
        )
    
    def enable_frame_layers (self):
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True

# MDFC CARDS
class MDFCBackTemplate (NormalTemplate):
    """
     * Template for the back faces of modal double faced cards.
    """
    def template_file_name (self):
        return "mdfc-back"
    
    def dfc_layer_group (self):
        return con.layers['MDFC_BACK']
    
    def __init__ (self, layout, file):
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
            ),
        ])


class MDFCFrontTemplate (MDFCBackTemplate):
    """
     * Template for the front faces of modal double faced cards.
    """
    def template_file_name (self):
        return "mdfc-front"
    
    def dfc_layer_group (self):
        return con.layers['MDFC_FRONT']

    def __init__(self, layout, file):
        super().__init__(layout, file)    

"""
Templates similar to NormalTemplate with new features
"""
class MutateTemplate (NormalTemplate):
    """
     * A template for Ikoria's mutate cards.  The layer structure of this template and NormalTemplate are close to identical, but this
     * template has a couple more text and reference layers for the top half of the textbox. It also doesn't include layers for Nyx
     * backgrounds or Companion crowns, but no mutate cards exist that would require these layers.
    """
    def template_file_name (self):
        return "mutate"
    
    def __init__ (self, layout, file):
        # split self.oracle_text between mutate text and actual text before calling self.super()
        split_rules_text = layout.oracle_text.split("\n")
        layout.mutate_text = split_rules_text[0]
        layout.oracle_text = "\n".join(split_rules_text[1:len(split_rules_text)])

        super().__init__(layout, file)

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
     * A template for Eldraine adventure cards. The layer structure of this template and NormalTemplate are close to identical, but this
     * template has a couple more text and reference layers for the left half of the textbox. It also doesn't include layers for Nyx 
     * backgrounds or Companion crowns, but no adventure cards exist that would require these layers.
    """
    def template_file_name (self):
        return "adventure"
    
    def __init__ (self, layout, file):
        super().__init__(layout, file)

        # add adventure name, mana cost, type line, and rules text fields to self.tx_layers
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        name = psd.getLayer(con.layers['NAME_ADVENTURE'], text_and_icons)
        mana_cost = psd.getLayer(con.layers['MANA_COST_ADVENTURE'], text_and_icons)
        rules_text = psd.getLayer(con.layers['RULES_TEXT_ADVENTURE'], text_and_icons)
        type_line = psd.getLayer(con.layers['TYPE_LINE_ADVENTURE'], text_and_icons)
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
            ),
        ])


class LevelerTemplate (NormalTemplate):
    """
     * Leveler template. No layers are scaled or positioned vertically so manual intervention is required.
    """
    def __init__ (self, layout, file):
        self.exit_early = True
        super().__init__(layout, file)

    def template_file_name (self):
        return "leveler"
    
    def rules_text_and_pt_layers (self, text_and_icons):
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
    
    def enable_frame_layers (self):

        # twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        psd.getLayer(self.layout.twins, con.layers['PT_AND_LEVEL_BOXES']).visible = True

        # pinlines and background
        psd.getLayer(self.layout.pinlines, con.layers['PINLINES_TEXTBOX']).visible = True
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True


class SagaTemplate (NormalTemplate):
    """
     * Saga template. No layers are scaled or positioned vertically so manual intervention is required.
    """
    def template_file_name (self):
        return "saga"
    
    def __init__ (self, layout, file):
        self.exit_early = True
        super().__init__(layout, file)

        # paste scryfall scan
        app.activeDocument.activeLayer = psd.getLayerSet(con.layers['TWINS'])
        self.paste_scryfall_scan(psd.getLayer(con.layers['SCRYFALL_SCAN_FRAME']))
    
    def rules_text_and_pt_layers (self, text_and_icons):
        saga_text_group = psd.getLayerSet("Saga", text_and_icons)
        stages = ["I", "II", "III", "IV"]

        for i in range(len(self.layout.saga_lines)):
            stage = stages[i]
            stage_group = psd.getLayerSet(stage, saga_text_group)
            stage_group.visible = True
            self.tx_layers.append(
                txt_layers.BasicFormattedTextField(
                    layer = psd.getLayer("Text", stage_group),
                    text_contents = self.layout.saga_lines[i],
                    text_color = psd.rgb_black()
                )
            )

    def enable_frame_layers (self):
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        psd.getLayer(self.layout.pinlines, con.layers['PINLINES_AND_SAGA_STRIPE']).visible = True
        psd.getLayer(self.layout.background, con.layers['TEXTBOX']).visible = True
        psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = True

"""
Planeswalker templates
"""
class PlaneswalkerTemplate (StarterTemplate):
    """
     * Planeswalker template - 3 or 4 loyalty abilities.
    """
    def template_file_name (self):
        return "pw"
    
    def __init__ (self, layout, file):
        self.exit_early = True
        super().__init__(layout, file)

        if self.layout.is_colorless: self.art_reference = psd.getLayer(con.layers['FULL_ART_FRAME'])
        else: self.art_reference = psd.getLayer(con.layers['PLANESWALKER_ART_FRAME'])

        ability_array = self.layout.oracle_text.split("\n")
        num_abilities = 3
        if len(ability_array) > 3: num_abilities = 4

        # docref for everything but legal and art reference is based on number of abilities
        self.docref = psd.getLayerSet("pw-"+str(num_abilities))
        self.docref.visible = True

        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'], self.docref)
        self.basic_text_layers(text_and_icons)

        # planeswalker ability layers
        group_names = [con.layers['FIRST_ABILITY'], con.layers['SECOND_ABILITY'], con.layers['THIRD_ABILITY'], con.layers['FOURTH_ABILITY']]
        loyalty_group = psd.getLayerSet(con.layers['LOYALTY_GRAPHICS'], self.docref)

        for i in range(len(ability_array)):
            if i == 4: break
            ability_group = psd.getLayerSet(group_names[i], loyalty_group)

            ability_text = ability_array[i]
            static_text_layer = psd.getLayer(con.layers['STATIC_TEXT'], ability_group)
            ability_text_layer = psd.getLayer(con.layers['ABILITY_TEXT'], ability_group)
            ability_layer = ability_text_layer
            colon_index = ability_text.find(": ")

            # determine if this is a static or activated ability by the presence of ":" in the start of the ability
            if colon_index > 0 and colon_index < 5:
                # activated ability

                # determine which loyalty group to enable, and set the loyalty symbol's text
                loyalty_graphic = psd.getLayerSet(ability_text[0], ability_group)
                loyalty_graphic.visible = True
                self.tx_layers.append(
                    txt_layers.TextField(
                        layer = psd.getLayer(con.layers['COST'], loyalty_graphic),
                        text_contents = ability_text[0:int(colon_index)],
                        text_color = psd.rgb_white(),
                    )
                )

                ability_text = ability_text[int(colon_index)+2:]

            else:
                # static ability
                ability_layer = static_text_layer
                ability_text_layer.visible = False
                static_text_layer.visible = True
                psd.getLayer("Colon", ability_group).visible = False
            
            self.tx_layers.append(
                txt_layers.BasicFormattedTextField(
                    layer = ability_layer,
                    text_contents = ability_text,
                    text_color = psd.get_text_layer_color(ability_layer),
                )
            )

        # starting loyalty
        self.tx_layers.append(
            txt_layers.TextField(
                layer = psd.getLayer(con.layers['TEXT'], psd.getLayerSet(con.layers['STARTING_LOYALTY'], loyalty_group)),
                text_contents = self.layout.scryfall['loyalty'],
                text_color = psd.rgb_white(),
            )
        )

        # paste scryfall scan
        app.activeDocument.activeLayer = psd.getLayerSet(con.layers['TEXTBOX'], self.docref)
        self.paste_scryfall_scan(psd.getLayer(con.layers['SCRYFALL_SCAN_FRAME']))
    
    def enable_frame_layers (self):
        # twins and pt box
        psd.getLayer(self.layout.twins, psd.getLayerSet(con.layers['TWINS'], self.docref)).visible = True

        # pinlines
        psd.getLayer(self.layout.pinlines, psd.getLayerSet(con.layers['PINLINES'], self.docref)).visible = True

        # background
        self.enable_background()

    
    def enable_background (self):
        psd.getLayer(self.layout.background, psd.getLayerSet(con.layers['BACKGROUND'], self.docref)).visible = True
    

class PlaneswalkerExtendedTemplate (PlaneswalkerTemplate):
    """
     * An extended version of PlaneswalkerTemplate. Functionally identical except for the lack of background textures.
    """
    def template_file_name (self):
        return "pw-extended"
    
    def enable_background (self):
        pass

"""

# Misc. Templates
PlanarTemplate = Class({
    extends_: ChilliBaseTemplate,
    template_file_name: function () {
        return "planar"
    },
    constructor: function (layout, file, file_path) {
        self.super(layout, file, file_path)
        exit_early = True

        docref = app.activeDocument
        self.art_reference = docref.layers.getByName(con.layers.ART_FRAME)
        // artist
        replace_text(docref.layers.getByName(con.layers.LEGAL).layers.getByName(con.layers.ARTIST), "Artist", self.layout.artist)

        // card name, type line, expansion symbol
        text_and_icons = docref.layers.getByName(con.layers.TEXT_AND_ICONS)
        name = text_and_icons.layers.getByName(con.layers.NAME)
        type_line = text_and_icons.layers.getByName(con.layers.TYPE_LINE)
        expansion_symbol = text_and_icons.layers.getByName(con.layers.EXPANSION_SYMBOL)

        // note: overwriting self.tx_layers because the paintbrush symbol is part of the artist text layer, so we inserted the
        // artist name separately earlier with replace_text(), and the artist usually comes for free with self.tx_layers.
        self.tx_layers = [
            new TextField(
                layer = name,
                text_contents = self.layout.name,
                text_color = get_text_layer_color(name),
            ),
            new ScaledTextField(
                layer = type_line,
                text_contents = self.layout.type_line,
                text_color = get_text_layer_color(type_line),
                reference_layer = expansion_symbol,
            )
        ]

        static_ability = text_and_icons.layers.getByName(con.layers.STATIC_ABILITY)
        chaos_ability = text_and_icons.layers.getByName(con.layers.CHAOS_ABILITY)

        if (self.layout.type_line === con.layers.PHENOMENON) {
            // phenomenon card - insert oracle text into static ability layer and disable chaos ability & layer mask on textbox
            self.tx_layers.push(
                new BasicFormattedTextField(
                    layer = static_ability,
                    text_contents = self.layout.oracle_text,
                    text_color = get_text_layer_color(static_ability),
                )
            )
            textbox = docref.layers.getByName(con.layers.TEXTBOX)
            docref.activeLayer = textbox
            disable_active_layer_mask()
            text_and_icons.layers.getByName(con.layers.CHAOS_SYMBOL).visible = False
            chaos_ability.visible = False
        } else {
            // plane card - split oracle text on last line break, insert everything before it into static ability layer and the rest
            // into chaos ability layer
            linebreak_index = self.layout.oracle_text.lastIndexOf("\n")
            self.tx_layers = self.tx_layers.concat([
                new BasicFormattedTextField(
                    layer = static_ability,
                    text_contents = self.layout.oracle_text.slice(0, linebreak_index),
                    text_color = get_text_layer_color(static_ability),
                ),
                new BasicFormattedTextField(
                    layer = chaos_ability,
                    text_contents = self.layout.oracle_text.slice(linebreak_index + 1),
                    text_color = get_text_layer_color(chaos_ability),
                ),
            ])
        }

        // paste scryfall scan
        app.activeDocument.activeLayer = docref.layers.getByName(con.layers.TEXTBOX)
        self.paste_scryfall_scan(app.activeDocument.layers.getByName(con.layers.SCRYFALL_SCAN_FRAME), file_path, True)
    },
    enable_frame_layers: function () { },
})
"""
"""
Basic land Templates
"""
class BasicLandTemplate (BaseTemplate):
    """
     * Basic land template - no text and icons (aside from legal), just a layer for each of the eleven basic lands.
    """
    def template_file_name (self):
        return "basic"
    
    def template_suffix (self):
        return self.layout.artist
    
    def __init__ (self, layout, file):
        super().__init__(layout, file)

        self.art_reference = psd.getLayer(con.layers['BASIC_ART_FRAME'])
        layout.is_basic = True

    def enable_frame_layers (self):
        psd.getLayer(self.layout.name).visible = True
        if cfg.auto_symbol_size: expansion_reference = psd.getLayer(con.layers['EXPANSION_REFERENCE'])
        else: expansion_reference = None
        self.tx_layers.append(
            txt_layers.ExpansionSymbolField(
                layer = psd.getLayer("Expansion Symbol"),
                text_contents = self.symbol_char,
                rarity = "common",
                reference = expansion_reference,
            )
        )

class BasicLandUnstableTemplate (BaseTemplate):
    """
     * Basic land template for the borderless basics from Unstable.
    """
    def template_file_name (self):
        return "basic-unstable"
    
    def template_suffix (self):
        return "Unstable - "+self.layout.artist
    
    def __init__ (self, layout, file):
        super().__init__(layout, file)

        self.art_reference = psd.getLayer(con.layers['BASIC_ART_FRAME'])
        layout.is_basic = True

    def enable_frame_layers (self):
        psd.getLayer(self.layout.name).visible = True

class BasicLandTherosTemplate (BasicLandTemplate):
    """
     * Basic land template for the full-art Nyx basics from Theros: Beyond Death.
    """
    def template_file_name (self):
        return "basic-theros"
    
    def template_suffix (self):
        return "Theros - "+self.layout.artist

class BasicLandClassicTemplate (BasicLandTemplate):
    """
     * Basic land template for 7th Edition basics.
    """
    def template_file_name (self):
        return "basic-classic"
    
    def template_suffix (self):
        return "Classic - "+self.layout.artist