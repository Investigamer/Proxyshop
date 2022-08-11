"""
PHOTOSHOP HELPER FUNCTIONS
"""
import _ctypes
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

# Ensure scaling with pixels, font size with points
app.preferences.rulerUnits = ps.Units.Pixels
app.preferences.typeUnits = ps.Units.Points


"""
SYSTEM FUNCTIONS
"""


def check_fonts(fonts: list):
    """
    Check if given fonts exist in users Photoshop Application.
    @return: Array of missing fonts or None
    """
    missing = []
    for f in fonts:
        try: assert isinstance(app.fonts.getByName(f).name, str)
        except AssertionError: missing.append(f)
    if len(missing) == 0: return
    else: return missing


"""
UTILITY FUNCTIONS
"""


def getLayer(name: str, group=None):
    """
    Retrieve layer object.
    @param name: Name of the layer
    @param group: Group name/object, or ordered list of group names/objects
    @return: Layer object requested
    """
    try:
        layer_set = None
        if group is None:
            # No LayerSet given
            for layer in app.activeDocument.layers:
                if layer.name == name: return layer
        elif isinstance(group, str):
            # LayerSet name given
            layer_set = app.activeDocument.layerSets.getByName(group)
        elif isinstance(group, (tuple, list)):
            # List of layerSet names/objects given
            for g in group:
                # First in list or not?
                if not layer_set:
                    if isinstance(g, str): layer_set = app.activeDocument.layerSets.getByName(g)
                    else: layer_set = g
                else:
                    if isinstance(g, str): layer_set = getLayerSet(g, layer_set)
                    else: layer_set = g
        else: layer_set = group
        # Else, assume layerSet object given

        # Find our layer
        for layer in layer_set.layers:
            if layer.name == name:
                return layer
    except: return


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


"""
COLOR FUNCTIONS
"""


def rgb_black():
    """
    Creates a black SolidColor object.
    @return: SolidColor object
    """
    color = ps.SolidColor()
    color.rgb.red = 0
    color.rgb.green = 0
    color.rgb.blue = 0
    return color


def rgb_grey():
    """
    Creates a grey SolidColor object.
    @return: SolidColor object.
    """
    color = ps.SolidColor()
    color.rgb.red = 170
    color.rgb.green = 170
    color.rgb.blue = 170
    return color


def rgb_white():
    """
    Creates a white SolidColor object.
    @return: SolidColor object.
    """
    color = ps.SolidColor()
    color.rgb.red = 255
    color.rgb.green = 255
    color.rgb.blue = 255
    return color


def get_rgb(r, g, b):
    """
    Creates a SolidColor object with the given RGB values.
    @param r: Integer from 0 to 255 for red spectrum.
    @param g: Integer from 0 to 255 for green spectrum.
    @param b: Integer from 0 to 255 for blue spectrum.
    @return: SolidColor object.
    """
    color = ps.SolidColor()
    color.rgb.red = r
    color.rgb.green = g
    color.rgb.blue = b
    return color


"""
LAYER PROPERTIES
"""


def layer_bounds_no_effects(layer):
    """
    Returns the bounds of a given layer without its effects applied.
    @param layer: A layer object
    @return list: Pixel location top left, top right, bottom left, bottom right.
    """
    current = app.activeDocument.activeLayer
    app.activeDocument.activeLayer = layer
    bounds = app.eval_javascript(
        "app.activeDocument.activeLayer.boundsNoEffects"
    )
    app.activeDocument.activeLayer = current
    return [int(num) for num in bounds.replace(" px", "").split(",")]


def get_dimensions_no_effects(layer):
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


def get_layer_dimensions(layer):
    """
    Compute the width and height dimensions of a layer.
    @param layer: A layer object
    @return dict: Height and width of the layer.
    """
    return {
        'width': layer.bounds[2]-layer.bounds[0],
        'height': layer.bounds[3]-layer.bounds[1],
    }


"""
TEXT LAYER PROPERTIES
"""


def get_text_layer_bounds(layer, text=False):
    """
    Return an object with the specified text layer's bounding box.
    @param layer: Layer to get the bounds of.
    @param text: Force old way for legacy text layers.
    @return: Array of the bounds of the given layer.
    """
    if int(app.version[0:2]) < 21 or text:
        layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
        layer_copy.rasterize(ps.RasterizeType.TextContents)
        layer_bounds = layer.bounds
        layer_copy.remove()
        return layer_bounds
    else: return layer.bounds


def get_text_layer_dimensions(layer, text=False):
    """
    Return an object with the specified text layer's width and height, which is achieved by rasterising
    the layer and computing its width and height from its bounds.
    @param layer: Layer to get the dimensions of.
    @param text: Force old way for legacy text layers.
    @return: Dict containing height and width of the given layer.
    """
    if int(app.version[0:2]) < 21 or text:
        layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
        layer_copy.rasterize(ps.RasterizeType.TextContents)
        dimensions = get_layer_dimensions(layer_copy)
        layer_copy.remove()
        return dimensions
    else: return get_layer_dimensions(layer)


def get_text_layer_color(layer):
    """
    Occasionally, Photoshop has issues with retrieving the color of a text layer. This helper guards
    against errors and null values by defaulting to rgb_black() in the event of a problem.
    @param layer: Layer object that must be TextLayer
    """
    try:
        if layer.kind == ps.LayerKind.TextLayer:
            return layer.textItem.color
        else: return rgb_black()
    except _ctypes.COMError: return rgb_black()


"""
LAYER ACTIONS
"""


def create_new_layer(layer_name=None):
    """
    Creates a new layer below the currently active layer. The layer will be visible.
    @param layer_name: Optional name for the new layer
    @return: Newly created layer object
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


def lock_layer(layer, protection = "protectAll"):
    """
    Locks the given layer.
    @param layer: A layer object
    @param protection: protectAll to lock, protectNone to unlock
    """
    desc819 = ps.ActionDescriptor()
    ref378 = ps.ActionReference()
    ref378.putIdentifier(cID("Lyr "), layer.id)
    desc819.putReference(cID("null"), ref378)
    desc820 = ps.ActionDescriptor()
    desc820.putBoolean(sID(protection), True)
    idlayerLocking = sID("layerLocking")
    desc819.putObject(idlayerLocking, idlayerLocking, desc820)
    app.executeAction(sID("applyLocking"), desc819, NO_DIALOG)


def unlock_layer(layer):
    """
    Unlocks the given layer.
    @param layer: A layer object
    """
    lock_layer(layer, "protectNone")


def select_layer_bounds(layer):
    """
    Select the bounding box of a given layer.
    @param layer: Layer to select the pixels of.
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


def select_current_layer():
    """
    Select pixels of the active layer.
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


def select_layer_pixels(layer):
    """
    Selects the pixels of a given layer.
    @param layer: Layer object
    """
    des1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref2 = ps.ActionReference()
    ref1.putProperty(cID("Chnl"), cID("fsel"))
    des1.putReference(cID("null"), ref1)
    ref2.putEnumerated(cID("Chnl"), cID("Chnl"), cID("Trsp"))
    ref2.putIdentifier(cID("Lyr "), layer.id)
    des1.putReference(cID("T   "), ref2)
    app.executeAction(cID("setd"), des1, NO_DIALOG)


def align(align_type = "AdCH", layer = None, ref = None):
    """
    Align the currently active layer to current selection, vertically or horizontally.
    Used with align_vertical() or align_horizontal().
    `align_type`: "AdCV" vertical, "AdCH" horizontal
    """
    # Optionally create a selection based on given reference
    if ref: select_layer_pixels(ref)

    # Optionally make a given layer the active layer
    if layer: app.activeDocument.activeLayer = layer

    # Align the current layer to selection
    desc = ps.ActionDescriptor()
    ref = ps.ActionReference()
    ref.putEnumerated(cID("Lyr "), cID("Ordn"), cID("Trgt"))
    desc.putReference(cID("null"), ref)
    desc.putEnumerated(cID("Usng"), cID("ADSt"), cID(align_type))
    app.executeAction(cID("Algn"), desc, NO_DIALOG)


def align_vertical(layer = None, ref = None):
    """
    Align the currently active layer vertically with respect to the current selection.
    """
    align("AdCV", layer, ref)


def align_horizontal(layer = None, ref = None):
    """
    Align the currently active layer horizontally with respect to the current selection.
    """
    align("AdCH", layer, ref)


def frame_layer(layer, reference, anchor=ps.AnchorPosition.TopLeft, smallest=False, align_h=True, align_v=True):
    """
    Scale a layer equally to the bounds of a reference layer, then center the layer vertically and horizontally
    within those bounds.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = get_layer_dimensions(reference)

    # Determine how much to scale the layer by such that it fits into the reference layer's bounds
    if smallest: scale = 100 * min((ref_dim['width'] / layer_dim['width']), (ref_dim['height'] / layer_dim['height']))
    else: scale = 100 * max((ref_dim['width'] / layer_dim['width']), (ref_dim['height'] / layer_dim['height']))
    layer.resize(scale, scale, anchor)

    # Align the layer
    select_layer_bounds(reference)
    app.activeDocument.activeLayer = layer
    if align_h: align_horizontal()
    if align_v: align_vertical()
    clear_selection()


def set_active_layer_mask(visible=True):
    """
    Set the visibility of the active layer's layer mask.
    """
    desc3078 = ps.ActionDescriptor()
    desc3079 = ps.ActionDescriptor()
    ref1567 = ps.ActionReference()
    ref1567.putEnumerated(cID("Lyr "), cID("Ordn"), cID("Trgt"))
    desc3078.putReference(cID("null"), ref1567)
    desc3079.putBoolean(cID("UsrM"), visible)
    desc3078.putObject(cID("T   "), cID("Lyr "), desc3079)
    app.executeAction(cID("setd"), desc3078, NO_DIALOG)


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


def set_layer_mask(layer, visible=True):
    """
    Set the visibility of the active layer's layer mask.
    """
    desc1 = ps.ActionDescriptor()
    desc2 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putIdentifier(cID("Lyr "), layer.id)
    desc1.putReference(cID("null"), ref1)
    desc2.putBoolean(cID("UsrM"), visible)
    desc1.putObject(cID("T   "), cID("Lyr "), desc2)
    app.executeAction(cID("setd"), desc1, NO_DIALOG)


def enable_mask(layer):
    """
    Enables a given layer's mask.
    @param layer: A layer object
    """
    set_layer_mask(layer, True)


def disable_mask(layer):
    """
    Disables a given layer's mask.
    @param layer: A layer object
    """
    set_layer_mask(layer, False)


def merge_layers(layer_1, layer_2):
    """
    Merge two layers together.
    @param layer_1: First layer object.
    @param layer_2: Second layer object.
    @return: Returns the merged layer.
    """
    desc1 = ps.ActionDescriptor()
    desc2 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref2 = ps.ActionReference()
    ref1.putIdentifier(sID("layer"), layer_1.id)
    desc1.PutReference(sID("target"), ref1)
    ref2.putIdentifier(sID("layer"), layer_2.id)
    desc2.PutReference(sID("target"), ref2)
    desc2.PutEnumerated(
        sID("selectionModifier"),
        sID("selectionModifierType"),
        sID("addToSelection")
    )
    app.ExecuteAction(sID("select"), desc1, NO_DIALOG)
    app.ExecuteAction(sID("select"), desc2, NO_DIALOG)
    app.ExecuteAction(sID("mergeLayersNew"), ps.ActionDescriptor(), NO_DIALOG)
    return app.activeDocument.activeLayer


def apply_stroke(layer, stroke_weight, stroke_color=rgb_black()):
    """
    Applies an outer stroke to the active layer with the specified weight and color.
    """
    desc608 = ps.ActionDescriptor()
    desc609 = ps.ActionDescriptor()
    desc610 = ps.ActionDescriptor()
    desc611 = ps.ActionDescriptor()
    ref149 = ps.ActionReference()
    ref149.putProperty(cID("Prpr"), cID("Lefx"))
    ref149.putIdentifier(cID("Lyr "), layer.id)
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
    app.executeAction(cID("setd"), desc608, NO_DIALOG)


def clear_layer_style(layer):
    """
    Removes all layer style effects.
    @param layer: Layer object
    """
    current = app.activeDocument.activeLayer
    app.activeDocument.activeLayer = layer
    desc1600 = ps.ActionDescriptor()
    ref126 = ps.ActionReference()
    ref126.PutEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    desc1600.PutReference(sID("target"), ref126)
    app.ExecuteAction(sID("disableLayerStyle"), desc1600, NO_DIALOG)
    app.activeDocument.activeLayer = current


def rasterize_layer_style(layer):
    """
    Rasterizes a layer including its style.
    @param layer: Layer object
    """
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putIdentifier(sID("layer"), layer.id)
    desc1.PutReference(sID("target"),  ref1)
    desc1.PutEnumerated(sID("what"), sID("rasterizeItem"), sID("layerStyle"))
    app.ExecuteAction(sID("rasterizeLayer"), desc1, NO_DIALOG)


def paste_file(layer, file, action=None, action_args=None):
    """
    Pastes the given file into the specified layer.
    @param layer: Layer object to paste the image into.
    @param file: Filepath of the image to open.
    @param action: Optional action function to call on the image before importing it.
    @param action_args: Optional arguments to pass to the action function
    """
    # Select the correct layer, then load the file
    prev_active_layer = app.activeDocument.activeLayer
    app.activeDocument.activeLayer = layer
    app.load(file)

    # Optionally run action on art before importing it
    if action:
        if action_args: action(**action_args)
        else: action()

    # Select the entire image, copy it, and close the file
    app.activeDocument.selection.selectAll()
    app.activeDocument.selection.copy()
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)

    # Paste the image into the specific layer, then switch back
    app.activeDocument.paste()
    app.activeDocument.activeLayer = prev_active_layer


def paste_file_into_new_layer(file):
    """
    Wrapper for paste_file which creates a new layer for the file next to the active layer.
    Returns the new layer.
    """
    new_layer = create_new_layer("New Layer")
    paste_file(new_layer, file)
    return new_layer


"""
TEXT LAYER ACTIONS
"""


def replace_text(layer, find, replace):
    """
    Replace all instances of `replace_this` in the specified layer with `replace_with`.
    @param layer: Layer object to search through.
    @param find: Text string to search for.
    @param replace: Text string to replace matches with.
    """
    # Set the active layer
    current = app.activeDocument.activeLayer
    app.activeDocument.activeLayer = layer

    # Find and replace
    desc31 = ps.ActionDescriptor()
    ref3 = ps.ActionReference()
    desc32 = ps.ActionDescriptor()
    ref3.putProperty(sID("property"), sID("findReplace"))
    ref3.putEnumerated(cID('TxLr'), cID('Ordn'), cID('Trgt'))
    desc31.putReference(sID("null"), ref3)
    desc32.putString(sID("find"), f"{find}")
    desc32.putString(sID("replace"), f"{replace}")
    if int(app.version[0:2]) > 22 or cfg.targeted_replace:
        if cfg.targeted_replace: app.bringToFront()
        desc32.putBoolean(sID("checkAll"), False)
    else: desc32.putBoolean(sID("checkAll"), True)
    desc32.putBoolean(sID("forward"), True)
    desc32.putBoolean(sID("caseSensitive"), True)
    desc32.putBoolean(sID("wholeWord"), False)
    desc32.putBoolean(sID("ignoreAccents"), True)
    desc31.putObject(sID("using"), sID("findReplace"), desc32)
    app.executeAction(sID("findReplace"), desc31, NO_DIALOG)

    # Reset current selected
    app.activeDocument.activeLayer = current


"""
DOCUMENT ACTIONS
"""


def clear_selection():
    """
    Clear the current selection.
    """
    app.activeDocument.selection.select([])


def trim_transparent_pixels():
    """
    Trim transparent pixels from Photoshop document.
    """
    desc258 = ps.ActionDescriptor()
    desc258.PutEnumerated(sID("trimBasedOn"), sID("trimBasedOn"), sID("transparency"))
    desc258.PutBoolean(sID("top"), True)
    desc258.PutBoolean(sID("bottom"), True)
    desc258.PutBoolean(sID("left"), True)
    desc258.PutBoolean(sID("right"), True)
    app.ExecuteAction(sID("trim"), desc258, NO_DIALOG)


def run_action(action_set, action):
    """
    Runs a Photoshop action.
    @param action_set: Name of the group the action is in.
    @param action: Name of the action.
    """
    desc310 = ps.ActionDescriptor()
    ref7 = ps.ActionReference()
    desc310.PutBoolean(sID("dontRecord"), False)
    desc310.PutBoolean(sID("forceNotify"), True)
    ref7.PutName(sID("action"),  action)
    ref7.PutName(sID("actionSet"),  action_set)
    desc310.PutReference(sID("target"),  ref7)
    app.ExecuteAction(sID("play"), desc310, NO_DIALOG)


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
    desc34.putBoolean(cID("Cpy "), True)
    desc34.putEnumerated(sID("saveStage"), sID("saveStageType"), sID("saveSucceeded"))
    app.executeAction(cID("save"), desc34, ps.SaveOptions.DoNotSaveChanges)


def close_document():
    """
    Close the document
    """
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)


def open_svg(path, max_width=500, dpi=1200):
    """
    Opens a rasterized SVG file in Photoshop.
    @param path: Path to the file
    @param max_width: Max width, height will be proportional
    @param dpi: Pixel density of the image
    """
    desc227 = ps.ActionDescriptor()
    desc228 = ps.ActionDescriptor()
    desc227.PutBoolean(sID("dontRecord"), False)
    desc227.PutBoolean(sID("forceNotify"), True)
    desc227.PutPath(sID("target"), path)
    desc228.PutUnitDouble(sID("width"), sID("pixelsUnit"), max_width)
    desc228.PutUnitDouble(sID("resolution"), sID("densityUnit"), dpi)
    desc228.PutEnumerated(sID("mode"), sID("colorSpace"), sID("RGBColor"))
    desc228.PutBoolean(sID("antiAlias"), True)
    desc228.PutBoolean(sID("constrainProportions"), True)
    desc227.PutObject(sID("as"), sID("svgFormat"), desc228)
    app.ExecuteAction(sID("open"), desc227, NO_DIALOG)


def reset_document(filename):
    """
    Reset all changes to the current document
    @param filename: Document file name
    """
    idslct = cID("slct")
    desc9 = ps.ActionDescriptor()
    idnull = cID("null")
    ref1 = ps.ActionReference()
    idSnpS = cID("SnpS")
    ref1.putName(idSnpS, filename)
    desc9.putReference(idnull, ref1)
    app.executeAction(idslct, desc9, NO_DIALOG)


"""
DESIGN UTILITIES
"""


def content_fill_empty_area(layer=None):
    """
    Helper function intended to streamline the workflow of making extended art cards.
    This script rasterizes the active layer and fills all empty pixels in the canvas
    on the layer using content-aware fill.
    """
    # Change active layer
    current = app.activeDocument.activeLayer
    if layer: app.activeDocument.activeLayer = layer

    # Select pixels of active layer
    desc307 = ps.ActionDescriptor()
    ref257 = ps.ActionReference()
    ref257.putProperty(cID("Chnl"), cID("fsel"))
    desc307.putReference(cID("null"), ref257)
    ref258 = ps.ActionReference()
    idChnl = cID("Chnl")
    ref258.putEnumerated(idChnl, idChnl, cID("Trsp"))
    if layer: ref258.putIdentifier(sID("layer"), layer.id)
    desc307.putReference(cID("T   "), ref258)
    app.executeAction(cID("setd"), desc307, NO_DIALOG)

    # Rasterize
    docRef = app.activeDocument
    active_layer = docRef.activeLayer
    active_layer.rasterize(ps.RasterizeType.EntireLayer)

    # Manipulate selection - invert, expand 8px, smooth 4px
    selection = docRef.selection
    selection.invert()
    selection.expand(10)
    selection.smooth(4)

    # Content aware fill
    desc12 = ps.ActionDescriptor()
    desc12.putEnumerated(cID("Usng"), cID("FlCn"), sID("contentAware"))
    desc12.putUnitDouble(cID("Opct"), cID("#Prc"), 100)
    desc12.putEnumerated(cID("Md  "), cID("BlnM"), cID("Nrml"))
    app.executeAction(cID("Fl  "), desc12, NO_DIALOG)
    selection.deselect()

    # Reset active
    app.activeDocument.activeLayer = current


def apply_vibrant_saturation(VibValue, SatValue):
    """
    Experimental scoot action to add vibrancy and saturation.
    @param VibValue: Vibrancy level integer
    @param SatValue: Saturation level integer
    """
    # dialogMode (Have dialog popup?)
    idvibrance = sID("vibrance")
    desc232 = ps.ActionDescriptor()
    desc232.putInteger(idvibrance, VibValue)
    desc232.putInteger(cID("Strt"), SatValue)
    app.executeAction(idvibrance, desc232, NO_DIALOG)


def repair_edges(edge=6):
    """
    Select a small area at the edges of an image and content aware fill to repair upscale damage.
    @param edge: How many pixels to select at the edge.
    """
    # Select all
    desc632724 = ps.ActionDescriptor()
    ref489 = ps.ActionReference()
    ref489.PutProperty(sID("channel"), sID("selection"))
    desc632724.PutReference(sID("target"), ref489)
    desc632724.PutEnumerated(sID("to"), sID("ordinal"), sID("allEnum"))
    app.ExecuteAction(sID("set"), desc632724, NO_DIALOG)

    # Contract selection
    contract = ps.ActionDescriptor()
    contract.PutUnitDouble(sID("by"), sID("pixelsUnit"), edge)
    contract.PutBoolean(sID("selectionModifyEffectAtCanvasBounds"), True)
    app.ExecuteAction(sID("contract"), contract, NO_DIALOG)

    # Inverse the selection
    app.ExecuteAction(sID("inverse"), None, NO_DIALOG)

    # Content aware fill
    desc_caf = ps.ActionDescriptor()
    desc_caf.PutEnumerated(
        sID("cafSamplingRegion"),
        sID("cafSamplingRegion"),
        sID("cafSamplingRegionRectangular")
    )
    desc_caf.PutBoolean(sID("cafSampleAllLayers"), False)
    desc_caf.PutEnumerated(
        sID("cafColorAdaptationLevel"),
        sID("cafColorAdaptationLevel"),
        sID("cafColorAdaptationDefault")
    )
    desc_caf.PutEnumerated(
        sID("cafRotationAmount"),
        sID("cafRotationAmount"),
        sID("cafRotationAmountNone")
    )
    desc_caf.PutBoolean(sID("cafScale"), False)
    desc_caf.PutBoolean(sID("cafMirror"), False)
    desc_caf.PutEnumerated(
        sID("cafOutput"),
        sID("cafOutput"),
        sID("cafOutputToNewLayer")
    )
    app.ExecuteAction(sID("cafWorkspace"), desc_caf, NO_DIALOG)

    # Deselect
    app.activeDocument.selection.deselect()


"""
PROXYSHOP UTILITIES
"""


def fill_expansion_symbol(reference, color=rgb_black()):
    """
    Give the symbol a background for open space symbols (i.e. M10)
    @param reference: Reference layer to put the new fill layer underneath
    @param color: Color of the background fill
    """
    # Magic Wand contiguous outside symbol
    coords = ps.ActionDescriptor()
    coords.putUnitDouble(cID("Hrzn"), cID("#Pxl"), 100)
    coords.putUnitDouble(cID("Vrtc"), cID("#Pxl"), 100)
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
    app.activeDocument.selection.contract(1)

    """ # Not necessary?
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
    app.activeDocument.selection.expand(4)
    """

    # Make a new layer
    layer = app.activeDocument.artLayers.add()
    layer.name = "Expansion Mask"
    layer.blendMode = ps.BlendMode.NormalBlend
    layer.visible = True
    layer.moveAfter(reference)

    # Fill selection with stroke color
    app.foregroundColor = color
    click3 = ps.ActionDescriptor()
    click3.putObject(cID("From"), cID("Pnt "), coords)
    click3.putInteger(cID("Tlrn"), 0)
    click3.putEnumerated(cID("Usng"), cID("FlCn"), cID("FrgC"))
    click3.putBoolean(cID("Cntg"), False)
    app.executeAction(cID("Fl  "), click3)

    # Clear Selection
    clear_selection()

    # Maximum filter to keep the antialiasing normal
    # layer.applyMaximum(1) # Do we need this?

    return layer


def insert_scryfall_scan(image_url):
    """
    Downloads the specified scryfall scan and inserts it into a new layer next to the active layer.
    Returns the new layer.
    """
    scryfall_scan = card_scan(image_url)
    if scryfall_scan: return paste_file_into_new_layer(scryfall_scan)
    return None
