"""
TESTING UTILITY
For contributors and plugin development.
"""
# Standard Library Imports
from typing import Optional, Union
from _ctypes import COMError
from os import path as osp
from pprint import pprint
import warnings
import logging
import json

# Use this to force a working directory if IDE doesn't support it
# os.chdir(os.path.abspath(os.path.join(os.getcwd(), '..', '..')))

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    ElementPlacement,
    ActionList,
    DialogModes
)

# Local Imports
from src.helpers.layers import getLayer, getLayerSet, merge_layers, select_layer_bounds
from src.helpers.text import get_text_scale_factor, get_text_key, apply_text_key
from src.helpers.document import points_to_pixels
from src.utils.fonts import get_fonts_from_psd
from src.utils.objects import PhotoshopHandler
from src.helpers.masks import copy_layer_mask
from src.helpers import get_layer_dimensions, get_color
from src.core import get_templates
from src.constants import con

# Photoshop infrastructure
app: PhotoshopHandler = con.app
cID = app.charIDtoTypeID
sID = app.stringIDtoTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

# Ignore warnings from the psd_tools module
logging.getLogger('psd_tools').setLevel(logging.FATAL)
warnings.filterwarnings("ignore", module='psd_tools')

# Reference Box colors
ORANGE = [255, 172, 64]
TANG = [255, 97, 11]
RED = [192, 55, 38]
TAN = [245, 235, 210]
BLACK = [0, 0, 0]


"""
TEMPLATE TESTING UTILITIES
"""


def test_new_color(new: str, old: Optional[str] = None, ignore: Optional[list[str]] = None):
    """
    Enables given color in all necessary groups. Optionally disable a color in those groups.
    @param new: Color to enable.
    @param old: Color to disable.
    @param ignore: Groups to ignore.
    @return:
    """
    if ignore is None:
        ignore = ["Pinlines & Textbox"]
    groups = ["Name & Title Boxes", "Legendary Crown", "Pinlines & Textbox", "Background", "PT Box"]
    for r in ignore:
        groups.remove(r)
    for g in groups:
        # Enable new color
        getLayer(new, g).visible = True
        # Disable old color
        if old:
            getLayer(old, g).visible = False


def make_duals(
    name: str = "Pinlines & Textbox",
    mask_top: Optional[str] = "MASK",
    mask_bottom: Optional[str] = None
):
    """
    Creates dual color layers for a given group.
    @param name: Name of the group.
    @param mask_top: Mask to place on top color.
    @param mask_bottom: Mask to place on bottom color.
    @return:
    """
    duals = ["WU", "WB", "RW", "GW", "UB", "UR", "GU", "BR", "BG", "RG"]
    group = getLayerSet(name)
    mask_top = getLayer(mask_top, group) if mask_top else None
    mask_bottom = getLayer(mask_bottom, group) if mask_bottom else None
    ref = getLayer("W", group)

    # Loop through each dual
    for dual in duals:
        # Change layer visibility
        top = getLayer(dual[0], group).duplicate(ref, ElementPlacement.PlaceBefore)
        bottom = getLayer(dual[1], group).duplicate(top, ElementPlacement.PlaceAfter)
        top.visible = True
        bottom.visible = True

        # Enable masks
        if mask_top:
            copy_layer_mask(mask_top, top)
        if mask_bottom:
            copy_layer_mask(mask_bottom, bottom)

        # Merge the layers and rename
        new_layer = merge_layers([top, bottom])
        new_layer.name = dual


def create_blended_layer(
    colors: Union[str, list[str]],
    group: LayerSet,
    masks: Union[None, ArtLayer, list[ArtLayer]] = None
):
    """
    Create a multicolor layer using a gradient mask.
    @param colors: Colors to use.
    @param group: Group to look for the color layers within.
    @param masks: Layers containing a gradient mask.
    """
    if not masks:
        # No mask provided
        masks = [getLayer("Mask")]
    elif isinstance(masks, ArtLayer):
        # Single layer provided
        masks = [masks]
    layers: list[ArtLayer] = []

    # Enable each layer color
    for i, color in enumerate(colors):
        layer = getLayer(color, group)
        layer.visible = True

        # Position the new layer and add a mask to previous, if previous layer exists
        if layers:
            layer.move(layers[i-1], ElementPlacement.PlaceAfter)
            copy_layer_mask(masks[i-1], layers[i-1])

        # Add to the layer list
        layers.append(layer)


"""
ACTION DESCRIPTOR/GETTER HELPERS
"""


def check_if_needed(key, keys_stored):
    """
    Check if double key has been locked, skip int keys if it is.
    @param key: This key.
    @param keys_stored: Keys already stored.
    @return: True if needed, False if skipped.
    """
    if 'double' in keys_stored:
        if key in ['largeInt', 'int']:
            return False
    return True


def try_all_getters(desc: ActionDescriptor, type_id) -> dict:
    """
    Try all possible getter functions for this Descriptor and Type ID.
    @param desc: Current descriptor object.
    @param type_id: TypeID to send the getter for.
    @return: All values returned from our getters.
    """
    values = {}
    getters = {
        'bool': 'getBoolean',
        'class': 'getClass',
        'enumType': 'getEnumerationType',
        'enumVal': 'getEnumerationValue',
        'list': 'getList',
        'objType': 'getObjectType',
        'objValue': 'getObjectValue',
        'path': 'getPath',
        'ref': 'getReference',
        'str': 'getString',
        'type': 'getType',
        'double': 'getUnitDoubleValue',
        'int': 'getInteger',
        'largeInt': 'getLargeInteger',
    }
    for k, func in getters.items():
        if not check_if_needed(k, values.keys()):
            # Skip this getter
            continue
        try:
            # Send the getter
            result = getattr(desc, func)(type_id)
            if k == 'list':
                # Getter may have returned an ActionList, grab the first object
                result = get_action_items(result.getObjectValue(0))
            values[k] = result
        except (COMError, NameError, KeyError):
            # Skip this getter
            pass
    return values


def get_action_items(desc) -> dict:
    """
    Try to pull objects and getters from each action key in a descriptor.
    @param desc: Current descriptor.
    @return: Recursive dict of all objects and getters matched to each key.
    """
    items = {}
    try:
        count = desc.count
    except COMError:
        count = 0
    for i in range(count):
        type_id: int = desc.getKey(i)
        string_id: str = app.typeIDToStringID(type_id)
        if desc.hasKey(type_id):
            try:
                result = get_action_items(desc.getObjectValue(type_id))
                if result:
                    items[string_id] = result
            except COMError:
                # Try every getter till one works
                try:
                    result = try_all_getters(desc, type_id)
                    items[string_id] = result
                except COMError:
                    pass
    return items


def dump_layer_action_descriptors(layer: ArtLayer, path: str) -> dict:
    """
    Combs through all available descriptor keys for a layer, dumps it to JSOn, and returns as a dict.
    @param layer: Layer to scan.
    @param path: Path to save the JSON dump.
    @return: Dict containing descriptors by key and value, in a branching tree.
    """
    # Get the layer descriptor
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = app.executeActionGet(reference)

    # Generate a dict of all descriptors
    actions = get_action_items(descriptor)

    # Dump the dict to a JSON file and return it
    with open(path, "w", encoding="utf-8-sig") as f:
        json.dump(actions, f)
    return actions


"""
TEXTBOX HELPERS
"""


def get_textbox_bounds_alternate(layer: ArtLayer) -> list[int]:
    """
    Get the bounds of a TextLayer's bounding box, slower than the original function.
    Will likely remove in the future, but has some potentially useful insights.
    @param layer: ArtLayer with "kind" of TextLayer.
    @return: List of left, top, right, bottom points of the box.
    """
    # Establish the textKey descriptor
    text_key = get_text_key(layer)

    # Establish the X and Y coordinates of the box
    x_scale, y_scale = get_text_scale_factor(text_key=text_key, axis=['xx', 'yy'])
    click_point = text_key.getObject(sID('textClickPoint'))
    x_pos = click_point.getUnitDoubleValue(sID('horizontal')) * x_scale
    y_pos = click_point.getUnitDoubleValue(sID('vertical')) * y_scale

    # Establish the bounds of the box
    shape = text_key.getList(sID('textShape')).getObjectValue(0)
    bounds = shape.getObjectValue(sID('bounds'))

    return [
        int(points_to_pixels((bounds.getUnitDoubleValue(sID('left')) * x_scale) + x_pos)),
        int(points_to_pixels((bounds.getUnitDoubleValue(sID('top')) * y_scale) + y_pos)),
        int(points_to_pixels((bounds.getUnitDoubleValue(sID('right')) * x_scale) + x_pos)),
        int(points_to_pixels((bounds.getUnitDoubleValue(sID('bottom')) * y_scale) + y_pos))
    ]


"""
DICT HELPERS
"""


def get_differing_dict(d1: dict, d2: dict):
    """
    Recursively generates a new dictionary comprised of differing values in two dicts.
    @param d1: First dictionary.
    @param d2: Second dictionary.
    @return: A dictionary comprised of differing key value pairs.
    """
    new_dict = {}
    for key, val in d1.items():
        if isinstance(val, dict):
            new_dict[key] = get_differing_dict(d1[key], d2[key])
        elif val != d2[key]:
            new_dict[key] = [val, d2[key]]
    return new_dict


"""
TEXT FUNCTIONS
"""


def apply_single_line_composer(layer: ArtLayer) -> None:
    """
    Set the text composer of the layer to 'Single Line Composer'.
    @param layer: TextLayer to apply the composer to.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    ref1.PutProperty(sID("property"), sID("paragraphStyle"))
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.PutReference(sID("target"), ref1)
    desc2.PutInteger(sID("textOverrideFeatureName"), 808464691)
    desc2.PutBoolean(sID("textEveryLineComposer"), False)
    desc1.PutObject(sID("to"), sID("paragraphStyle"), desc2)
    app.Executeaction(sID("set"), desc1, NO_DIALOG)


def combine_text_items(from_layer: ArtLayer, to_layer: ArtLayer, sep: Optional[str] = " "):
    """
    Append the "from_layer" contents to the end of "to_layer" contents with optional separator.
    Preserves the complete style range formatting of both text contents.
    @param from_layer: TextLayer to pull contents from.
    @param to_layer: TextLayer to append the contents of from_layer to.
    @param sep: Optional separator to place between them.
    """
    # Grab the text key of each layer
    from_tk = get_text_key(from_layer)
    to_tk = get_text_key(to_layer)

    # Grab the style range of each layer and establish our offset
    from_range = from_tk.getList(sID("textStyleRange"))
    to_range = to_tk.getList(sID("textStyleRange"))
    offset = len(sep) if sep else 0

    # For each item in the "from" style range, update the position and apply style to target
    for i in range(from_range.count):
        from_style = from_range.getObjectValue(i)
        id_from = from_style.getInteger(sID("from"))
        id_to = from_style.getInteger(sID("to"))
        from_style.putInteger(sID("from"), id_from + len(to_tk.getString(sID("textKey"))) + (offset if i != 0 else 0))
        from_style.putInteger(sID("to"), id_to + len(to_tk.getString(sID("textKey"))) + offset)
        to_range.putObject(sID("textStyleRange"), from_style)

    # Combine the contents and apply the updated style range
    contents = str(to_tk.getString(sID("textKey")) + sep + from_tk.getString(sID("textKey")))
    to_tk.putString(sID("textKey"), contents)
    to_tk.putList(sID("textStyleRange"), to_range)

    # Apply the updated text key to the target layer
    apply_text_key(to_layer, to_tk)


def reset_transform_factor(layer: ArtLayer) -> None:
    """
    Reset the transform xx and yy factors of a given layer.
    @param layer: TextLayer to reset transform factors for.
    """
    key = get_text_key(layer)
    if key.hasKey(sID('transform')):

        # Check the scale factor
        desc = key.getObjectValue(sID("transform"))
        xx = desc.getUnitDoubleValue(sID("xx")) if desc.hasKey(sID("xx")) else 1
        yy = desc.getUnitDoubleValue(sID("yy")) if desc.hasKey(sID("xx")) else 1

        # Fix the scale factor
        if xx == 1 and yy == 1:
            return
        if xx != 1:
            desc.putDouble(sID("xx"), 1)
        if yy != 1:
            desc.putDouble(sID("yy"), 1)

        # Update the scale factor
        key.putObject(sID("transform"), sID("transform"), desc)
        apply_text_key(layer, key)


"""
XMP UTILS
"""


def xmp_remove_ancestors() -> None:
    """Remove DocumentAncestors property from XMP data."""
    if not app.documents:
        # No documents open
        app.alert("There are no open documents. Please open a file to run this script.")
        return

    # XMP data
    app.eval_javascript('''
        if (ExternalObject.AdobeXMPScript == undefined) {
          ExternalObject.AdobeXMPScript = new ExternalObject("lib:AdobeXMPScript");
        }
        var xmp = new XMPMeta( activeDocument.xmpMetadata.rawData);  
        xmp.deleteProperty(XMPConst.NS_PHOTOSHOP, "DocumentAncestors");
        app.activeDocument.xmpMetadata.rawData = xmp.serialize();
    ''')


"""
VECTOR SHAPE UTILS
"""


def create_color_shape(layer: ArtLayer, color: list) -> ArtLayer:
    layer_name = layer.name
    color = get_color(color)
    app.activeDocument.activeLayer = layer
    select_layer_bounds()

    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putClass(sID("path"))
    desc1.putReference(sID("target"), ref1)
    ref2.putProperty(sID("selectionClass"), sID("selection"))
    desc1.putReference(sID("from"), ref2)
    desc1.putUnitDouble(sID("tolerance"), sID("pixelsUnit"), 2.000000)
    app.executeaction(sID("make"), desc1, NO_DIALOG)

    ref1 = ActionReference()
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    desc3 = ActionDescriptor()
    desc4 = ActionDescriptor()
    ref1.putClass(sID("contentLayer"))
    desc1.putReference(sID("target"),  ref1)
    desc4.putDouble(sID("red"), color.rgb.red)
    desc4.putDouble(sID("green"), color.rgb.green)
    desc4.putDouble(sID("blue"), color.rgb.blue)
    desc3.putObject(sID("color"), sID("RGBColor"),  desc4)
    desc2.putObject(sID("type"), sID("solidColorLayer"),  desc3)
    desc1.putObject(sID("using"), sID("contentLayer"),  desc2)
    app.executeaction(sID("make"), desc1,  NO_DIALOG)
    app.activeDocument.activeLayer.name = layer_name

    # Check dims
    dims = get_layer_dimensions(layer)
    dims = (dims['width'], dims['height'])
    new_dims = get_layer_dimensions(app.activeDocument.activeLayer)
    new_dims = (new_dims['width'], new_dims['height'])
    if not dims == new_dims:
        print("DIMS CHANGED:", layer_name)
        print("Before:", dims)
        print("After:", new_dims)

    layer.remove()
    app.activeDocument.activeLayer.visible = False
    return app.activeDocument.activeLayer


"""
FONT UTILS
"""


def log_all_template_fonts() -> dict:
    """Create a log of every font found for each PSD template."""
    docs = {
        temp['template_path']: f"{temp['plugin_name'] or 'BASE'} - {temp['layout']} - {temp['name']}"
        for card_type, templates in get_templates().items()
        for temp in templates if osp.exists(temp['template_path'])
    }

    # Track progress
    doc_fonts, master, current, total = {}, {}, 1, len(docs)

    # Check each document
    logging.basicConfig(level=logging.INFO)
    for psd_file, temp_name in docs.items():

        # Alert the user
        logging.info(f"READING FONTS — {temp_name} [{osp.basename(psd_file)}] [{current}/{total}]")
        current += 1

        # Open document, get fonts, close document
        doc_fonts[temp_name] = get_fonts_from_psd(psd_file)

    # Create master list
    for doc, fonts in doc_fonts.items():
        for f in fonts:
            master.setdefault(str(f), []).append(doc)

    # Log a sorted master list
    master: dict[str, list] = {k: v for k, v in sorted(master.items(), key=lambda item: len(item[1]))}
    with open(f'logs/FONTS.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2)
    return master
