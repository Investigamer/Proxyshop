"""
SILVAN'S TEMPLATES
"""
import proxyshop.text_layers as txt_layers
# from proxyshop import format_text
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
    def template_file_name(self): return "SilvanMTG/extended"
    def template_suffix(self): return "Extended"

    def __init__(self, layout):
        # strip out reminder text for extended cards
        cfg.remove_reminder = True
        super().__init__(layout)

    def enable_frame_layers(self):

        # Easy reference
        docref = app.activeDocument

        # twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # pinlines
        pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        if self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # background
        background = psd.getLayerSet(con.layers['BACKGROUND'])
        if self.layout.is_nyx: background = psd.getLayerSet(con.layers['NYX'])
        psd.getLayer(self.layout.background, background).visible = True

        if self.is_legendary:
            # legendary crown
            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            psd.getLayer(self.layout.pinlines, crown).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True

            # Mask the top border sides
            docref.activeLayer = background
            psd.enable_active_layer_mask()

            # enable companion texture
            if self.is_companion: psd.getLayer(self.layout.pinlines, con.layers['COMPANION']).visible = True

            # Hollow crown
            if self.layout.is_nyx or self.is_companion:
                # Enable the hollow crown shadow and layer mask on crown, pinlines, and shadows
                super().enable_hollow_crown(crown, pinlines)
                docref.activeLayer = psd.getLayer("Shadows Light", "Shadows")
                psd.enable_active_layer_mask()

        # Content aware fill
        docref.activeLayer = self.art_layer
        psd.content_fill_empty_area()


"""
MDFC TEMPLATES
"""


class SilvanMDFCBackTemplate (temp.NormalTemplate):
    """
    Silvan extended template modified for MDFC
    """
    def template_file_name(self): return "SilvanMTG/extended-mdfc-back"
    def dfc_layer_group(self): return con.layers['MDFC_BACK']
    def template_suffix(self): return "Extended"

    def __init__(self, layout):
        super().__init__(layout)

        # Set visibility of top & bottom mdfc elements and set text of left & right text
        mdfc_group = psd.getLayerSet(self.dfc_layer_group(), con.layers['TEXT_AND_ICONS'])
        mdfc_group_top = psd.getLayerSet(con.layers['TOP'], mdfc_group)
        mdfc_group_bottom = psd.getLayerSet(con.layers['BOTTOM'], mdfc_group)
        psd.getLayer(self.layout.twins, mdfc_group_top).visible = True
        psd.getLayer(self.layout.other_face_twins, mdfc_group_bottom).visible = True
        left = psd.getLayer(con.layers['LEFT'], mdfc_group)
        right = psd.getLayer(con.layers['RIGHT'], mdfc_group)

        # Add text layers
        self.tx_layers.extend([
            txt_layers.BasicFormattedTextField(
                layer = right,
                text_contents = self.layout.other_face_right,
                text_color = psd.get_text_layer_color(right),
            ),
            txt_layers.ScaledTextField(
                layer = left,
                text_contents = self.layout.other_face_left,
                text_color = psd.get_text_layer_color(left),
                reference_layer = right,
            ),
        ])

    def enable_frame_layers(self):

        # twins and pt box
        psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # pinlines
        if self.is_land: pinlines = psd.getLayer(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayer(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # background
        if self.layout.is_nyx: background = psd.getLayerSet(con.layers['NYX'])
        else: background = psd.getLayerSet(con.layers['BACKGROUND'])
        psd.getLayer(self.layout.background, background).visible = True

        if self.is_legendary:
            # legendary crown
            crown = psd.getLayerSet(con.layers['LEGENDARY_CROWN'])
            psd.getLayer(self.layout.pinlines, crown).visible = True
            border = psd.getLayerSet(con.layers['BORDER'])
            psd.getLayer(con.layers['NORMAL_BORDER'], border).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], border).visible = True

            # Companion texture
            if self.is_companion: psd.getLayer(self.layout.pinlines, con.layers['COMPANION']).visible = True

            # Hollow crown
            if (self.is_legendary and self.layout.is_nyx) or self.is_companion:
                # Enable the hollow crown shadow and layer mask on crown, pinlines, and shadows
                super().enable_hollow_crown(crown, pinlines)

        # Content aware fill
        app.activeDocument.activeLayer = self.art_layer
        psd.content_fill_empty_area()


class SilvanMDFCFrontTemplate (SilvanMDFCBackTemplate):
    """
    Silvan extended template modified for MDFC
    """
    def template_file_name(self): return "SilvanMTG/extended-mdfc-front"
    def dfc_layer_group(self): return con.layers['MDFC_FRONT']
    def template_suffix(self): return "Extended"
