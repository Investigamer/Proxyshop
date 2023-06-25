"""
* SAGA TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api.application import ArtLayer

# Local Imports
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.enums.layers import LAYERS
from src.layouts import CardLayout
import src.format_text as ft
import src.helpers as psd


class SagaTemplate (NormalTemplate):
    """
    * A template for Saga cards introduced in Dominaria.
    * Utilizes some of the same automated positioning techniques as Planeswalker templates.

    Adds:
        * Ability icons, layers, and dividers.
        * A reminder text layer at the top which describes how the Saga functions.
        * Also has some layer support for double faced sagas.
    """

    def __init__(self, layout: CardLayout):
        self._abilities: list[ArtLayer] = []
        self._icons: list[list[ArtLayer]] = []
        super().__init__(layout)

    """
    LAYER PROPERTIES
    """

    @cached_property
    def pinlines_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.background, LAYERS.TEXTBOX)

    @property
    def ability_layers(self) -> list[ArtLayer]:
        return self._abilities

    @ability_layers.setter
    def ability_layers(self, value):
        self._abilities = value

    @property
    def icon_layers(self) -> list[list[ArtLayer]]:
        return self._icons

    @icon_layers.setter
    def icon_layers(self, value):
        self._icons = value

    @cached_property
    def saga_group(self):
        return psd.getLayerSet("Saga", self.text_group)

    @cached_property
    def ability_divider(self) -> ArtLayer:
        return psd.getLayer(LAYERS.DIVIDER, self.saga_group)

    """
    TRANSFORM PROPERTIES
    """

    @cached_property
    def transform_icon_layer(self) -> Optional[ArtLayer]:
        return psd.getLayer(self.layout.transform_icon, [self.text_group, 'tf-front'])

    """
    METHODS
    """

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Saga stripe
        psd.getLayer(self.pinlines, LAYERS.PINLINES_AND_SAGA_STRIPE).visible = True

        # Is this transform?
        if self.layout.other_face:
            # Icon
            psd.getLayerSet('Circle', self.text_group).visible = True
            self.transform_icon_layer.visible = True

            # Nameplate
            psd.enable_mask(self.twins_layer.parent)
            psd.getLayer(self.background, 'TF Twins').visible = True

    def rules_text_and_pt_layers(self):

        # Add description text with reminder
        self.text.append(
            text_classes.FormattedTextArea(
                layer=psd.getLayer("Reminder Text", self.saga_group),
                contents=self.layout.saga_description,
                reference=psd.getLayer("Description Reference", self.text_group)
            )
        )

        # Iterate through each saga stage and add line to text layers
        for line in self.layout.saga_lines:
            layer = psd.getLayer(LAYERS.TEXT, self.saga_group).duplicate()
            self.ability_layers.append(layer)
            self.icon_layers.append([psd.getLayer(n, self.saga_group).duplicate() for n in line['icons']])
            self.text.append(
                text_classes.FormattedTextField(
                    layer = layer,
                    contents = line['text']
                )
            )

    def post_text_layers(self) -> None:

        # Core vars
        spacing = self.app.scale_by_height(80)
        spaces = len(self.ability_layers) - 1
        spacing_total = (spaces * 1.5) + 2
        ref_height = psd.get_layer_dimensions(self.textbox_reference)['height']
        total_height = ref_height - (((spacing * 1.5) * spaces) + (spacing * 2))

        # Resize text items till they fit in the available space
        ft.scale_text_layers_to_fit(self.ability_layers, total_height)

        # Get the exact gap between each layer left over
        layer_heights = sum([psd.get_text_layer_dimensions(lyr)["height"] for lyr in self.ability_layers])
        gap = (ref_height - layer_heights) * (1 / spacing_total)
        inside_gap = (ref_height - layer_heights) * (1.5 / spacing_total)

        # Space Saga lines evenly apart
        psd.spread_layers_over_reference(self.ability_layers, self.textbox_reference, gap, inside_gap)

        # Align icons to respective text layers
        for i, ref_layer in enumerate(self.ability_layers):
            # Skip if this is a passive ability
            icons = self.icon_layers[i]
            if len(icons) > 1:
                psd.space_layers_apart(icons, spacing/3)
                icon_layer = psd.merge_layers(icons)
            else:
                icon_layer = icons[0]
            self.docref.selection.select([
                [0, ref_layer.bounds[1]],
                [ref_layer.bounds[0], ref_layer.bounds[1]],
                [ref_layer.bounds[0], ref_layer.bounds[3]],
                [0, ref_layer.bounds[3]]
            ])
            psd.align_vertical(icon_layer)
            self.docref.selection.deselect()

        # Position divider lines
        self.position_divider_lines()

    def position_divider_lines(self):

        # Position a line between each ability layer
        for i in range(len(self.ability_layers) - 1):
            divider = self.ability_divider.duplicate()
            psd.position_between_layers(divider, self.ability_layers[i], self.ability_layers[i + 1])
