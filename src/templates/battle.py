"""
* BATTLE TEMPLATES
"""

from collections.abc import Callable, Sequence
from functools import cached_property

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
from src.enums.layers import LAYERS
from src.helpers.layers import get_reference_layer
from src.layouts import BattleLayout, NormalLayout
from src.schema.colors import ColorObject, GradientConfig, pinlines_color_map
from src.templates._core import BaseTemplate
from src.templates._vector import VectorTemplate
from src.text_layers import FormattedTextArea, TextField
from src.utils.adobe import ReferenceLayer

"""
* Modifier Classes
"""


class BattleMod(BaseTemplate):
    """
    * A template modifier for Battle cards introduced in March of the Machine.

    Adds:
        * Defense text in bottom right of the card.
        * Flipside Power/Toughness text if reverse side is a creature.
        * Might add support for Transform icon in the future, if other symbols are used.
    """

    def __init__(self, layout: NormalLayout):
        super().__init__(layout)

    """
    * Layout Check
    """

    @cached_property
    def is_layout_battle(self) -> bool:
        """bool: Checks if this card matches BattleLayout."""
        return isinstance(self.layout, BattleLayout)

    """
    * Mixin Methods
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Class text layers."""
        funcs = [self.text_layers_battle] if self.is_layout_battle else []
        return [*super().text_layer_methods, *funcs]

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Rotate card sideways."""
        funcs = [psd.rotate_counter_clockwise] if self.is_layout_battle else []
        return [*super().post_text_methods, *funcs]

    """
    * Text Layers
    """

    @cached_property
    def text_layer_name(self) -> ArtLayer | None:
        """Doesn't need to be shifted."""
        return psd.getLayer(LAYERS.NAME, self.text_group)

    @cached_property
    def text_layer_rules(self) -> ArtLayer | None:
        """Supports noncreature and creature, with or without flipside PT."""
        if self.is_transform and self.is_front and self.is_flipside_creature:
            return psd.getLayer(LAYERS.RULES_TEXT_FLIP, self.text_group)
        return psd.getLayer(LAYERS.RULES_TEXT, self.text_group)

    @cached_property
    def text_layer_flipside_pt(self) -> ArtLayer | None:
        """Flipside power/toughness layer for front face Transform cards."""
        return psd.getLayer(LAYERS.FLIPSIDE_POWER_TOUGHNESS, self.text_group)

    @cached_property
    def text_layer_defense(self) -> ArtLayer | None:
        """Battle defense number in bottom right corner."""
        return psd.getLayer(LAYERS.DEFENSE, self.text_group)

    """
    * References
    """

    @cached_property
    def defense_reference(self) -> ReferenceLayer | None:
        """Optional[ArtLayer]: Reference used to detect collision with the PT box."""
        return get_reference_layer(
            f"{LAYERS.DEFENSE_REFERENCE} Flip"
            if self.is_flipside_creature
            else LAYERS.DEFENSE_REFERENCE,
            self.text_group,
        )

    """
    * Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Overwrite rules text to enforce vertical text nudge with defense shield collision."""

        # Call super instead if not a Battle type card
        if not self.is_layout_battle:
            return super().rules_text_and_pt_layers()

        if self.text_layer_rules:
            # Rules Text and Power / Toughness
            self.text.append(
                FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.oracle_text,
                    flavor=self.layout.flavor_text,
                    reference=self.textbox_reference,
                    divider=self.divider_layer,
                    pt_reference=self.defense_reference,
                    centered=self.is_centered,
                )
            )

    """
    * Battle Methods
    """

    def text_layers_battle(self) -> None:
        """Add and modify text layers required by Battle cards."""

        if isinstance(self.layout, BattleLayout) and self.text_layer_defense:
            # Add defense text
            self.text.append(
                TextField(layer=self.text_layer_defense, contents=self.layout.defense)
            )

        # Add flipside Power/Toughness
        if self.is_flipside_creature and self.text_layer_flipside_pt:
            self.text.append(
                TextField(
                    layer=self.text_layer_flipside_pt,
                    contents=str(self.layout.other_face_power)
                    + "/"
                    + str(self.layout.other_face_toughness),
                )
            )


"""
* Template Classes
"""


class BattleTemplate(BattleMod, VectorTemplate):
    """Battle template using vector shape layers and automatic pinlines / multicolor generation."""

    """
    * Bool Properties
    """

    @cached_property
    def is_legendary(self) -> bool:
        return False

    """
    * Groups
    """

    @cached_property
    def background_group(self) -> LayerSet | None:
        return

    """
    * Colors
    """

    @cached_property
    def pinlines_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Must be returned as SolidColor or gradient notation."""
        return psd.get_pinline_gradient(
            self.identity
            if 1 < len(self.identity) < self.color_limit
            else self.pinlines,
            color_map=self.pinlines_color_map,
            location_map={2: [0.4543, 0.5886]},
        )

    """
    * Shape Layers
    """

    @cached_property
    def textbox_shape(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.NORMAL, [self.textbox_group, LAYERS.SHAPE])

    @cached_property
    def enabled_shapes(self) -> list[ArtLayer | LayerSet | None]:
        return [self.textbox_shape]


class UniversesBeyondBattleTemplate(BattleTemplate):
    """Universes Beyond version of BattleTemplate."""

    """
    * Colors
    """

    @cached_property
    def pinlines_color_map(self) -> dict[str, ColorObject]:
        return {
            **pinlines_color_map,
            "W": (246, 247, 241),
            "U": (0, 131, 193),
            "B": (44, 40, 33),
            "R": (237, 66, 31),
            "G": (5, 129, 64),
            "Gold": (239, 209, 107),
            "Land": (165, 150, 132),
            "Artifact": (227, 228, 230),
            "Colorless": (227, 228, 230),
        }

    @cached_property
    def twins_colors(self) -> str:
        return f"{self.twins} Beyond"

    """
    * Groups
    """

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        """Textbox Beyond group."""
        return psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond")

    """
    * Shape Layers
    """

    @cached_property
    def textbox_shape(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.NORMAL, [self.textbox_group, LAYERS.SHAPE])
