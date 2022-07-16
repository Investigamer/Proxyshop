"""
MRTEFERI TEMPLATES
"""
from actions import pencilsketch, sketch
import proxyshop.templates as temp
from proxyshop.constants import con
from proxyshop.settings import cfg
import proxyshop.helpers as psd
import proxyshop.core as core
import photoshop.api as ps
app = ps.Application()


"""
LOAD CONFIGURATION
"""


my_config = core.import_json_config("MrTeferi/config.json")
sketch_cfg = my_config['Sketch']


"""
NORMAL TEMPLATES
"""


class SketchTemplate (temp.NormalTemplate):
    """
    Sketch showcase from MH2
    Original PSD by Nelynes
    """
    template_file_name = "MrTeferi/sketch"
    template_suffix = "Sketch"

    def __init__(self, layout):

        # Run a sketch action?
        if sketch_cfg['action'] == 1:
            self.art_action = sketch.run
        elif sketch_cfg['action'] == 2:
            self.art_action = pencilsketch.run
            self.art_action_args = {
                'rough_sketch': bool(sketch_cfg['rough-sketch-lines']),
                'draft_sketch': bool(sketch_cfg['draft-sketch-lines']),
                'colored': bool(sketch_cfg['colored']),
            }

        # self.art_action_args = [True]
        super().__init__(layout)

    def enable_hollow_crown(self, crown, pinlines, shadows=None):
        return


class KaldheimTemplate (temp.NormalTemplate):
    """
    Kaldheim viking legendary showcase.
    Original Template by FeuerAmeise
    """
    template_file_name = "MrTeferi/kaldheim"
    template_suffix = "Kaldheim"

    def __init__(self, layout):
        cfg.remove_reminder = True
        super().__init__(layout)

    def enable_frame_layers(self):

        # PT Box, no title boxes for this one
        if self.is_creature:
            # Check if vehicle
            if "Vehicle" in self.layout.type_line:
                psd.getLayer("Vehicle", con.layers['PT_BOX']).visible = True
            else: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True
        else: psd.getLayerSet(con.layers['PT_BOX']).visible = False

        # Land or not?
        if self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])

        # Check if vehicle
        if self.layout.type_line.find("Vehicle") >= 0: psd.getLayer("Vehicle", pinlines).visible = True
        else: psd.getLayer(self.layout.pinlines, pinlines).visible = True


class CrimsonFangTemplate (temp.NormalTemplate):
    """
    The crimson vow showcase template.
    Original template by michayggdrasil
    Works for Normal and Transform cards
    Transform is kinda experimental.
    """
    template_file_name = "MrTeferi/crimson-fang"
    template_suffix = "Fang"

    def enable_frame_layers(self):
        # Twins if transform card
        tf_twins = self.layout.twins+"-mdfc"

        # Transform stuff + twins
        if self.name_shifted:
            psd.getLayer("Button", con.layers['TEXT_AND_ICONS']).visible = True
            if self.layout.face == 0: psd.getLayer(con.layers['TF_FRONT'], con.layers['TEXT_AND_ICONS']).visible = True
            else: psd.getLayer(con.layers['TF_BACK'], con.layers['TEXT_AND_ICONS']).visible = True
            psd.getLayer(tf_twins, con.layers['TWINS']).visible = True
        else: psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True

        # PT Box
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines
        if self.name_shifted and self.layout.face == 1:
            pinlines = psd.getLayerSet("MDFC "+con.layers['PINLINES_TEXTBOX'])
            if not self.layout.is_colorless:
                psd.getLayer(self.layout.pinlines, con.layers['COLOR_INDICATOR']).visible = True
        elif self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # background
        psd.getLayer(self.layout.pinlines, con.layers['BACKGROUND']).visible = True

        if self.is_legendary:
            # legendary crown
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            border = psd.getLayerSet(con.layers['BORDER'])
            psd.getLayer(con.layers['NORMAL_BORDER'], border).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], border).visible = True


class PhyrexianTemplate (temp.NormalTemplate):
    """
    From the Phyrexian secret lair promo
    """
    template_file_name = "MrTeferi/phyrexian"
    template_suffix = "Phyrexian"

    def enable_frame_layers(self):

        # PT Box, no title boxes for this one
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True
        else: psd.getLayerSet(con.layers['PT_BOX']).visible = False

        # Pinlines, land or nonland?
        if self.is_land: psd.getLayer(self.layout.pinlines, con.layers['LAND_PINLINES_TEXTBOX']).visible = True
        else: psd.getLayer(self.layout.pinlines, con.layers['PINLINES_TEXTBOX']).visible = True


class DoubleFeatureTemplate (temp.NormalTemplate):
    """
    Midnight Hunt / Vow Double Feature Showcase
    Original assets from Warpdandy's Proximity Template
    """
    template_file_name = "MrTeferi/double-feature"
    template_suffix = "Double Feature"

    def enable_frame_layers(self):
        # Transform stuff
        """
        text_and_icons = psd.getLayerSet(con.layers['TEXT_AND_ICONS'])
        if self.name_shifted:
            psd.getLayer("Button", text_and_icons).visible = True
            if self.layout.face == 0: psd.getLayer(con.layers['TF_FRONT'], text_and_icons).visible = True
            else: psd.getLayer(con.layers['TF_BACK'], text_and_icons).visible = True
        """
        # PT Box
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # TF Card?
        if self.name_shifted and self.layout.face == 1:
            psd.getLayer(self.layout.pinlines, con.layers['COLOR_INDICATOR']).visible = True

        # Background
        psd.getLayer(self.layout.pinlines, con.layers['BACKGROUND']).visible = True

        # Legendary crown
        if self.is_legendary:
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True


class MaleMPCTemplate (temp.NormalTemplate):
    """
    MaleMPC's extended black box template.
    """
    template_file_name = "MrTeferi/male-mpc"
    template_suffix = "Extended Black"

    def __init__(self, layout):
        cfg.remove_reminder = True
        super().__init__(layout)

    def enable_frame_layers(self):
        # Type of pinlines
        if self.is_land:
            lower = "Lower Land Pinlines"
            upper = con.layers['LAND_PINLINES_TEXTBOX']
        else:
            lower = "Lower Pinlines"
            upper = con.layers['PINLINES_TEXTBOX']

        # Lower pinlines
        psd.getLayer(self.layout.pinlines, lower).visible = True

        # Hide pinlines and shadow if legendary
        if self.is_legendary:
            psd.enable_mask(psd.getLayer(con.layers['SHADOWS']))
            psd.enable_mask(psd.getLayerSet(upper))
        super().enable_frame_layers()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)


"""
CLASSIC TEMPLATE VARIANTS
"""


class PromoClassicTemplate (temp.NormalClassicTemplate):
    """
    Identical to NormalClassic
    Promo star added
    """
    template_suffix = "Classic Promo"

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add the promo star
        psd.getLayer("Promo Star", con.layers['TEXT_AND_ICONS']).visible = True


class ColorshiftedTemplate (temp.NormalTemplate):
    """
    Planar Chaos era colorshifted template
    Rendered from CC and MSE assets
    """
    template_file_name = "MrTeferi/colorshifted"
    template_suffix = "Shifted"

    def __init__(self, layout):
        cfg.real_collector = False
        super().__init__(layout)

    def enable_frame_layers(self):

        # White brush and artist for black border
        if self.layout.pinlines[0:1] == "B" and len(self.layout.pinlines) < 3:
            psd.getLayer("Artist", self.legal_layer).textItem.color = psd.rgb_white()
            psd.getLayer("Brush B", self.legal_layer).visible = False
            psd.getLayer("Brush W", self.legal_layer).visible = True

        # PT Box, no title boxes for this one
        if self.is_creature:
            # Check if vehicle
            if self.layout.type_line.find("Vehicle") >= 0:
                psd.getLayer("Vehicle", con.layers['PT_BOX']).visible = True
            else: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True
        else: psd.getLayerSet(con.layers['PT_BOX']).visible = False

        # Pinlines
        psd.getLayer(self.layout.pinlines, con.layers['PINLINES_TEXTBOX']).visible = True

        # Legendary crown
        if self.is_legendary:
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True

        # Alternate titleboxes
        if "Artifact" in self.layout.type_line and self.layout.pinlines != "Artifact":
            if self.is_legendary: psd.getLayer("Legendary Artifact", "Twins").visible = True
            else: psd.getLayer("Normal Artifact", "Twins").visible = True
        elif "Land" in self.layout.type_line:
            if self.is_legendary: psd.getLayer("Legendary Land", "Twins").visible = True
            else: psd.getLayer("Normal Land", "Twins").visible = True


"""
BASIC LAND TEMPLATES
"""


class BasicLandDarkMode (temp.BasicLandTemplate):
    """
    Basic land Dark Mode
    Credit to Vittorio Masia (Sid)
    """
    template_file_name = "MrTeferi/basic-dark-mode"
    template_suffix = f"Dark"

    def __init__(self, layout):
        cfg.save_artist_name = True
        super().__init__(layout)

    def collector_info(self):
        artist = psd.getLayer(con.layers['ARTIST'], con.layers['LEGAL'])
        psd.replace_text(artist, "Artist", self.layout.artist)

    def enable_frame_layers(self):
        psd.content_fill_empty_area(self.art_layer)
        super().enable_frame_layers()
