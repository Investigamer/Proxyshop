"""
SILVAN'S TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.templates import ExtendedTemplate, MDFCTemplate
from src.enums.layers import LAYERS
import src.helpers as psd


class SilvanExtendedTemplate (ExtendedTemplate):
    """
    Silvan's legendary extended template used for WillieTanner proxies
    """
    template_suffix = "Extended"

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        # Background
        if self.is_nyx:
            return psd.getLayer(self.background, LAYERS.NYX)
        if self.background == "Colorless":
            return
        return psd.getLayer(self.background, LAYERS.BACKGROUND)

    def enable_crown(self) -> None:
        # Add background mask
        super().enable_crown()
        psd.enable_mask(self.background_layer.parent)

    def enable_hollow_crown(self, shadows: Optional[ArtLayer] = None) -> None:
        # Mask shadows overlaying hollow crown
        super().enable_hollow_crown()
        if shadows := psd.getLayer("Shadows Light", "Shadows"):
            psd.enable_mask(shadows)


"""
MDFC TEMPLATES
"""


class SilvanMDFCTemplate (MDFCTemplate):
    """
    Silvan extended template modified for MDFC
    """
    template_suffix = "Extended"

    @cached_property
    def is_content_aware_enabled(self):
        return True
