"""
* LEVELER TEMPLATES
"""

from collections.abc import Callable
from functools import cached_property

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import LevelerLayout
from src.templates._core import NormalTemplate
from src.utils.adobe import ReferenceLayer

"""
* Modifier Classes
"""


class LevelerMod(NormalTemplate):
    """
    * Modifier for Level-Up cards introduced in Rise of the Eldrazi.

    Adds:
        * First, second, and third level ability text.
        * First, second, and third level power/toughness.
        * Level requirements for second and third stage.
    """

    """
    * Checks
    """

    @cached_property
    def is_leveler(self) -> bool:
        return isinstance(self.layout, LevelerLayout)

    """
    * Mixin Methods
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Adventure text layers."""
        funcs = [self.text_layers_leveler] if self.is_leveler else []
        return [*super().text_layer_methods, *funcs]

    """
    * Groups
    """

    @cached_property
    def leveler_group(self) -> LayerSet | None:
        """Group containing Leveler text layers."""
        return psd.getLayerSet("Leveler Text", self.text_group)

    """
    * Layers
    """

    @cached_property
    def pt_layer(self) -> ArtLayer | None:
        if self.is_leveler:
            return psd.getLayer(self.twins, LAYERS.PT_AND_LEVEL_BOXES)
        return super().pt_layer

    """
    * Text Layers
    """

    @cached_property
    def text_layer_rules(self) -> ArtLayer | None:
        if self.is_leveler:
            return psd.getLayer("Rules Text - Level Up", self.leveler_group)
        return super().text_layer_rules

    @cached_property
    def text_layer_pt(self) -> ArtLayer | None:
        if self.is_leveler:
            return psd.getLayer("Top Power / Toughness", self.leveler_group)
        return super().text_layer_pt

    """
    * Leveler Text Layers
    """

    @cached_property
    def text_layer_rules_x_y(self) -> ArtLayer | None:
        return psd.getLayer("Rules Text - Levels X-Y", self.leveler_group)

    @cached_property
    def text_layer_rules_z(self) -> ArtLayer | None:
        return psd.getLayer("Rules Text - Levels Z+", self.leveler_group)

    @cached_property
    def text_layer_level_middle(self) -> ArtLayer | None:
        return psd.getLayer("Middle Level", self.leveler_group)

    @cached_property
    def text_layer_level_bottom(self) -> ArtLayer | None:
        return psd.getLayer("Bottom Level", self.leveler_group)

    @cached_property
    def text_layer_pt_middle(self) -> ArtLayer | None:
        return psd.getLayer("Middle Power / Toughness", self.leveler_group)

    @cached_property
    def text_layer_pt_bottom(self) -> ArtLayer | None:
        return psd.getLayer("Bottom Power / Toughness", self.leveler_group)

    """
    * References
    """

    @cached_property
    def textbox_reference(self) -> ReferenceLayer | None:
        if self.is_leveler:
            return psd.get_reference_layer(
                f"{LAYERS.TEXTBOX_REFERENCE} - Level Text", self.leveler_group
            )
        return super().textbox_reference

    """
    * Leveler References
    """

    @cached_property
    def textbox_reference_x_y(self) -> ArtLayer | None:
        return psd.get_reference_layer(
            f"{LAYERS.TEXTBOX_REFERENCE} - Level X-Y", self.leveler_group
        )

    @cached_property
    def textbox_reference_z(self) -> ArtLayer | None:
        return psd.get_reference_layer(
            f"{LAYERS.TEXTBOX_REFERENCE} - Levels Z+", self.leveler_group
        )

    """
    * Leveler Text Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and power/toughness text."""

        if isinstance(self.layout, LevelerLayout):
            # Level-Up text and starting P/T
            if self.text_layer_rules:
                self.text.append(
                    text_classes.FormattedTextArea(
                        layer=self.text_layer_rules,
                        contents=self.layout.level_up_text,
                        reference=self.textbox_reference,
                    )
                )
            if self.text_layer_pt:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_pt,
                        contents=str(self.layout.power)
                        + "/"
                        + str(self.layout.toughness),
                    )
                )
        else:
            return super().rules_text_and_pt_layers()

    def text_layers_leveler(self):
        """Add and modify text layers required by Leveler cards."""
        if isinstance(self.layout, LevelerLayout):
            # Add Leveler sections

            # Level 2
            if self.text_layer_level_middle:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_level_middle,
                        contents=self.layout.middle_level,
                    )
                )
            if self.text_layer_pt_middle:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_pt_middle,
                        contents=self.layout.middle_power_toughness,
                    )
                )
            if self.text_layer_rules_x_y:
                self.text.append(
                    text_classes.FormattedTextArea(
                        layer=self.text_layer_rules_x_y,
                        contents=self.layout.middle_text,
                        reference=self.textbox_reference_x_y,
                    )
                )

            # Level 3
            if self.text_layer_level_bottom:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_level_bottom,
                        contents=self.layout.bottom_level,
                    )
                )
            if self.text_layer_pt_bottom:
                self.text.append(
                    text_classes.TextField(
                        layer=self.text_layer_pt_bottom,
                        contents=self.layout.bottom_power_toughness,
                    )
                )
            if self.text_layer_rules_z:
                self.text.append(
                    text_classes.FormattedTextArea(
                        layer=self.text_layer_rules_z,
                        contents=self.layout.bottom_text,
                        reference=self.textbox_reference_z,
                    )
                )


"""
* Template Classes
"""


class LevelerTemplate(LevelerMod, NormalTemplate):
    """Template for Level-Up cards introduced in Rise of the Eldrazi."""
