"""
* SilvanMTG Templates
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.enums.layers import LAYERS
import src.helpers as psd
from src.templates import MDFCMod, ExtendedMod, M15Template

"""
* Template Classes
"""


class SilvanExtendedTemplate (ExtendedMod, M15Template):
    """Silvan's legendary extended template used for WillieTanner proxies."""
    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> Optional[ArtLayer]:

        # Background
        if self.is_nyx:
            return psd.getLayer(self.background, LAYERS.NYX)
        if self.background == LAYERS.COLORLESS:
            return
        return psd.getLayer(self.background, LAYERS.BACKGROUND)

    def enable_crown(self) -> None:

        # Add background mask
        super().enable_crown()
        if self.background_layer:
            psd.enable_mask(self.background_layer.parent)


class SilvanMDFCTemplate (MDFCMod, ExtendedMod, M15Template):
    """Silvan extended template modified for MDFC cards."""

    def enable_crown(self) -> None:
        super().enable_crown()

        # Enable pinlines and background mask
        psd.enable_vector_mask(self.pinlines_layer.parent)
        psd.enable_vector_mask(self.background_layer.parent)
