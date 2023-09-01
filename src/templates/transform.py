"""
* DOUBLE FACED TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional, Callable

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src.templates._core import BaseTemplate, NormalTemplate
from src.templates._vector import VectorTemplate
from src.enums.photoshop import Dimensions
from src.enums.mtg import TransformIcons
from src.text_layers import TextField
from src.enums.layers import LAYERS
import src.helpers as psd


"""
* TRANSFORM MODIFIER CLASSES
"""


class TransformMod(BaseTemplate):
    """
    * Modifier for Transform templates.

    Adds:
        * Flipside power/toughness on the front if opposite side is a Creature.
        * Transform icon, inherited from BaseTemplate, is made visible.
    Modifies:
        * Rules text layer has 2 new options: a creature and noncreature option with flipside PT cutout.
        * PT, name, and type text are all white UNLESS this is an eldrazi, e.g. Eldritch Moon transform cards.
    """

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        # Add Transform frame layers step
        parent_funcs = super().frame_layer_methods
        return [*parent_funcs, self.enable_transform_layers] if self.is_transform else parent_funcs

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        # Add Transform text layers step
        parent_funcs = super().text_layer_methods
        return [*parent_funcs, self.text_layers_transform] if self.is_transform else parent_funcs

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Supports noncreature and creature, with or without flipside PT."""
        if self.is_transform and self.is_front and self.is_flipside_creature:
            if self.is_creature:
                return psd.getLayer(LAYERS.RULES_TEXT_CREATURE_FLIP, self.text_group)
            return psd.getLayer(LAYERS.RULES_TEXT_NONCREATURE_FLIP, self.text_group)
        return super().text_layer_rules

    @cached_property
    def text_layer_flipside_pt(self) -> Optional[ArtLayer]:
        """Flipside power/toughness layer for front face Transform cards."""
        return psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_group)

    """
    FRAME LAYER METHODS
    """

    def enable_transform_layers(self) -> None:
        """Enable layers that are required by transform cards."""

        # Enable transform icon
        if self.transform_icon_layer:
            self.transform_icon_layer.visible = True

        # Enable front / back specific layers
        if self.is_front:
            return self.enable_transform_layers_front()
        return self.enable_transform_layers_back()

    def enable_transform_layers_front(self) -> None:
        """Enables layers that are required by front face transform cards."""
        pass

    def enable_transform_layers_back(self) -> None:
        """Enables layers that are required by back face transform cards."""
        pass

    """
    TEXT LAYER METHODS
    """

    def text_layers_transform(self) -> None:
        """Adds and modifies text layers for transform cards."""

        # Enable front / back specific layers
        if self.is_front:
            return self.text_layers_transform_front()
        return self.text_layers_transform_back()

    def text_layers_transform_front(self) -> None:
        """Adds and modifies text layers for front face transform cards."""

        # Add flipside Power/Toughness
        if self.is_flipside_creature:
            self.text.append(
                TextField(
                    layer=self.text_layer_flipside_pt,
                    contents=str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness)
                )
            )

    def text_layers_transform_back(self) -> None:
        """Adds and modifies text layers for back face transform cards."""

        # Rear face Eldrazi cards: Black rules, typeline, and PT text
        if self.layout.transform_icon == TransformIcons.MOONELDRAZI:
            self.text_layer_name.textItem.color = self.RGB_BLACK
            self.text_layer_type.textItem.color = self.RGB_BLACK
            if self.is_creature:
                self.text_layer_pt.textItem.color = self.RGB_BLACK


class VectorTransformMod(TransformMod, VectorTemplate):
    """Transform mod for vector templates."""

    """
    FRAME LAYERS
    """

    @cached_property
    def transform_circle_layer(self) -> Optional[ArtLayer]:
        """White circle backing behind Transform Icon."""
        return psd.getLayerSet(LAYERS.TRANSFORM, self.text_group)

    """
    FRAME LAYER METHODS
    """

    def enable_transform_layers(self) -> None:
        """Enable layers that are required by transform cards."""

        # Enable transform circle background
        self.transform_circle_layer.visible = True
        super().enable_transform_layers()

    """
    TEXT LAYER METHODS
    """

    def text_layers_transform_back(self) -> None:
        """Adds and modifies text layers for back face transform cards."""

        # Rear face non-Eldrazi cards: White rules, typeline, and PT text with FX enabled
        if self.layout.transform_icon != TransformIcons.MOONELDRAZI:
            psd.enable_layer_fx(self.text_layer_name)
            psd.enable_layer_fx(self.text_layer_type)
            self.text_layer_name.textItem.color = psd.rgb_white()
            self.text_layer_type.textItem.color = psd.rgb_white()
            if self.is_creature:
                psd.enable_layer_fx(self.text_layer_pt)
                self.text_layer_pt.textItem.color = psd.rgb_white()


"""
* TRANSFORM TEMPLATE CLASSES
"""


class TransformTemplate (TransformMod, NormalTemplate):
    """Template for double faced Transform cards introduced in Innistrad block."""


class IxalanTemplate (NormalTemplate):
    """Template for the back face lands for transforming cards from Ixalan block."""

    """
    TOGGLE
    """

    @property
    def is_creature(self) -> bool:
        # Only lands for this one
        return False

    @property
    def is_name_shifted(self) -> bool:
        # No transform icon to shift name
        return False

    """
    EXPANSION SYMBOL
    """

    @cached_property
    def expansion_symbol_alignments(self) -> list[Dimensions]:
        # Expansion symbol is entirely centered
        return [Dimensions.CenterX, Dimensions.CenterY]

    """
    FRAME LAYERS
    """

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:
        # Uses pinline color for background choice
        return psd.getLayer(self.pinlines, LAYERS.BACKGROUND)

    """
    METHODS
    """

    def basic_text_layers(self):
        # No mana cost layer, no scaling typeline
        self.text.extend([
            TextField(
                layer = self.text_layer_name,
                contents = self.layout.name),
            TextField(
                layer = self.text_layer_type,
                contents = self.layout.type_line)
        ])

    def enable_frame_layers(self):
        # Only background frame layer
        self.background_layer.visible = True
