"""
SILVAN'S TEMPLATES
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from photoshop.api._artlayer import ArtLayer

# Local Imports
import src.templates as temp
import src.helpers as psd
from src.utils.enums_layers import LAYERS


class SilvanExtendedTemplate (temp.NormalTemplate):
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

    def load_artwork(self):
        super().load_artwork()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)

    def enable_crown(self) -> None:
        super().enable_crown()
        psd.enable_mask(self.background_layer.parent)

    def enable_hollow_crown(self, shadows: Optional[ArtLayer] = None) -> None:
        super().enable_hollow_crown()

        # Mask shadows overlaying hollow crown
        if shadows := psd.getLayer("Shadows Light", "Shadows"):
            psd.enable_mask(shadows)


"""
MDFC TEMPLATES
"""


class SilvanMDFCTemplate (temp.MDFCTemplate):
    """
    Silvan extended template modified for MDFC
    """
    template_suffix = "Extended"

    def load_artwork(self):
        super().load_artwork()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)
