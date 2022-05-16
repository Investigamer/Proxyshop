"""
PHOTOSHOP HELPER FUNCTIONS
"""
import os
from proxyshop.scryfall import card_scan
from proxyshop.settings import cfg
import photoshop.api as ps

# QOL Definitions
cwd = os.getcwd()
app = ps.Application()
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = ps.DialogModes.DisplayNoDialogs


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


def layer_bounds_no_effects(layer):
    """
    Returns the bounds of a given layer without its effects applied.
    @param layer: A layer object
    @return list: Pixel location top left, top right, bottom left, bottom right.
    """
    current = app.activeDocument.activeLayer
    app.activeDocument.activeLayer = layer
    bounds = app.eval_javascript(
        f"""app.activeDocument.activeLayer.boundsNoEffects"""
    )
    app.activeDocument.activeLayer = current
    return [int(num) for num in bounds.replace(" px", "").split(",")]


def layer_dimensions_no_effects(layer):
    """
    Compute the dimensions of a layer without its effects applied.
    @param layer: A layer object
    @return dict: Height and width of the layer
    """
    bounds = layer_bounds_no_effects(layer)
    return {
        'width': bounds[2] - bounds[0],
        'height': bounds[3] - bounds[1],
    }


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
        cID("Lyr "),
        cID("Ordn"),
        cID("Trgt"))
    desc.putReference(cID("null"), ref)
    desc.putEnumerated(
        cID("Usng"),
        cID("ADSt"),
        cID(align_type))
    app.executeAction(
        cID("Algn"),
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
    idLyr = cID("Lyr ")
    ref1567.putEnumerated(idLyr,
        cID("Ordn"),
        cID("Trgt"))
    desc3078.putReference(cID("null"), ref1567)
    desc3079.putBoolean(cID("UsrM"), visible)
    desc3078.putObject(cID("T   "), idLyr, desc3079)
    app.executeAction(cID("setd"), desc3078, ps.DialogModes.DisplayNoDialogs)


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
    ref149.putProperty(cID("Prpr"), cID("Lefx"))
    ref149.putEnumerated(cID("Lyr "), cID("Ordn"), cID("Trgt"))
    desc608.putReference(cID("null"), ref149)
    desc609.putUnitDouble(cID("Scl "), cID("#Prc"), 200)
    desc610.putBoolean(cID("enab"), True)
    desc610.putEnumerated(cID("Styl"), cID("FStl"), cID("OutF"))
    desc610.putEnumerated(cID("PntT"), cID("FrFl"), cID("SClr"))
    desc610.putEnumerated(cID("Md  "), cID("BlnM"), cID("Nrml"))
    desc610.putUnitDouble(cID("Opct"), cID("#Prc"), 100)
    desc610.putUnitDouble(cID("Sz  "), cID("#Pxl"), int(stroke_weight))
    desc611.putDouble(cID("Rd  "), stroke_color.rgb.red)
    desc611.putDouble(cID("Grn "), stroke_color.rgb.green)
    desc611.putDouble(cID("Bl  "), stroke_color.rgb.blue)
    desc610.putObject(cID("Clr "), cID("RGBC"), desc611)
    desc609.putObject(cID("FrFX"), cID("FrFX"), desc610)
    desc608.putObject(cID("T   "), cID("Lefx"), desc609)
    app.executeAction(cID("setd"), desc608, ps.DialogModes.DisplayNoDialogs)


def save_document_png(file_name):
    """
    Save the current document to /out/ as a PNG.
    """
    desc3 = ps.ActionDescriptor()
    desc4 = ps.ActionDescriptor()
    desc4.putEnumerated(cID("PGIT"), cID("PGIT"), cID("PGIN"))
    desc4.putEnumerated(cID("PNGf"), cID("PNGf"), cID("PGAd"))
    desc4.putInteger(cID("Cmpr"), 3)
    desc3.putObject(cID("As  "), cID("PNGF"), desc4)
    desc3.putPath(cID("In  "), os.path.join(cwd, f"out/{file_name}.png"))
    desc3.putBoolean(cID("Cpy "), True)
    app.executeAction(cID("save"), desc3, NO_DIALOG)


def save_document_jpeg(file_name):
    """
    Save the current document to /out/ as a JPEG.
    """
    desc34 = ps.ActionDescriptor()
    desc35 = ps.ActionDescriptor()
    desc35.putInteger(cID("EQlt"), 12)
    desc35.putInteger(cID("Scns"), 3)
    desc35.putEnumerated(cID("MttC"), cID("MttC"), cID("None"))
    desc34.putObject(cID("As  "), cID("JPEG"), desc35)
    desc34.putPath(cID("In  "), os.path.join(cwd, f"out/{file_name}.jpg"))
    desc34.putInteger(cID("DocI"), 349)
    desc34.putBoolean(cID("Cpy "), True)
    desc34.putEnumerated(sID("saveStage"), sID("saveStageType"), sID("saveSucceeded"))
    app.executeAction(cID("save"), desc34, ps.SaveOptions.DoNotSaveChanges)


def close_document():
    """
    Close the document
    """
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)


def reset_document(filename):
    """
    Reset all changes to the current document
    """
    idslct = cID("slct")
    desc9 = ps.ActionDescriptor()
    idnull = cID("null")
    ref1 = ps.ActionReference()
    idSnpS = cID("SnpS")
    ref1.putName(idSnpS, filename)
    desc9.putReference(idnull, ref1)
    app.executeAction(idslct, desc9, NO_DIALOG)


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

    # Create new layer at top of layers
    active_layer = app.activeDocument.activeLayer
    layer = app.activeDocument.artLayers.add()

    # Name it & set blend mode to normal
    layer.name = layer_name
    layer.blendMode = ps.BlendMode.NormalBlend
    layer.visible = True

    # Move the layer below
    layer.moveAfter(active_layer)

    return layer


def replace_text(layer, find, replace):
    """
    Replace all instances of `replace_this` in the specified layer with `replace_with`.
    """
    app.activeDocument.activeLayer = layer

    # Find and replace
    desc31 = ps.ActionDescriptor()
    ref3 = ps.ActionReference()
    desc32 = ps.ActionDescriptor()
    ref3.putProperty(sID("property"), sID("findReplace"))
    ref3.putEnumerated(sID("textLayer"), sID("active"), sID("targetEnum"))
    desc31.putReference(sID("target"), ref3)
    desc32.putString(sID("find"), f"{find}")
    desc32.putString(sID("replace"), f"{replace}")
    # Developmental fix for non-targeted replacement
    if cfg.targeted_replace:
        app.bringToFront()
        desc32.putBoolean(sID("checkAll"), False)
    else: desc32.putBoolean(sID("checkAll"), True)
    desc32.putBoolean(sID("forward"), True)
    desc32.putBoolean(sID("caseSensitive"), False)
    desc32.putBoolean(sID("wholeWord"), False)
    desc32.putBoolean(sID("ignoreAccents"), True)
    desc31.putObject(sID("using"), sID("findReplace"), desc32)
    app.executeAction(sID("findReplace"), desc31, NO_DIALOG)


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
    ref257.putProperty(cID("Chnl"), cID("fsel"))
    desc307.putReference(cID("null"), ref257)
    ref258 = ps.ActionReference()
    idChnl = cID("Chnl")
    ref258.putEnumerated(idChnl, idChnl, cID("Trsp"))
    desc307.putReference(cID("T   "), ref258)
    app.executeAction(cID("setd"), desc307, NO_DIALOG)

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
    desc12.putEnumerated(cID("Usng"), cID("FlCn"), sID("contentAware"))
    desc12.putUnitDouble(cID("Opct"), cID("#Prc"), 100)
    desc12.putEnumerated(cID("Md  "), cID("BlnM"), cID("Nrml"))
    app.executeAction(cID("Fl  "), desc12, NO_DIALOG)
    selection.deselect()


def apply_vibrant_saturation(VibValue, SatValue):
    """
    Experimental scoot action
    """
    # dialogMode (Have dialog popup?)
    idvibrance = sID("vibrance")
    desc232 = ps.ActionDescriptor()
    desc232.putInteger(idvibrance, VibValue)
    desc232.putInteger(cID("Strt"), SatValue)
    app.executeAction(idvibrance, desc232, ps.DialogModes.DisplayNoDialogs)


def fill_expansion_symbol(reference, stroke_color=rgb_black()):
    """
    Give the symbol a background for open space symbols (i.e. M10)
    """

    # Magic Wand contiguous outside symbol
    coords = ps.ActionDescriptor()
    coords.putUnitDouble(cID("Hrzn"),cID("#Pxl"), 100)
    coords.putUnitDouble(cID("Vrtc"),cID("#Pxl"), 100)
    click1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putProperty(cID("Chnl"), cID("fsel"))
    click1.putReference(cID("null"), ref1)
    click1.putObject(cID("T   "), cID("Pnt "), coords)
    click1.putInteger(cID("Tlrn"), 12)
    click1.putBoolean(cID("AntA"), True)
    app.executeAction(cID("setd"), click1)

    # Invert selection
    app.activeDocument.selection.invert()

    # Magic Wand cross select
    click2 = ps.ActionDescriptor()
    ref2 = ps.ActionReference()
    ref2.putProperty(cID("Chnl"), cID("fsel"))
    click2.putReference(cID("null"), ref2)
    click2.putObject(cID("T   "), cID("Pnt "), coords)
    click2.putInteger(cID("Tlrn"), 12)
    click2.putBoolean(cID("AntA"), True)
    click2.putBoolean(cID("Cntg"), False)
    app.executeAction(cID("IntW"), click2)

    # Make a new layer
    layer = app.activeDocument.artLayers.add()
    layer.name = "Expansion Mask"
    layer.blendMode = ps.BlendMode.NormalBlend
    layer.visible = True
    layer.moveAfter(reference)

    # Fill selection with stroke color
    app.foregroundColor = stroke_color
    click3 = ps.ActionDescriptor()
    click3.putObject(cID("From"), cID("Pnt "), coords)
    click3.putInteger(cID("Tlrn"), 0)
    click3.putEnumerated(cID("Usng"), cID("FlCn"), cID("FrgC"))
    click3.putBoolean(cID("Cntg"), False)
    app.executeAction(cID("Fl  "), click3)

    # Clear Selection
    clear_selection()

    # Maximum filter to keep the antialiasing normal
    layer.applyMaximum(1)


def select_current_layer():
    """
    Select pixels of active layer
    """
    des1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref258 = ps.ActionReference()
    ref1.putProperty(cID("Chnl"), cID("fsel"))
    des1.putReference(cID("null"), ref1)
    idChnl = cID("Chnl")
    ref258.putEnumerated(idChnl, idChnl, cID("Trsp"))
    des1.putReference(cID("T   "), ref258)
    app.executeAction(cID("setd"), des1, NO_DIALOG)