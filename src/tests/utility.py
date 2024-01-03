"""
* General Testing Utility
* For contributors and plugin development.
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional, Union
from _ctypes import COMError
from xml.dom import minidom
import warnings
import logging
import json
import csv
import os

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    ElementPlacement,
    DialogModes,
    LayerKind)
from psd_tools.constants import Resource
from psd_tools import PSDImage
from psd_tools.psd.image_resources import ImageResource
import xml.etree.ElementTree as ET
os.environ['HEADLESS'] = "True"

# Local Imports
from src import APP, TEMPLATES
import src.helpers as psd
from src.enums.adobe import LayerContainer

# Photoshop infrastructure
cID, sID = APP.charIDtoTypeID, APP.stringIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

# Reference Box colors
ORANGE = [255, 172, 64]
TANG = [255, 97, 11]
RED = [192, 55, 38]
TAN = [245, 235, 210]
BLACK = [0, 0, 0]

"""
* Template Design Testing
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
        psd.getLayer(new, g).visible = True
        # Disable old color
        if old:
            psd.getLayer(old, g).visible = False


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
    group = psd.getLayerSet(name)
    mask_top = psd.getLayer(mask_top, group) if mask_top else None
    mask_bottom = psd.getLayer(mask_bottom, group) if mask_bottom else None
    ref = psd.getLayer("W", group)

    # Loop through each dual
    for dual in duals:
        # Change layer visibility
        top = psd.getLayer(dual[0], group).duplicate(ref, ElementPlacement.PlaceBefore)
        bottom = psd.getLayer(dual[1], group).duplicate(top, ElementPlacement.PlaceAfter)
        top.visible = True
        bottom.visible = True

        # Enable masks
        if mask_top:
            psd.copy_layer_mask(mask_top, top)
        if mask_bottom:
            psd.copy_layer_mask(mask_bottom, bottom)

        # Merge the layers and rename
        new_layer = psd.merge_layers([top, bottom])
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
        masks = [psd.getLayer("Mask")]
    elif isinstance(masks, ArtLayer):
        # Single layer provided
        masks = [masks]
    layers: list[ArtLayer] = []

    # Enable each layer color
    for i, color in enumerate(colors):
        layer = psd.getLayer(color, group)
        layer.visible = True

        # Position the new layer and add a mask to previous, if previous layer exists
        if layers:
            layer.move(layers[i - 1], ElementPlacement.PlaceAfter)
            psd.copy_layer_mask(masks[i - 1], layers[i - 1])

        # Add to the layer list
        layers.append(layer)


"""
* Action Descriptor Getters
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
        string_id: str = APP.typeIDToStringID(type_id)
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
    descriptor = APP.executeActionGet(reference)

    # Generate a dict of all descriptors
    actions = get_action_items(descriptor)

    # Dump the dict to a JSON file and return it
    with open(path, "w", encoding="utf-8-sig") as f:
        json.dump(actions, f)
    return actions


"""
* Dict Utilities
"""


def get_differing_dict(d1: dict, d2: dict):
    """Recursively generates a new dictionary comprised of differing values in two dicts.

    Args:
        d1: First dictionary.
        d2: Second dictionary.

    Returns:
        A dictionary comprised of differing key value pairs.
    """
    new_dict = {}
    for key, val in d1.items():
        if isinstance(val, dict):
            new_dict[key] = get_differing_dict(d1[key], d2[key])
        elif val != d2[key]:
            new_dict[key] = [val, d2[key]]
    return new_dict


"""
* Text Utilities
"""


def apply_single_line_composer(layer: ArtLayer) -> None:
    """Set the text composer of the layer to 'Single Line Composer'.

    Args:
        layer: TextLayer to apply the composer to.
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
    APP.Executeaction(sID("set"), desc1, NO_DIALOG)


def combine_text_items(from_layer: ArtLayer, to_layer: ArtLayer, sep: Optional[str] = " "):
    """Append the "from_layer" contents to the end of "to_layer" contents with optional separator.
        Preserves the complete style range formatting of both text contents.

    Args:
        from_layer: TextLayer to pull contents from.
        to_layer: TextLayer to append the contents of from_layer to.
        sep: Optional separator to place between them.
    """
    # Grab the text key of each layer
    from_tk = psd.get_text_key(from_layer)
    to_tk = psd.get_text_key(to_layer)

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
    psd.apply_text_key(to_layer, to_tk)


def reset_transform_factor(layer: ArtLayer) -> None:
    """Reset the transform xx and yy factors of a given layer.

    Args:
        layer: TextLayer to reset transform factors for.
    """
    key = psd.get_text_key(layer)
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
        psd.apply_text_key(layer, key)


"""
* XMP Utilities
"""


def xmp_remove_ancestors() -> None:
    """Remove DocumentAncestors property from XMP data."""

    # Check that a document is open
    if not APP.documents:
        print('No documents open!')
        return

    # XMP data
    APP.eval_javascript('''
        if (ExternalObject.AdobeXMPScript == undefined) {
          ExternalObject.AdobeXMPScript = new ExternalObject("lib:AdobeXMPScript");
        }
        var xmp = new XMPMeta( activeDocument.xmpMetadata.rawData);  
        xmp.deleteProperty(XMPConst.NS_PHOTOSHOP, "DocumentAncestors");
        APP.activeDocument.xmpMetadata.rawData = xmp.serialize();
    ''')


"""
* Vector Shape Utilities
"""


def create_color_shape(layer: ArtLayer, color: list) -> ArtLayer:
    layer_name = layer.name
    color = psd.get_color(color)
    docref = APP.activeDocument
    docsel = docref.selection
    docref.activeLayer = layer
    psd.select_layer_bounds(layer, docsel)

    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putClass(sID("path"))
    desc1.putReference(sID("target"), ref1)
    ref2.putProperty(sID("selectionClass"), sID("selection"))
    desc1.putReference(sID("from"), ref2)
    desc1.putUnitDouble(sID("tolerance"), sID("pixelsUnit"), 2.000000)
    APP.executeaction(sID("make"), desc1, NO_DIALOG)

    ref1 = ActionReference()
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    desc3 = ActionDescriptor()
    desc4 = ActionDescriptor()
    ref1.putClass(sID("contentLayer"))
    desc1.putReference(sID("target"), ref1)
    desc4.putDouble(sID("red"), color.rgb.red)
    desc4.putDouble(sID("green"), color.rgb.green)
    desc4.putDouble(sID("blue"), color.rgb.blue)
    desc3.putObject(sID("color"), sID("RGBColor"), desc4)
    desc2.putObject(sID("type"), sID("solidColorLayer"), desc3)
    desc1.putObject(sID("using"), sID("contentLayer"), desc2)
    APP.executeaction(sID("make"), desc1, NO_DIALOG)
    APP.activeDocument.activeLayer.name = layer_name

    # Check dims
    dims = psd.get_layer_dimensions(layer)
    dims = (dims['width'], dims['height'])
    new_dims = psd.get_layer_dimensions(docref.activeLayer)
    new_dims = (new_dims['width'], new_dims['height'])
    if not dims == new_dims:
        print("DIMS CHANGED:", layer_name)
        print("Before:", dims)
        print("After:", new_dims)

    layer.remove()
    docref.activeLayer.visible = False
    return docref.activeLayer


"""
* Font Utilities
"""


def log_all_template_fonts() -> dict:
    """Create a log of every font found for each PSD template."""

    # Ignore warnings from the psd_tools module
    logging.getLogger('psd_tools').setLevel(logging.FATAL)
    warnings.filterwarnings("ignore", module='psd_tools')

    def _get_fonts_from_psd(doc_path: str) -> set[str]:
        """
        Get a set of every font found in a given Photoshop document.
        @param doc_path: Path to the Photoshop document.
        @return: Set of font names found in the document.
        """
        file, fonts = PSDImage.open(doc_path), set()
        for layer in [n for n in file.descendants() if n.kind == 'type']:
            for style in layer.engine_dict['StyleRun']['RunArray']:
                font_key = style['StyleSheet']['StyleSheetData']['Font']
                fonts.add(layer.resource_dict['FontSet'][font_key]['Name'])
        return fonts

    # PSD documents to test
    docs = {
        t.path_psd: f"{t.name} ({t.plugin.name if t.plugin else 'BASE'})"
        for t in TEMPLATES
    }

    # Track progress
    doc_fonts, master, current, total = {}, {}, 1, len(docs)

    # Check each document
    logging.basicConfig(level=logging.INFO)
    for f, temp_name in docs.items():

        # Alert the user
        logging.info(f"READING FONTS — {temp_name} [{f.name}] [{current}/{total}]")
        current += 1

        # Open document, get fonts, close document
        doc_fonts[temp_name] = _get_fonts_from_psd(f)

    # Create master list
    for doc, font_list in doc_fonts.items():
        for f in font_list:
            master.setdefault(str(f), []).append(doc)

    # Log a sorted master list
    master: dict[str, list] = {k: v for k, v in sorted(master.items(), key=lambda item: len(item[1]))}
    with open(f'logs/FONTS.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2)
    return master


"""
* Project: Data Sets
* Exploring the use of data set variables for potential performance gains.
* Status: Likely not helpful
"""


def insert_data_set_variables(xml_data: str, from_path: str, to_path: Optional[str] = None) -> None:
    """Inserts data set variable XML into a PSD document.

    Args:
        xml_data: Data to insert into the document.
        from_path: Path of the PSD file.
        to_path: Path of new PSD file created, overwrites from_path if not provided.
    """
    # Decide the to_path
    to_path = to_path or from_path

    # Ignore warnings from the psd_tools module
    logging.getLogger('psd_tools').setLevel(logging.FATAL)
    warnings.filterwarnings("ignore", module='psd_tools')

    # Open the PSD file
    f = PSDImage.open(from_path)

    # Replace the image variables data
    new_resource = ImageResource(b'MeSa', key=Resource.IMAGE_READY_VARIABLES, name='', data=xml_data.encode(
        encoding='UTF-8', errors='strict'))
    f.image_resources[Resource.IMAGE_READY_VARIABLES] = new_resource

    # Save the PSD file
    f.save(to_path)


def print_data_set_variables(path: str) -> None:
    """Print data set variable XML data for a given document.

    Args:
        path: Path to a PSD document.
    """
    data = PSDImage.open(path).image_resources.get_data(
        Resource.IMAGE_READY_DATA_SETS)
    pretty_xml = minidom.parseString(data).toprettyxml()

    # Print without excess newlines
    print('\n'.join([line for line in pretty_xml.split('\n') if line.strip()]))


def format_data_set_variable_name(text: str) -> str:
    """Formats string as a data set variable name.

    Args:
        text: Text to format as a data set variable name.

    Returns:
        Properly formatted data set variable name.
    """
    return text.title().replace(
        ' ', '').replace(
        '-', '').replace(
        '&', '')


def get_data_set_variables(
    group: Optional[Union[LayerContainer]] = None,
    tree: Optional[str] = None
) -> list[dict[str, str]]:
    """Get data set variables for all ArtLayer and LayerSet objects in document or LayerSet.

    Args:
        group: LayerSet or Document, use activeDocument if not provided.
        tree: Tree to add to variable names, empty str if not provided.

    Returns:
        List of data set variable dicts.
    """

    # Establish current tree
    tree = f'{tree}{format_data_set_variable_name(group.name)}.' if tree and group else (
        f'{format_data_set_variable_name(group.name)}.' if group else '')

    # Establish group or top level document container
    group = group or APP.activeDocument
    layer_vars: list[dict[str, str]] = []

    # Add layer variables
    for n in group.artLayers:
        with suppress(Exception):
            if n.kind == LayerKind.TextLayer:
                layer_vars.append({
                    'varName': f'{tree}{format_data_set_variable_name(n.name)}.Text',
                    'trait': 'textcontent',
                    'docRef': f"id('{n.id}')"
                })
            elif 'Frame' in n.name:
                layer_vars.append({
                    'varName': f'{tree}{format_data_set_variable_name(n.name)}.Image',
                    'trait': 'fileref',
                    'placementMethod': 'fill',
                    'align': 'center',
                    'valign': 'middle',
                    'clip': 'false',
                    'docRef': f"id('{n.id}')"
                })
            layer_vars.append({
                'varName': f'{tree}{format_data_set_variable_name(n.name)}.Visible',
                'trait': 'visibility',
                'docRef': f"id('{n.id}')"
            })

    # Add layer group variables
    for n in group.layerSets:
        with suppress(Exception):
            layer_vars.append({
                'varName': f'{tree}{format_data_set_variable_name(n.name)}.Visible',
                'trait': 'visibility',
                'docRef': f"id('{n.id}')"
            })
            layer_vars.extend(get_data_set_variables(n, tree))
    return layer_vars


def get_data_set_variable_xml():
    """Generate data set variable XML for all layers in document."""

    # Create the root element
    root = ET.Element('variableSets', xmlns="http://ns.adobe.com/Variables/1.0/")

    # Create variableSet -> variables
    variableSet = ET.SubElement(root, 'variableSet')
    variableSet.set('locked', 'none')
    variableSet.set('varSetName', 'binding1')
    variables = ET.SubElement(variableSet, 'variables')

    # Add your variables, could do this programmatically for each layer
    for var in get_data_set_variables():
        variable = ET.SubElement(variables, 'variable')
        for k, v in var.items():
            variable.set(k, v)

    # Convert the XML to a string
    return (ET.tostring(root, encoding='utf8', method='xml', short_empty_elements=False)
            .decode().replace('<?xml version=\'1.0\' encoding=\'utf8\'?>\n', '', 1).replace('><', '>\n<')) + '\n'


def create_data_set_csv(data_set: dict[str, str], path: str) -> None:
    """Create a data set CSV that can be imported for Photoshop's data set variable system.

    Args:
        data_set: A dictionary where variable names are the keys and variable values are the values.
        path: Path to save the CSV to.
    """
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data_set.keys())
        writer.writerow(data_set.values())


def import_data_set(path: str) -> None:
    """Imports a data set into Photoshop's data set variable system.

    Args:
        path: Path to the data set CSV file where the first line are the variable names.
    """
    desc = ActionDescriptor()
    ref = ActionReference()
    ref.putClass(sID("dataSetClass"))
    desc.putReference(sID("null"), ref)
    desc.putPath(sID("using"), path)
    desc.putEnumerated(sID("encoding"), sID("dataSetEncoding"), sID("dataSetEncodingAuto"))
    desc.putBoolean(sID("eraseAll"), True)
    desc.putBoolean(sID("useFirstColumn"), True)
    APP.executeAction(sID("importDataSets"), desc, NO_DIALOG)


def apply_data_set(data_set_name: str) -> None:
    """Applies a data set from Photoshop's data set variable system.

    Args:
        data_set_name: Name of the data set.
    """
    desc = ActionDescriptor()
    setRef = ActionReference()
    setRef.putName(sID("dataSetClass"), data_set_name)
    desc.putReference(sID("null"), setRef)
    APP.executeAction(sID("apply"), desc, NO_DIALOG)
