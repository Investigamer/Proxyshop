"""
SILVAN'S TEMPLATES
"""
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

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Remove colorless background
        if self.layout.background == "Colorless":
            psd.getLayer(self.layout.background, con.layers['BACKGROUND']).visible = False

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
