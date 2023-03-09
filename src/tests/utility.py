"""
TESTING UTILITY
For contributors and plugin development.
"""
# CORE MODULES
import os
import colorama
from colorama import Fore
from operator import itemgetter
from time import perf_counter
from typing import Optional, Union, Callable

import photoshop.api as ps
from photoshop.api._artlayer import ArtLayer

from src.constants import con

con.headless = True
import src.helpers as psd

app = ps.Application()
cID = app.charIDToTypeID
sID = app.stringIDToTypeID


"""
CURRENTLY IN DEVELOPMENT
"""


def place_watermark(ref: ArtLayer, name: str = "GU") -> ArtLayer:
    """
    Places an SVG watermark.
    @param ref: Reference used to frame the watermark.
    @param name: Name to give the new watermark layer.
    @return: New watermark player.
    """
    wm = psd.import_svg(os.path.join(con.path_img, f"watermarks/{name}.svg"))
    psd.align_vertical(wm, ref)
    psd.align_horizontal(wm, ref)
    app.activeDocument.activeLayer.opacity = 50
    psd.frame_layer(wm, ref, smallest=True)
    wm.resize(80, 80, ps.AnchorPosition.MiddleCenter)
    wm.move(psd.getLayerSet("Pinlines & Textbox"), ps.ElementPlacement.PlaceBefore)
    wm.blendMode = ps.BlendMode.ColorBurn
    return wm


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
        top = psd.getLayer(dual[0], group).duplicate(ref, ps.ElementPlacement.PlaceBefore)
        bottom = psd.getLayer(dual[1], group).duplicate(top, ps.ElementPlacement.PlaceAfter)
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
    args_new=None,
    args_old=None,
    check_result=True
) -> None:
    """
    Test the execution time of a new function against an older function.
    @param new_func: New callable function to test.
    @param old_func: Older callable function to compare against.
    @param iterations: How many times to run these functions, higher means better sample size.
    @param args_new: Args to pass to the newer function.
    @param args_old: Args to pass to the older function.
    """
    # Test configuration
    if not args_new:
        args_new = []
    if not args_old:
        args_old = []
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
        results[0]['value'] = new_func(*args_new)
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
REQUESTS TESTING
"""

"""
code = 'xln'
number = '96'
lang = 'fr'
res = requests.get(
    url=f'https://api.scryfall.com/cards/{code}/{number}/{lang}',
    params={
        'pretty': True
    }
)
print(res.url)
print(res.json())
"""
