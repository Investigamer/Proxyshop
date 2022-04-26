"""
PHOTOSHOP HELPER FUNCTIONS
"""
import os
from proxyshop.scryfall import card_scan
import photoshop.api as ps
cwd = os.getcwd()
app = ps.Application()


def getLayer(name, group=None):
    """
    Retrieve layer object.
    @param name: Name of the layer
    @param group: Parent group name or object.
    @return: Layer object requested
    """
    if group is None:
        # No set given
        for layer in app.activeDocument.layers:
            if layer.name == name:
                return layer
    else:
        if isinstance(group, str):
            # Set name given
            layer_set = app.activeDocument.layerSets.getByName(group)
            for layer in layer_set.layers:
                if layer.name == name:
                    return layer
        else:
            # Set object given
            for layer in group.layers:
                if layer.name == name:
                    return layer
    # None found
    return None


def getLayerSet(name, group=None):
    """
    Retrieve layer group object.
    @param name: Name of the group
    @param group: Parent group name or object.
    @return: Group object requested.
    """
    if group:
        if isinstance(group, str):
            # Set name given
            layer_set = app.activeDocument.layerSets.getByName(group)
            return layer_set.layerSets.getByName(name)
        # Set object given
        return group.layerSets.getByName(name)
    # Look through entire document
    return app.activeDocument.layerSets.getByName(name)


def rgb_black():
    """
    Creates and returns a Solidcolor with RGB values for solid black.
    """
    color = ps.SolidColor()
    color.rgb.red = 0
    color.rgb.green = 0
    color.rgb.blue = 0
    return color


def rgb_grey():
    """
    Creates and returns a Solidcolor with RGB values for solid black.
    """
    color = ps.SolidColor()
    color.rgb.red = 170
    color.rgb.green = 170
    color.rgb.blue = 170
    return color


def rgb_white():
    """
    Creates and returns a Solidcolor with RGB values for solid white.
    """
    color = ps.SolidColor()
    color.rgb.red = 255
    color.rgb.green = 255
    color.rgb.blue = 255
    return color


def get_rgb(r, g, b):
    """
    Creates and returns a SolidColor with RGB values given.
    """
    color = ps.SolidColor()
    color.rgb.red = r
    color.rgb.green = g
    color.rgb.blue = b
    return color


def compute_layer_dimensions(layer):
    """
    Return an object with the specified layer's width and height (computed from its bounds).
    """
    return {
        'width': layer.bounds[2]-layer.bounds[0],
        'height': layer.bounds[3]-layer.bounds[1],
    }


def compute_text_layer_dimensions(layer):
    """
    Return an object with the specified text layer's width and height, which is achieved by rasterising
    the layer and computing its width and height from its bounds.
    """
    layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
    layer_copy.rasterize(ps.RasterizeType.TextContents)
    dimensions = compute_layer_dimensions(layer_copy)
    layer_copy.remove()
    return dimensions


def compute_text_layer_bounds(layer):
    """
    Return an object with the specified text layer's bounding box.
    """

    layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
    layer_copy.rasterize(ps.RasterizeType.TextContents)
    layer_bounds = layer.bounds
    layer_copy.remove()
    return layer_bounds


def select_layer_pixels(layer):
    """
    Select the bounding box of a given layer.
    """
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
    """
    Clear the current selection.
    """
    app.activeDocument.selection.select([])


def align(align_type):
    """
    Align the currently active layer to current selection, vertically or horizontally.
    Used with align_vertical() or align_horizontal().
    `align_type`: "AdCV" vertical, "AdCH" horizontal
    """
    desc = ps.ActionDescriptor()
    ref = ps.ActionReference()
    ref.putEnumerated(
        app.charIDToTypeID("Lyr "),
        app.charIDToTypeID("Ordn"),
        app.charIDToTypeID("Trgt"))
    desc.putReference(app.charIDToTypeID("null"), ref)
    desc.putEnumerated(
        app.charIDToTypeID("Usng"),
        app.charIDToTypeID("ADSt"),
        app.charIDToTypeID(align_type))
    app.executeAction(
        app.charIDToTypeID("Algn"),
        desc,
        ps.DialogModes.DisplayNoDialogs)


def align_vertical():
    """
    Align the currently active layer vertically with respect to the current selection.
    """
    align("AdCV")


def align_horizontal():
    """
    Align the currently active layer horizontally with respect to the current selection.
    """
    align("AdCH")


def frame_layer(layer, reference_layer):
    """
    Scale a layer equally to the bounds of a reference layer, then centre the layer vertically and horizontally
    within those bounds.
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
    Scale a layer equally to the bounds of a reference layer, then centre the layer vertically and horizontally
    within those bounds.
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


def set_active_layer_mask(visible=True):
    """
    Set the visibility of the active layer's layer mask.
    """
    desc3078 = ps.ActionDescriptor()
    desc3079 = ps.ActionDescriptor()
    ref1567 = ps.ActionReference()
    idLyr = app.charIDToTypeID("Lyr ")
    ref1567.putEnumerated(idLyr,
        app.charIDToTypeID("Ordn"),
        app.charIDToTypeID("Trgt"))
    desc3078.putReference(app.charIDToTypeID("null"), ref1567)
    desc3079.putBoolean(app.charIDToTypeID("UsrM"), visible)
    desc3078.putObject(app.charIDToTypeID("T   "), idLyr, desc3079)
    app.executeAction(app.charIDToTypeID("setd"), desc3078, ps.DialogModes.DisplayNoDialogs)


def enable_active_layer_mask():
    """
    Enables the active layer's layer mask.
    """
    set_active_layer_mask(True)


def disable_active_layer_mask():
    """
    Disables the active layer's layer mask.
    """
    set_active_layer_mask(False)


def apply_stroke(stroke_weight, stroke_color):
    """
    Applies an outer stroke to the active layer with the specified weight and color.
    """
    desc608 = ps.ActionDescriptor()
    desc609 = ps.ActionDescriptor()
    desc610 = ps.ActionDescriptor()
    desc611 = ps.ActionDescriptor()
    ref149 = ps.ActionReference()
    idLefx = app.charIDToTypeID("Lefx")
    idFrFX = app.charIDToTypeID("FrFX")
    idPrc = app.charIDToTypeID("#Prc")
    ref149.putProperty(app.charIDToTypeID("Prpr"), idLefx)
    ref149.putEnumerated(
        app.charIDToTypeID("Lyr "),
        app.charIDToTypeID("Ordn"),
        app.charIDToTypeID("Trgt"))
    desc608.putReference(app.charIDToTypeID("null"), ref149)
    desc609.putUnitDouble(app.charIDToTypeID("Scl "), idPrc, 200.000000)
    desc610.putBoolean(app.charIDToTypeID("enab"), True)
    desc610.putEnumerated(
        app.charIDToTypeID("Styl"),
        app.charIDToTypeID("FStl"),
        app.charIDToTypeID("OutF"))
    desc610.putEnumerated(
        app.charIDToTypeID("PntT"),
        app.charIDToTypeID("FrFl"),
        app.charIDToTypeID("SClr"))
    desc610.putEnumerated(
        app.charIDToTypeID("Md  "),
        app.charIDToTypeID("BlnM"),
        app.charIDToTypeID("Nrml"))
    desc610.putUnitDouble(
        app.charIDToTypeID("Opct"),
        idPrc, 100.000000)
    desc610.putUnitDouble(
        app.charIDToTypeID("Sz  "),
        app.charIDToTypeID("#Pxl"),
        int(stroke_weight))
    desc611.putDouble(app.charIDToTypeID("Rd  "), stroke_color.rgb.red)
    desc611.putDouble(app.charIDToTypeID("Grn "), stroke_color.rgb.green)
    desc611.putDouble(app.charIDToTypeID("Bl  "), stroke_color.rgb.blue)
    desc610.putObject(app.charIDToTypeID("Clr "), app.charIDToTypeID("RGBC"), desc611)
    desc609.putObject(idFrFX, idFrFX, desc610)
    desc608.putObject(app.charIDToTypeID("T   "), idLefx, desc609)
    app.executeAction(app.charIDToTypeID("setd"), desc608, ps.DialogModes.DisplayNoDialogs)


def save_document_png(file_name):
    """
    Save the current document to /out/ as a PNG.
    """
    idsave = app.charIDToTypeID("save")
    desc3 = ps.ActionDescriptor()
    idAs = app.charIDToTypeID("As  ")
    idCmpr = app.charIDToTypeID("Cmpr")
    desc4 = ps.ActionDescriptor()
    idPGIT = app.charIDToTypeID("PGIT")
    idPGIN = app.charIDToTypeID("PGIN")
    desc4.putEnumerated(idPGIT, idPGIT, idPGIN)
    idPNGf = app.charIDToTypeID("PNGf")
    idPGAd = app.charIDToTypeID("PGAd")
    desc4.putEnumerated(idPNGf, idPNGf, idPGAd)
    desc4.putInteger(idCmpr, 3)
    idPNGF = app.charIDToTypeID("PNGF")
    desc3.putObject(idAs, idPNGF, desc4)
    idIn = app.charIDToTypeID("In  ")
    file_name_with_path = os.path.join(cwd, f"out/{file_name}.png")
    desc3.putPath(idIn, file_name_with_path)
    idCpy = app.charIDToTypeID("Cpy ")
    desc3.putBoolean(idCpy, True)
    app.executeAction(idsave, desc3, ps.DialogModes.DisplayNoDialogs)


def save_document_jpeg(file_name):
    """
    Save the current document to /out/ as a JPEG.
    """
    desc34 = ps.ActionDescriptor()
    desc35 = ps.ActionDescriptor()
    desc35.putInteger(app.charIDToTypeID("EQlt"), 12)
    desc35.putInteger(app.charIDToTypeID("Scns"), 3)
    idMttC = app.charIDToTypeID("MttC")
    idNone = app.charIDToTypeID("None")
    desc35.putEnumerated(idMttC, idMttC, idNone)
    desc34.putObject(
        app.charIDToTypeID("As  "),
        app.charIDToTypeID("JPEG"),
        desc35)
    desc34.putPath(app.charIDToTypeID("In  "),
        os.path.join(cwd, f"out/{file_name}.jpg"))
    desc34.putInteger(app.charIDToTypeID("DocI"), 349 )
    desc34.putBoolean(app.charIDToTypeID("Cpy "), True)
    desc34.putEnumerated(
        app.stringIDToTypeID("saveStage"),
        app.stringIDToTypeID("saveStageType"),
        app.stringIDToTypeID("saveSucceeded"))
    app.executeAction(
        app.charIDToTypeID("save"),
        desc34,
        ps.SaveOptions.DoNotSaveChanges)


def close_document():
    """
    Close the document
    """
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)


def reset_document(filename):
    """
    Reset all changes to the current document
    """
    idslct = app.charIDToTypeID( "slct" )
    desc9 = ps.ActionDescriptor()
    idnull = app.charIDToTypeID( "null" )
    ref1 = ps.ActionReference()
    idSnpS = app.charIDToTypeID( "SnpS" )
    ref1.putName( idSnpS, filename )
    desc9.putReference( idnull, ref1 )
    app.executeAction( idslct, desc9, ps.DialogModes.DisplayNoDialogs )


def get_text_layer_color(layer):
    """
    Occasionally, Photoshop has issues with retrieving the color of a text layer. This helper guards
    against errors and null values by defaulting to rgb_black() in the event of a problem.
    """
    try:
        text_layer_color = layer.textItem.color
        if text_layer_color is None: text_layer_color = rgb_black()
    except:
        text_layer_color = rgb_black()
    return text_layer_color


def create_new_layer(layer_name=None):
    """
    Creates a new layer below the currently active layer. The layer will be visible.
    """
    if layer_name is None: layer_name = "Layer"

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
    """
    Replace all instances of `replace_this` in the specified layer with `replace_with`.
    """
    app.activeDocument.activeLayer = layer
    idreplace = app.stringIDToTypeID("replace")
    desc22 = ps.ActionDescriptor()
    ref3 = ps.ActionReference()
    ref3.putProperty(app.charIDToTypeID("Prpr"), idreplace)
    ref3.putEnumerated(app.charIDToTypeID("TxLr"),
        app.charIDToTypeID("Ordn"),
        app.charIDToTypeID("Al  "))
    desc22.putReference(app.charIDToTypeID("null"), ref3)
    desc23 = ps.ActionDescriptor()
    desc23.putString(app.stringIDToTypeID("find"), replace_this)
    desc23.putString(idreplace, replace_with)
    desc23.putBoolean(app.stringIDToTypeID("checkAll"), True)
    desc23.putBoolean(app.charIDToTypeID("Fwd "), True)
    desc23.putBoolean(app.stringIDToTypeID("caseSensitive"), False)
    desc23.putBoolean(app.stringIDToTypeID("wholeWord"), False)
    desc23.putBoolean(app.stringIDToTypeID("ignoreAccents"), True)
    desc22.putObject(app.charIDToTypeID("Usng"), app.stringIDToTypeID("findReplace"), desc23)
    app.executeAction(idreplace, desc22, ps.DialogModes.DisplayNoDialogs)


def paste_file(layer, file):
    """
    Pastes the given file into the specified layer.
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
    Wrapper for paste_file which creates a new layer for the file next to the active layer. Returns the new layer.
    """
    new_layer = create_new_layer("New Layer")
    paste_file(new_layer, file)
    return new_layer


def insert_scryfall_scan(image_url):
    """
    Downloads the specified scryfall scan and inserts it into a new layer next to the active layer. Returns the new layer.
    """
    scryfall_scan = card_scan(image_url)
    if scryfall_scan: return paste_file_into_new_layer(scryfall_scan)
    return None


def content_fill_empty_area():
    """
    Helper function intended to streamline the workflow of making extended art cards.
    This script rasterizes the active layer and fills all empty pixels in the canvas
    on the layer using content-aware fill.
    """
    # select pixels of active layer
    desc307 = ps.ActionDescriptor()
    ref257 = ps.ActionReference()
    ref257.putProperty(app.charIDToTypeID("Chnl"), app.charIDToTypeID("fsel"))
    desc307.putReference(app.charIDToTypeID("null"), ref257)
    ref258 = ps.ActionReference()
    idChnl = app.charIDToTypeID("Chnl")
    ref258.putEnumerated(idChnl, idChnl, app.charIDToTypeID("Trsp"))
    desc307.putReference( app.charIDToTypeID("T   "), ref258)
    app.executeAction(
        app.charIDToTypeID("setd"),
        desc307,
        ps.DialogModes.DisplayNoDialogs)

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
    desc12 = ps.ActionDescriptor()
    desc12.putEnumerated(
        app.charIDToTypeID("Usng"),
        app.charIDToTypeID("FlCn"),
        app.stringIDToTypeID("contentAware"))
    desc12.putUnitDouble(
        app.charIDToTypeID("Opct"),
        app.charIDToTypeID("#Prc"),
        100.000000)
    desc12.putEnumerated(
        app.charIDToTypeID("Md  "),
        app.charIDToTypeID("BlnM"),
        app.charIDToTypeID("Nrml"))
    app.executeAction(
        app.charIDToTypeID("Fl  "),
        desc12,
        ps.DialogModes.DisplayNoDialogs)

    selection.deselect()


def apply_vibrant_saturation(VibValue, SatValue):
    """
    Experimental scoot action
    """
    # dialogMode (Have dialog popup?)
    idvibrance = app.stringIDToTypeID("vibrance")
    desc232 = ps.ActionDescriptor()
    desc232.putInteger( idvibrance, VibValue )
    desc232.putInteger( app.charIDToTypeID("Strt"), SatValue )
    app.executeAction( idvibrance, desc232, ps.DialogModes.DisplayNoDialogs )


def fill_expansion_symbol(reference, stroke_color=rgb_black()):
    """
    Give the symbol a background for open space symbols (i.e. M10)
    """

    # Magic Wand contiguous outside symbol
    coords = ps.ActionDescriptor()
    coords.putUnitDouble(app.CharIDToTypeID( "Hrzn" ),app.CharIDToTypeID( "#Pxl" ), 100)
    coords.putUnitDouble(app.CharIDToTypeID( "Vrtc" ),app.CharIDToTypeID( "#Pxl" ), 100)
    click1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putProperty(app.CharIDToTypeID( "Chnl" ), app.CharIDToTypeID( "fsel" ) )
    click1.putReference(app.CharIDToTypeID( "null" ), ref1 )
    click1.putObject(app.CharIDToTypeID( "T   " ), app.CharIDToTypeID( "Pnt " ), coords )
    click1.putInteger(app.CharIDToTypeID( "Tlrn" ), 12 )
    click1.putBoolean(app.CharIDToTypeID( "AntA" ), True )
    app.executeAction(app.CharIDToTypeID("setd"), click1 )

    # Invert selection
    app.activeDocument.selection.invert()

    # Magic Wand cross select
    click2 = ps.ActionDescriptor()
    ref2 = ps.ActionReference()
    ref2.putProperty(app.CharIDToTypeID( "Chnl" ), app.CharIDToTypeID( "fsel" ) )
    click2.putReference(app.CharIDToTypeID( "null" ), ref2 )
    click2.putObject(app.CharIDToTypeID( "T   " ), app.CharIDToTypeID( "Pnt " ), coords )
    click2.putInteger(app.CharIDToTypeID( "Tlrn" ), 12 )
    click2.putBoolean(app.CharIDToTypeID( "AntA" ), True )
    click2.putBoolean(app.CharIDToTypeID( "Cntg" ), False )
    app.executeAction(app.CharIDToTypeID("IntW"), click2 )

    # Make a new layer
    layer = app.activeDocument.artLayers.add()
    layer.name = "Expansion Mask"
    layer.blendMode = ps.BlendMode.NormalBlend
    layer.visible = True
    layer.moveAfter(reference)

    # Fill selection with stroke color
    app.foregroundColor = stroke_color
    click3 = ps.ActionDescriptor()
    click3.putObject(app.CharIDToTypeID( "From" ), app.CharIDToTypeID( "Pnt " ), coords )
    click3.putInteger(app.CharIDToTypeID( "Tlrn" ), 0)
    click3.putEnumerated(
        app.CharIDToTypeID( "Usng" ),
        app.CharIDToTypeID( "FlCn" ),
        app.CharIDToTypeID( "FrgC" ))
    click3.putBoolean( app.CharIDToTypeID( "Cntg" ), False )
    app.executeAction( app.CharIDToTypeID( "Fl  " ), click3 )

    # Clear Selection
    clear_selection()

    # Maximum filter to keep the antialiasing normal
    layer.applyMaximum(1)


def select_current_layer():
    """
    Select pixels of active layer
    """
    desc307 = ps.ActionDescriptor()
    ref257 = ps.ActionReference()
    ref257.putProperty(app.charIDToTypeID("Chnl"), app.charIDToTypeID("fsel"))
    desc307.putReference(app.charIDToTypeID("null"), ref257)
    ref258 = ps.ActionReference()
    idChnl = app.charIDToTypeID("Chnl")
    ref258.putEnumerated(idChnl, idChnl, app.charIDToTypeID("Trsp"))
    desc307.putReference( app.charIDToTypeID("T   "), ref258)
    app.executeAction(
        app.charIDToTypeID("setd"),
        desc307,
        ps.DialogModes.DisplayNoDialogs)