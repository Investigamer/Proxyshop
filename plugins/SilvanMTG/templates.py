"""
SILVAN'S TEMPLATES
"""
from typing import Optional

from photoshop.api._artlayer import ArtLayer

import src.templates as temp
from src.constants import con
import src.helpers as psd
import photoshop.api as ps
app = ps.Application()


class SilvanExtendedTemplate (temp.NormalTemplate):
    """
    Silvan's legendary extended template used for WillieTanner proxies
    """
    template_file_name = "extended"
    template_suffix = "Extended"

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        # Background
        if self.is_nyx:
            return psd.getLayer(self.background, con.layers.NYX)
        if self.background == "Colorless":
            return
        return psd.getLayer(self.background, con.layers.BACKGROUND)

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


class SilvanMDFCBackTemplate (temp.MDFCBackTemplate):
    """
    Silvan extended template modified for MDFC
    """
    template_file_name = "extended-mdfc-back"
    dfc_layer_group = con.layers.MDFC_BACK
    template_suffix = "Extended"

    def load_artwork(self):
        super().load_artwork()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)


class SilvanMDFCFrontTemplate (SilvanMDFCBackTemplate):
    """
    Silvan extended template modified for MDFC
    """
    template_file_name = "extended-mdfc-front"
    dfc_layer_group = con.layers.MDFC_FRONT
    template_suffix = "Extended"
