from functools import cached_property
from typing import Callable

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

from src.enums.layers import LAYERS
from src.helpers.bounds import (
    get_group_dimensions,
    get_layer_dimensions,
    get_layer_height,
)
from src.helpers.layers import duplicate_group, getLayer, getLayerSet, select_layer
from src.helpers.position import spread_layers_over_reference
from src.helpers.text import scale_text_layers_to_height
from src.layouts import StationLayout
from src.templates._core import NormalTemplate
from src.text_layers import FormattedTextField


class StationMod(NormalTemplate):
    """
    A template modifier for Station cards introduced in Edge of Eternities.

    Adds:
        * Station requirement, ability and P/T texts and shapes.
    """

    # region Checks

    @cached_property
    def is_station(self) -> bool:
        """Checks if this card uses Station layout"""
        return isinstance(self.layout, StationLayout)

    @cached_property
    def is_centered(self) -> bool:
        if self.is_station:
            return False
        return super().is_centered

    # endregion Checks

    # region Options

    @cached_property
    def rules_text_gap(self) -> int | float:
        return 64

    # endregion Options

    # region Groups

    @cached_property
    def station_group(self) -> LayerSet | None:
        return getLayerSet(LAYERS.STATION)

    @cached_property
    def station_level_base_group(self) -> LayerSet | None:
        return getLayerSet(LAYERS.LEVEL, self.station_group)

    @cached_property
    def station_level_groups(self) -> list[LayerSet]:
        groups: list[LayerSet] = []
        if self.station_level_base_group:
            if isinstance(self.layout, StationLayout):
                for i in range(len(self.layout.stations) - 1):
                    select_layer(self.station_level_base_group)
                    groups.append(
                        duplicate_group(f"{self.station_level_base_group.name} {i}")
                    )
            groups.append(self.station_level_base_group)
        return groups

    @cached_property
    def station_requirement_groups(self) -> list[LayerSet]:
        groups: list[LayerSet] = []
        for level_group in self.station_level_groups:
            if group := getLayerSet(LAYERS.REQUIREMENT, level_group):
                groups.append(group)
        return groups

    @cached_property
    def station_pt_groups(self) -> list[LayerSet]:
        groups: list[LayerSet] = []
        for level_group in self.station_level_groups:
            if group := getLayerSet(LAYERS.PT_BOX, level_group):
                groups.append(group)
        return groups

    # endregion Groups

    # region Text layers

    @cached_property
    def station_requirement_text_layers(self) -> list[ArtLayer]:
        layers: list[ArtLayer] = []
        for requirement_group in self.station_requirement_groups:
            if layer := getLayer(LAYERS.TEXT, requirement_group):
                layers.append(layer)
        return layers

    @cached_property
    def station_level_text_layers(self) -> list[ArtLayer]:
        layers: list[ArtLayer] = []
        if isinstance(self.layout, StationLayout):
            for details, level_group in zip(
                self.layout.stations, self.station_level_groups
            ):
                if layer := getLayer(
                    LAYERS.RULES_TEXT_CREATURE
                    if "pt" in details
                    else LAYERS.RULES_TEXT,
                    level_group,
                ):
                    layers.append(layer)
        return layers

    @cached_property
    def station_pt_text_layers(self) -> list[ArtLayer]:
        layers: list[ArtLayer] = []
        for pt_group in self.station_pt_groups:
            if layer := getLayer(LAYERS.TEXT, pt_group):
                layers.append(layer)
        return layers

    # endregion Text layers

    # region Mixin methods

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Station text layers."""
        funcs = super().text_layer_methods
        if self.is_station:
            funcs.append(self.text_layers_station)
        return funcs

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        """Add Station frame layers."""
        funcs = super().frame_layer_methods
        if self.is_station:
            funcs.append(self.frame_layers_station)
        return funcs

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Position Station abilities."""
        funcs = super().post_text_methods
        if self.is_station:
            funcs.append(self.layer_positioning_station)
        return funcs

    # endregion Mixin methods

    # region Text layer methods

    def text_layers_station(self) -> None:
        """Add and modify text layers relating to Station cards."""
        if isinstance(self.layout, StationLayout):
            for details, ability, requirement, pt in zip(
                self.layout.stations,
                self.station_level_text_layers,
                self.station_requirement_text_layers,
                self.station_pt_text_layers,
            ):
                self.text.append(
                    FormattedTextField(layer=ability, contents=details["ability"])
                )
                requirement.textItem.contents = details["requirement"]
                if "pt" in details:
                    pt.textItem.contents = (
                        f"{details['pt']['power']}/{details['pt']['toughness']}"
                    )

    # endregion Text layer methods

    # region Frame layer methods

    def frame_layers_station(self) -> None:
        """Enable frame layers required by Station cards."""
        if self.station_group:
            self.station_group.visible = True

        if isinstance(self.layout, StationLayout):
            for details, group in zip(self.layout.stations, self.station_pt_groups):
                if "pt" in details:
                    group.visible = True

    # endregion Frame layer methods

    # region Positioning methods

    def align_center_ys(self, group: LayerSet, ref: ArtLayer) -> None:
        dims = get_group_dimensions(group)
        dims_ref = get_layer_dimensions(ref)
        group.translate(0, dims_ref["center_y"] - dims["center_y"])

    def layer_positioning_station(self) -> None:
        """Positions and sizes Station ability layers."""
        if (
            isinstance(self.layout, StationLayout)
            and self.textbox_reference
            and self.text_layer_rules
        ):
            spacing = self.app.scale_by_dpi(self.rules_text_gap)
            spaces = len(self.layout.stations) + 1
            ref_height = self.textbox_reference.dims["height"]
            spacing_total = spaces * spacing + spacing
            total_height = ref_height - spacing_total

            ability_layers = [self.text_layer_rules, *self.station_level_text_layers]

            # Resize text items till they fit in the available space
            scale_text_layers_to_height(
                text_layers=ability_layers,
                ref_height=total_height,
            )

            # Get the exact gap between each layer left over
            layer_heights = sum([get_layer_height(lyr) for lyr in ability_layers])
            gap = (ref_height - layer_heights) * (spacing / spacing_total)
            inside_gap = (ref_height - layer_heights) * (spacing / spacing_total)

            # Space lines evenly apart
            spread_layers_over_reference(
                layers=ability_layers,
                ref=self.textbox_reference,
                gap=gap,
                inside_gap=inside_gap,
            )

            # Shift requirement and pt elements
            for details, level_text, requirement, pt in zip(
                self.layout.stations,
                self.station_level_text_layers,
                self.station_requirement_groups,
                self.station_pt_groups,
            ):
                self.align_center_ys(requirement, level_text)
                if "pt" in details:
                    self.align_center_ys(pt, level_text)

    # endregion Positioning methods
