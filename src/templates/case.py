from functools import cached_property
from typing import Callable

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

from src.enums.layers import LAYERS
from src.helpers.bounds import get_layer_height
from src.helpers.layers import getLayer, getLayerSet
from src.helpers.position import position_dividers, spread_layers_over_reference
from src.helpers.text import scale_text_layers_to_height
from src.layouts import CaseLayout
from src.templates._core import NormalTemplate
from src.text_layers import FormattedTextField


class CaseMod(NormalTemplate):
    """
    * A template modifier for Case cards introduced in Murders at Karlov Manor.

    Adds:
        * Evenly spaced ability sections and dividers.
    """

    def __init__(self, layout: CaseLayout, **kwargs: None):
        self.line_layers: list[ArtLayer] = []
        self.divider_layers: list[ArtLayer] = []
        super().__init__(layout, **kwargs)

    """
    * Checks
    """

    @cached_property
    def is_case_layout(self) -> bool:
        """bool: Checks if this card uses Case layout."""
        return isinstance(self.layout, CaseLayout)

    """
    * Mixin Methods
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Case text layers."""
        funcs = [self.text_layers_case] if self.is_case_layout else []
        return [*super().text_layer_methods, *funcs]

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        """Add Case frame layers."""
        funcs = [self.frame_layers_case] if self.is_case_layout else []
        return [*super().frame_layer_methods, *funcs]

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Position Case abilities and dividers."""
        funcs = [self.layer_positioning_case] if self.is_case_layout else []
        return [*super().post_text_methods, *funcs]

    """
    * Groups
    """

    @cached_property
    def case_group(self) -> LayerSet | None:
        return getLayerSet(LAYERS.CASE)

    """
    * Text Layers
    """

    @cached_property
    def text_layer_ability(self) -> ArtLayer | None:
        return getLayer(LAYERS.TEXT, self.case_group)

    @cached_property
    def case_ability_divider(self) -> ArtLayer | None:
        return getLayer(LAYERS.DIVIDER, self.case_group)

    """
    * Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        if self.is_case_layout and not self.is_creature:
            return
        return super().rules_text_and_pt_layers()

    """
    * Text Layer Methods
    """

    def text_layers_case(self) -> None:
        """Add and modify text layers relating to Case type cards."""

        skip_divider_for = len(self.layout.case_lines) - 1

        # Add text fields for each line
        for i, line in enumerate(self.layout.case_lines):
            # Create a new ability line
            if layer := self.text_layer_ability:
                line_layer: ArtLayer = layer if i == 0 else layer.duplicate()
                self.line_layers.append(line_layer)
                self.text.append(FormattedTextField(layer=line_layer, contents=line))

            # Use existing ability divider or create a new one
            if i != skip_divider_for and (layer := self.case_ability_divider):
                divider: ArtLayer = (
                    self.case_ability_divider
                    if i == 0
                    else self.case_ability_divider.duplicate()
                )
                self.divider_layers.append(divider)

    """
    * Frame Layer Methods
    """

    def frame_layers_case(self) -> None:
        """Enable frame layers required by Case cards. None by default."""
        pass

    """
    * Positioning Methods
    """

    def layer_positioning_case(self) -> None:
        """Positions and sizes Case ability layers and dividers."""

        # Core vars
        spacing = self.app.scale_by_dpi(80)
        spaces = len(self.line_layers)
        divider_height = (
            get_layer_height(self.divider_layers[0])
            if len(self.divider_layers) > 0
            else 0
        )
        ref_height: float | int = self.textbox_reference.dims["height"]
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        scale_text_layers_to_height(
            text_layers=self.line_layers, ref_height=total_height
        )

        # Get the exact gap between each layer left over
        layer_heights = sum([get_layer_height(lyr) for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * (
            (spacing + divider_height) / spacing_total
        )

        # Space lines evenly apart
        spread_layers_over_reference(
            layers=self.line_layers,
            ref=self.textbox_reference,
            gap=gap,
            inside_gap=inside_gap,
        )

        # Position a divider between each ability line
        if len(self.divider_layers) == len(self.line_layers) - 1:
            position_dividers(
                dividers=self.divider_layers,
                layers=self.line_layers,
                docref=self.docref,
            )
