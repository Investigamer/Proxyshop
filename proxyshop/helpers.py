import os
import re
import proxyshop.constants as con
import proxyshop.settings as cfg
import photoshop.api as ps
app = ps.Application()

# Ensure scaling with pixels, font size with points
app.preferences.rulerUnits = ps.Units.Pixels
app.preferences.typeUnits = ps.Units.Points

"""
ALL FUNCTIONS HAVE ACCES TO PHOTOSHOP
"""
def getLayer(name, set=None):
    # Retrieve layer 
    if set == None:
        # No set given
        for layer in app.activeDocument.layers:
            if layer.name == name:
                return layer
    else:
        if type(set) == str:
            # Set name given
            layer_set = app.activeDocument.layerSets.getByName(set)
            for layer in layer_set.layers:
                if layer.name == name:
                    return layer
        else:
            # Set object given
            for layer in set.layers:
                if layer.name == name:
                    return layer
    return None

def getLayerSet(name, set=None):
    # Retrieve layer set
    if set:
        if type(set) == str:
            # Set name given
            layer_set = app.activeDocument.layerSets.getByName(set)
            return layer_set.layerSets.getByName(name)
        else: 
            # Set object given
            return set.layerSets.getByName(name)
    # Look through entire document
    else: return app.activeDocument.layerSets.getByName(name)

def rgb_black():
    """
     * Creates and returns a Solidcolor with RGB values for solid black.
    """
    color = ps.SolidColor()
    color.rgb.red = 0
    color.rgb.green = 0
    color.rgb.blue = 0
    return color

def rgb_white():
    """
     * Creates and returns a Solidcolor with RGB values for solid white.
    """
    color = ps.SolidColor()
    color.rgb.red = 255
    color.rgb.green = 255
    color.rgb.blue = 255
    return color

def compute_layer_dimensions(layer):
    # Return an object with the specified layer's width and height (computed from its bounds).
    return {
        'width': layer.bounds[2]-layer.bounds[0],
        'height': layer.bounds[3]-layer.bounds[1],
    }

def compute_text_layer_dimensions(layer):
    """
     * Return an object with the specified text layer's width and height, which is achieved by rasterising
     * the layer and computing its width and height from its bounds.
    """
    layer_copy = layer.Duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
    layer_copy.rasterize(ps.RasterizeType.TextContents)
    dimensions = compute_layer_dimensions(layer_copy)
    layer_copy.delete()
    return dimensions

def select_layer_pixels(layer):
    # Select the bounding box of a given layer.
    left = layer.bounds[0]
    top = layer.bounds[1]
    right = layer.bounds[2]
    bottom = layer.bounds[3]

    app.activeDocument.selection.select([
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom]
    ])

def clear_selection():
    #Clear the current selection.
    app.activeDocument.selection.select([])

def align(align_type):
    """
     * Align the currently active layer with respect to the current selection, either vertically or horizontally.
     * Intended to be used with align_vertical() or align_horizontal().
    """
    idAlgn = app.charIDToTypeID("Algn")
    desc = ps.ActionDescriptor()
    idnull = app.charIDToTypeID("null")
    ref = ps.ActionReference()
    idLyr = app.charIDToTypeID("Lyr ")
    idOrdn = app.charIDToTypeID("Ordn")
    idTrgt = app.charIDToTypeID("Trgt")
    ref.putEnumerated(idLyr, idOrdn, idTrgt)
    desc.putReference(idnull, ref)
    idUsng = app.charIDToTypeID("Usng")
    idADSt = app.charIDToTypeID("ADSt")
    idAdCH = app.charIDToTypeID(align_type)  # align type - "AdCV" for vertical, "AdCH" for horizontal
    desc.putEnumerated(idUsng, idADSt, idAdCH)
    app.executeAction(idAlgn, desc, ps.DialogModes.DisplayNoDialogs)

def align_vertical():
    # Align the currently active layer vertically with respect to the current selection.
    align("AdCV")

def align_horizontal():
    # Align the currently active layer horizontally with respect to the current selection.
    align("AdCH")

def frame_layer(layer, reference_layer):
    """
     * Scale a layer equally to the bounds of a reference layer, then centre the layer vertically and horizontally
     * within those bounds.
    """
    layer_dimensions = compute_layer_dimensions(layer)
    reference_dimensions = compute_layer_dimensions(reference_layer)

    # Determine how much to scale the layer by such that it fits into the reference layer's bounds
    scale_factor = 100 * max(reference_dimensions['width'] / layer_dimensions['width'], reference_dimensions['height'] / layer_dimensions['height'])
    layer.resize(scale_factor, scale_factor, ps.AnchorPosition.TopLeft)

    select_layer_pixels(reference_layer)
    app.activeDocument.activeLayer = layer
    align_horizontal()
    align_vertical()
    clear_selection()

def frame_expansion_symbol(layer, reference_layer, centered):
    """
     * Scale a layer equally to the bounds of a reference layer, then centre the layer vertically and horizontally
     * within those bounds.
    """
    layer_dimensions = compute_layer_dimensions(layer)
    reference_dimensions = compute_layer_dimensions(reference_layer)

    # Determine how much to scale the layer by such that it fits into the reference layer's bounds
    scale_factor = 100 * min(reference_dimensions['width'] / layer_dimensions['width'], reference_dimensions['height'] / layer_dimensions['height'])
    layer.resize(scale_factor, scale_factor, ps.AnchorPosition.MiddleRight)

    select_layer_pixels(reference_layer)
    app.activeDocument.activeLayer = layer

    if centered: align_horizontal()
    align_vertical()
    clear_selection()

def set_active_layer_mask(visible):
    # Set the visibility of the active layer's layer mask.
    idsetd = app.charIDToTypeID("setd")
    desc3078 = ps.ActionDescriptor()
    idnull = app.charIDToTypeID("null")
    ref1567 = ps.ActionReference()
    idLyr = app.charIDToTypeID("Lyr ")
    idOrdn = app.charIDToTypeID("Ordn")
    idTrgt = app.charIDToTypeID("Trgt")
    ref1567.putEnumerated(idLyr, idOrdn, idTrgt)
    desc3078.putReference(idnull, ref1567)
    idT = app.charIDToTypeID("T   ")
    desc3079 = ps.ActionDescriptor()
    idUsrM = app.charIDToTypeID("UsrM")
    desc3079.putBoolean(idUsrM, visible)
    idLyr = app.charIDToTypeID("Lyr ")
    desc3078.putObject(idT, idLyr, desc3079)
    app.executeAction(idsetd, desc3078, ps.DialogModes.DisplayNoDialogs)

def enable_active_layer_mask():
    # Enables the active layer's layer mask.
    set_active_layer_mask(True)

def disable_active_layer_mask():
    # Disables the active layer's layer mask.
    set_active_layer_mask(False)

def apply_stroke(stroke_weight, stroke_color):
    # Applies an outer stroke to the active layer with the specified weight and color.
    idsetd = app.charIDToTypeID("setd")
    desc608 = ps.ActionDescriptor()
    idnull = app.charIDToTypeID("null")
    ref149 = ps.ActionReference()
    idPrpr = app.charIDToTypeID("Prpr")
    idLefx = app.charIDToTypeID("Lefx")
    ref149.putProperty(idPrpr, idLefx)
    idLyr = app.charIDToTypeID("Lyr ")
    idOrdn = app.charIDToTypeID("Ordn")
    idTrgt = app.charIDToTypeID("Trgt")
    ref149.putEnumerated(idLyr, idOrdn, idTrgt)
    desc608.putReference(idnull, ref149)
    idT = app.charIDToTypeID("T   ")
    desc609 = ps.ActionDescriptor()
    idScl = app.charIDToTypeID("Scl ")
    idPrc = app.charIDToTypeID("#Prc")
    desc609.putUnitDouble(idScl, idPrc, 200.000000)
    idFrFX = app.charIDToTypeID("FrFX")
    desc610 = ps.ActionDescriptor()
    idenab = app.charIDToTypeID("enab")
    desc610.putBoolean(idenab, True)
    idStyl = app.charIDToTypeID("Styl")
    idFStl = app.charIDToTypeID("FStl")
    idInsF = app.charIDToTypeID("OutF")
    desc610.putEnumerated(idStyl, idFStl, idInsF)
    idPntT = app.charIDToTypeID("PntT")
    idFrFl = app.charIDToTypeID("FrFl")
    idSClr = app.charIDToTypeID("SClr")
    desc610.putEnumerated(idPntT, idFrFl, idSClr)
    idMd = app.charIDToTypeID("Md  ")
    idBlnM = app.charIDToTypeID("BlnM")
    idNrml = app.charIDToTypeID("Nrml")
    desc610.putEnumerated(idMd, idBlnM, idNrml)
    idOpct = app.charIDToTypeID("Opct")
    idPrc = app.charIDToTypeID("#Prc")
    desc610.putUnitDouble(idOpct, idPrc, 100.000000)
    idSz = app.charIDToTypeID("Sz  ")
    idPxl = app.charIDToTypeID("#Pxl")
    desc610.putUnitDouble(idSz, idPxl, int(stroke_weight))
    idClr = app.charIDToTypeID("Clr ")
    desc611 = ps.ActionDescriptor()
    idRd = app.charIDToTypeID("Rd  ")
    desc611.putDouble(idRd, stroke_color.rgb.red)
    idGrn = app.charIDToTypeID("Grn ")
    desc611.putDouble(idGrn, stroke_color.rgb.green)
    idBl = app.charIDToTypeID("Bl  ")
    desc611.putDouble(idBl, stroke_color.rgb.blue)
    idRGBC = app.charIDToTypeID("RGBC")
    desc610.putObject(idClr, idRGBC, desc611)
    idFrFX = app.charIDToTypeID("FrFX")
    desc609.putObject(idFrFX, idFrFX, desc610)
    idLefx = app.charIDToTypeID("Lefx")
    desc608.putObject(idT, idLefx, desc609)
    app.executeAction(idsetd, desc608, ps.DialogModes.DisplayNoDialogs)

def save_and_close(file_name):
    # Saves the current document to the output folder (/out/) as a PNG and closes the document without saving.
    idsave = app.charIDToTypeID("save")
    desc3 = ps.ActionDescriptor()
    idAs = app.charIDToTypeID("As  ")
    desc4 = ps.ActionDescriptor()
    idPGIT = app.charIDToTypeID("PGIT")
    idPGIN = app.charIDToTypeID("PGIN")
    desc4.putEnumerated(idPGIT, idPGIT, idPGIN)
    idPNGf = app.charIDToTypeID("PNGf")
    idPGAd = app.charIDToTypeID("PGAd")
    desc4.putEnumerated(idPNGf, idPNGf, idPGAd)
    
    # Save fast? (uncompressed)
    if cfg.fast_save:
        idCmpr = app.charIDToTypeID( "Cmpr" )
        desc4.putInteger( idCmpr, 0 )
    
    idPNGF = app.charIDToTypeID("PNGF")
    desc3.putObject(idAs, idPNGF, desc4)
    idIn = app.charIDToTypeID("In  ")
    file_name_with_path = os.path.join(con.cwd, f"out/{file_name}.png")
    desc3.putPath(idIn, file_name_with_path)
    idCpy = app.charIDToTypeID("Cpy ")
    desc3.putBoolean(idCpy, True)
    app.executeAction(idsave, desc3, ps.DialogModes.DisplayNoDialogs)
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)

def get_text_layer_color(layer):
    """
     * Occasionally, Photoshop has issues with retrieving the color of a text layer. This helper guards
     * against errors and null values by defaulting to rgb_black() in the event of a problem.
    """
    try:
        text_layer_color = layer.textItem.color
        if text_layer_color == None: text_layer_color = rgb_black()
    except:
        text_layer_color = rgb_black()
    return text_layer_color

def create_new_layer(layer_name=None):
    """
     * Creates a new layer below the currently active layer. The layer will be visible.
    """
    if layer_name == None: layer_name = "Layer"

    # create new layer at top of layers
    active_layer = app.activeDocument.activeLayer
    layer = app.activeDocument.artLayers.add()

    # name it & set blend mode to normal
    layer.name = layer_name
    layer.blendMode = ps.BlendMode.NormalBlend
    layer.visible = True

    # Move the layer below
    layer.moveAfter(active_layer)

    return layer

def replace_text(layer, replace_this, replace_with):
    # Replace all instances of `replace_this` in the specified layer with `replace_with`.
    app.activeDocument.activeLayer = layer
    idreplace = app.stringIDToTypeID("replace")
    desc22 = ps.ActionDescriptor()
    idnull = app.charIDToTypeID("null")
    ref3 = ps.ActionReference()
    idPrpr = app.charIDToTypeID("Prpr")
    idreplace = app.stringIDToTypeID("replace")
    ref3.putProperty(idPrpr, idreplace)
    idTxLr = app.charIDToTypeID("TxLr")
    idOrdn = app.charIDToTypeID("Ordn")
    idAl = app.charIDToTypeID("Al  ")
    ref3.putEnumerated(idTxLr, idOrdn, idAl)
    desc22.putReference(idnull, ref3)
    idUsng = app.charIDToTypeID("Usng")
    desc23 = ps.ActionDescriptor()
    idfind = app.stringIDToTypeID("find")
    desc23.putString(idfind, replace_this)
    idreplace = app.stringIDToTypeID("replace")
    desc23.putString(idreplace, replace_with)
    idcheckAll = app.stringIDToTypeID("checkAll")
    desc23.putBoolean(idcheckAll, True)
    idFwd = app.charIDToTypeID("Fwd ")
    desc23.putBoolean(idFwd, True)
    idcaseSensitive = app.stringIDToTypeID("caseSensitive")
    desc23.putBoolean(idcaseSensitive, False)
    idwholeWord = app.stringIDToTypeID("wholeWord")
    desc23.putBoolean(idwholeWord, False)
    idignoreAccents = app.stringIDToTypeID("ignoreAccents")
    desc23.putBoolean(idignoreAccents, True)
    idfindReplace = app.stringIDToTypeID("findReplace")
    desc22.putObject(idUsng, idfindReplace, desc23)
    app.executeAction(idreplace, desc22, ps.DialogModes.DisplayNoDialogs)

def paste_file(layer, file):
    """
     * Pastes the given file into the specified layer.
    """
    prev_active_layer = app.activeDocument.activeLayer
    app.activeDocument.activeLayer = layer
    app.load(file)
    # note context switch to art file
    app.activeDocument.selection.selectAll()
    app.activeDocument.selection.copy()
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
    # note context switch back to template
    app.activeDocument.paste()

    # return document to previous state
    app.activeDocument.activeLayer = prev_active_layer

def paste_file_into_new_layer(file):
    """
     * Wrapper for paste_file which creates a new layer for the file next to the active layer. Returns the new layer.
    """
    new_layer = create_new_layer("New Layer")
    paste_file(new_layer, file)
    return new_layer

def insert_scryfall_scan(image_url):
    """
     * Downloads the specified scryfall scan and inserts it into a new layer next to the active layer. Returns the new layer.
    """
    import proxyshop.scryfall as scry
    scryfall_scan = scry.card_scan(image_url)
    return paste_file_into_new_layer(scryfall_scan)

def content_fill_empty_area():
    """
     * Helper function intended to streamline the workflow of making extended art cards.
     * This script rasterises the active layer and fills all empty pixels in the canvas on the layer using content-aware fill.
    """
    # select pixels of active layer
    id1268 = app.charIDToTypeID("setd")
    desc307 = ps.ActionDescriptor()
    id1269 = app.charIDToTypeID("null")
    ref257 = ps.ActionReference()
    id1270 = app.charIDToTypeID("Chnl")
    id1271 = app.charIDToTypeID("fsel")
    ref257.putProperty(id1270, id1271)
    desc307.putReference(id1269, ref257)
    id1272 = app.charIDToTypeID("T   ")
    ref258 = ps.ActionReference()
    id1273 = app.charIDToTypeID("Chnl")
    id1274 = app.charIDToTypeID("Chnl")
    id1275 = app.charIDToTypeID("Trsp")
    ref258.putEnumerated(id1273, id1274, id1275)
    desc307.putReference(id1272, ref258)
    app.executeAction(id1268, desc307, ps.DialogModes.DisplayNoDialogs)

    # rasterise
    docRef = app.activeDocument
    active_layer = docRef.activeLayer
    active_layer.rasterize(ps.RasterizeType.EntireLayer)

    # manipulate selection - invert, expand 8px, smooth 4px
    selection = docRef.selection
    selection.invert()
    selection.expand(10)
    selection.smooth(4)

    # content aware fill
    idFl = app.charIDToTypeID("Fl  ")
    desc12 = ps.ActionDescriptor()
    idUsng = app.charIDToTypeID("Usng")
    idFlCn = app.charIDToTypeID("FlCn")
    idcontentAware = app.stringIDToTypeID("contentAware")
    desc12.putEnumerated(idUsng, idFlCn, idcontentAware)
    idOpct = app.charIDToTypeID("Opct")
    idPrc = app.charIDToTypeID("#Prc")
    desc12.putUnitDouble(idOpct, idPrc, 100.000000)
    idMd = app.charIDToTypeID("Md  ")
    idBlnM = app.charIDToTypeID("BlnM")
    idNrml = app.charIDToTypeID("Nrml")
    desc12.putEnumerated(idMd, idBlnM, idNrml)
    app.executeAction(idFl, desc12, ps.DialogModes.DisplayNoDialogs)

    selection.deselect()

def VibrantSaturation(VibValue, SatValue):
    """
     * Experimental scoot action
    """
    #dialogMode
    #dialogMode = 3
    idvibrance = app.stringIDToTypeID("vibrance")
    desc232 = ps.ActionDescriptor()
    idvibrance = app.stringIDToTypeID("vibrance")
    desc232.putInteger( idvibrance, VibValue )
    idStrt = app.charIDToTypeID( "Strt" )
    desc232.putInteger( idStrt, SatValue )
    app.executeAction( idvibrance, desc232, ps.DialogModes.DisplayNoDialogs )