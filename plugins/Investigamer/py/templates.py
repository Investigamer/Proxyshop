"""
* Plugin: Investigamer
"""

from collections.abc import Callable
from functools import cached_property

from photoshop.api._artlayer import ArtLayer

import src.helpers as psd
from src.enums.layers import LAYERS
from src.templates import ExtendedMod, NormalTemplate, TransformMod

from .actions import pencilsketch, sketch

"""
* Template Classes
"""


class SketchTemplate(NormalTemplate):
    """
    * Sketch showcase from MH2
    * Original PSD by Nelynes
    """

    template_suffix = "Sketch"

    """
    * Sketch Action
    """

    @cached_property
    def art_action(self) -> Callable[[], None] | None:
        action = self.config.get_setting(
            section="ACTION", key="Sketch.Action", default="Advanced Sketch"
        )
        if action == "Advanced Sketch":
            return lambda: pencilsketch.run(
                self.render_operation,
                draft_sketch=self.config.get_bool_setting(
                    section="ACTION", key="Draft.Sketch.Lines", default=False
                ),
                rough_sketch=self.config.get_bool_setting(
                    section="ACTION", key="Rough.Sketch.Lines", default=False
                ),
                black_and_white=self.config.get_bool_setting(
                    section="ACTION", key="Black.And.White", default=False
                ),
                manual_editing=self.config.get_bool_setting(
                    section="ACTION", key="Sketch.Manual.Editing", default=False
                ),
            )
        if action == "Quick Sketch":
            return sketch.run
        return


class KaldheimTemplate(NormalTemplate):
    """
    Kaldheim viking legendary showcase.
    Original Template by FeuerAmeise
    """

    template_suffix = "Kaldheim"

    # Static Properties
    @cached_property
    def is_legendary(self) -> bool:
        return False

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        return None

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
        return None

    """
    * Layer Properties
    """

    @cached_property
    def pt_layer(self) -> ArtLayer | None:
        # Enable vehicle support
        if "Vehicle" in self.layout.type_line:
            return psd.getLayer("Vehicle", LAYERS.PT_BOX)
        return psd.getLayer(self.twins, LAYERS.PT_BOX)

    @cached_property
    def pinlines_layer(self) -> ArtLayer | None:
        # Enable vehicle support
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        if "Vehicle" in self.layout.type_line:
            return psd.getLayer("Vehicle", LAYERS.PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)


class CrimsonFangTemplate(TransformMod, NormalTemplate):
    """The crimson vow showcase template. Original template by michayggdrasil.

    Notes:
        Transform features are kind of unfinished.
    """

    template_suffix = "Fang"

    # Static Properties
    @cached_property
    def is_flipside_creature(self) -> bool:
        return False

    """
    * Details
    """

    @cached_property
    def background(self) -> str:
        # Use pinlines colors for background
        return self.pinlines

    """
    * Layer Properties
    """

    @cached_property
    def pinlines_layer(self) -> ArtLayer | None:
        # Support backside colors
        if self.is_land:
            return psd.getLayer(self.pinlines, LAYERS.LAND_PINLINES_TEXTBOX)
        if self.is_transform and not self.is_front:
            return psd.getLayer(self.pinlines, "MDFC " + LAYERS.PINLINES_TEXTBOX)
        return psd.getLayer(self.pinlines, LAYERS.PINLINES_TEXTBOX)

    def enable_transform_layers(self):
        # Enable circle backing
        if layer := psd.getLayerSet(LAYERS.TRANSFORM, self.text_group):
            layer.visible = True
        super().enable_transform_layers()

    def text_layers_transform(self) -> None:
        # No text layer changes
        pass


class PhyrexianTemplate(NormalTemplate):
    """From the Phyrexian secret lair promo."""

    template_suffix = "Phyrexian"

    # Static Properties
    @cached_property
    def background_layer(self) -> ArtLayer | None:
        return None

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
        return None


class DoubleFeatureTemplate(NormalTemplate):
    """
    Midnight Hunt / Vow Double Feature Showcase
    Original assets from Warpdandy's Proximity Template
    Doesn't support companion, nyx, or twins layers.
    """

    template_suffix = "Double Feature"

    # Static Properties
    @cached_property
    def pinlines_layer(self) -> ArtLayer | None:
        return None

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
        return None

    """
    * Layer Properties
    """

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        return psd.getLayer(self.pinlines, LAYERS.BACKGROUND)


"""
CLASSIC TEMPLATE VARIANTS
"""


class ColorshiftedTemplate(NormalTemplate):
    """
    Planar Chaos era colorshifted template
    Rendered from CC and MSE assets. Most title boxes are built into pinlines.
    Doesn't support special layers for nyx, companion, land, or colorless.
    """

    template_suffix = "Colorshifted"

    # Static Properties
    @cached_property
    def is_land(self) -> bool:
        return False

    @cached_property
    def is_colorless(self) -> bool:
        return False

    """
    * Layer Properties
    """

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
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
    def pt_layer(self) -> ArtLayer | None:
        if self.is_creature:
            # Check if vehicle
            if "Vehicle" in self.layout.type_line:
                return psd.getLayer("Vehicle", LAYERS.PT_BOX)
            return psd.getLayer(self.twins, LAYERS.PT_BOX)

    """
    * Methods
    """

    def collector_info(self):
        # Artist and set layer
        artist_layer = psd.getLayer(LAYERS.ARTIST, self.legal_group)
        if artist_layer:
            psd.replace_text(artist_layer, "Artist", self.layout.artist)

        # Switch to white brush and artist name
        if self.layout.pinlines[0:1] == "B" and len(self.pinlines) < 3:
            if artist_layer:
                artist_layer.textItem.color = psd.rgb_white()
            if layer := psd.getLayer("Brush B", self.legal_group):
                layer.visible = False
            if layer := psd.getLayer("Brush W", self.legal_group):
                layer.visible = True


"""
BASIC LAND TEMPLATES
"""


class BasicLandDarkMode(ExtendedMod, NormalTemplate):
    """Basic land Dark Mode. Credit to Vittorio Masia (Sid)

    Todo:
        Transition to 'Normal' type.
    """

    template_suffix = "Dark Mode"

    def collector_info(self):
        # Collector info only has artist
        if layer := psd.getLayer(LAYERS.ARTIST, self.legal_group):
            layer.textItem.contents = self.layout.artist
