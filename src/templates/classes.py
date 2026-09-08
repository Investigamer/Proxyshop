"""
* CLASS TEMPLATES
"""

from collections.abc import Callable, Sequence
from functools import cached_property

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
from src.enums.layers import LAYERS
from src.helpers.bounds import get_dimensions_from_bounds
from src.helpers.layers import get_reference_layer
from src.helpers.position import RefSide, check_bounds_overlap
from src.layouts import ClassLayout, NormalLayout
from src.schema.colors import ColorObject, GradientConfig, pinlines_color_map
from src.templates._core import NormalTemplate
from src.templates._cosmetic import VectorNyxMod
from src.templates._vector import MaskAction, VectorTemplate
from src.text_layers import FormattedTextField, TextField
from src.utils.adobe import ReferenceLayer

"""
* Modifier Classes
"""


class ClassMod(NormalTemplate):
    """
    * A template modifier for Class cards introduced in Adventures in the Forgotten Realms.
    * Utilizes similar automated positioning techniques as Planeswalker templates.

    Adds:
        * Level stage groups which contain a cost and level text layer, as well as the divider bar.
        * Level line groups which contain the ability text for each level.
        * A positioning step to evenly space the abilities and stage dividers.
    """

    def __init__(self, layout: NormalLayout):
        self._class_line_layers: list[ArtLayer] = []
        self._class_stage_layers: list[LayerSet] = []
        super().__init__(layout)

    """
    * Checks
    """

    @cached_property
    def is_class_layout(self) -> bool:
        """bool: Checks if this card is a ClassLayout object."""
        return isinstance(self.layout, ClassLayout)

    """
    * Mixin Methods
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable[[], None]]:
        """Add Class text layers."""
        funcs = [self.text_layers_classes] if self.is_class_layout else []
        return [*super().text_layer_methods, *funcs]

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        """Add Class text layers."""
        funcs = [self.frame_layers_classes] if self.is_class_layout else []
        return [*super().frame_layer_methods, *funcs]

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Position Class abilities and stage dividers."""
        funcs = [self.layer_positioning_classes] if self.is_class_layout else []
        return [*super().post_text_methods, *funcs]

    """
    * Class Groups
    """

    @cached_property
    def class_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.CLASS)

    @cached_property
    def stage_group(self) -> LayerSet | None:
        return psd.getLayerSet(LAYERS.STAGE, self.class_group)

    """
    * Class Text Layers
    """

    @cached_property
    def text_layer_ability(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.TEXT, self.class_group)

    @cached_property
    def class_text_layer_reminder(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.REMINDER_TEXT, self.class_group)

    """
    * Class Abilities
    """

    @property
    def class_line_layers(self) -> list[ArtLayer]:
        return self._class_line_layers

    @class_line_layers.setter
    def class_line_layers(self, value: list[ArtLayer]):
        self._class_line_layers = value

    """
    * Class Dividers
    """

    @cached_property
    def class_reminder_divider(self) -> ArtLayer | LayerSet | None:
        return psd.getLayer(LAYERS.DIVIDER, self.class_group)

    @property
    def class_stage_layers(self) -> list[LayerSet]:
        return self._class_stage_layers

    @class_stage_layers.setter
    def class_stage_layers(self, value: list[LayerSet]):
        self._class_stage_layers = value

    """
    * Text Layer Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Skip this step for Class cards."""
        if self.is_class_layout and not self.is_creature:
            return
        return super().rules_text_and_pt_layers()

    """
    * Class Text Layer Methods
    """

    def text_layers_classes(self) -> None:
        """Add and modify text layers relating to Class type cards."""
        if isinstance(self.layout, ClassLayout) and self.text_layer_ability:
            # Add reminder text
            if self.class_text_layer_reminder:
                self.text.append(
                    FormattedTextField(
                        layer=self.class_text_layer_reminder,
                        contents=self.layout.class_description,
                    )
                )

            # Add first static line
            self.class_line_layers.append(self.text_layer_ability)
            self.text.append(
                FormattedTextField(
                    layer=self.text_layer_ability,
                    contents=self.layout.class_lines[0]["text"],
                )
            )

            # Add text fields for each line and class stage
            for i, line in enumerate(self.layout.class_lines[1:]):
                # Create a new ability line
                line_layer = self.text_layer_ability.duplicate()
                self.class_line_layers.append(line_layer)

                self.text.append(
                    FormattedTextField(layer=line_layer, contents=line["text"])
                )

                if self.stage_group:
                    # Use existing stage divider or create new one
                    stage = self.stage_group if i == 0 else self.stage_group.duplicate()
                    cost, level = [*stage.artLayers][:2]
                    self.class_stage_layers.append(stage)

                    # Add text layers to be formatted
                    self.text.extend(
                        [
                            FormattedTextField(layer=cost, contents=f"{line['cost']}:"),
                            TextField(
                                layer=level,
                                contents=f"{line['level_translation']}{line['level']}",
                            ),
                        ]
                    )

    """
    * Class Frame Layer Methods
    """

    def frame_layers_classes(self) -> None:
        """Enable frame layers required by Class cards. None by default."""

    """
    * Class Positioning Methods
    """

    def layer_positioning_classes(self) -> None:
        """Positions and sizes class ability layers and stage dividers."""
        if self.textbox_reference:
            # Ensure that textbox reference bounds don't overlap with reminder
            reminder_end: float = 0
            if self.class_text_layer_reminder:
                reminder_dims = psd.get_layer_dimensions(self.class_text_layer_reminder)
                reminder_end = reminder_dims["bottom"]

                if self.class_reminder_divider:
                    divider_dims = psd.get_layer_dimensions(self.class_reminder_divider)
                    reminder_end += divider_dims["height"]

                # Offset ability text from reminder text if they could otherwise overlap
                textbox_ref_bounds = self.textbox_reference.bounds
                if check_bounds_overlap(
                    self.class_text_layer_reminder.bounds,
                    textbox_ref_bounds,
                    RefSide.ANY,
                ):
                    new_bounds = (
                        textbox_ref_bounds[0],
                        max(textbox_ref_bounds[1], reminder_end),
                        textbox_ref_bounds[2],
                        textbox_ref_bounds[3],
                    )
                    # Override the cached bounds with modified bounds.
                    # It is assumed that bounds without effects aren't needed,
                    # so they aren't overridden.
                    self.textbox_reference.bounds = new_bounds
                    self.textbox_reference.dims = get_dimensions_from_bounds(new_bounds)

            # Core vars
            spacing = self.app.scale_by_dpi(80)
            spaces = len(self.class_line_layers) - 1
            divider_height = psd.get_layer_height(self.class_stage_layers[0])
            ref_height = self.textbox_reference.dims["height"]
            spacing_total = (spaces * (spacing + divider_height)) + (spacing * 2)
            total_height = ref_height - spacing_total

            # Resize text items till they fit in the available space
            psd.scale_text_layers_to_height(
                text_layers=self.class_line_layers, ref_height=total_height
            )

            # Get the exact gap between each layer left over
            layer_heights = sum(
                [psd.get_layer_height(lyr) for lyr in self.class_line_layers]
            )
            gap = (ref_height - layer_heights) * (spacing / spacing_total)
            inside_gap = (ref_height - layer_heights) * (
                (spacing + divider_height) / spacing_total
            )

            # Space Class lines evenly apart
            psd.spread_layers_over_reference(
                layers=self.class_line_layers,
                ref=self.textbox_reference,
                gap=gap,
                inside_gap=inside_gap,
            )

            # Position a class stage between each ability line
            psd.position_dividers(
                dividers=self.class_stage_layers,
                layers=self.class_line_layers,
                docref=self.docref,
            )

            # Position reminder divider
            if self.class_reminder_divider:
                first_line_layer_dims = psd.get_layer_dimensions(
                    self.class_line_layers[0]
                )
                divider_dims = psd.get_layer_dimensions(self.class_reminder_divider)
                delta = (
                    (reminder_text_end := reminder_end - divider_dims["height"])
                    + (first_line_layer_dims["top"] - reminder_text_end) / 2
                    - divider_dims["center_y"]
                )
                self.class_reminder_divider.translate(0, delta)


"""
* Template Classes
"""


class ClassVectorTemplate(VectorNyxMod, ClassMod, VectorTemplate):
    """Class template using vector shape layers and automatic pinlines / multicolor generation."""

    """
    * Bool
    """

    @cached_property
    def is_name_shifted(self) -> bool:
        """Back face TF symbol is on right side."""
        return bool(self.is_transform and self.is_front)

    """
    * Colors
    """

    @cached_property
    def textbox_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """list[str]: Support back side texture names."""
        colors = list(self.identity) if self.is_within_color_limit else [self.pinlines]
        # Is this card a back face transform?
        if self.is_transform and not self.is_front:
            return [f"{n} {LAYERS.BACK}" for n in colors]
        return colors

    @cached_property
    def crown_colors(
        self,
    ) -> ColorObject | Sequence[ColorObject] | Sequence[GradientConfig]:
        """Return RGB notation or Gradient dict notation for adjustment layers."""
        return psd.get_pinline_gradient(
            colors=self.pinlines, color_map=self.crown_color_map
        )

    """
    * Groups
    """

    @cached_property
    def crown_group(self) -> LayerSet | None:
        """Use inner shape group for Legendary Crown."""
        return psd.getLayerSet(LAYERS.SHAPE, [self.docref, LAYERS.LEGENDARY_CROWN])

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        """Must enable textbox group."""
        if group := psd.getLayerSet(LAYERS.TEXTBOX, self.docref):
            group.visible = True
            return group

    """
    * Layers
    """

    @cached_property
    def twins_layer(self) -> ArtLayer | None:
        # Use Back face versions for back side Transform
        return psd.getLayer(
            f"{self.twins} {LAYERS.BACK}"
            if self.is_transform and not self.is_front
            else self.twins,
            self.twins_group,
        )

    """
    * References
    """

    @cached_property
    def art_reference(self) -> ReferenceLayer | None:
        return get_reference_layer(LAYERS.ART_FRAME + " Left")

    @cached_property
    def textbox_reference(self) -> ReferenceLayer | None:
        if self.is_front and self.is_flipside_creature:
            return psd.get_reference_layer(
                f"{LAYERS.TEXTBOX_REFERENCE} {LAYERS.TRANSFORM_FRONT}", self.class_group
            )
        return psd.get_reference_layer(LAYERS.TEXTBOX_REFERENCE, self.class_group)

    @cached_property
    def textbox_position_reference(self) -> ArtLayer | None:
        return psd.getLayer(LAYERS.ART_FRAME + " Right")

    """
    * Blending Masks
    """

    @cached_property
    def textbox_masks(self) -> list[ArtLayer]:
        """Blends the textbox colors."""
        if layer := psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.TEXTBOX]):
            return [layer]
        return []

    @cached_property
    def background_masks(self) -> list[ArtLayer]:
        """Blends the background colors."""
        if layer := psd.getLayer(LAYERS.HALF, [self.mask_group, LAYERS.BACKGROUND]):
            return [layer]
        return []

    """
    * Shapes
    """

    @cached_property
    def border_shape(self) -> ArtLayer | None:
        """Support a Normal and Legendary border for front-face Transform."""
        if self.is_transform and self.is_front:
            return psd.getLayer(
                f"{LAYERS.LEGENDARY if self.is_legendary else LAYERS.NORMAL} {LAYERS.TRANSFORM_FRONT}",
                self.border_group,
            )
        return super().border_shape

    @cached_property
    def pinlines_shapes(self) -> list[ArtLayer | LayerSet | None]:
        """Support front and back face Transform pinlines, and optional Legendary pinline shape."""
        shapes: list[ArtLayer | LayerSet | None] = []
        if self.is_legendary and (
            group := psd.getLayerSet(
                LAYERS.LEGENDARY, [self.pinlines_group, LAYERS.SHAPE]
            )
        ):
            shapes.append(group)
        if group := psd.getLayerSet(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform
            else LAYERS.NORMAL,
            [self.pinlines_group, LAYERS.SHAPE],
        ):
            shapes.append(group)
        return shapes

    @cached_property
    def twins_shape(self) -> ArtLayer | None:
        """Support both front and back face Transform shapes."""
        return psd.getLayer(
            (LAYERS.TRANSFORM_FRONT if self.is_front else LAYERS.TRANSFORM_BACK)
            if self.is_transform
            else LAYERS.NORMAL,
            [self.twins_group, LAYERS.SHAPE],
        )

    @cached_property
    def outline_shape(self) -> ArtLayer | None:
        """Outline for the textbox and art."""
        return psd.getLayer(
            LAYERS.TRANSFORM_FRONT
            if self.is_transform and self.is_front
            else LAYERS.NORMAL,
            LAYERS.OUTLINE,
        )

    @cached_property
    def enabled_shapes(self) -> list[ArtLayer | LayerSet | None]:
        """Add support for outline shape and multiple pinlines shapes."""
        return [
            *self.pinlines_shapes,
            self.outline_shape,
            self.border_shape,
            self.twins_shape,
        ]

    """
    * Masks to Enable
    """

    @cached_property
    def pinlines_mask(
        self,
    ) -> (
        MaskAction
        | tuple[ArtLayer | LayerSet, ArtLayer | LayerSet]
        | ArtLayer
        | LayerSet
        | None
    ):
        """Mask hiding pinlines effects inside textbox and art frame."""
        if (
            layer := psd.getLayer(
                LAYERS.TRANSFORM_FRONT
                if self.is_transform and self.is_front
                else LAYERS.NORMAL,
                [self.mask_group, LAYERS.PINLINES],
            )
        ) and self.pinlines_group:
            return (layer, self.pinlines_group)

    @cached_property
    def enabled_masks(
        self,
    ) -> list[
        MaskAction
        | tuple[ArtLayer | LayerSet, ArtLayer | LayerSet]
        | ArtLayer
        | LayerSet
        | None
    ]:
        """Support a pinlines mask."""
        return [self.pinlines_mask]

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self) -> None:
        super().enable_frame_layers()
        self.align_class_textbox()

    """
    * Class Frame Layer Methods
    """

    def frame_layers_classes(self):
        """Enable layers relating to Class type cards."""

        # Enable class group
        if self.class_group:
            self.class_group.visible = True

        # Disable Saga banner
        if layer := psd.getLayerSet("Banner Top"):
            layer.visible = False

    def align_class_textbox(self) -> None:
        # Merge the textbox and shift it to right half
        psd.merge_group(self.textbox_group)
        psd.align_horizontal(
            layer=self.active_layer, ref=self.textbox_position_reference
        )


class UniversesBeyondClassTemplate(ClassVectorTemplate):
    """Saga Vector template with Universes Beyond frame treatment."""

    template_suffix = "Universes Beyond"

    # Color Maps
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

    """
    * Colors
    """

    @cached_property
    def textbox_colors(self) -> list[str]:
        """list[str]: Support identity by color limit, fallback to pinline colors."""
        if self.is_within_color_limit:
            return [n for n in self.identity]
        return [self.pinlines]

    @cached_property
    def twins_colors(self) -> str:
        """str: Universes Beyond variant texture name."""
        return f"{self.twins} Beyond"

    """
    * Groups
    """

    @cached_property
    def background_group(self) -> LayerSet | None:
        """LayerSet: Universes Beyond variant group."""
        return psd.getLayerSet(f"{LAYERS.BACKGROUND} Beyond")

    @cached_property
    def textbox_group(self) -> LayerSet | None:
        """LayerSet: Universes Beyond variant group. Must be enabled."""
        if group := psd.getLayerSet(f"{LAYERS.TEXTBOX} Beyond"):
            group.visible = True
            return group
