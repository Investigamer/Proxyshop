"""
* Miscellaneous utils that are awaiting refinement/relocation.
"""

import csv
import json
import logging
import warnings
import xml.etree.ElementTree as ET
from _ctypes import COMError
from collections.abc import Iterable, Sequence
from contextlib import suppress
from os import PathLike
from typing import Any
from xml.dom import minidom

from photoshop.api import ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import DialogModes, ElementPlacement, LayerKind
from psd_tools import PSDImage
from psd_tools.constants import Resource
from psd_tools.psd.image_resources import ImageResource

import src.helpers as psd
from src import APP
from src._loader import AppTemplate
from src.schema.colors import ColorObject

_logger = logging.getLogger(__name__)

# Reference Box colors
ORANGE = [255, 172, 64]
TANG = [255, 97, 11]
RED = [192, 55, 38]
TAN = [245, 235, 210]
BLACK = [0, 0, 0]

"""
* Template Design Testing
"""


def test_new_color(
    new: str, old: str | None = None, ignore: list[str] | None = None
) -> None:
    """Enables given color in all necessary groups. Optionally disable a color in those groups.

    Args:
        new: Color to enable.
        old: Color to disable.
        ignore: Groups to ignore.
    """
    if ignore is None:
        ignore = ["Pinlines & Textbox"]
    groups = [
        "Name & Title Boxes",
        "Legendary Crown",
        "Pinlines & Textbox",
        "Background",
        "PT Box",
    ]
    for r in ignore:
        groups.remove(r)
    for g in groups:
        # Enable new color
        if new_layer := psd.getLayer(new, g):
            new_layer.visible = True
        # Disable old color
        if old and (old_layer := psd.getLayer(old, g)):
            old_layer.visible = False


def make_duals(
    name: str = "Pinlines & Textbox",
    mask_top: ArtLayer | None = None,
    mask_bottom: ArtLayer | None = None,
):
    """Creates dual color layers for a given group.

    Args:
        name: Name of the group.
        mask_top: Mask to place on top color.
        mask_bottom: Mask to place on bottom color.
    """
    duals = ["WU", "WB", "RW", "GW", "UB", "UR", "GU", "BR", "BG", "RG"]
    group = psd.getLayerSet(name)
    ref = psd.getLayer("W", group)

    # Loop through each dual
    for dual in duals:
        if (top := psd.getLayer(dual[0], group)) and (
            bottom := psd.getLayer(dual[1], group)
        ):
            top = top.duplicate(ref, ElementPlacement.PlaceBefore)
            bottom = bottom.duplicate(top, ElementPlacement.PlaceAfter)

            # Change layer visibility
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
    colors: str | list[str],
    group: LayerSet,
    masks: Sequence[ArtLayer] | None = None,
) -> None:
    """Create a multicolor layer using a gradient mask.

    Args:
        colors: Colors to use.
        group: Group to look for the color layers within.
        masks: Layers containing a gradient mask.
    """
    layers: list[ArtLayer] = []

    # Enable each layer color
    for i, color in enumerate(colors):
        if layer := psd.getLayer(color, group):
            layer.visible = True

            # Position the new layer and add a mask to previous, if previous layer exists
            if layers:
                prev_idx = i - 1
                layer.move(layers[prev_idx], ElementPlacement.PlaceAfter)
                if masks and prev_idx < len(masks):
                    psd.copy_layer_mask(masks[i - 1], layers[i - 1])

            # Add to the layer list
            layers.append(layer)


"""
* Action Descriptor Getters
"""


def check_if_needed(key: str, keys_stored: Iterable[str]):
    """Check if double key has been locked, skip int keys if it is.

    Args:
        key: This key.
        keys_stored: Keys already stored.

    Returns:
        True if needed, False if skipped.
    """
    return not ("double" in keys_stored and key in ["largeInt", "int"])


def try_all_getters(desc: ActionDescriptor, type_id: int) -> dict[str, Any]:
    """Try all possible getter functions for this Descriptor and Type ID.

    Args:
        desc: Current descriptor object.
        type_id: TypeID to send the getter for.

    Returns:
        All values returned from our getters.
    """
    values: dict[str, Any] = {}
    getters = {
        "bool": "getBoolean",
        "class": "getClass",
        "enumType": "getEnumerationType",
        "enumVal": "getEnumerationValue",
        "list": "getList",
        "objType": "getObjectType",
        "objValue": "getObjectValue",
        "path": "getPath",
        "ref": "getReference",
        "str": "getString",
        "type": "getType",
        "double": "getUnitDoubleValue",
        "int": "getInteger",
        "largeInt": "getLargeInteger",
    }
    for k, func in getters.items():
        if not check_if_needed(k, values.keys()):
            # Skip this getter
            continue
        try:
            # Send the getter
            result = getattr(desc, func)(type_id)
            if k == "list":
                # Getter may have returned an ActionList, grab the first object
                result = get_action_items(result.getObjectValue(0))
            values[k] = result
        except COMError, NameError, KeyError:
            # Skip this getter
            pass
    return values


def get_action_items(desc: ActionDescriptor) -> dict[str, Any]:
    """Try to pull objects and getters from each action key in a descriptor.

    Args:
        desc: Current descriptor.

    Returns:
        Recursive dict of all objects and getters matched to each key.
    """
    items: dict[str, Any] = {}
    try:
        count = desc.count
    except COMError:
        count = 0
    for i in range(count):
        type_id: int = desc.getKey(i)
        string_id: str = APP.instance.typeIDToStringID(type_id)
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


def dump_layer_action_descriptors(layer: ArtLayer, path: str) -> dict[str, Any]:
    """Combs through all available descriptor keys for a layer, dumps it to JSOn, and returns as a dict.

    Args:
        layer: Layer to scan.
        path: Path to save the JSON dump.

    Returns:
        Dict containing descriptors by key and value, in a branching tree.
    """
    # Get the layer descriptor
    reference = ActionReference()
    reference.putIdentifier(APP.instance.sID("layer"), layer.id)
    descriptor = APP.instance.executeActionGet(reference)

    # Generate a dict of all descriptors
    actions = get_action_items(descriptor)

    # Dump the dict to a JSON file and return it
    with open(path, "w", encoding="utf-8-sig") as f:
        json.dump(actions, f)
    return actions


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
    ref1.putProperty(APP.instance.sID("property"), APP.instance.sID("paragraphStyle"))
    ref1.putIdentifier(APP.instance.sID("textLayer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc2.putInteger(APP.instance.sID("textOverrideFeatureName"), 808464691)
    desc2.putBoolean(APP.instance.sID("textEveryLineComposer"), False)
    desc1.putObject(APP.instance.sID("to"), APP.instance.sID("paragraphStyle"), desc2)
    APP.instance.executeAction(
        APP.instance.sID("set"), desc1, DialogModes.DisplayNoDialogs
    )


def combine_text_items(from_layer: ArtLayer, to_layer: ArtLayer, sep: str = " "):
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
    from_range = from_tk.getList(APP.instance.sID("textStyleRange"))
    to_range = to_tk.getList(APP.instance.sID("textStyleRange"))
    offset = len(sep) if sep else 0

    # For each item in the "from" style range, update the position and apply style to target
    for i in range(from_range.count):
        from_style = from_range.getObjectValue(i)
        id_from = from_style.getInteger(APP.instance.sID("from"))
        id_to = from_style.getInteger(APP.instance.sID("to"))
        from_style.putInteger(
            APP.instance.sID("from"),
            id_from
            + len(to_tk.getString(APP.instance.sID("textKey")))
            + (offset if i != 0 else 0),
        )
        from_style.putInteger(
            APP.instance.sID("to"),
            id_to + len(to_tk.getString(APP.instance.sID("textKey"))) + offset,
        )
        to_range.putObject(APP.instance.sID("textStyleRange"), from_style)

    # Combine the contents and apply the updated style range
    contents = str(
        to_tk.getString(APP.instance.sID("textKey"))
        + sep
        + from_tk.getString(APP.instance.sID("textKey"))
    )
    to_tk.putString(APP.instance.sID("textKey"), contents)
    to_tk.putList(APP.instance.sID("textStyleRange"), to_range)

    # Apply the updated text key to the target layer
    psd.apply_text_key(to_layer, to_tk)


def reset_transform_factor(layer: ArtLayer) -> None:
    """Reset the transform xx and yy factors of a given layer.

    Args:
        layer: TextLayer to reset transform factors for.
    """
    key = psd.get_text_key(layer)
    if key.hasKey(APP.instance.sID("transform")):
        # Check the scale factor
        desc = key.getObjectValue(APP.instance.sID("transform"))
        xx = (
            desc.getUnitDoubleValue(APP.instance.sID("xx"))
            if desc.hasKey(APP.instance.sID("xx"))
            else 1
        )
        yy = (
            desc.getUnitDoubleValue(APP.instance.sID("yy"))
            if desc.hasKey(APP.instance.sID("xx"))
            else 1
        )

        # Fix the scale factor
        if xx == 1 and yy == 1:
            return
        if xx != 1:
            desc.putDouble(APP.instance.sID("xx"), 1)
        if yy != 1:
            desc.putDouble(APP.instance.sID("yy"), 1)

        # Update the scale factor
        key.putObject(
            APP.instance.sID("transform"), APP.instance.sID("transform"), desc
        )
        psd.apply_text_key(layer, key)


"""
* XMP Utilities
"""


def xmp_remove_ancestors() -> None:
    """Remove DocumentAncestors property from XMP data."""

    # Check that a document is open
    if not APP.instance.documents:
        print("No documents open!")
        return

    # XMP data
    APP.instance.eval_javascript("""
        if (ExternalObject.AdobeXMPScript == undefined) {
          ExternalObject.AdobeXMPScript = new ExternalObject("lib:AdobeXMPScript");
        }
        var xmp = new XMPMeta( activeDocument.xmpMetadata.rawData);  
        xmp.deleteProperty(XMPConst.NS_PHOTOSHOP, "DocumentAncestors");
        APP.instance.activeDocument.xmpMetadata.rawData = xmp.serialize();
    """)


"""
* Vector Shape Utilities
"""


def create_color_shape(layer: ArtLayer, color: ColorObject) -> ArtLayer:
    layer_name = layer.name
    color = psd.get_color(color)
    docref = APP.instance.activeDocument
    docsel = docref.selection
    docref.activeLayer = layer
    psd.select_layer_bounds(layer, docsel)

    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putClass(APP.instance.sID("path"))
    desc1.putReference(APP.instance.sID("target"), ref1)
    ref2.putProperty(APP.instance.sID("selectionClass"), APP.instance.sID("selection"))
    desc1.putReference(APP.instance.sID("from"), ref2)
    desc1.putUnitDouble(
        APP.instance.sID("tolerance"), APP.instance.sID("pixelsUnit"), 2.000000
    )
    APP.instance.executeAction(
        APP.instance.sID("make"), desc1, DialogModes.DisplayNoDialogs
    )

    ref1 = ActionReference()
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    desc3 = ActionDescriptor()
    desc4 = ActionDescriptor()
    ref1.putClass(APP.instance.sID("contentLayer"))
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc4.putDouble(APP.instance.sID("red"), color.rgb.red)
    desc4.putDouble(APP.instance.sID("green"), color.rgb.green)
    desc4.putDouble(APP.instance.sID("blue"), color.rgb.blue)
    desc3.putObject(APP.instance.sID("color"), APP.instance.sID("RGBColor"), desc4)
    desc2.putObject(
        APP.instance.sID("type"), APP.instance.sID("solidColorLayer"), desc3
    )
    desc1.putObject(APP.instance.sID("using"), APP.instance.sID("contentLayer"), desc2)
    APP.instance.executeAction(
        APP.instance.sID("make"), desc1, DialogModes.DisplayNoDialogs
    )
    APP.instance.activeDocument.activeLayer.name = layer_name

    # Check dims
    dims = psd.get_layer_dimensions(layer)
    dims = (dims["width"], dims["height"])
    new_dims = psd.get_layer_dimensions(docref.activeLayer)
    new_dims = (new_dims["width"], new_dims["height"])
    if dims != new_dims:
        print("DIMS CHANGED:", layer_name)
        print("Before:", dims)
        print("After:", new_dims)

    layer.remove()
    docref.activeLayer.visible = False

    created_layer = docref.activeLayer
    if not isinstance(created_layer, ArtLayer):
        raise TypeError("Created color shape layer isn't the active layer as expected")

    return created_layer


"""
* Font Utilities
"""


def log_all_template_fonts(templates: Iterable[AppTemplate]) -> dict[str, list[str]]:
    """Create a log of every font found for each PSD template."""

    # Ignore warnings from the psd_tools module
    logging.getLogger("psd_tools").setLevel(logging.FATAL)
    warnings.filterwarnings("ignore", module="psd_tools")

    def _get_fonts_from_psd(doc_path: str | PathLike[str]) -> set[str]:
        """
        Get a set of every font found in a given Photoshop document.
        @param doc_path: Path to the Photoshop document.
        @return: Set of font names found in the document.
        """
        file = PSDImage.open(doc_path)  # pyright: ignore[reportUnknownMemberType]
        fonts: set[str] = set()
        for layer in [n for n in file.descendants() if n.kind == "type"]:
            for style in layer.engine_dict["StyleRun"]["RunArray"]:  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
                font_key = style["StyleSheet"]["StyleSheetData"]["Font"]  # pyright: ignore[reportUnknownVariableType]
                fonts.add(layer.resource_dict["FontSet"][font_key]["Name"])  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue]
        return fonts

    # PSD documents to test
    docs = {
        t.path_psd: f"{t.name} ({t.plugin.name if t.plugin else 'BASE'})"
        for t in templates
    }

    # Track progress
    doc_fonts: dict[str, set[str]] = {}
    master: dict[str, list[str]] = {}
    current = 1
    total = len(docs)

    for f, temp_name in docs.items():
        # Alert the user
        _logger.info(f"READING FONTS — {temp_name} [{f.name}] [{current}/{total}]")
        current += 1

        # Open document, get fonts, close document
        doc_fonts[temp_name] = _get_fonts_from_psd(f)

    # Create master list
    for doc, font_list in doc_fonts.items():
        for f in font_list:
            master.setdefault(str(f), []).append(doc)

    # Log a sorted master list
    master = {k: v for k, v in sorted(master.items(), key=lambda item: len(item[1]))}
    with open("logs/FONTS.json", "w", encoding="utf-8") as f:
        json.dump(master, f, indent=2)
    return master


"""
* Project: Data Sets
* Exploring the use of data set variables for potential performance gains.
* Status: Likely not helpful
"""


def insert_data_set_variables(
    xml_data: str, from_path: str, to_path: str | None = None
) -> None:
    """Inserts data set variable XML into a PSD document.

    Args:
        xml_data: Data to insert into the document.
        from_path: Path of the PSD file.
        to_path: Path of new PSD file created, overwrites from_path if not provided.
    """
    # Decide the to_path
    to_path = to_path or from_path

    # Ignore warnings from the psd_tools module
    logging.getLogger("psd_tools").setLevel(logging.FATAL)
    warnings.filterwarnings("ignore", module="psd_tools")

    # Open the PSD file
    f = PSDImage.open(from_path)  # pyright: ignore[reportUnknownMemberType]

    # Replace the image variables data
    new_resource = ImageResource(
        b"MeSa",
        key=Resource.IMAGE_READY_VARIABLES,
        name="",
        data=xml_data.encode(encoding="UTF-8", errors="strict"),
    )
    f.image_resources[Resource.IMAGE_READY_VARIABLES] = new_resource

    # Save the PSD file
    f.save(to_path)  # pyright: ignore[reportUnknownMemberType]


def print_data_set_variables(path: str) -> None:
    """Print data set variable XML data for a given document.

    Args:
        path: Path to a PSD document.
    """
    data = PSDImage.open(path).image_resources.get_data(Resource.IMAGE_READY_DATA_SETS)  # pyright: ignore[reportUnknownMemberType]
    pretty_xml = minidom.parseString(data).toprettyxml()

    # Print without excess newlines
    print("\n".join([line for line in pretty_xml.split("\n") if line.strip()]))


def format_data_set_variable_name(text: str) -> str:
    """Formats string as a data set variable name.

    Args:
        text: Text to format as a data set variable name.

    Returns:
        Properly formatted data set variable name.
    """
    return text.title().replace(" ", "").replace("-", "").replace("&", "")


def get_data_set_variables(
    group: LayerSet | Document | None = None, tree: str | None = None
) -> list[dict[str, str]]:
    """Get data set variables for all ArtLayer and LayerSet objects in document or LayerSet.

    Args:
        group: LayerSet or Document, use activeDocument if not provided.
        tree: Tree to add to variable names, empty str if not provided.

    Returns:
        List of data set variable dicts.
    """

    # Establish current tree
    tree = (
        f"{tree}{format_data_set_variable_name(group.name)}."
        if tree and group
        else (f"{format_data_set_variable_name(group.name)}." if group else "")
    )

    # Establish group or top level document container
    group = group or APP.instance.activeDocument
    layer_vars: list[dict[str, str]] = []

    # Add layer variables
    for n in group.artLayers:
        with suppress(Exception):
            if n.kind == LayerKind.TextLayer:
                layer_vars.append(
                    {
                        "varName": f"{tree}{format_data_set_variable_name(n.name)}.Text",
                        "trait": "textcontent",
                        "docRef": f"id('{n.id}')",
                    }
                )
            elif "Frame" in n.name:
                layer_vars.append(
                    {
                        "varName": f"{tree}{format_data_set_variable_name(n.name)}.Image",
                        "trait": "fileref",
                        "placementMethod": "fill",
                        "align": "center",
                        "valign": "middle",
                        "clip": "false",
                        "docRef": f"id('{n.id}')",
                    }
                )
            layer_vars.append(
                {
                    "varName": f"{tree}{format_data_set_variable_name(n.name)}.Visible",
                    "trait": "visibility",
                    "docRef": f"id('{n.id}')",
                }
            )

    # Add layer group variables
    for n in group.layerSets:
        with suppress(Exception):
            layer_vars.append(
                {
                    "varName": f"{tree}{format_data_set_variable_name(n.name)}.Visible",
                    "trait": "visibility",
                    "docRef": f"id('{n.id}')",
                }
            )
            layer_vars.extend(get_data_set_variables(n, tree))
    return layer_vars


def get_data_set_variable_xml():
    """Generate data set variable XML for all layers in document."""

    # Create the root element
    root = ET.Element("variableSets", xmlns="https://ns.adobe.com/Variables/1.0/")

    # Create variableSet -> variables
    variableSet = ET.SubElement(root, "variableSet")
    variableSet.set("locked", "none")
    variableSet.set("varSetName", "binding1")
    variables = ET.SubElement(variableSet, "variables")

    # Add your variables, could do this programmatically for each layer
    for var in get_data_set_variables():
        variable = ET.SubElement(variables, "variable")
        for k, v in var.items():
            variable.set(k, v)

    # Convert the XML to a string
    return (
        ET.tostring(root, encoding="utf8", method="xml", short_empty_elements=False)
        .decode()
        .replace("<?xml version='1.0' encoding='utf8'?>\n", "", 1)
        .replace("><", ">\n<")
    ) + "\n"


def create_data_set_csv(data_set: dict[str, str], path: str) -> None:
    """Create a data set CSV that can be imported for Photoshop's data set variable system.

    Args:
        data_set: A dictionary where variable names are the keys and variable values are the values.
        path: Path to save the CSV to.
    """
    with open(path, "w", newline="") as file:
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
    ref.putClass(APP.instance.sID("dataSetClass"))
    desc.putReference(APP.instance.sID("null"), ref)
    desc.putPath(APP.instance.sID("using"), path)
    desc.putEnumerated(
        APP.instance.sID("encoding"),
        APP.instance.sID("dataSetEncoding"),
        APP.instance.sID("dataSetEncodingAuto"),
    )
    desc.putBoolean(APP.instance.sID("eraseAll"), True)
    desc.putBoolean(APP.instance.sID("useFirstColumn"), True)
    APP.instance.executeAction(
        APP.instance.sID("importDataSets"), desc, DialogModes.DisplayNoDialogs
    )


def apply_data_set(data_set_name: str) -> None:
    """Applies a data set from Photoshop's data set variable system.

    Args:
        data_set_name: Name of the data set.
    """
    desc = ActionDescriptor()
    setRef = ActionReference()
    setRef.putName(APP.instance.sID("dataSetClass"), data_set_name)
    desc.putReference(APP.instance.sID("null"), setRef)
    APP.instance.executeAction(
        APP.instance.sID("apply"), desc, DialogModes.DisplayNoDialogs
    )
