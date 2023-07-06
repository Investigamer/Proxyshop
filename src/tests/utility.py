"""
TESTING UTILITY
For contributors and plugin development.
"""
# Standard Library Imports
from time import perf_counter
from typing import Optional, Union, Callable
from _ctypes import COMError
from operator import itemgetter
import json

# Use this to force a working directory if IDE doesn't support it
# os.chdir(os.path.abspath(os.path.join(os.getcwd(), '..', '..')))

# Third Party Imports
import colorama
from colorama import Fore
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
from src.constants import con
from src.helpers.document import points_to_pixels
from src.helpers.layers import getLayer, getLayerSet, merge_layers
from src.helpers.masks import copy_layer_mask
from src.helpers.text import get_text_scale_factor, get_text_key, apply_text_key
from src.utils.objects import PhotoshopHandler

con.headless = True

app: PhotoshopHandler = con.app
cID = app.charIDtoTypeID
sID = app.stringIDtoTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

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
    name="Pinlines & Textbox",
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
EXECUTION TIME TESTING
"""


def test_execution_time(
    new_func: Callable,
    old_func: Callable,
    iterations=1000,
    args=None,
    args_old=None,
    check_result=True,
    reset_func: Optional[Callable] = None
) -> None:
    """
    Test the execution time of a new function against an older function.
    @param new_func: New callable function to test.
    @param old_func: Older callable function to compare against.
    @param iterations: How many times to run these functions, higher means better sample size.
    @param args: Args to pass to the newer function, and older function unless specified in args_old.
    @param args_old: Args to pass to the older function.
    @param check_result: Whether to check if results match.
    @param reset_func: Optional function to call to reset app state between actions.
    """
    # Test configuration
    if not args:
        args = []
    if not args_old:
        args_old = args
    colorama.init(autoreset=True)
    results: list[dict[str, Union[None, int, float, str, list]]] = [
        {
            'value': None,
            'average': 0,
            'times': [],
            'type': 'Newer'
        },
        {
            'value': None,
            'average': 0,
            'times': [],
            'type': 'Older'
        }
    ]

    # Test new functionality
    for i in range(iterations):
        s = perf_counter()
        results[0]['value'] = new_func(*args)
        results[0]['times'].append(perf_counter()-s)
        if reset_func:
            reset_func()
    results[0]['average'] = sum(results[0]['times'])/len(results[0]['times'])

    # Test old functionality
    for i in range(iterations):
        s = perf_counter()
        results[1]['value'] = old_func(*args_old)
        results[1]['times'].append(perf_counter()-s)
        if reset_func:
            reset_func()
    results[1]['average'] = sum(results[1]['times'])/len(results[1]['times'])

    # Report results
    for i, res in enumerate(results):
        print(f"{res['type']} method: {res['average']}")

    # Compare results
    final = sorted(results, key=itemgetter('average'))
    slower = final[1]['average']
    faster = final[0]['average']
    delta = slower - faster
    percent = round(delta/((slower + faster)/2) * 100, 2)
    print(f"{Fore.GREEN}The {final[0]['type']} method is {percent}% faster!")
    if check_result:
        print(f"Results check: {Fore.GREEN+'SUCCESS' if final[0]['value'] == final[1]['value'] else Fore.RED+'FAILED'}")
        if final[0]['value']:
            print(final[0]['value'])
            print(final[1]['value'])


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


def remove_text_segment(layer: ArtLayer, start: int, end: int) -> None:
    # Establish our text key and descriptor ID's
    app.activeDocument.activeLayer = layer
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(sID("textKey"))
    new_text = current_text[0:start:] + current_text[end + 1::]
    idFrom = sID("from")
    idTo = sID("to")

    # Find the range where target text exists
    for n in [sID("textStyleRange"), sID("paragraphStyleRange")]:
        offset = 0
        style_ranges: list[ActionDescriptor] = []
        text_range = key.getList(n)
        logged = {}
        for i in range(text_range.count):

            # Each item in textStyleRange list
            style = text_range.getObjectValue(i)

            # Indexes of this range
            i_left = style.getInteger(idFrom)
            i_right = style.getInteger(idTo)

            # Log and adjust identical ranges
            signature = (i_left, i_right)
            if signature in logged:
                if not (action := logged.get(signature)):
                    # Remove range entirely
                    continue
                # Adjust range with logged value
                style.putInteger(idTo, i_left - action)
                style.putInteger(idFrom, i_right - action)
                style_ranges.append(style)
                continue

            # Adjust range with current offset
            left = start - offset
            right = end - offset
            i_start = i_left - offset
            i_end = i_right - offset

            # Segment out of left bound
            if i_end < left:
                print("Segment OUT OF BOUND - LEFT", i_start, i_end, left, right)
                logged[signature] = 0
                style_ranges.append(style)
                continue

            # Segment out of right bound
            if i_start > right:
                print("Segment OUT OF BOUND - RIGHT", i_start, i_end, left, right)
                logged[signature] = offset
                style.putInteger(idTo, i_left - offset)
                style.putInteger(idFrom, i_right - offset)
                style_ranges.append(style)
                continue

            # Exclude entire segment, i.e. [[1, 2, 3, 4]]
            if i_start >= left and i_end <= right:
                print("Segment EXCLUDED", i_start, i_end, left, right)
                offset += i_end - i_start + 1
                logged[signature] = None
                continue

            # Segment has a partial match
            if i_start >= left and right <= i_end:
                # Exclude initial segment, i.e. [[1, 2], 3, 4]
                offset += right - i_start + 1
                print("Segment INITIAL", i_start, i_end, left, right)
            elif i_start < left < i_end <= right:
                # Exclude trailing segment, i.e. [1, 2, [3, 4]]
                offset += i_end - left + 1
                print("Segment TRAILING", i_start, i_end, left, right)
            elif i_start < left and right < i_end:
                # Exclude nested segment, i.e. [1, [2, 3, 4], 5, 6, 7]
                offset += right - left + 1
                print("Segment NESTED", i_start, i_end, left, right)

            # Make replacement
            logged[signature] = offset
            style.putInteger(idTo, i_left - offset)
            style.putInteger(idFrom, i_right - offset)
            style_ranges.append(style)

        # Apply changes
        style_range = ActionList()
        for r in style_ranges:
            style_range.putObject(n, r)
        key.putList(n, style_range)
        key.putString(sID("textKey"), new_text)
        apply_text_key(layer, key)
