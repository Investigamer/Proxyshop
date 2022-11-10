"""
MRTEFERI TEMPLATES
"""
from functools import cached_property
from typing import Optional

from photoshop.api._artlayer import ArtLayer

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

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

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

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        if "Vehicle" in self.layout.type_line:
            return psd.getLayer("Vehicle", con.layers['PT_BOX'])
        return psd.getLayer(self.twins, con.layers['PT_BOX'])

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        if self.is_land:
            return psd.getLayer(self.pinlines, con.layers['LAND_PINLINES_TEXTBOX'])
        if "Vehicle" in self.layout.type_line:
            return psd.getLayer("Vehicle", con.layers['PINLINES_TEXTBOX'])
        return psd.getLayer(self.pinlines, con.layers['PINLINES_TEXTBOX'])


class CrimsonFangTemplate (temp.NormalTemplate):
    """
    The crimson vow showcase template.
    Original template by michayggdrasil
    Works for Normal and Transform cards
    Transform is kinda experimental.
    """
    template_file_name = "MrTeferi/crimson-fang"
    template_suffix = "Fang"

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Pinlines
        if self.is_land:
            return psd.getLayer(self.pinlines, con.layers['LAND_PINLINES_TEXTBOX'])
        if self.name_shifted and not self.is_front:
            return psd.getLayer(self.pinlines, "MDFC " + con.layers['PINLINES_TEXTBOX'])
        return psd.getLayer(self.pinlines, con.layers['PINLINES_TEXTBOX'])

    @cached_property
    def transform_icon(self) -> Optional[ArtLayer]:
        if self.name_shifted and self.is_front:
            return psd.getLayer("tf-front", [self.text_layers])
        elif self.name_shifted:
            return psd.getLayer("tf-back", [self.text_layers])
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add transform if necessary
        if self.name_shifted and self.transform_icon:
            psd.getLayer("Button", self.text_layers).visible = True
            self.transform_icon.visible = True


class PhyrexianTemplate (temp.NormalTemplate):
    """
    From the Phyrexian secret lair promo
    """
    template_file_name = "MrTeferi/phyrexian"
    template_suffix = "Phyrexian"

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return


class DoubleFeatureTemplate (temp.NormalTemplate):
    """
    Midnight Hunt / Vow Double Feature Showcase
    Original assets from Warpdandy's Proximity Template
    Doesn't support companion, nyx, or twins layers.
    """
    template_file_name = "MrTeferi/double-feature"
    template_suffix = "Double Feature"

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        return


class MaleMPCTemplate (temp.NormalTemplate):
    """
    MaleMPC's extended black box template.
    """
    template_file_name = "MrTeferi/male-mpc"
    template_suffix = "Extended Black"

    def __init__(self, layout):
        cfg.remove_reminder = True
        super().__init__(layout)

    @cached_property
    def pinlines_layer_bottom(self) -> Optional[ArtLayer]:
        if self.is_land:
            return psd.getLayer(self.pinlines, "Lower Land Pinlines")
        return psd.getLayer(self.pinlines, "Lower Pinlines")

    def enable_frame_layers(self):

        # Hide pinlines and shadow if legendary
        super().enable_frame_layers()

        # Lower pinlines
        self.pinlines_layer_bottom.visible = True

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)

    def enable_crown(self):
        psd.enable_mask(psd.getLayer(con.layers['SHADOWS']))
        psd.enable_mask(self.pinlines_layer.parent)
        super().enable_crown()


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
    Rendered from CC and MSE assets. Most titleboxes are built into pinlines.
    Doesn't support special layers for nyx, companion, land, or colorless.
    """
    template_file_name = "MrTeferi/colorshifted"
    template_suffix = "Shifted"

    def __init__(self, layout):
        cfg.real_collector = False
        super().__init__(layout)

    @cached_property
    def twins_layer(self) -> Optional[ArtLayer]:
        if "Artifact" in self.layout.type_line and self.pinlines != "Artifact":
            if self.is_legendary:
                return psd.getLayer("Legendary Artifact", "Twins")
            return psd.getLayer("Normal Artifact", "Twins")
        elif "Land" in self.layout.type_line:
            if self.is_legendary:
                return psd.getLayer("Legendary Land", "Twins")
            return psd.getLayer("Normal Land", "Twins")
        return

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        if self.is_creature:
            # Check if vehicle
            if "Vehicle" in self.layout.type_line:
                return psd.getLayer("Vehicle", con.layers['PT_BOX'])
            return psd.getLayer(self.twins, con.layers['PT_BOX'])
        return psd.getLayerSet(con.layers['PT_BOX'])

    @property
    def is_nyx(self) -> bool:
        return False

    @property
    def is_companion(self) -> bool:
        return False

    @property
    def is_land(self) -> bool:
        return False

    @property
    def is_colorless(self) -> bool:
        return False

    def enable_frame_layers(self):

        # White brush and artist for black border
        if self.layout.pinlines[0:1] == "B" and len(self.pinlines) < 3:
            psd.getLayer("Artist", self.legal_layer).textItem.color = psd.rgb_white()
            psd.getLayer("Brush B", self.legal_layer).visible = False
            psd.getLayer("Brush W", self.legal_layer).visible = True

        super().enable_frame_layers()


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
        # Collector info only has artist
        psd.replace_text(psd.getLayer(con.layers['ARTIST'], self.legal_layer), "Artist", self.layout.artist)

    def load_artwork(self):
        super().load_artwork()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)
