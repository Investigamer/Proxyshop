"""
MRTEFERI TEMPLATES
"""
# Standard Library
from functools import cached_property
from typing import Optional, Callable

# Third Party
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.templates import (
    BasicLandTemplate,
    NormalEssentialsTemplate
)
from actions import pencilsketch, sketch
from src.enums.layers import LAYERS
from src.settings import cfg
import src.helpers as psd


"""
NORMAL TEMPLATES
"""


class SketchTemplate (NormalEssentialsTemplate):
    """
    Sketch showcase from MH2
    Original PSD by Nelynes
    """
    template_suffix = "Sketch"

    """
    SKETCH ACTION
    """

    @property
    def art_action(self) -> Optional[Callable]:
        action = cfg.get_setting(
            section="ACTION",
            key="Sketch.Action",
            default="Advanced Sketch",
            is_bool=False
        )
        if action == "Advanced Sketch":
            return pencilsketch.run
        if action == "Quick Sketch":
            return sketch.run
        return

    @property
    def art_action_args(self) -> Optional[dict]:
        if not self.art_action == pencilsketch.run:
            return
        return {
            'thr': self.event,
            'rough_sketch': cfg.get_setting(
                section="ACTION",
                key="Rough.Sketch.Lines",
                default=False
            ),
            'draft_sketch': cfg.get_setting(
                section="ACTION",
                key="Draft.Sketch.Lines",
                default=False
            ),
            'black_and_white': cfg.get_setting(
                section="ACTION",
                key="Black.And.White",
                default=False
            ),
            'manual_editing': cfg.get_setting(
                section="ACTION",
                key="Sketch.Manual.Editing",
                default=False
            )
        }


class KaldheimTemplate (NormalEssentialsTemplate):
    """
    Kaldheim viking legendary showcase.
    Original Template by FeuerAmeise
    """
    template_suffix = "Kaldheim"

    """
    TOGGLE
    """

    @property
    def is_legendary(self) -> bool:
        return False

    """
    LAYERS
    """

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        # Enable vehicle support
        if "Vehicle" in self.layout.type_line:
            return psd.getLayer("Vehicle", LAYERS.PT_BOX)
        return psd.getLayer(self.twins, LAYERS.PT_BOX)

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Enable vehicle support
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        if "Vehicle" in self.layout.type_line:
            return psd.getLayer("Vehicle", LAYERS.PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)


class CrimsonFangTemplate (NormalEssentialsTemplate):
    """
    The crimson vow showcase template.
    Original template by michayggdrasil
    Works for Normal and Transform cards
    Transform is kinda experimental.
    """
    template_suffix = "Fang"

    """
    TOGGLE
    """

    @property
    def background(self):
        return self.pinlines

    """
    LAYERS
    """

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Pinlines
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        if self.is_transform and not self.is_front:
            return psd.getLayer(self.pinlines, "MDFC " + LAYERS.PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    @cached_property
    def transform_icon_layer(self) -> Optional[ArtLayer]:
        if self.is_transform and self.is_front:
            return psd.getLayer("tf-front", self.text_group)
        elif self.is_transform:
            return psd.getLayer("tf-back", self.text_group)
        return

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add transform if necessary
        if self.transform_icon_layer:
            psd.getLayerSet(LAYERS.TRANSFORM, self.text_group).visible = True
            self.transform_icon_layer.visible = True


class PhyrexianTemplate (NormalEssentialsTemplate):
    """
    From the Phyrexian secret lair promo
    """
    template_suffix = "Phyrexian"

    """
    LAYERS
    """

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return


class DoubleFeatureTemplate (NormalEssentialsTemplate):
    """
    Midnight Hunt / Vow Double Feature Showcase
    Original assets from Warpdandy's Proximity Template
    Doesn't support companion, nyx, or twins layers.
    """
    template_suffix = "Double Feature"

    """
    LAYERS
    """

    @property
    def twins_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, LAYERS.BACKGROUND)


"""
CLASSIC TEMPLATE VARIANTS
"""


class ColorshiftedTemplate (NormalEssentialsTemplate):
    """
    Planar Chaos era colorshifted template
    Rendered from CC and MSE assets. Most titleboxes are built into pinlines.
    Doesn't support special layers for nyx, companion, land, or colorless.
    """
    template_suffix = "Shifted"

    """
    TOGGLE
    """

    @property
    def is_land(self) -> bool:
        return False

    @property
    def is_colorless(self) -> bool:
        return False

    """
    LAYERS
    """

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
                return psd.getLayer("Vehicle", LAYERS.PT_BOX)
            return psd.getLayer(self.twins, LAYERS.PT_BOX)
        return psd.getLayerSet(LAYERS.PT_BOX)

    """
    METHODS
    """

    def collector_info(self):
        # Artist and set layer
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        psd.replace_text(artist_layer, "Artist", self.layout.artist)

        # Switch to white brush and artist name
        if self.layout.pinlines[0:1] == "B" and len(self.pinlines) < 3:
            artist_layer.textItem.color = psd.rgb_white()
            psd.getLayer("Brush B", self.legal_group).visible = False
            psd.getLayer("Brush W", self.legal_group).visible = True


"""
BASIC LAND TEMPLATES
"""


class BasicLandDarkMode (BasicLandTemplate):
    """
    Basic land Dark Mode
    Credit to Vittorio Masia (Sid)
    """
    template_suffix = "Dark"

    @cached_property
    def is_content_aware_enabled(self):
        return True

    def collector_info(self):
        # Collector info only has artist
        psd.replace_text(psd.getLayer(LAYERS.ARTIST, self.legal_group), "Artist", self.layout.artist)
