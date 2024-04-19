"""
* Plugin: Investigamer
"""
# Standard Library
from functools import cached_property
from typing import Optional, Callable

# Third Party
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src import CFG, ENV
from src.enums.layers import LAYERS
import src.helpers as psd
from src.templates import TransformMod, NormalTemplate, ExtendedMod

# Plugin Imports
from .actions import sketch, pencilsketch

"""
* Template Classes
"""


class SketchTemplate (NormalTemplate):
    """
    * Sketch showcase from MH2
    * Original PSD by Nelynes
    """
    template_suffix = "Sketch"

    """
    * Sketch Action
    """

    @property
    def art_action(self) -> Optional[Callable]:
        # Skip action if in test mode
        if ENV.TEST_MODE:
            return
        action = CFG.get_setting(
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
        # Skip if in test mode or using quick sketch
        if ENV.TEST_MODE or not self.art_action == pencilsketch.run:
            return
        return {
            'thr': self.event,
            'rough_sketch': CFG.get_setting(
                section="ACTION",
                key="Rough.Sketch.Lines",
                default=False
            ),
            'draft_sketch': CFG.get_setting(
                section="ACTION",
                key="Draft.Sketch.Lines",
                default=False
            ),
            'black_and_white': CFG.get_setting(
                section="ACTION",
                key="Black.And.White",
                default=False
            ),
            'manual_editing': CFG.get_setting(
                section="ACTION",
                key="Sketch.Manual.Editing",
                default=False
            )
        }


class KaldheimTemplate (NormalTemplate):
    """
    Kaldheim viking legendary showcase.
    Original Template by FeuerAmeise
    """
    template_suffix = "Kaldheim"

    # Static Properties
    is_legendary = False
    background_layer = None
    twins_layer = None

    """
    * Layer Properties
    """

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


class CrimsonFangTemplate (TransformMod, NormalTemplate):
    """The crimson vow showcase template. Original template by michayggdrasil.

    Notes:
        Transform features are kind of unfinished.
    """
    template_suffix = "Fang"

    # Static Properties
    is_flipside_creature = False

    """
    * Details
    """

    @property
    def background(self):
        # Use pinlines colors for background
        return self.pinlines

    """
    * Layer Properties
    """

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        # Support backside colors
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        if self.is_transform and not self.is_front:
            return psd.getLayer(self.pinlines, "MDFC " + LAYERS.PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    def enable_transform_layers(self):
        # Enable circle backing
        psd.getLayerSet(LAYERS.TRANSFORM, self.text_group).visible = True
        super().enable_transform_layers()

    def text_layers_transform(self) -> None:
        # No text layer changes
        pass


class PhyrexianTemplate (NormalTemplate):
    """From the Phyrexian secret lair promo."""
    template_suffix = "Phyrexian"

    # Static Properties
    background_layer = None
    twins_layer = None


class DoubleFeatureTemplate (NormalTemplate):
    """
    Midnight Hunt / Vow Double Feature Showcase
    Original assets from Warpdandy's Proximity Template
    Doesn't support companion, nyx, or twins layers.
    """
    template_suffix = "Double Feature"

    # Static Properties
    pinlines_layer = None
    twins_layer = None

    """
    * Layer Properties
    """

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.pinlines, LAYERS.BACKGROUND)


"""
CLASSIC TEMPLATE VARIANTS
"""


class ColorshiftedTemplate (NormalTemplate):
    """
    Planar Chaos era colorshifted template
    Rendered from CC and MSE assets. Most title boxes are built into pinlines.
    Doesn't support special layers for nyx, companion, land, or colorless.
    """
    template_suffix = "Colorshifted"

    # Static Properties
    is_land = False
    is_colorless = False

    """
    * Layer Properties
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
    * Methods
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


class BasicLandDarkMode (ExtendedMod, NormalTemplate):
    """Basic land Dark Mode. Credit to Vittorio Masia (Sid)

    Todo:
        Transition to 'Normal' type.
    """
    template_suffix = "Dark Mode"

    def collector_info(self):
        # Collector info only has artist
        psd.getLayer(LAYERS.ARTIST, self.legal_group).textItem.contents = self.layout.artist
