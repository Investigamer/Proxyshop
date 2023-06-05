"""
* CLASS TEMPLATES
"""
# Standard Library Imports
from functools import cached_property

# Third Party Imports
from photoshop.api.application import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import CardLayout
import src.format_text as ft
import src.helpers as psd


class ClassTemplate (NormalTemplate):
    """
    * A template for Class cards introduced in Adventures in the Forgotten Realms.
    * Utilizes some of the same automated positioning techniques as Planeswalker templates.

    Adds:
        * Level stage groups which contain a cost and level text layer, as well as the divider bar.
        * Level line groups which contain the ability text for each level.
    """

    def __init__(self, layout: CardLayout):
        self._line_layers: list[ArtLayer] = []
        self._stage_layers: list[LayerSet] = []
        super().__init__(layout)

    """
    LAYERS
    """

    @cached_property
    def class_group(self) -> LayerSet:
        return psd.getLayerSet("Class", LAYERS.TEXT_AND_ICONS)

    @cached_property
    def stage_group(self) -> LayerSet:
        return psd.getLayerSet("Stage", self.class_group)

    @property
    def line_layers(self) -> list[ArtLayer]:
        return self._line_layers

    @line_layers.setter
    def line_layers(self, value):
        self._line_layers = value

    @property
    def stage_layers(self) -> list[LayerSet]:
        return self._stage_layers

    @stage_layers.setter
    def stage_layers(self, value):
        self._stage_layers = value

    """
    METHODS
    """

    def rules_text_and_pt_layers(self) -> None:

        # Add first static line
        level_1 = psd.getLayer(LAYERS.TEXT, self.class_group)
        self.line_layers.append(level_1)
        self.text.append(
            text_classes.FormattedTextField(
                layer=level_1,
                contents=self.layout.class_lines[0]['text']
            )
        )

        # Add text fields for each line and class stage
        for i, line in enumerate(self.layout.class_lines[1:]):
            line_layer = level_1.duplicate()
            self.active_layer = self.stage_group
            stage = psd.duplicate_group(f"{self.stage_group.name} {i + 1}")
            self.line_layers.append(line_layer)
            self.stage_layers.append(stage)
            self.text.extend([
                text_classes.FormattedTextField(
                    layer=line_layer,
                    contents=line['text']
                ),
                text_classes.FormattedTextField(
                    layer=psd.getLayer("Cost", stage),
                    contents=f"{line['cost']}:"
                ),
                text_classes.TextField(
                    layer=psd.getLayer("Level", stage),
                    contents=f"Level {line['level']}"
                )
            ])
        self.stage_group.visible = False

    def post_text_layers(self) -> None:

        # Core vars
        spacing = self.app.scale_by_height(80)
        spaces = len(self.line_layers) - 1
        divider_height = psd.get_layer_dimensions(self.stage_layers[0])['height']
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
        total_height = ref_height - spacing_total

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.line_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.line_layers])
        gap = (ref_height - layer_heights) * (spacing / spacing_total)
        inside_gap = (ref_height - layer_heights) * ((spacing + divider_height) / spacing_total)

        # Space Class lines evenly apart
        psd.spread_layers_over_reference(self.line_layers, self.textbox_reference, gap, inside_gap)

        # Position divider lines
        self.position_divider_lines()

    def position_divider_lines(self):

        # Position a line between each ability layer
        for i in range(len(self.line_layers) - 1):
            psd.position_between_layers(self.stage_layers[i], self.line_layers[i], self.line_layers[i + 1])
