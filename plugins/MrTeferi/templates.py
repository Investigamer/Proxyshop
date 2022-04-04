"""
MRTEFERI TEMPLATES
"""
# pylint: disable=C0116, E0401
from proxyshop import format_text
#import proxyshop.text_layers as txt_layers
import proxyshop.templates as temp
import proxyshop.constants as con
import proxyshop.helpers as psd
app = psd.app
cfg = con.cfg
lyr = con.layers

"""
NORMAL TEMPLATES
"""
class SketchTemplate (temp.NormalTemplate):
    """
     * Sketch showcase from MH2
     * Original template by Nelynes
    """
    def template_file_name (self):
        return "MrTeferi/sketch"

    def template_suffix (self):
        return "Sketch"

    def enable_frame_layers (self):
        super().enable_frame_layers()
        if self.layout.rarity != "common": psd.getLayer("common", con.layers['TEXT_AND_ICONS']).visible = False
        """
        Interesting Sketch integration?

        app.activeDocument.activeLayer = app.activeDocument.layers.getByName("Layer 1")
        content_fill_empty_area()
        self.art_reference.visible = False
        doc_ref.layers.getByName(con.layersART_FRAME).visible=False
        //app.activeDocument.activeLayer.applyDiffuseGlow(0,2,13)
        app.activeDocument.activeLayer.applyUnSharpMask(100,5,50)
        app.activeDocument.activeLayer.autoContrast()
        app.activeDocument.activeLayer.autoLevels()
        app.activeDocument.activeLayer.adjustBrightnessContrast(0,10)
        VibrantSaturation(100,-30)
        # =======================================================
        idPly = charIDToTypeID( "Ply " )
        desc5002 = new ActionDescriptor()
        idnull = charIDToTypeID( "null" )
        ref1210 = new ActionReference()
        idActn = charIDToTypeID( "Actn" )
        ref1210.putName( idActn, "NewSketchify" )
        idASet = charIDToTypeID( "ASet" )
        ref1210.putName( idASet, "Scoots Actions" )
        desc5002.putReference( idnull, ref1210 )
        executeAction( idPly, desc5002, DialogModes.NO )
        """


class KaldheimTemplate (temp.NormalTemplate):
    """
     * Kaldheim viking legendary showcase.
     * Original Template by FeuerAmeise
    """
    def template_file_name (self):
        return "MrTeferi/kaldheim"

    def template_suffix (self):
        return "Kaldheim"

    def __init__ (self, layout, file):
        if not cfg.remove_reminder:
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        super().__init__(layout, file)

    def enable_frame_layers (self):

        # PT Box, no title boxes for this one
        if self.is_creature:
            # Check if vehicle
            if "Vehicle" in self.layout.type_line:
                psd.getLayer("Vehicle", con.layers['PT_BOX']).visible = True
            else: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True
        else: psd.getLayerSet(con.layers['PT_BOX']).visible = False

        # Land or not?
        if self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])

        # Check if vehicle
        if self.layout.type_line.find("Vehicle") >= 0: psd.getLayer("Vehicle", pinlines).visible = True
        else: psd.getLayer(self.layout.pinlines, pinlines).visible = True



class CrimsonFangTemplate (temp.NormalTemplate):
    """
     * The crimson vow showcase template.
     * Original template by michayggdrasil
     * Works for Normal and Transform cards
     * Transform is kinda experimental.
    """
    def template_file_name (self):
        return "MrTeferi/crimson-fang"

    def template_suffix (self):
        return "Fang"

    def enable_frame_layers (self):
        # Twins if tf card
        tf_twins = self.layout.twins+"-mdfc"

        # Transform stuff + twins
        if self.name_shifted:
            psd.getLayer("Button", con.layers['TEXT_AND_ICONS']).visible = True
            if self.layout.face == 0: psd.getLayer(con.layers['TF_FRONT'], con.layers['TEXT_AND_ICONS']).visible = True
            else: psd.getLayer(con.layers['TF_BACK'], con.layers['TEXT_AND_ICONS']).visible = True
            psd.getLayer(tf_twins, con.layers['TWINS']).visible = True
        else: psd.getLayer(self.layout.twins, con.layers['TWINS']).visible = True

        # PT Box
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # Pinlines
        if self.name_shifted and self.layout.face == 1:
            pinlines = psd.getLayerSet("MDFC "+con.layers['PINLINES_TEXTBOX'])
            if not self.layout.is_colorless: psd.getLayer(self.layout.pinlines, con.layers['COLOR_INDICATOR']).visible = True
        elif self.is_land: pinlines = psd.getLayerSet(con.layers['LAND_PINLINES_TEXTBOX'])
        else: pinlines = psd.getLayerSet(con.layers['PINLINES_TEXTBOX'])
        psd.getLayer(self.layout.pinlines, pinlines).visible = True

        # background
        psd.getLayer(self.layout.pinlines, con.layers['BACKGROUND']).visible = True

        if self.is_legendary:
            # legendary crown
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            border = psd.getLayerSet(con.layers['BORDER'])
            psd.getLayer(con.layers['NORMAL_BORDER'], border).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], border).visible = True


class PhyrexianTemplate (temp.NormalTemplate):
    """
     * From the Phyrexian secret lair promo
    """
    def template_file_name (self):
        return "MrTeferi/phyrexian"

    def template_suffix (self):
        return "Phyrexian"

    def enable_frame_layers (self):

        # PT Box, no title boxes for this one
        if self.is_creature:
            psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True
        else: psd.getLayerSet(con.layers['PT_BOX']).visible = False

        # Pinlines
        if self.is_land:
            # Land Group
            psd.getLayer(self.layout.pinlines, con.layers['LAND_PINLINES_TEXTBOX']).visible = True
        else:
            # Nonland
            psd.getLayer(self.layout.pinlines, con.layers['PINLINES_TEXTBOX']).visible = True


class DoubleFeatureTemplate (temp.NormalTemplate):
    """
     * Midnight Hunt / Vow Double Feature Showcase
     * Original assets from Warpdandy's Proximity Template
    """
    def template_file_name (self):
        return "MrTeferi/double-feature"

    def template_suffix (self):
        return "Double Feature"

    def enable_frame_layers (self):
        # Transform stuff
        """
        if self.name_shifted:
            docref.layers.getByName(con.layers['TEXT_AND_ICONS']).layers.getByName("Button").visible = True
            if self.layout.face == 0:
                docref.layers.getByName(con.layers['TEXT_AND_ICONS']).layers.getByName(con.layers['TF_FRONT']).visible = True
            else docref.layers.getByName(con.layers['TEXT_AND_ICONS']).layers.getByName(con.layers['TF_BACK']).visible = True
        """
        #PT Box
        if self.is_creature: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True

        # TF Card?
        try:
            if self.name_shifted and self.layout.face == 1:
                psd.getLayer(self.layout.pinlines, con.layerscolor_INDICATOR).visible = True
        except: pass

        # Background
        psd.getLayer(self.layout.pinlines, con.layers['BACKGROUND']).visible = True

        # Legendary crown
        if self.is_legendary:
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True


class MaleMPCTemplate (temp.NormalTemplate):
    """
     * MaleMPC's extended black box template.
    """
    def template_file_name (self):
        return "MrTeferi/male-mpc"

    def template_suffix (self):
        return "Extended Black"

    def __init__ (self, layout, file):
        if not cfg.remove_reminder:
            layout.oracle_text = format_text.strip_reminder_text(layout.oracle_text)
        super().__init__(layout, file)

"""
CLASSIC TEMPLATE VARIANTS
"""
class PromoClassicTemplate (temp.NormalClassicTemplate):
    """
     * Identical to NormalClassic
     * Promo star added
    """
    def template_suffix (self):
        return "Classic Promo"

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add the promo star
        psd.getLayer("Promo Star", con.layers['TEXT_AND_ICONS']).visible = True

class ColorshiftedTemplate (temp.NormalTemplate):
    """
     * Planar Chaos era colorshifted template
     * Rendered from CC and MSE assets
    """
    def template_file_name (self):
        return "MrTeferi/colorshifted"

    def template_suffix (self):
        return "Shifted"

    def __init__ (self, layout, file):
        # Classic footer
        layout.no_collector = True
        super().__init__(layout, file)

        # White brush and artist for black border
        if layout.pinlines[0:1] == "B" and len(layout.pinlines) < 3:
            psd.getLayer("Artist","Legal").textItem.color = psd.rgb_white()
            psd.getLayer("Brush B", "Legal").visible = False
            psd.getLayer("Brush W", "Legal").visible = True

    def enable_frame_layers (self):

        # PT Box, no title boxes for this one
        if self.is_creature:
            # Check if vehicle
            if self.layout.type_line.find("Vehicle") >= 0:
                psd.getLayer("Vehicle", con.layers['PT_BOX']).visible = True
            else: psd.getLayer(self.layout.twins, con.layers['PT_BOX']).visible = True
        else: psd.getLayerSet(con.layers['PT_BOX']).visible = False

        # Pinlines
        psd.getLayer(self.layout.pinlines, con.layers['PINLINES_TEXTBOX']).visible = True

        # Legendary crown
        if self.is_legendary:
            psd.getLayer(self.layout.pinlines, con.layers['LEGENDARY_CROWN']).visible = True
            psd.getLayer(con.layers['NORMAL_BORDER'], con.layers['BORDER']).visible = False
            psd.getLayer(con.layers['LEGENDARY_BORDER'], con.layers['BORDER']).visible = True

        # Alternate titleboxes
        if "Artifact" in self.layout.type_line and self.layout.pinlines != "Artifact":
            if self.is_legendary: psd.getLayer("Legendary Artifact", "Twins").visible = True
            else: psd.getLayer("Normal Artifact", "Twins").visible = True
        elif "Land" in self.layout.type_line:
            if self.is_legendary: psd.getLayer("Legendary Land", "Twins").visible = True
            else: psd.getLayer("Normal Land", "Twins").visible = True
