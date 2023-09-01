"""
* BATTLE TEMPLATES
"""
# Standard Library
from functools import cached_property
from typing import Callable, Optional, Union

# Third Party Imports
from photoshop.api import SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
import src.helpers as psd
from src.enums.layers import LAYERS
from src.enums.mtg import pinline_color_map
from src.layouts import BattleLayout
from src.text_layers import TextField, CreatureFormattedTextArea
from src.templates._core import BaseTemplate
from src.templates._vector import VectorTemplate


"""
MODIFIER CLASSES
"""


class BattleMod (BaseTemplate):
    """
    * A template modifier for Battle cards introduced in March of the Machine.

    Adds:
        * Defense text in bottom right of the card.
        * Flipside Power/Toughness text if reverse side is a creature.
        * Might add support for Transform icon in the future, if other symbols are used.
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Add Class text layers."""
        funcs = [self.text_layers_battle] if isinstance(self.layout, BattleLayout) else []
        return [*super().text_layer_methods, *funcs]

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_name(self) -> Optional[ArtLayer]:
        """Doesn't need to be shifted."""
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        """Supports noncreature and creature, with or without flipside PT."""
        if self.is_transform and self.is_front and self.is_flipside_creature:
            return psd.getLayer(LAYERS.RULES_TEXT_FLIP, self.text_group)
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @cached_property
    def text_layer_flipside_pt(self) -> Optional[ArtLayer]:
        """Flipside power/toughness layer for front face Transform cards."""
        return psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_group)

    @cached_property
    def text_layer_defense(self) -> Optional[ArtLayer]:
        """Battle defense number in bottom right corner."""
        return psd.getLayer(LAYERS.DEFENSE, self.text_group)

    """
    REFERENCES
    """

    @cached_property
    def pt_top_reference(self) -> Optional[ArtLayer]:
        """Reference used to get the top of the PT box."""
        return psd.getLayer(
            f"{LAYERS.PT_TOP_REFERENCE} Flip" if self.is_flipside_creature else LAYERS.PT_TOP_REFERENCE,
            self.text_group)

    @cached_property
    def pt_adjustment_reference(self) -> Optional[ArtLayer]:
        """Reference used to get the location of the PT box."""
        return psd.getLayer(
            f"{LAYERS.PT_REFERENCE} Flip" if self.is_flipside_creature else LAYERS.PT_REFERENCE,
            self.text_group)

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:
        """Overwrite rules text to enforce vertical text nudge with defense shield collision."""

        # Call super instead if not a Battle type card
        if not isinstance(self.layout, BattleLayout):
            return super().rules_text_and_pt_layers()

        # Rules Text and Power / Toughness
        self.text.extend([
            CreatureFormattedTextArea(
                layer = self.text_layer_rules,
                contents = self.layout.oracle_text,
                flavor = self.layout.flavor_text,
                reference = self.textbox_reference,
                divider = self.divider_layer,
                pt_reference = self.pt_adjustment_reference,
                pt_top_reference = self.pt_top_reference,
                centered = self.is_centered
            ),
            TextField(
                layer = self.text_layer_pt,
                contents = f"{self.layout.power}/{self.layout.toughness}"
            ) if self.is_creature else None
        ])

    def post_text_layers(self) -> None:
        """Rotate document 90 degrees counter-clockwise before saving."""

        # Call super instead if not a Battle type card
        if not isinstance(self.layout, BattleLayout):
            return super().post_text_layers()
        psd.rotate_counter_clockwise()

    """
    BATTLE METHODS
    """

    def text_layers_battle(self) -> None:
        """Add and modify text layers required by Battle cards."""

        # Add defense text
        self.text.append(
            TextField(
                layer=self.text_layer_defense,
                contents=self.layout.defense))

        # Add flipside Power/Toughness
        if self.is_flipside_creature:
            self.text.append(
                TextField(
                    layer=self.text_layer_flipside_pt,
                    contents=str(self.layout.other_face_power) + "/" + str(self.layout.other_face_toughness)
                )
            )


"""
TEMPLATE CLASSES
"""


class BattleTemplate (BattleMod, VectorTemplate):
    """Battle template using vector shape layers and automatic pinlines / multicolor generation."""

    """
    BOOLS
    """

    @property
    def is_legendary(self) -> bool:
        return False

    """
    GROUPS
    """

    @property
    def background_group(self) -> Optional[LayerSet]:
        return

    """
    COLORS
    """

    @cached_property
    def pinlines_colors(self) -> Union[SolidColor, list[dict]]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity if 1 < len(self.identity) < self.color_limit else self.pinlines,
            color_map=self.pinline_color_map,
            location_map={2: [.4543, .5886]}
        )

    """
    SHAPES
    """

    @cached_property
    def textbox_shape(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.NORMAL, [self.textbox_group, LAYERS.SHAPE])

    @cached_property
    def enabled_shapes(self) -> list[Union[ArtLayer, LayerSet, None]]:
        return [self.textbox_shape]


class UniversesBeyondBattleTemplate (BattleTemplate):
    """Universes Beyond version of BattleTemplate."""

    """
    COLORS
    """

    @cached_property
    def pinline_color_map(self) -> dict:
        colors = pinline_color_map.copy()
        colors.update({
            'W': [246, 247, 241],
            'U': [0, 131, 193],
            'B': [44, 40, 33],
            'R': [237, 66, 31],
            'G': [5, 129, 64],
            'Gold': [239, 209, 107],
            'Land': [165, 150, 132],
            'Artifact': [227, 228, 230],
            'Colorless': [227, 228, 230]
        })
        return colors

    @cached_property
    def twins_colors(self) -> Optional[str]:
        return f"{self.twins} Beyond"

    """
    GROUPS
    """

    @cached_property
    def textbox_group(self) -> LayerSet:
        """Textbox Beyond group."""
        return psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond")

    """
    SHAPES
    """

    @cached_property
    def textbox_shape(self) -> Optional[ArtLayer]:
        return psd.getLayer(LAYERS.NORMAL, [self.textbox_group, LAYERS.SHAPE])
