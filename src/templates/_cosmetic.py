"""
* Cosmetic Template Class Modifiers
"""
# Standard Library Imports
from typing import Optional, Callable

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.layers import LAYERS
import src.helpers as psd
from src.templates._core import BaseTemplate
from src.templates._vector import VectorTemplate
from src.utils.properties import auto_prop_cached

"""
* Mods that change 'Art Frame' behavior
"""


class ExtendedMod (BaseTemplate):
    """
    Modifier for Extended templates.

    Modifies:
        - 'is_content_aware_enabled': Enabled
    """
    frame_suffix = 'Extended'
    is_content_aware_enabled = True


class FullartMod (BaseTemplate):
    """
    Modifier for Fullart templates.

    Modifies:
        - 'is_fullart': Enabled
    """
    frame_suffix = 'Fullart'
    is_fullart = True


class BorderlessMod (BaseTemplate):
    """
    Modifier for Borderless templates.

    Modifies:
        - 'is_fullart': Enabled
        - 'is_content_aware_enabled': Enabled
        - 'background_layer': None
    """
    frame_suffix = 'Borderless'
    is_fullart = True
    is_content_aware_enabled = True

    """
    * Layers
    """

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        """Borderless cards have no 'Background' layer."""
        return


class VectorBorderlessMod (BorderlessMod):
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

    @property
    def background_group(self) -> Optional[LayerSet]:
        """Borderless cards have no 'Background' group."""
        return


"""
* Mods that add additional frame elements
"""


class NyxMod (BaseTemplate):
    """
    Modifier for 'Nyxtouched' supported templates.

    Modifies:
        - 'is_hollow_crown': Enabled for Nyxtouched cards
        - 'background_layer': Use 'Nyx' layer for Nyxtouched cards
    """

    """
    * Bool
    """

    @auto_prop_cached
    def is_hollow_crown(self) -> bool:
        """Enable hollow crown for Nyx cards."""
        if self.is_nyx:
            return True
        return super().is_hollow_crown

    """
    * Layers
    """

    @auto_prop_cached
    def background_layer(self) -> Optional[ArtLayer]:
        """Try finding a Nyx background layer if the card is a 'Nyxtouched' frame."""
        if self.is_nyx:
            if layer := psd.getLayer(self.background, LAYERS.NYX):
                return layer
        return super().background_layer


class VectorNyxMod (NyxMod, VectorTemplate):
    """
    Modifier for vectorized 'Nyxtouched' supported templates.

    Inherits:
        - 'NyxMod'

    Adds:
        - 'background_group': Use 'Nyx' group if card is Nyxtouched.
    """

    @auto_prop_cached
    def background_group(self) -> Optional[LayerSet]:
        """Try finding a Nyx background group if the card is a 'Nyxtouched' frame."""
        if self.is_nyx:
            if layer := psd.getLayerSet(LAYERS.NYX):
                return layer
        return super().background_group


class CompanionMod (BaseTemplate):
    """
    Modifier for 'Companion' supported templates.

    Modifies:
        - 'is_hollow_crown': Enabled for Companion cards

    Adds:
        - 'companion_layer': Defines the Companion texture layer if card is Companion
        - 'enable_companion_layers': Called when card is a Companion
    """

    @auto_prop_cached
    def frame_layer_methods(self) -> list[Callable]:
        """Add companion layers step."""
        funcs = [self.enable_companion_layers] if self.is_companion else []
        return [*super().frame_layer_methods, *funcs]

    """
    * Bool
    """

    @auto_prop_cached
    def is_hollow_crown(self) -> bool:
        """Enable hollow crown for Companion cards."""
        if self.is_companion:
            return True
        return super().is_hollow_crown

    """
    * Layers
    """

    @auto_prop_cached
    def companion_layer(self) -> Optional[ArtLayer]:
        """Companion inner crown layer."""
        return psd.getLayer(self.pinlines, LAYERS.COMPANION)

    """
    * Companion Methods
    """

    def enable_companion_layers(self) -> None:
        """Enable Hollow Crown companion texture."""
        if self.is_legendary and self.companion_layer:
            self.companion_layer.visible = True


class VectorCompanionMod (CompanionMod, VectorTemplate):
    """
    Modifier for vectorized 'Companion' supported templates.

    Inherits:
        - 'CompanionMod'

    Adds:
        - 'companion_group': Defines the group containing Companion textures if card is Companion

    Modifies:
        - 'enable_companion_layers': Uses 'create_blended_layer' to blend companion textures.
    """

    @auto_prop_cached
    def companion_group(self) -> Optional[LayerSet]:
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
                colors=self.crown_colors,
                masks=self.crown_masks)
