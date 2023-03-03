"""
PHOTOSHOP HELPER FUNCTIONS
"""
from typing import Optional, Union
import os

import photoshop.api as ps
from photoshop.api import PhotoshopPythonAPIError, SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

from proxyshop.constants import con
from proxyshop.scryfall import card_scan
from proxyshop.settings import cfg

# QOL Definitions
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


def check_fonts(fonts: list) -> list:
    """
    Check if given fonts exist in users Photoshop Application.
    @return: Array of missing fonts or None
    """
    missing = []
    for f in fonts:
        try:
            assert isinstance(app.fonts.getByName(f).name, str)
        except AssertionError:
            missing.append(f)
    return missing


"""
UTILITY FUNCTIONS
"""


def getLayer(name: str, group: Optional[Union[str, list, tuple, LayerSet]] = None) -> Optional[ArtLayer]:
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
                if layer.name == name:
                    return layer
        elif isinstance(group, str):
            # LayerSet name given
            layer_set = app.activeDocument.layerSets.getByName(group)
        elif isinstance(group, (tuple, list)):
            # List of layerSet names/objects given
            for g in group:
                # First in list or not?
                if not layer_set:
                    if isinstance(g, str):
                        layer_set = app.activeDocument.layerSets.getByName(g)
                    else:
                        layer_set = g
                else:
                    layer_set = layer_set.layerSets.getByName(g)
        else:
            # Else, assume layerSet object given
            layer_set = group

        # Find our layer
        for layer in layer_set.layers:
            if layer.name == name:
                return layer
    except (PhotoshopPythonAPIError, AttributeError, TypeError):
        print(f'\nLayer "{name}" could not be found!')
    return


def getLayerSet(name: str, group: Optional[Union[str, list, tuple, LayerSet]] = None) -> Optional[LayerSet]:
    """
    Retrieve layer group object.
    @param name: Name of the group
    @param group: Parent group name or object.
    @return: Group object requested.
    """
    try:
        if group:
            layer_set = None
            if isinstance(group, str):
                # Set name given
                layer_set = app.activeDocument.layerSets.getByName(group)
                return layer_set.layerSets.getByName(name)
            elif isinstance(group, (tuple, list)):
                # Tuple or list of groups
                for g in group:
                    # First in the list
                    if not layer_set:
                        if isinstance(g, str):
                            layer_set = app.activeDocument.layerSets.getByName(g)
                        else:
                            layer_set = g
                    else:
                        layer_set = layer_set.layerSets.getByName(g)
                return layer_set.layerSets.getByName(name)
            # Set object given
            return group.layerSets.getByName(name)
        # Look through entire document
        return app.activeDocument.layerSets.getByName(name)
    except (PhotoshopPythonAPIError, AttributeError, TypeError):
        print(f'\nLayerSet "{name}" could not be found!')
    return


"""
COLOR FUNCTIONS
"""


def rgb_black() -> ps.SolidColor:
    """
    Creates a black SolidColor object.
    @return: SolidColor object
    """
    color = ps.SolidColor()
    color.rgb.red = 0
    color.rgb.green = 0
    color.rgb.blue = 0
    return color


def rgb_grey() -> ps.SolidColor:
    """
    Creates a grey SolidColor object.
    @return: SolidColor object.
    """
    color = ps.SolidColor()
    color.rgb.red = 170
    color.rgb.green = 170
    color.rgb.blue = 170
    return color


def rgb_white() -> ps.SolidColor:
    """
    Creates a white SolidColor object.
    @return: SolidColor object.
    """
    color = ps.SolidColor()
    color.rgb.red = 255
    color.rgb.green = 255
    color.rgb.blue = 255
    return color


def get_rgb(r: int, g: int, b: int) -> ps.SolidColor:
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


def get_cmyk(c: float, m: float, y: float, k: float) -> ps.SolidColor:
    """
    Creates a SolidColor object with the given CMYK values.
    @param c: Float from 0.0 to 100.0 for Cyan component.
    @param m: Float from 0.0 to 100.0 for Magenta component.
    @param y: Float from 0.0 to 100.0 for Yellow component.
    @param k: Float from 0.0 to 100.0 for blacK component.
    @return: SolidColor object.
    """
    color = ps.SolidColor()
    color.cmyk.cyan = c
    color.cmyk.magenta = m
    color.cmyk.yellow = y
    color.cmyk.black = k
    return color


def get_color(color: Union[list[int], str, dict]) -> ps.SolidColor:
    """
    Automatically get either cmyk or rgb color given a range of
    @param color: Array containing 3 (RGB) or 4 (CMYK) numbers between 0 and 255, or the name of a known color.
    @return: SolidColor object.
    """
    try:
        if isinstance(color, SolidColor):
            # Solid color given
            return color
        if isinstance(color, dict):
            # Color dictionary
            if 'r' in color.keys():
                # RGB
                return get_rgb(color['r'], color['g'], color['b'])
            elif 'c' in color.keys():
                # CMYK
                return get_cmyk(color['c'], color['m'], color['y'], color['k'])
        if isinstance(color, str):
            # Named color
            if color in con.colors:
                return get_color(con.colors[color])
        if isinstance(color, list):
            # List notation
            if len(color) == 3:
                # RGB
                return get_rgb(*color)
            elif len(color) == 4:
                # CMYK
                return get_cmyk(*color)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid color notation given: {color}")
    raise ValueError(f"Unrecognized color notation given: {color}")


def apply_rgb(action: ps.ActionDescriptor, color: ps.SolidColor) -> None:
    """
    Apply RGB SolidColor object to action descriptor.
    @param action: ActionDescriptor object.
    @param color: SolidColor object matching RGB model.
    """
    ad = ps.ActionDescriptor()
    ad.putDouble(sID("red"), color.rgb.red)
    ad.putDouble(sID("green"), color.rgb.green)
    ad.putDouble(sID("blue"), color.rgb.blue)
    action.putObject(sID("color"), sID("RGBColor"), ad)


def apply_cmyk(action: ps.ActionDescriptor, color: ps.SolidColor) -> None:
    """
    Apply CMYK SolidColor object to action descriptor.
    @param action: ActionDescriptor object.
    @param color: SolidColor object matching CMYK model.
    """
    ad = ps.ActionDescriptor()
    ad.putDouble(cID("Cyn "), color.cmyk.cyan)
    ad.putDouble(cID("Mgnt"), color.cmyk.magenta)
    ad.putDouble(cID("Ylw "), color.cmyk.yellow)
    ad.putDouble(cID("Blck"), color.cmyk.black)
    action.putObject(cID("Clr "), cID("CMYC"), ad)


def apply_color(action: ps.ActionDescriptor, color: ps.SolidColor) -> None:
    """
    Applies color to the specified action descriptor.
    @param action: ActionDescriptor object.
    @param color: CMYK or RGB SolidColor object.
    """
    if color.model == ps.ColorModel.RGBModel:
        apply_rgb(action, color)
    elif color.model == ps.ColorModel.CMYKModel:
        apply_cmyk(action, color)
    else:
        raise ValueError(f"Received unsupported color object: {color}")


"""
LAYER PROPERTIES
"""


def layer_bounds_no_effects(layer: Union[ArtLayer, LayerSet]) -> list[int, int, int, int]:
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


def get_dimensions_no_effects(layer: Union[ArtLayer, LayerSet]) -> dict[str: Union[float, int]]:
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


def get_layer_dimensions(layer: Union[ArtLayer, LayerSet]) -> dict[str: Union[float, int]]:
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


def get_text_layer_bounds(layer: ArtLayer, legacy: bool = False) -> dict[str: Union[int, float]]:
    """
    Return an object with the specified text layer's bounding box.
    @param layer: Layer to get the bounds of.
    @param legacy: Force old way for legacy text layers.
    @return: Array of the bounds of the given layer.
    """
    if int(app.version[0:2]) < 21 or legacy:
        layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
        layer_copy.rasterize(ps.RasterizeType.TextContents)
        layer_bounds = layer.bounds
        layer_copy.remove()
        return layer_bounds
    return layer.bounds


def get_text_layer_dimensions(layer, legacy: bool = False) -> dict[str: Union[int, float]]:
    """
    Return an object with the specified text layer's width and height, which is achieved by rasterising
    the layer and computing its width and height from its bounds.
    @param layer: Layer to get the dimensions of.
    @param legacy: Force old way for legacy text layers.
    @return: Dict containing height and width of the given layer.
    """
    if int(app.version[0:2]) < 21 or legacy:
        layer_copy = layer.duplicate(app.activeDocument, ps.ElementPlacement.PlaceInside)
        layer_copy.rasterize(ps.RasterizeType.TextContents)
        dimensions = get_layer_dimensions(layer_copy)
        layer_copy.remove()
        return dimensions
    return get_layer_dimensions(layer)


def get_text_layer_color(layer: ArtLayer) -> ps.SolidColor:
    """
    Occasionally, Photoshop has issues with retrieving the color of a text layer. This helper guards
    against errors and null values by defaulting to rgb_black() in the event of a problem.
    @param layer: Layer object that must be TextLayer
    @return: SolidColor object representing the color of the text item.
    """
    if isinstance(layer, ArtLayer) and layer.kind == ps.LayerKind.TextLayer:
        if hasattr(layer.textItem, 'color'):
            return layer.textItem.color
        print(f"Couldn't retrieve color of layer: {layer.name}")
    return rgb_black()


def get_text_scale_factor(layer: Optional[ArtLayer] = None, axis: str = "xx") -> float:
    """
    Get the scale factor of the document for changing text size.
    @param layer: The layer to make active and run the check on.
    @param axis: xx for horizontal, yy for vertical.
    @return: Float scale factor
    """
    # Change the active layer, if needed
    if layer:
        app.activeDocument.activeLayer = layer

    # Get the scale factor if not 1
    factor = 1
    ref = ps.ActionReference()
    ref.putEnumerated(cID("Lyr "), cID("Ordn"), cID("Trgt"))
    desc = app.executeActionGet(ref).getObjectValue(sID('textKey'))
    if desc.hasKey(sID('transform')):
        transform = desc.getObjectValue(sID('transform'))
        factor = transform.getUnitDoubleValue(sID(axis))
    return factor


def set_text_size(size: int, layer: Optional[ArtLayer] = None) -> None:
    """
    Manually assign font size to a layer using action descriptors.
    @param layer: Layer containing TextItem
    @param size: New size of layer
    """
    # Set the active layer if needed
    if layer:
        app.activeDocument.activeLayer = layer

    # Set the new size
    desc2361 = ps.ActionDescriptor()
    ref68 = ps.ActionReference()
    desc2362 = ps.ActionDescriptor()
    ref68.putProperty(sID("property"), sID("textStyle"))
    ref68.putEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc2361.putReference(sID("target"), ref68)
    desc2362.putInteger(sID("textOverrideFeatureName"), 808465458)
    desc2362.putInteger(sID("typeStyleOperationType"), 3)
    desc2362.PutUnitDouble(sID("size"), sID("pointsUnit"), size)
    desc2361.putObject(sID("to"), sID("textStyle"), desc2362)
    app.ExecuteAction(sID("set"), desc2361, NO_DIALOG)


def update_text_layer_size(
    layer: ArtLayer,
    change: float,
    factor: Optional[float] = None,
) -> None:
    """
    Sets the text item size while ensuring proper scaling.
    @param layer: Layer containing TextItem object.
    @param change: Difference in size (+/-).
    @param factor: Scale factor of text item.
    """
    # Set the active layer if needed
    if not factor:
        factor = get_text_scale_factor()

    # Increase the size
    set_text_size(size=(factor*layer.textItem.size)+change)


"""
LAYER ACTIONS
"""


def select_layer(
    layer: Union[ArtLayer, LayerSet],
    add: bool = False,
    make_visible: bool = False
):
    """
    Select a layer (make active) and optionally force it to be visible.
    @param layer: Layer to select.
    @param add: Add to existing selection.
    @param make_visible: Make the layer visible if not currently visible?
                         Doesn't work with adding layers to selection.
    """
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.PutIdentifier(sID("layer"), layer.id)
    desc1.PutReference(sID("target"), ref1)
    # Add to currently selected layers?
    if add:
        desc1.PutEnumerated(
            sID('selectionModifier'),
            sID('selectionModifierType'),
            sID('addToSelection')
        )
    # Force visible?
    desc1.PutBoolean(sID("makeVisible"), make_visible)
    app.executeAction(sID('select'), desc1, ps.DialogModes.DisplayNoDialogs)


def select_layers(layers: list[ArtLayer, LayerSet]):
    """
    Makes a list of layers active (selected) in the layer panel.
    @param layers: List of layers or layer sets.
    """
    # Select none, then add all layers to selection
    select_no_layers()
    for lay in layers:
        select_layer(lay, add=True)


def select_no_layers() -> None:
    """
    Deselect all layers.
    """
    selectNone = ps.ActionDescriptor()
    ref = ps.ActionReference()
    ref.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    selectNone.putReference(cID("null"), ref)
    app.executeAction(sID("selectNoLayers"), selectNone, NO_DIALOG)


def merge_layers(layers: list[ArtLayer] = None, name: Optional[str] = None) -> ArtLayer:
    """
    Merge a set of layers together.
    @param layers: Layers to be merged, uses active if not provided.
    @param name: Name of the newly created layer.
    @return: Returns the merged layer.
    """
    # Select none, then select entire list
    if layers:
        select_layers(layers)

    # Merge layers and return result
    app.ExecuteAction(sID("mergeLayersNew"), ps.ActionDescriptor(), NO_DIALOG)
    if name:
        app.activeDocument.activeLayer.name = name
    return app.activeDocument.activeLayer


def group_layers(
    name: Optional[str] = "New Group",
    layers: Optional[list[Union[ArtLayer, LayerSet]]] = None,
) -> LayerSet:
    """
    Groups the selected layers.
    @param name: Name of the new group.
    @param layers: Layers to group, will use active if not provided.
    @return: The newly created group.
    """
    # Select layers if given
    if layers:
        select_layers(layers)

    # Group the layers
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref2 = ps.ActionReference()
    ref1.putClass(sID("layerSection"))
    desc1.putReference(sID('null'), ref1)
    ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
    desc1.putReference(cID('From'), ref2)
    desc2 = ps.ActionDescriptor()
    desc2.putString(cID('Nm  '), name)
    desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
    desc1.putInteger(sID("layerSectionStart"), 0)
    desc1.putInteger(sID("layerSectionEnd"), 1)
    desc1.putString(cID('Nm  '), name)
    app.executeAction(cID('Mk  '), desc1, ps.DialogModes.DisplayNoDialogs)
    return app.activeDocument.activeLayer


def copy_layer_mask(
    layer_from: Union[ArtLayer, LayerSet],
    layer_to: Union[ArtLayer, LayerSet]
) -> None:
    """
    Copies layer mask from one layer to another.
    @param layer_from: Layer to copy from.
    @param layer_to: Layer to copy to.
    """
    desc255 = ps.ActionDescriptor()
    ref17 = ps.ActionReference()
    ref18 = ps.ActionReference()
    desc255.PutClass(sID("new"), sID("channel"))
    ref17.PutEnumerated(sID("channel"), sID("channel"), sID("mask"))
    ref17.PutIdentifier(sID("layer"), layer_to.id)
    desc255.PutReference(sID("at"), ref17)
    ref18.PutEnumerated(sID("channel"), sID("channel"), sID("mask"))
    ref18.PutIdentifier(sID("layer"), layer_from.id)
    desc255.PutReference(sID("using"), ref18)
    app.ExecuteAction(sID("make"), desc255, ps.DialogModes.DisplayNoDialogs)


def duplicate_group(name: str):
    """
    Duplicates current active layer set without renaming contents.
    @param name: Name to give the newly created layer set.
    @return: The newly created layer set object.
    """
    desc241 = ps.ActionDescriptor()
    ref4 = ps.ActionReference()
    ref4.PutEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    desc241.PutReference(sID("target"),  ref4)
    desc241.PutString(sID("name"), name)
    desc241.PutInteger(sID("version"),  5)
    app.ExecuteAction(sID("duplicate"), desc241, ps.DialogModes.DisplayNoDialogs)
    return app.activeDocument.activeLayer


def create_new_layer(layer_name: Optional[str] = None) -> ArtLayer:
    """
    Creates a new layer below the currently active layer. The layer will be visible.
    @param layer_name: Optional name for the new layer
    @return: Newly created layer object
    """
    if layer_name is None:
        layer_name = "Layer"

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


def smart_layer(layer: Union[ArtLayer, LayerSet] = None) -> ArtLayer:
    """
    Makes the active layer or layer set a smart layer.
    Optionally make a given layer active first.
    @param layer: [Optional] Layer to make active.
    @return: Newly created smart layer.
    """
    if layer:
        app.activeDocument.activeLayer = layer
    app.ExecuteAction(sID("newPlacedLayer"), None, ps.DialogModes.DisplayNoDialogs)
    return app.activeDocument.activeLayer


def lock_layer(layer: Union[ArtLayer, LayerSet], protection: str = "protectAll") -> None:
    """
    Locks the given layer.
    @param layer: The layer to lock.
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


def unlock_layer(layer: Union[ArtLayer, LayerSet]) -> None:
    """
    Unlocks the given layer.
    @param layer: The layer to unlock.
    """
    lock_layer(layer, "protectNone")


def select_layer_bounds(layer: ArtLayer = app.activeDocument.activeLayer):
    """
    Select the bounding box of a given layer.
    @param layer: Layer to select the pixels of. Uses active layer if not provided.
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


def select_layer_pixels(layer: Optional[ArtLayer]) -> None:
    """
    Select pixels of the active layer.
    @param layer: Layer to select. Uses active layer if not provided.
    """
    idChnl = cID("Chnl")
    des1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref2 = ps.ActionReference()
    ref1.putProperty(idChnl, cID("fsel"))
    des1.putReference(cID("null"), ref1)
    ref2.putEnumerated(idChnl, idChnl, cID("Trsp"))
    if layer:
        ref2.putIdentifier(sID("layer"), layer.id)
    des1.putReference(sID("to"), ref2)
    app.executeAction(sID("set"), des1, NO_DIALOG)


def align(
    align_type: str = "AdCH",
    layer: Optional[Union[ArtLayer, LayerSet]] = None,
    reference: Optional[Union[ArtLayer, LayerSet]] = None
) -> None:
    """
    Align the currently active layer to current selection, vertically or horizontally.
    Used with align_vertical() or align_horizontal().
    @param align_type: "AdCV" vertical, "AdCH" horizontal.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    # Optionally create a selection based on given reference
    if reference:
        select_layer_pixels(reference)

    # Optionally make a given layer the active layer
    if layer:
        app.activeDocument.activeLayer = layer

    # Align the current layer to selection
    desc = ps.ActionDescriptor()
    ref = ps.ActionReference()
    ref.putEnumerated(cID("Lyr "), cID("Ordn"), cID("Trgt"))
    desc.putReference(cID("null"), ref)
    desc.putEnumerated(cID("Usng"), cID("ADSt"), cID(align_type))
    app.executeAction(cID("Algn"), desc, NO_DIALOG)


def align_vertical(
    layer: Optional[Union[ArtLayer, LayerSet]] = None,
    reference: Optional[ArtLayer] = None
) -> None:
    """
    Align the currently active layer vertically with respect to the current selection.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    align("AdCV", layer, reference)


def align_horizontal(
        layer: Optional[Union[ArtLayer, LayerSet]] = None,
        reference: Optional[Union[ArtLayer, LayerSet]] = None
) -> None:
    """
    Align the currently active layer horizontally with respect to the current selection.
    @param layer: ArtLayer or LayerSet to align. Uses active layer if not provided.
    @param reference: Reference to align the layer within. Uses current selection if not provided.
    """
    align("AdCH", layer, reference)


def position_between_layers(
    layer: Union[ArtLayer, LayerSet],
    top_layer: Union[ArtLayer, LayerSet],
    bottom_layer: Union[ArtLayer, LayerSet]
) -> None:
    """
    Align layer vertically between two reference layers.
    @param layer: Layer to align vertically
    @param top_layer: Reference layer above the layer to be aligned.
    @param bottom_layer: Reference layer below the layer to be aligned.
    """
    app.activeDocument.selection.select([
        [0, top_layer.bounds[3]],
        [app.activeDocument.width, top_layer.bounds[3]],
        [app.activeDocument.width, bottom_layer.bounds[1]],
        [0, bottom_layer.bounds[1]]
    ])
    align_vertical(layer)
    clear_selection()


def spread_layers_over_reference(
    layers: list[ArtLayer],
    ref: ArtLayer,
    gap: Union[int, float],
    inside_gap: Union[int, float, None] = None
) -> None:
    """
    Spread layers apart across a reference layer.
    @param layers: List of ArtLayers or LayerSets.
    @param ref: Reference used as the maximum height boundary for all layers given.
    @param gap: Gap between the top of the reference and the first layer.
    @param inside_gap: Gap between each layer, uses gap instead of not provided.
    """
    # Position the top layer relative to the reference
    delta = (ref.bounds[1] + gap) - layers[0].bounds[1]
    layers[0].translate(0, delta)

    # Position the bottom layers relative to the top
    space_layers_apart(layers, inside_gap or gap)


def space_layers_apart(layers: list[Union[ArtLayer, LayerSet]], gap: Union[int, float]) -> None:
    """
    Position list of layers apart using a given gap.
    @param layers: List of ArtLayers or LayerSets.
    @param gap: Gap in pixels.
    """
    # Position each layer relative to the one above it
    for i in range((len(layers) - 1)):
        delta = (layers[i].bounds[3] + gap) - layers[i + 1].bounds[1]
        layers[i + 1].translate(0, delta)


def frame_layer(
    layer: ArtLayer,
    reference: ArtLayer,
    anchor: ps.AnchorPosition = ps.AnchorPosition.TopLeft,
    smallest: bool = False,
    align_h: bool = True,
    align_v: bool = True
) -> None:
    """
    Scale a layer equally to the bounds of a reference layer, then center the layer vertically and horizontally
    within those bounds.
    """
    # Get layer and reference dimensions
    layer_dim = get_layer_dimensions(layer)
    ref_dim = get_layer_dimensions(reference)

    # Determine how much to scale the layer by such that it fits into the reference layer's bounds
    action = min if smallest else max
    scale = 100 * action((ref_dim['width'] / layer_dim['width']), (ref_dim['height'] / layer_dim['height']))
    layer.resize(scale, scale, anchor)

    # Align the layer
    select_layer_bounds(reference)
    app.activeDocument.activeLayer = layer
    if align_h:
        align_horizontal()
    if align_v:
        align_vertical()
    clear_selection()


def set_active_layer_mask(visible: bool = True) -> None:
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


def enable_active_layer_mask() -> None:
    """
    Enables the active layer's layer mask.
    """
    set_active_layer_mask(True)


def disable_active_layer_mask() -> None:
    """
    Disables the active layer's layer mask.
    """
    set_active_layer_mask(False)


def set_layer_mask(layer: ArtLayer, visible: bool = True) -> None:
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


def enable_mask(layer: Union[ArtLayer, LayerSet]) -> None:
    """
    Enables a given layer's mask.
    @param layer: A layer object
    """
    set_layer_mask(layer, True)


def disable_mask(layer: Union[ArtLayer, LayerSet]) -> None:
    """
    Disables a given layer's mask.
    @param layer: A layer object
    """
    set_layer_mask(layer, False)


def leaf_layers() -> list[ArtLayer]:
    """
    Utility function to iterate over leaf layers in a document
    """
    to_visit = [node for node in app.activeDocument.layers]
    layers = []
    while to_visit:
        node = to_visit.pop()
        try:
            to_visit.extend([n for n in node.layers])
        except (NameError, AttributeError):
            # It's a leaf node, no sublayers
            layers.append(node)
    return layers


def apply_stroke(
    layer: ArtLayer,
    stroke_weight: int,
    stroke_color: ps.SolidColor = rgb_black()
) -> None:
    """
    Applies an outer stroke to the active layer with the specified weight and color.
    """
    desc608 = ps.ActionDescriptor()
    desc609 = ps.ActionDescriptor()
    desc610 = ps.ActionDescriptor()
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
    apply_color(desc610, stroke_color)
    desc609.putObject(cID("FrFX"), cID("FrFX"), desc610)
    desc608.putObject(cID("T   "), cID("Lefx"), desc609)
    app.executeAction(cID("setd"), desc608, NO_DIALOG)


def clear_layer_style(layer: ArtLayer) -> None:
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


def rasterize_layer_style(layer: ArtLayer) -> None:
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


def import_art(layer: ArtLayer, file: str) -> None:
    """
    Imports an art file into the active layer.
    @param layer: Layer to make active and receive image.
    @param file: Image file to import.
    """
    desc = ps.ActionDescriptor()
    app.activeDocument.activeLayer = layer
    desc.putPath(app.charIDToTypeID("null"), file)
    app.executeAction(app.charIDToTypeID("Plc "), desc)
    app.activeDocument.activeLayer.name = "Layer 1"


def import_svg(
    file: str,
    ref: Union[ArtLayer, LayerSet] = None,
    placement: Optional[ps.ElementPlacement] = None
) -> ArtLayer:
    """
    Imports an SVG image, then moves it if needed.
    @param file: SVG file to import.
    @param ref: Reference used to move layer.
    @param placement: Placement based on the reference.
    @return: New layer containing SVG.
    """
    # Import the art
    desc = ps.ActionDescriptor()
    desc.putPath(app.charIDToTypeID("null"), file)
    app.executeAction(app.charIDToTypeID("Plc "), desc)

    # Position the layer if needed
    if ref and placement:
        app.activeDocument.activeLayer.move(ref, placement)
    return app.activeDocument.activeLayer


def paste_file(
    layer: ArtLayer,
    file: str,
    action: any = None,
    action_args: dict = None
) -> None:
    """
    Pastes the given file into the specified layer.
    @param layer: Layer object to paste the image into.
    @param file: Filepath of the image to open.
    @param action: Optional action function to call on the image before importing it.
    @param action_args: Optional arguments to pass to the action function
    """
    # Select the correct layer, then load the file
    app.activeDocument.activeLayer = layer
    app.load(file)

    # Optionally run action on art before importing it
    if action:
        action(**action_args) if action_args else action()

    # Select the entire image, copy it, and close the file
    app.activeDocument.selection.selectAll()
    app.activeDocument.selection.copy()
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)

    # Paste the image into the specific layer
    app.activeDocument.paste()


def paste_file_into_new_layer(file: str) -> ArtLayer:
    """
    Wrapper for paste_file which creates a new layer for the file next to the active layer.
    Returns the new layer.
    """
    new_layer = create_new_layer("New Layer")
    paste_file(new_layer, file)
    return new_layer


"""
LAYER EFFECTS
"""


def add_color_to_gradient(
    action_list: ps.ActionList,
    color: ps.SolidColor,
    location: int,
    midpoint: int
) -> None:
    """

    @param action_list: Action list to add this color to.
    @param color: SolidColor object
    @param location: Location of the color along the track.
    @param midpoint: Percentage midpoint between this color and the next.
    @return:
    """
    action = ps.ActionDescriptor()
    apply_color(action, color)
    action.PutEnumerated(sID("type"), sID("colorStopType"), sID("userStop"))
    action.PutInteger(sID("location"), location)
    action.PutInteger(sID("midpoint"), midpoint)
    action_list.PutObject(sID("colorStop"), action)


def apply_fx(layer: Union[ArtLayer, LayerSet], effects: list[dict]) -> None:
    """
    Apply multiple layer effects to a layer.
    @param layer: Layer or Layer Set object.
    @param effects: List of effects to apply.
    """
    # Set up the main action
    app.activeDocument.activeLayer = layer
    main_action = ps.ActionDescriptor()
    fx_action = ps.ActionDescriptor()
    main_ref = ps.ActionReference()
    main_ref.PutProperty(sID("property"), sID("layerEffects"))
    main_ref.PutEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    main_action.PutReference(sID("target"), main_ref)

    # Add each action from fx dictionary
    for fx in effects:
        if fx['type'] == 'stroke':
            apply_fx_stroke(fx_action, **fx)
        elif fx['type'] == 'gradient':
            apply_fx_gradient(fx_action, **fx)
        elif fx['type'] == 'drop-shadow':
            apply_fx_drop_shadow(fx_action, **fx)

    # Apply all fx actions
    main_action.PutObject(sID("to"), sID("layerEffects"), fx_action)
    app.ExecuteAction(sID("set"), main_action, ps.DialogModes.DisplayNoDialogs)


def apply_fx_stroke(action: ps.ActionDescriptor, **kw) -> None:
    """
    Adds stroke effect to layer effects action.
    @param action: Pending layer effects action descriptor.
    @param kw: Optional keywords governing stroke behavior.
    """
    d = ps.ActionDescriptor()
    if kw.get("style") == 'in':
        stroke_style = 'insetFrame'
    elif kw.get("style") == 'center':
        stroke_style = 'centeredFrame'
    else:
        stroke_style = 'outsetFrame'
    d.PutEnumerated(sID("style"), sID("frameStyle"), sID(stroke_style))
    d.PutEnumerated(sID("paintType"), sID("frameFill"), sID("solidColor"))
    d.PutEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    d.PutUnitDouble(sID("opacity"), sID("percentUnit"), int(kw.get('opacity', 100)))
    d.PutUnitDouble(sID("size"), sID("pixelsUnit"), int(kw.get('weight', 6)))
    apply_color(d, get_color(kw.get('color', [0, 0, 0])))
    d.PutBoolean(sID("overprint"), False)
    action.PutObject(sID("frameFX"), sID("frameFX"), d)


def apply_fx_drop_shadow(action: ps.ActionDescriptor, **kw) -> None:
    """
    Adds drop shadow effect to layer effects action.
    @param action: Pending layer effects action descriptor.
    @param kw: Optional keywords governing drop shadow behavior.
    """
    d1 = ps.ActionDescriptor()
    d2 = ps.ActionDescriptor()
    d_color = ps.ActionDescriptor()
    d1.PutEnumerated(sID("mode"), sID("blendMode"), sID("multiply"))
    d_color.PutDouble(sID("red"), 0.000000)
    d_color.PutDouble(sID("grain"), 0.000000)
    d_color.PutDouble(sID("blue"), 0.000000)
    d1.PutObject(sID("color"), sID("RGBColor"), d_color)
    d1.PutUnitDouble(sID("opacity"), sID("percentUnit"), float(kw.get('opacity', 100.000000)))
    d1.PutBoolean(sID("useGlobalAngle"), False)
    d1.PutUnitDouble(sID("localLightingAngle"), sID("angleUnit"), float(kw.get('rotation', 45.000000)))
    d1.PutUnitDouble(sID("distance"), sID("pixelsUnit"), float(kw.get('distance', 10.000000)))
    d1.PutUnitDouble(sID("chokeMatte"), sID("pixelsUnit"), float(kw.get('spread', 0.000000)))
    d1.PutUnitDouble(sID("blur"), sID("pixelsUnit"), float(kw.get('size', 0.000000)))
    d1.PutUnitDouble(sID("noise"), sID("percentUnit"), 0.000000)
    d1.PutBoolean(sID("antiAlias"), False)
    d2.PutString(sID("name"), "Linear")
    d1.PutObject(sID("transferSpec"), sID("shapeCurveType"), d2)
    d1.PutBoolean(sID("layerConceals"), True)
    action.PutObject(sID("dropShadow"), sID("dropShadow"), d1)


def apply_fx_gradient(action: ps.ActionDescriptor, **kw) -> None:
    """
    Adds gradient effect to layer effects action.
    @param action: Pending layer effects action descriptor.
    @param kw: Optional keywords governing gradient behavior.
    """
    d1 = ps.ActionDescriptor()
    d2 = ps.ActionDescriptor()
    d3 = ps.ActionDescriptor()
    d4 = ps.ActionDescriptor()
    d5 = ps.ActionDescriptor()
    color_list = ps.ActionList()
    transparency_list = ps.ActionList()
    d1.PutEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    d1.PutUnitDouble(sID("opacity"), sID("percentUnit"),  int(kw.get('opacity', 100)))
    d2.PutEnumerated(sID("gradientForm"), sID("gradientForm"), sID("customStops"))
    d2.PutDouble(sID("interfaceIconFrameDimmed"),  int(kw.get('size', 4096)))
    for c in kw.get('colors', []):
        add_color_to_gradient(
            color_list,
            get_color(c.get('color', [0, 0, 0])),
            int(c.get('location', 0)),
            int(c.get('midpoint', 50))
        )
    d2.PutList(sID("colors"),  color_list)
    d3.PutUnitDouble(sID("opacity"), sID("percentUnit"),  100)
    d3.PutInteger(sID("location"),  0)
    d3.PutInteger(sID("midpoint"),  50)
    transparency_list.PutObject(sID("transferSpec"),  d3)
    d4.PutUnitDouble(sID("opacity"), sID("percentUnit"),  100)
    d4.PutInteger(sID("location"),  int(kw.get('size', 4096)))
    d4.PutInteger(sID("midpoint"),  50)
    transparency_list.PutObject(sID("transferSpec"),  d4)
    d2.PutList(sID("transparency"),  transparency_list)
    d1.PutObject(sID("gradient"), sID("gradientClassEvent"),  d2)
    d1.PutUnitDouble(sID("angle"), sID("angleUnit"), int(kw.get('rotation', 45)))
    d1.PutEnumerated(sID("type"), sID("gradientType"), sID("linear"))
    d1.PutBoolean(sID("reverse"), False)
    d1.PutBoolean(sID("dither"), False)
    d1.PutEnumerated(cID("gs99"), sID("gradientInterpolationMethodType"), sID("classic"))
    d1.PutBoolean(sID("align"), True)
    d1.PutUnitDouble(sID("scale"), sID("percentUnit"), int(kw.get('scale', 70)))
    d5.PutUnitDouble(sID("horizontal"), sID("percentUnit"),  0)
    d5.PutUnitDouble(sID("vertical"), sID("percentUnit"),  0)
    d1.PutObject(sID("offset"), sID("paint"),  d5)
    action.PutObject(sID("gradientFill"), sID("gradientFill"),  d1)


def apply_fx_fill(action: ps.ActionDescriptor, **kw) -> None:
    """
    Adds a solid color overlay to layer effects action.
    @param action: Pending layer effects action descriptor.
    @param kw: Optional keywords governing overlay behavior.
    """
    pass


"""
TEXT LAYER ACTIONS
"""


def replace_text(layer: ArtLayer, find: str, replace: str) -> None:
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
    # if cfg.targeted_replace: app.bringToFront()
    desc32.putBoolean(
        sID("checkAll"),  # Targeted replace doesn't work on old PS versions
        False if cfg.targeted_replace and int(app.version[0:2]) > 22 else True
    )
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


def clear_selection() -> None:
    """
    Clear the current selection.
    """
    app.activeDocument.selection.select([])


def trim_transparent_pixels() -> None:
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


def run_action(action_set: str, action: str) -> None:
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


def save_document_png(file_name: str, directory='out') -> None:
    """
    Save the current document to /out/ as a PNG.
    @param file_name: Name of the output file.
    @param directory: Directory to save the file.
    """
    png_options = ps.PNGSaveOptions()
    png_options.compression = 3
    app.activeDocument.saveAs(
        file_path=os.path.join(con.cwd, f"{directory}/{file_name}.png"),
        options=png_options, asCopy=True
    )


def save_document_jpeg(file_name: str, directory='out') -> None:
    """
    Save the current document to /out/ as a JPEG.
    @param file_name: Name of the output file.
    @param directory: Directory to save the file.
    """
    jpeg_options = ps.JPEGSaveOptions(quality=12)
    jpeg_options.scans = 3
    app.activeDocument.saveAs(
        file_path=os.path.join(con.cwd, f"{directory}/{file_name}.jpg"),
        options=jpeg_options, asCopy=True
    )


def save_document_psd(file_name: str, directory='out') -> None:
    """
    Save the current document to /out/ as PSD.
    @param file_name: Name of the output file.
    @param directory: Directory to save the file.
    """
    app.activeDocument.saveAs(
        file_path=os.path.join(con.cwd, f"{directory}/{file_name}.psd"),
        options=ps.PhotoshopSaveOptions(),
        asCopy=True
    )


def close_document() -> None:
    """
    Close the document
    """
    app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)


def open_svg(path: str, max_width: int = 500, dpi: int = 1200) -> None:
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


def reset_document(filename: str) -> None:
    """
    Reset all changes to the current document.
    @param filename: Document file name
    """
    if '/' in filename:
        filename = filename.split('/')[-1]
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


def content_fill_empty_area(layer: Optional[ArtLayer] = None) -> None:
    """
    Helper function intended to streamline the workflow of making extended art cards.
    This script rasterizes the active layer and fills all empty pixels in the canvas
    on the layer using content-aware fill.
    """
    # Change active layer
    current = app.activeDocument.activeLayer
    if layer:
        app.activeDocument.activeLayer = layer

    # Select pixels of active layer
    desc307 = ps.ActionDescriptor()
    ref257 = ps.ActionReference()
    ref257.putProperty(cID("Chnl"), cID("fsel"))
    desc307.putReference(cID("null"), ref257)
    ref258 = ps.ActionReference()
    idChnl = cID("Chnl")
    ref258.putEnumerated(idChnl, idChnl, cID("Trsp"))
    if layer:
        ref258.putIdentifier(sID("layer"), layer.id)
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


def apply_vibrant_saturation(vibrancy: int, saturation: int) -> None:
    """
    Experimental scoot action to add vibrancy and saturation.
    @param vibrancy: Vibrancy level integer
    @param saturation: Saturation level integer
    """
    # dialogMode (Have dialog popup?)
    idvibrance = sID("vibrance")
    desc232 = ps.ActionDescriptor()
    desc232.putInteger(idvibrance, vibrancy)
    desc232.putInteger(cID("Strt"), saturation)
    app.executeAction(idvibrance, desc232, NO_DIALOG)


def repair_edges(edge: int = 6) -> None:
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


def insert_scryfall_scan(image_url: str) -> Optional[ArtLayer]:
    """
    Downloads the specified scryfall scan and inserts it into a new layer next to the active layer.
    Returns the new layer.
    """
    scryfall_scan = card_scan(image_url)
    if scryfall_scan:
        return paste_file_into_new_layer(scryfall_scan)
    return


"""
EXPANSION SYMBOL
"""


def fill_expansion_symbol(reference: ArtLayer, color: ps.SolidColor = rgb_black()) -> ArtLayer:
    """
    Give the symbol a background for open space symbols (i.e. M10)
    @param reference: Reference layer to put the new fill layer underneath
    @param color: Color of the background fill
    """
    # Magic Wand contiguous outside symbol
    coords = ps.ActionDescriptor()
    coords.putUnitDouble(cID("Hrzn"), cID("#Pxl"), 5)
    coords.putUnitDouble(cID("Vrtc"), cID("#Pxl"), 5)
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

    # Make a new layer
    layer = app.activeDocument.artLayers.add()
    layer.name = "Expansion Mask"
    layer.blendMode = ps.BlendMode.NormalBlend
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
    return layer


def process_expansion_symbol_info(symbol: Union[str, list], rarity: str) -> Optional[tuple[str, list]]:
    """
    Takes in set code and returns information needed to build the expansion symbol.
    @param symbol: Symbol chosen by layout object.
    @param rarity: Rarity of the symbol.
    @return: List of dicts containing information about this symbol.
    """
    # Ref not defined unless explicit
    ref = None
    symbols = []
    if isinstance(symbol, str):
        # Symbol as a string only
        symbol = {
            'char': symbol,
            'scale': 1,
            'stroke': format_symbol_fx_stroke([
                # Stroke outline action
                'white' if rarity == con.rarity_common else 'black',
                cfg.symbol_stroke
            ])
        }
        if cfg.fill_symbol:
            # Background fill action
            symbol['fill'] = get_color(
                'white' if rarity == con.rarity_common else 'black'
            )
        if rarity != con.rarity_common:
            # Gradient overlay action
            symbol['rarity'] = True
            symbol['gradient'] = format_symbol_fx_gradient(rarity)
        symbols.append(symbol)
    elif isinstance(symbol, dict):
        # Single layered symbol
        symbols.append(format_expansion_symbol_dict(symbol, rarity))
    elif isinstance(symbol, list):
        # Multilayered symbol
        for sym in symbol:
            symbols.append(format_expansion_symbol_dict(sym, rarity))
            if sym.get('reference', False):
                ref = sym['char']
    else:
        # Unsupported data type, return default symbol
        return process_expansion_symbol_info(con.set_symbols['MTG'], rarity)
    return ref or symbols[0]['char'], symbols


def format_expansion_symbol_dict(sym: dict, rarity: str) -> dict:
    # Required attributes
    symbol: dict = {
        'char': sym['char'],
        'rarity': sym.get('rarity', True)
    }

    # Scale attribute [Optional]
    if any(isinstance(sym.get('scale'), t) for t in [int, float]):
        symbol['scale'] = sym['scale']

    # Drop shadow attribute [Optional]
    if sym.get('drop-shadow'):
        symbol['drop-shadow'] = format_symbol_fx_drop_shadow(sym.get('drop-shadow'))

    # Uncommon only attributes
    if rarity != con.rarity_common:
        if 'stroke' not in sym or sym['stroke']:
            # Stroke definition - Optional, must be explicitly disabled
            symbol['stroke'] = format_symbol_fx_stroke(
                sym.get('stroke', ['black', cfg.symbol_stroke])
            )
        if sym.get('color'):
            # Color definition - Optional
            symbol['color'] = get_color(sym['color'])
        if sym.get('fill'):
            # Background fill definition - Optional
            symbol['fill'] = format_symbol_fx_fill(sym['fill'], rarity) if sym['fill'] != 'rarity' else 'rarity'
        if sym.get('rarity', True) or sym.get('fill') == 'rarity':
            # Generate gradient FX by default
            gradient = format_symbol_fx_gradient(
                rarity,
                sym.get('gradient')
            )
            if gradient:
                # Add only if its needed
                symbol['gradient'] = gradient
                symbol['rarity'] = sym.get('rarity', True)
        return symbol

    # Common only attributes
    if 'common-stroke' not in sym or sym['common-stroke']:
        # Stroke definition - Optional, must be explicitly disabled
        symbol['stroke'] = format_symbol_fx_stroke(
            sym.get('common-stroke', ['white', cfg.symbol_stroke])
        )
    if sym.get('common-color'):
        # Color definition [Optional]
        symbol['color'] = get_color(sym.get('common-color', 'black'))
    if sym.get('common-fill'):
        # Background fill definition [Optional]
        symbol['fill'] = get_color(sym.get('common-fill', 'white'))
    return symbol


def format_symbol_fx_fill(fx: Union[str, list, dict], rarity: str) -> SolidColor:
    """
    Format background fill effect info.
    @param fx: Background fill details.
    @param rarity: Card rarity.
    @return: Formatted background fill details.
    """
    if isinstance(fx, dict):
        if rarity[0] in fx:
            return get_color(fx[rarity[0]])
        return get_color(list(fx.values())[0])
    return get_color(fx)


def format_symbol_fx_stroke(fx: Union[bool, list, dict]) -> Optional[dict]:
    """
    Produces a correct dictionary for layer effects type: stroke.
    @param fx: The stroke definition we were given by the user.
    @return: Formatted stroke definition for this effect.
    """
    if isinstance(fx, dict):
        return {
            'type': 'stroke',
            'weight': fx.get('weight') or fx.get('size', cfg.symbol_stroke),
            'color': get_color(fx.get('color', [0, 0, 0])),
            'opacity': fx.get('opacity', 100),
            'style': fx.get('style', 'out')
        }
    if isinstance(fx, list):
        return {
            'type': 'stroke',
            'weight': fx[1],
            'color': get_color(con.colors[fx[0]]),
            'opacity': 100,
            'style': 'out'
        }
    return


def format_symbol_fx_drop_shadow(fx: Union[bool, dict]) -> Optional[dict]:
    """
    Produces a correct dictionary for layer effects type: drop-shadow.
    @param fx: The drop shadow definition we were given by the user.
    @return: Formatted drop shadow definition for this effect.
    """
    if isinstance(fx, bool) and fx:
        return {
            'type': 'drop-shadow',
            'opacity': 100,
            'rotation': 45,
            'distance': 10,
            'spread': 0,
            'size': 0,
        }
    if isinstance(fx, dict):
        return {
            'type': 'drop-shadow',
            'opacity': fx.get('opacity', 100),
            'rotation': fx.get('rotation', 45),
            'distance': fx.get('distance', 10),
            'spread': fx.get('spread', 0),
            'size': fx.get('size', 0),
        }
    return


def format_symbol_fx_gradient(rarity: str, gradient: Optional[dict] = None) -> Optional[dict]:
    """
    Produces a correct dictionary for layer effects type: gradient overlay.
    @param rarity: The rarity of this symbol.
    @param gradient: Gradient map to overwrite default gradient map.
    @return: Formatted gradient definition for this effect.
    """
    # Load and update gradient map if needed
    color_map = con.rarity_gradients.copy()
    gradient = {} if not isinstance(gradient, dict) else gradient
    rarities = gradient.get('colors')
    if isinstance(rarities, dict):
        # Validate gradient definitions
        for key, colors in rarities.items():
            if not isinstance(colors, list) or not colors:
                # None value is acceptable
                if not colors:
                    rarities[key] = None
                    continue
                # Must be a list
                print('Encountered unsupported gradient format for this symbol!')
                rarities[key] = color_map.get(key, color_map['u'])
                continue
            for i, color in enumerate(colors):
                if not isinstance(color, dict) or not color:
                    # Must be dict
                    print('Encountered unsupported gradient format for this symbol!')
                    rarities[key] = color_map.get(key, color_map['u'])
                    continue
                # Support some colors by name
                color['color'] = get_color(color.get('color'))
                color.setdefault('location', 2048)
                color.setdefault('midpoint',  50)
                # Validate types
                if (
                    not isinstance(color['color'], SolidColor)
                    or not isinstance(color['location'], int)
                    or not isinstance(color['midpoint'], int)
                ):
                    # Invalid data types given
                    print('Encountered unsupported gradient format for this symbol!')
                    rarities[key] = color_map.get(key, color_map['u'])
                    continue
        color_map.update(rarities)

    # Return None if no colors given
    gradient_colors = color_map[rarity[0]]
    if not gradient_colors:
        return

    # Process the new gradient map colors into SolidColor objects
    for color in gradient_colors:
        color['color'] = get_color(color['color'])

    # Create new definition
    return {
        'type': 'gradient',
        'size': gradient.get('size', 4096),
        'scale': gradient.get('scale', 70),
        'rotation': gradient.get('rotation', 45),
        'colors': gradient_colors
    }
