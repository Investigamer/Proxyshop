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
    template_file_name = "davidianstyle/stainedglass"
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
        set_layer = psd.getLayer("Set", self.legal_layer)
        pen_layer = psd.getLayer("Pen", self.legal_layer)
        artist_layer = psd.getLayer(con.layers['ARTIST'], self.legal_layer)

        # Fill set info if Auto.Set.Symbol is set
        if cfg.auto_symbol:
            set_layer.visible = True
            psd.replace_text(set_layer, "MTG", self.layout.set)

        # Fill artist info
        pen_layer.visible = True
        artist_layer.visible = True
        psd.replace_text(artist_layer, "Artist", self.layout.artist)

        # Fill in language if needed
        if self.layout.lang != "en": psd.replace_text(set_layer, "EN", self.layout.lang.upper())

        # Generate the expansion symbol
        self.create_expansion_symbol()

    def get_file_name(self):
        """
        Format the output filename.
        """
        if not hasattr(self, 'template_suffix'): suffix = None
        elif callable(self.template_suffix): suffix = self.template_suffix()
        else: suffix = self.template_suffix

        filename = self.layout.name
        if cfg.save_artist_name and self.layout.artist:
            filename += f" ({self.layout.artist})"
        if suffix:
            filename += f" [{suffix}]"

        return filename