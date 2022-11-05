"""
SILVAN'S TEMPLATES
"""
from typing import Optional

from photoshop.api._artlayer import ArtLayer

import proxyshop.templates as temp
from proxyshop.constants import con
from proxyshop.settings import cfg
import proxyshop.helpers as psd
import photoshop.api as ps
app = ps.Application()


class SilvanExtendedTemplate (temp.NormalTemplate):
    """
    Silvan's legendary extended template used for WillieTanner proxies
    """
    template_file_name = "SilvanMTG/extended"
    template_suffix = "Extended"

    def __init__(self, layout):
        cfg.remove_reminder = True
        super().__init__(layout)

    @property
    def background_layer(self) -> Optional[ArtLayer]:
        # Background
        if self.is_nyx:
            return psd.getLayer(self.background, con.layers['NYX'])
        if self.background == "Colorless":
            return
        return psd.getLayer(self.background, con.layers['BACKGROUND'])

    def load_artwork(self):
        super().load_artwork()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)


"""
MDFC TEMPLATES
"""


class SilvanMDFCBackTemplate (temp.MDFCBackTemplate):
    """
    Silvan extended template modified for MDFC
    """
    template_file_name = "SilvanMTG/extended-mdfc-back"
    dfc_layer_group = con.layers['MDFC_BACK']
    template_suffix = "Extended"

    def __init__(self, layout):
        cfg.remove_reminder = True
        super().__init__(layout)

    def load_artwork(self):
        super().load_artwork()

        # Content aware fill
        psd.content_fill_empty_area(self.art_layer)


class SilvanMDFCFrontTemplate (SilvanMDFCBackTemplate):
    """
    Silvan extended template modified for MDFC
    """
    template_file_name = "SilvanMTG/extended-mdfc-front"
    dfc_layer_group = con.layers['MDFC_FRONT']
    template_suffix = "Extended"
