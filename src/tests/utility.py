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
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    ElementPlacement,
    LayerKind
)

# Local Imports
from src.constants import con
from src.utils.objects import PhotoshopHandler

con.headless = True
import src.helpers as psd

app = PhotoshopHandler()
cID = app.charIDToTypeID
sID = app.stringIDToTypeID


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
        psd.getLayer(new, g).visible = True
        # Disable old color
        if old:
            psd.getLayer(old, g).visible = False


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


"""
EXECUTION TIME TESTING
"""


def test_execution_time(
    new_func: Callable,
    old_func: Callable,
    iterations=1000,
    args=None,
    args_old=None,
    check_result=True
) -> None:
    """
    Test the execution time of a new function against an older function.
    @param new_func: New callable function to test.
    @param old_func: Older callable function to compare against.
    @param iterations: How many times to run these functions, higher means better sample size.
    @param args: Args to pass to the newer function, and older function unless specified in args_old.
    @param args_old: Args to pass to the older function.
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
    results[0]['average'] = sum(results[0]['times'])/len(results[0]['times'])

    # Test old functionality
    for i in range(iterations):
        s = perf_counter()
        results[1]['value'] = old_func(*args_old)
        results[1]['times'].append(perf_counter()-s)
    results[1]['average'] = sum(results[1]['times'])/len(results[1]['times'])

    # Report results
    for i, res in enumerate(results):
        print(f"{res['type']} method: {res['average']}")

    # Compare results
    final = sorted(results, key=itemgetter('average'))
    print(f"{Fore.GREEN}The {final[0]['type']} method is faster by {final[1]['average']-final[0]['average']} seconds!")
    if check_result:
        print(f"Results check: {Fore.GREEN+'SUCCESS' if final[0]['value'] == final[1]['value'] else Fore.RED+'FAILED'}")
        print(final[0]['value'])
        print(final[1]['value'])


"""
ACTION DESCRIPTOR/GETTER HELPERS
"""


def get_text_key(layer: ArtLayer):
    """
    Get the textKey action reference from a TextLayer.
    @param layer: ArtLayer with "kind" of TextLayer.
    @return:
    """
    # Ensure a valid layer object
    if not isinstance(layer, ArtLayer):
        raise Exception(f"Did not receive a valid layer!")
    if layer.kind != LayerKind.TextLayer:
        raise Exception(f"'{layer.name}' layer is not a TextLayer!")
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = app.executeActionGet(reference)
    return descriptor.getObjectValue(sID('textKey'))


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
    x_scale, y_scale = psd.get_text_scale_factor(text_key=text_key, axis=['xx', 'yy'])
    click_point = text_key.getObjectValue(sID('textClickPoint'))
    x_pos = click_point.getUnitDoubleValue(sID('horizontal')) * x_scale
    y_pos = click_point.getUnitDoubleValue(sID('vertical')) * y_scale

    # Establish the bounds of the box
    shape = text_key.getList(sID('textShape')).getObjectValue(0)
    bounds = shape.getObjectValue(sID('bounds'))

    return [
        int(psd.convert_points_to_pixels((bounds.getUnitDoubleValue(sID('left')) * x_scale) + x_pos)),
        int(psd.convert_points_to_pixels((bounds.getUnitDoubleValue(sID('top')) * y_scale) + y_pos)),
        int(psd.convert_points_to_pixels((bounds.getUnitDoubleValue(sID('right')) * x_scale) + x_pos)),
        int(psd.convert_points_to_pixels((bounds.getUnitDoubleValue(sID('bottom')) * y_scale) + y_pos))
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
