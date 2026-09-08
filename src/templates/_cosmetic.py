"""
* Cosmetic Template Class Modifiers
"""

from collections.abc import Callable
from functools import cached_property

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
from src.enums.layers import LAYERS
from src.helpers.layers import select_layer
from src.templates._core import BaseTemplate
from src.templates._vector import VectorTemplate
from src.text_layers import ScaledWidthTextField
from src.utils.adobe import ReferenceLayer

"""
* Mods that change 'Art Frame' behavior
"""


class ExtendedMod(BaseTemplate):
    """
    Modifier for Extended templates.

    Modifies:
        - 'is_content_aware_enabled': Enabled
    """

    frame_suffix = "Extended"

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        return True


class FullartMod(BaseTemplate):
    """
    Modifier for Fullart templates.

    Modifies:
        - 'is_fullart': Enabled
    """

    frame_suffix = "Fullart"

    @cached_property
    def is_fullart(self) -> bool:
        return True


class BorderlessMod(BaseTemplate):
    """
    Modifier for Borderless templates.

    Modifies:
        - 'is_fullart': Enabled
        - 'is_content_aware_enabled': Enabled
        - 'background_layer': None
    """

    frame_suffix = "Borderless"

    @cached_property
    def is_fullart(self) -> bool:
        return True

    @cached_property
    def is_content_aware_enabled(self) -> bool:
        return True

    """
    * Layers
    """

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        """Borderless cards have no 'Background' layer."""
        return


class VectorBorderlessMod(BorderlessMod):
    """
    Modifier for vectorized Borderless templates.

    Inherits:
        - 'BorderlessMod'
    Modifies:
        - 'background_group': None
    """

    """
    * Groups
    """

    @cached_property
    def background_group(self) -> LayerSet | None:
        """Borderless cards have no 'Background' group."""
        return


"""
* Mods that add additional frame elements
"""


class NyxMod(BaseTemplate):
    """
    Modifier for 'Nyxtouched' supported templates.

    Modifies:
        - 'is_hollow_crown': Enabled for Nyxtouched cards
        - 'background_layer': Use 'Nyx' layer for Nyxtouched cards
    """

    """
    * Bool
    """

    @cached_property
    def is_hollow_crown(self) -> bool:
        """Enable hollow crown for Nyx cards."""
        if self.is_nyx:
            return True
        return super().is_hollow_crown

    """
    * Layers
    """

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        """Try finding a Nyx background layer if the card is a 'Nyxtouched' frame."""
        if self.is_nyx and (layer := psd.getLayer(self.background, LAYERS.NYX)):
            return layer
        return super().background_layer


class VectorNyxMod(NyxMod, VectorTemplate):
    """
    Modifier for vectorized 'Nyxtouched' supported templates.

    Inherits:
        - 'NyxMod'

    Adds:
        - 'background_group': Use 'Nyx' group if card is Nyxtouched.
    """

    @cached_property
    def background_group(self) -> LayerSet | None:
        """Optional[LayerSet]: Try finding a Nyx background group if the card is a 'Nyxtouched' frame."""
        if self.is_nyx and (layer := psd.getLayerSet(LAYERS.NYX)):
            return layer
        return super().background_group


class CompanionMod(BaseTemplate):
    """
    Modifier for 'Companion' supported templates.

    Modifies:
        - 'is_hollow_crown': Enabled for Companion cards

    Adds:
        - 'companion_layer': Defines the Companion texture layer if card is Companion
        - 'enable_companion_layers': Called when card is a Companion
    """

    @cached_property
    def frame_layer_methods(self) -> list[Callable[[], None]]:
        """Add companion layers step."""
        funcs = [self.enable_companion_layers] if self.is_companion else []
        return [*super().frame_layer_methods, *funcs]

    """
    * Bool
    """

    @cached_property
    def is_hollow_crown(self) -> bool:
        """Enable hollow crown for Companion cards."""
        if self.is_companion:
            return True
        return super().is_hollow_crown

    """
    * Layers
    """

    @cached_property
    def companion_layer(self) -> ArtLayer | None:
        """Companion inner crown layer."""
        return psd.getLayer(self.pinlines, LAYERS.COMPANION)

    """
    * Companion Methods
    """

    def enable_companion_layers(self) -> None:
        """Enable Hollow Crown companion texture."""
        if self.is_legendary and self.companion_layer:
            self.companion_layer.visible = True


class VectorCompanionMod(CompanionMod, VectorTemplate):
    """
    Modifier for vectorized 'Companion' supported templates.

    Inherits:
        - 'CompanionMod'

    Adds:
        - 'companion_group': Defines the group containing Companion textures if card is Companion

    Modifies:
        - 'enable_companion_layers': Uses 'create_blended_layer' to blend companion textures.
    """

    @cached_property
    def companion_group(self) -> LayerSet | None:
        """Group containing Companion inner crown textures."""
        return psd.getLayerSet(LAYERS.COMPANION)

    """
    * Companion Methods
    """

    def enable_companion_layers(self) -> None:
        """Generate blended hollow crown Companion texture."""
        if self.is_legendary and self.companion_group:
            self.create_blended_layer(
                group=self.companion_group,
                colors=self.crown_colors
                if isinstance(self.crown_colors, str)
                else [color for color in self.crown_colors if isinstance(color, str)]
                if isinstance(self.crown_colors, list)
                else "",
                masks=self.crown_masks,
            )


"""
* Other Cosmetic Changes
"""


class NicknameMod(BaseTemplate):
    """Modifier for adding Nickname support to a template.

    Adds:
        - `is_nickname`: Boolean property which toggles Nickname behavior.
        - 'nickname_group': Defines the group containing Nickname frame elements.
        - `text_layer_nickname`: Defines the text layer the original card name gets moved to, so
            Nickname text may be added to the Card Name layer.
        - `nickname_shape`: Defines the shape layer used for the Nickname plat backing, also used
            as a reference layer to position the original name.

    Modifies:
        - Hooks the `basic_text_layers` method to swap the Card Name text with the Nickname text, and
            allows the user to manually enter the Nickname text before text formatting occurs, if
            nickname text wasn't provided automatically.
    """

    @cached_property
    def post_text_methods(self) -> list[Callable[[], None]]:
        """Add nickname text layers."""
        funcs = super().post_text_methods
        if self.is_nickname:
            funcs.append(self.format_nickname_text)
        return funcs

    """
    * Flags
    """

    @cached_property
    def is_nickname(self) -> bool:
        """Toggles nickname behavior. Can be overwritten to implement conditional logic."""
        return self.config.nickname_allow and (
            bool(self.layout.nickname) or self.config.nickname_prompt
        )

    """
    * Text Layers
    """

    @cached_property
    def text_layer_nickname(self) -> ArtLayer | None:
        """Alternate text layer to use for original card name when a nickname is used."""
        if layer := psd.getLayer(LAYERS.NICKNAME, self.text_group):
            layer.visible = True
            return layer

    """
    * Layer Groups
    """

    @cached_property
    def nickname_group(self) -> LayerSet | None:
        """Nickname frame element group."""
        return psd.getLayerSet(LAYERS.NICKNAME)

    """
    * Shape Layers
    """

    @cached_property
    def nickname_shape(self) -> ReferenceLayer | None:
        """Shape layer behind the original card name on the nickname frame element. Also used
        to position the original card name as a reference."""
        _shape_group = psd.getLayerSet(LAYERS.SHAPE, self.nickname_group)

        # Check for a legendary-specific nickname shape
        if self.is_legendary and (
            _layer := psd.get_reference_layer(LAYERS.LEGENDARY, _shape_group)
        ):
            return _layer
        return psd.get_reference_layer(LAYERS.NORMAL, _shape_group)

    """
    * Overwrite Methods
    """

    def basic_text_layers(self) -> None:
        """Hook basic text layers to swap the normal Card Name with a provided Nickname."""
        if not self.is_nickname:
            return super().basic_text_layers()

        # Ask user to input the nickname if not provided
        self.prompt_nickname_text()

        if self.text_layer_nickname:
            # Add original name
            self.text.append(
                ScaledWidthTextField(
                    layer=self.text_layer_nickname,
                    contents=str(self.layout.name),
                    reference=self.nickname_shape,
                )
            )
        self.layout.name = self.layout.nickname
        return super().basic_text_layers()

    """
    * Nickname Methods
    """

    def format_nickname_text(self) -> None:
        # Center the card name on the nickname plate
        psd.align_all(self.text_layer_nickname, self.nickname_shape)

    """
    * Utility Methods
    """

    def prompt_nickname_text(self) -> None:
        """Check if nickname text is already defined. If not, prompt the user."""
        if not self.layout.nickname and self.text_layer_name:
            _textItem = self.text_layer_name.textItem
            _textItem.contents = "ENTER NICKNAME"
            select_layer(self.text_layer_name)
            self.pause("Enter nickname text.")
            self.layout.nickname = _textItem.contents


class NicknameVectorMod(NicknameMod, VectorTemplate):
    """Modifier for adding Nickname support to a vector template."""

    @cached_property
    def enabled_shapes(self) -> list[ArtLayer | LayerSet | None]:
        """Add Nickname shape if needed."""
        _shapes = super().enabled_shapes
        if self.is_nickname:
            _shapes.append(self.nickname_shape)
        return _shapes
