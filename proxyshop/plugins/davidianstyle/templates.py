"""
DAVIDIANSTYLE'S TEMPLATES
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
        # Twins and p/t box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = False
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines
        if self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        pinlines.visible = True
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # Legendary crown
        if self.is_legendary:
            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            psd.getLayer(self.layout.pinlines, crown).visible = True

    def load_artwork(self):
        super().load_artwork()

    def collector_info(self):
        """
        Override default collector_info
        """
        # If creator is specified add the text
        if self.layout.creator:
            try: psd.getLayer("Creator", self.legal_layer).textItem.contents = self.layout.creator
            except Exception as e:
                console.update("Creator text layer not found, skipping that step.", e)

        # Layers we need
        pen_layer = psd.getLayer("Pen", self.legal_layer)
        set_layer = psd.getLayer("Set", self.legal_layer)
        artist_layer = psd.getLayer(con.layers['ARTIST'], self.legal_layer)

        # Fill set info / artist info
        pen_layer.visible = True
        set_layer.visible = True
        psd.replace_text(set_layer, "MTG", self.layout.set)
        artist_layer.visible = True
        psd.replace_text(artist_layer, "Artist", self.layout.artist)

        # Fill in language if needed
        if self.layout.lang != "en": psd.replace_text(set_layer, "EN", self.layout.lang.upper())
