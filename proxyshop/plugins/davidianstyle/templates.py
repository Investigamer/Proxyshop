"""
SILVAN'S TEMPLATES
"""
import proxyshop.templates as temp
from proxyshop.constants import con
from proxyshop.settings import cfg
import proxyshop.helpers as psd
import photoshop.api as ps
app = ps.Application()


class StainedGlassTemplate (temp.NormalTemplate):
    """
    Stained Glass template introduced in Dominaria United
    """
    template_file_name = "stainedglass.psd"
    template_suffix = "Stained Glass"

    def __init__(self, layout):
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
