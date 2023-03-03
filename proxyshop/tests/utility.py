"""
TESTING UTILITY
For contributors and plugin development.
"""
# CORE MODULES
import os
from time import perf_counter
from typing import Optional

import photoshop.api as ps
from photoshop.api._artlayer import ArtLayer

from proxyshop.constants import con
con.headless = True
import proxyshop.helpers as psd

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
    wm = psd.import_svg(os.path.join(con.cwd, f"proxyshop/img/watermarks/{name}.svg"))
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


def t1(arg):
    return 'result'


def t2(arg):
    return 'result'


# Establish your variables outside the test
variable = "Some variable"

# Test speed of first function
s = perf_counter()
result1 = t1(variable)
print(f"Test 1: {perf_counter()-s} seconds")

# Test speed of second function
s = perf_counter()
result2 = t2(variable)
print(f"Test 2: {perf_counter()-s} seconds")

# Optionally check that results match
print('\n')
print(result1)
print(result2)
