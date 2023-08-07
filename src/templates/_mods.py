"""
* VECTOR TEMPLATE
* Base classes and mixins
"""
# Standard Library
from functools import cached_property
from typing import Optional, Callable

# Third Party Imports
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.enums.layers import LAYERS
from src import helpers as psd
from src.enums.mtg import TransformIcons
from src.templates._core import BaseTemplate
from src.templates._vector import VectorTemplate
from src.text_layers import TextField, ScaledTextField, FormattedTextField


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
        if self.is_transform:
            return [*super().frame_layer_methods, self.enable_transform_layers]
        return super().frame_layer_methods

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        if self.is_transform:
            return [*super().text_layer_methods, self.text_layers_transform]
        return super().text_layer_methods

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # Does it have flipside PT cutout?
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


class VectorTransformMod(VectorTemplate):
    """Transform mod for vector templates."""

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        if self.is_transform:
            return [*super().frame_layer_methods, self.enable_transform_layers]
        return super().frame_layer_methods

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        if self.is_transform:
            return [*super().text_layer_methods, self.text_layers_transform]
        return super().text_layer_methods

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        # Does it have flipside PT cutout?
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

        # Enable transform circle and icon
        psd.getLayerSet(LAYERS.TRANSFORM, self.text_group).visible = True
        if self.transform_icon_layer:
            self.transform_icon_layer.visible = True

        # Enable front / back specific layers
        if self.is_front:
            return self.enable_transform_layers_front()
        return self.enable_transform_layers_back()

    def enable_transform_layers_front(self) -> None:
        """Enables layers that are required by front face transform cards."""

        # Enable transform front border mask
        psd.copy_layer_mask(psd.getLayer(LAYERS.TRANSFORM_FRONT, [self.mask_group, LAYERS.BORDER]), self.border_shape)

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

        # Rear face non-Eldrazi cards: White rules, typeline, and PT text with FX enabled
        if self.layout.transform_icon != TransformIcons.MOONELDRAZI:
            psd.enable_layer_fx(self.text_layer_name)
            psd.enable_layer_fx(self.text_layer_type)
            self.text_layer_name.textItem.color = psd.rgb_white()
            self.text_layer_type.textItem.color = psd.rgb_white()
            if self.is_creature:
                psd.enable_layer_fx(self.text_layer_pt)
                self.text_layer_pt.textItem.color = psd.rgb_white()


class MDFCMod(BaseTemplate):
    """
    * Modifier for MDFC templates.

    Adds:
        * MDFC Left text layer (opposing side type)
        * MDFC Right text layer (opposing side cost or land tap ability)
        * Top (arrow icon) and bottom (opposing side info) MDFC layer elements
    """

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        if self.is_mdfc:
            return [*super().frame_layer_methods, self.enable_mdfc_layers]
        return super().frame_layer_methods

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        if self.is_mdfc:
            return [*super().text_layer_methods, self.text_layers_mdfc]
        return super().text_layer_methods

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        """The back face card type."""
        return psd.getLayer(LAYERS.LEFT, self.dfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        """The back face mana cost or land tap ability."""
        return psd.getLayer(LAYERS.RIGHT, self.dfc_group)

    """
    METHODS
    """

    def text_layers_mdfc(self) -> None:
        """Adds and modifies text layers required by modal double faced cards."""

        # Add mdfc text layers
        self.text.extend([
            FormattedTextField(
                layer = self.text_layer_mdfc_right,
                contents = self.layout.other_face_right
            ),
            ScaledTextField(
                layer = self.text_layer_mdfc_left,
                contents = self.layout.other_face_left,
                reference = self.text_layer_mdfc_right,
            )
        ])

        # Front and back side layers
        if self.is_front:
            self.text_layers_mdfc_front()
        else:
            self.text_layers_mdfc_back()

    def text_layers_mdfc_front(self) -> None:
        """Add or modify front side MDFC tex layers."""
        pass

    def text_layers_mdfc_back(self) -> None:
        """Add or modify back side MDFC text layers."""
        pass

    def enable_mdfc_layers(self) -> None:
        """Enable layers that are required by modal double faced cards."""

        # MDFC elements at the top and bottom of the card
        psd.getLayer(
            self.twins,
            psd.getLayerSet(LAYERS.TOP, self.dfc_group)
        ).visible = True
        psd.getLayer(
            self.layout.other_face_twins,
            psd.getLayerSet(LAYERS.BOTTOM, self.dfc_group)
        ).visible = True

        # Front and back side layers
        if self.is_front:
            self.enable_mdfc_layers_front()
        else:
            self.enable_mdfc_layers_back()

    def enable_mdfc_layers_front(self) -> None:
        """Enable front side MDFC layers."""
        pass

    def enable_mdfc_layers_back(self) -> None:
        """Enable back side MDFC layers."""
        pass


class VectorMDFCMod(VectorTemplate):
    """MDFC mod for vector templates."""

    @cached_property
    def frame_layer_methods(self) -> list[Callable]:
        if self.is_mdfc:
            return [*super().frame_layer_methods, self.enable_mdfc_layers]
        return super().frame_layer_methods

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        if self.is_mdfc:
            return [*super().text_layer_methods, self.text_layers_mdfc]
        return super().text_layer_methods

    """
    TEXT LAYERS
    """

    @cached_property
    def text_layer_mdfc_left(self) -> Optional[ArtLayer]:
        """The back face card type."""
        return psd.getLayer(LAYERS.LEFT, self.dfc_group)

    @cached_property
    def text_layer_mdfc_right(self) -> Optional[ArtLayer]:
        """The back face mana cost or land tap ability."""
        return psd.getLayer(LAYERS.RIGHT, self.dfc_group)

    """
    METHODS
    """

    def text_layers_mdfc(self) -> None:
        """Adds and modifies text layers required by modal double faced cards."""

        # Add mdfc text layers
        self.text.extend([
            FormattedTextField(
                layer = self.text_layer_mdfc_right,
                contents = self.layout.other_face_right
            ),
            ScaledTextField(
                layer = self.text_layer_mdfc_left,
                contents = self.layout.other_face_left,
                reference = self.text_layer_mdfc_right,
            )
        ])

        # Front and back side layers
        if self.is_front:
            self.text_layers_mdfc_front()
        else:
            self.text_layers_mdfc_back()

    def text_layers_mdfc_front(self) -> None:
        """Add or modify front side MDFC tex layers."""
        pass

    def text_layers_mdfc_back(self) -> None:
        """Add or modify back side MDFC text layers."""
        pass

    def enable_mdfc_layers(self) -> None:
        """Enable layers that are required by modal double faced cards."""

        # MDFC elements at the top and bottom of the card
        psd.getLayer(
            self.twins,
            psd.getLayerSet(LAYERS.TOP, self.dfc_group)
        ).visible = True
        psd.getLayer(
            self.layout.other_face_twins,
            psd.getLayerSet(LAYERS.BOTTOM, self.dfc_group)
        ).visible = True

        # Front and back side layers
        if self.is_front:
            self.enable_mdfc_layers_front()
        else:
            self.enable_mdfc_layers_back()

    def enable_mdfc_layers_front(self) -> None:
        """Enable front side MDFC layers."""
        pass

    def enable_mdfc_layers_back(self) -> None:
        """Enable back side MDFC layers."""
        pass
