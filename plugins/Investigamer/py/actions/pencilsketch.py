"""
Pencil Sketchify Action Module
"""

from collections.abc import Iterable

import photoshop.api as ps
from photoshop.api.enumerations import DialogModes

from src import APP
from src.render.setup import RenderOperation

dialog_mode = DialogModes.DisplayNoDialogs

"""
* Action Funcs
"""


def new_layer(index: int):
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putClass(APP.instance.cID("Lyr "))
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc1.putInteger(APP.instance.cID("LyrI"), index)
    APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)


def select_bg():
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putName(APP.instance.cID("Lyr "), "Background")
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc1.putBoolean(APP.instance.cID("MkVs"), False)
    list1 = ps.ActionList()
    list1.putInteger(1)
    desc1.putList(APP.instance.cID("LyrI"), list1)
    APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)


def reset_colors():
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putProperty(APP.instance.cID("Clr "), APP.instance.cID("Clrs"))
    desc1.putReference(APP.instance.cID("null"), ref1)
    APP.instance.executeAction(APP.instance.cID("Rset"), desc1, dialog_mode)


def move_layer(pos: int, index: int | list[int]):
    if isinstance(index, int):
        index = [index]
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    ref2 = ps.ActionReference()
    ref2.putIndex(APP.instance.cID("Lyr "), pos)
    desc1.putReference(APP.instance.cID("T   "), ref2)
    desc1.putBoolean(APP.instance.cID("Adjs"), False)
    desc1.putInteger(APP.instance.cID("Vrsn"), 5)
    list1 = ps.ActionList()
    for i in index:
        list1.putInteger(i)
    desc1.putList(APP.instance.cID("LyrI"), list1)
    APP.instance.executeAction(APP.instance.cID("move"), desc1, dialog_mode)


def set_opacity(opacity: float):
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    desc2.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), opacity)
    desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
    APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)


def select_layer(name: str, index: int):
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putName(APP.instance.cID("Lyr "), name)
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc1.putBoolean(APP.instance.cID("MkVs"), False)
    list1 = ps.ActionList()
    list1.putInteger(index)
    desc1.putList(APP.instance.cID("LyrI"), list1)
    APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)


def select_layers(name: str, layers: list[int]):
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putName(APP.instance.cID("Lyr "), name)
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc1.putEnumerated(
        APP.instance.sID("selectionModifier"),
        APP.instance.sID("selectionModifierType"),
        APP.instance.sID("addToSelection"),
    )
    desc1.putBoolean(APP.instance.cID("MkVs"), False)
    list1 = ps.ActionList()
    for layer in layers:
        list1.putInteger(layer)
    desc1.putList(APP.instance.cID("LyrI"), list1)
    APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)


def auto_tone():
    desc1 = ps.ActionDescriptor()
    desc1.putBoolean(APP.instance.cID("Auto"), True)
    APP.instance.executeAction(APP.instance.cID("Lvls"), desc1, dialog_mode)


def auto_contrast():
    desc1 = ps.ActionDescriptor()
    desc1.putBoolean(APP.instance.cID("AuCo"), True)
    APP.instance.executeAction(APP.instance.cID("Lvls"), desc1, dialog_mode)


def hide_layer(name: str | None = None):
    desc1 = ps.ActionDescriptor()
    list1 = ps.ActionList()
    ref1 = ps.ActionReference()
    if name:
        ref1.putName(APP.instance.cID("Lyr "), name)
    else:
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
    list1.putReference(ref1)
    desc1.putList(APP.instance.cID("null"), list1)
    APP.instance.executeAction(APP.instance.cID("Hd  "), desc1, dialog_mode)


def show_layer(name: str | None = None):
    desc1 = ps.ActionDescriptor()
    list1 = ps.ActionList()
    ref1 = ps.ActionReference()
    if name:
        ref1.putName(APP.instance.cID("Lyr "), name)
    else:
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
    list1.putReference(ref1)
    desc1.putList(APP.instance.cID("null"), list1)
    APP.instance.executeAction(APP.instance.cID("Shw "), desc1, dialog_mode)


def delete_layers(layers: Iterable[int]):
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    list1 = ps.ActionList()
    for layer in layers:
        list1.putInteger(layer)
    desc1.putList(APP.instance.cID("LyrI"), list1)
    APP.instance.executeAction(APP.instance.cID("Dlt "), desc1, dialog_mode)


"""
BLENDING MODES
"""


def blend(key: str):
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    desc2.putEnumerated(
        APP.instance.cID("Md  "), APP.instance.cID("BlnM"), APP.instance.sID(key)
    )
    desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
    APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)


"""
FILTERS
"""


def filter_photocopy(detail: int = 2, darken: int = 5):
    """
    Apply photocopy filter.
    @param detail: Level of detail.
    @param darken: Darkness amount.
    """
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Phtc")
    )
    desc1.putInteger(APP.instance.sID("detail "), detail)
    desc1.putInteger(APP.instance.sID("darken"), darken)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)


# Utility commands
def blend_multiply():
    blend("multiply")


def blend_color_dodge():
    blend("colorDodge")


def blend_linear_light():
    blend("linearLight")


def blend_linear_burn():
    blend("linearBurn")


def blend_soft_light():
    blend("softLight")


def blend_screen():
    blend("screen")


def blend_overlay():
    blend("overlay")


def blend_color():
    blend("color")


def run(
    render_operation: RenderOperation,
    draft_sketch: bool = False,
    rough_sketch: bool = False,
    black_and_white: bool = True,
    manual_editing: bool = False,
):
    """
    Pencil Sketchify Steps
    """

    # Is the main layer "Layer 1"
    APP.instance.activeDocument.activeLayer.name = "Background"

    # Make - New Layer 1
    new_layer(139)

    # Select
    select_bg()

    # Make - Solid Color Layer
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putClass(APP.instance.sID("contentLayer"))
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    desc3 = ps.ActionDescriptor()
    desc4 = ps.ActionDescriptor()
    desc4.putInteger(APP.instance.cID("Rd  "), 166)
    desc4.putInteger(APP.instance.cID("Grn "), 166)
    desc4.putInteger(APP.instance.cID("Bl  "), 166)
    desc3.putObject(APP.instance.cID("Clr "), APP.instance.sID("RGBColor"), desc4)
    desc2.putObject(
        APP.instance.cID("Type"), APP.instance.sID("solidColorLayer"), desc3
    )
    desc1.putObject(APP.instance.cID("Usng"), APP.instance.sID("contentLayer"), desc2)
    APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)

    # Select
    select_bg()

    # Layer Via Copy - Background copy
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(3, 240)

    # Reset Colors
    reset_colors()

    # Filter Gallery - Photocopy
    filter_photocopy(detail=2, darken=5)

    # Set - Blending Multiply
    blend_multiply()

    # Select
    select_bg()

    # Layer Via Copy - Background copy 2
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(4, 242)

    # Reset Colors
    reset_colors()

    # Filter Gallery - Photocopy, Accented Edges
    desc1 = ps.ActionDescriptor()
    list1 = ps.ActionList()
    desc2 = ps.ActionDescriptor()
    desc3 = ps.ActionDescriptor()
    desc2.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("AccE")
    )
    desc2.putInteger(APP.instance.cID("EdgW"), 3)
    desc2.putInteger(APP.instance.cID("EdgB"), 20)
    desc2.putInteger(APP.instance.cID("Smth"), 15)
    list1.putObject(APP.instance.cID("GEfc"), desc2)
    desc3.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Phtc")
    )
    desc3.putInteger(APP.instance.cID("Dtl "), 1)
    desc3.putInteger(APP.instance.cID("Drkn"), 49)
    list1.putObject(APP.instance.cID("GEfc"), desc3)
    desc1.putList(APP.instance.cID("GEfs"), list1)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Set - Blending Multiply
    blend_multiply()

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 3
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(5, 244)

    # Reset Colors
    reset_colors()

    # Filter Gallery - Photocopy, Stamp
    desc1 = ps.ActionDescriptor()
    list1 = ps.ActionList()
    desc2 = ps.ActionDescriptor()
    desc2.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Stmp")
    )
    desc2.putInteger(APP.instance.cID("LgDr"), 25)
    desc2.putInteger(APP.instance.cID("Smth"), 40)
    list1.putObject(APP.instance.cID("GEfc"), desc2)
    desc3 = ps.ActionDescriptor()
    desc3.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Phtc")
    )
    desc3.putInteger(APP.instance.cID("Dtl "), 1)
    desc3.putInteger(APP.instance.cID("Drkn"), 49)
    list1.putObject(APP.instance.cID("GEfc"), desc3)
    desc1.putList(APP.instance.cID("GEfs"), list1)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Set - Blending Multiply
    blend_multiply()

    # Set
    set_opacity(25)

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 4
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(6, 246)

    # Reset
    reset_colors()

    # Filter Gallery - Glowing Edge
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("GlwE")
    )
    desc1.putInteger(APP.instance.cID("EdgW"), 1)
    desc1.putInteger(APP.instance.cID("EdgB"), 20)
    desc1.putInteger(APP.instance.cID("Smth"), 15)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Desaturate
    APP.instance.executeAction(
        APP.instance.cID("Dstt"), ps.ActionDescriptor(), dialog_mode
    )

    # Levels - Auto Tone
    auto_tone()

    # Levels - Auto Contrast
    auto_contrast()

    # Levels Adjustment
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.sID("presetKind"),
        APP.instance.sID("presetKindType"),
        APP.instance.sID("presetKindCustom"),
    )
    list1 = ps.ActionList()
    desc2 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Chnl"), APP.instance.cID("Chnl"), APP.instance.cID("Cmps")
    )
    desc2.putReference(APP.instance.cID("Chnl"), ref1)
    list2 = ps.ActionList()
    list2.putInteger(25)
    list2.putInteger(230)
    desc2.putList(APP.instance.cID("Inpt"), list2)
    list1.putObject(APP.instance.cID("LvlA"), desc2)
    desc1.putList(APP.instance.cID("Adjs"), list1)
    APP.instance.executeAction(APP.instance.cID("Lvls"), desc1, dialog_mode)

    # Invert
    APP.instance.executeAction(
        APP.instance.cID("Invr"), ps.ActionDescriptor(), dialog_mode
    )

    # Set
    blend_multiply()

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 5
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(7, 248)

    # Layer Via Copy - Background Copy 6
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Invert
    APP.instance.executeAction(
        APP.instance.cID("Invr"), ps.ActionDescriptor(), dialog_mode
    )

    # Gaussian Blur
    desc1 = ps.ActionDescriptor()
    desc1.putUnitDouble(APP.instance.cID("Rds "), APP.instance.cID("#Pxl"), 50)
    APP.instance.executeAction(APP.instance.sID("gaussianBlur"), desc1, dialog_mode)

    # Set - Blending Color Dodge
    blend_color_dodge()

    # Select
    select_layers("Background copy 5", [248, 249])

    # Merge Layers
    APP.instance.executeAction(
        APP.instance.sID("mergeLayersNew"), ps.ActionDescriptor(), dialog_mode
    )

    # Desaturate
    APP.instance.executeAction(
        APP.instance.cID("Dstt"), ps.ActionDescriptor(), dialog_mode
    )

    # Layer Via Copy - Background Copy 7
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Reset
    reset_colors()

    # Filter Gallery - Glowing Edge
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("GlwE")
    )
    desc1.putInteger(APP.instance.cID("EdgW"), 1)
    desc1.putInteger(APP.instance.cID("EdgB"), 20)
    desc1.putInteger(APP.instance.cID("Smth"), 15)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Invert
    APP.instance.executeAction(
        APP.instance.cID("Invr"), ps.ActionDescriptor(), dialog_mode
    )

    # Set
    blend_multiply()

    # Set
    set_opacity(80)

    # Select
    select_layers("Background copy 6", [249, 250])

    # Merge Layers
    APP.instance.executeAction(
        APP.instance.sID("mergeLayersNew"), ps.ActionDescriptor(), dialog_mode
    )

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 5
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(8, 252)

    # Desaturate
    APP.instance.executeAction(
        APP.instance.cID("Dstt"), ps.ActionDescriptor(), dialog_mode
    )

    # High Pass Filter
    desc1 = ps.ActionDescriptor()
    desc1.putUnitDouble(APP.instance.cID("Rds "), APP.instance.cID("#Pxl"), 30)
    APP.instance.executeAction(APP.instance.sID("highPass"), desc1, dialog_mode)

    # Set - Blending Linear Light
    blend_linear_light()

    # Set - Layer Style, Blending Options: Blend if Gray
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    list1 = ps.ActionList()
    desc3 = ps.ActionDescriptor()
    ref2 = ps.ActionReference()
    ref2.putEnumerated(
        APP.instance.cID("Chnl"), APP.instance.cID("Chnl"), APP.instance.cID("Gry ")
    )
    desc3.putReference(APP.instance.cID("Chnl"), ref2)
    desc3.putInteger(APP.instance.cID("SrcB"), 0)
    desc3.putInteger(APP.instance.cID("Srcl"), 0)
    desc3.putInteger(APP.instance.cID("SrcW"), 75)
    desc3.putInteger(APP.instance.cID("Srcm"), 125)
    desc3.putInteger(APP.instance.cID("DstB"), 55)
    desc3.putInteger(APP.instance.cID("Dstl"), 125)
    desc3.putInteger(APP.instance.cID("DstW"), 255)
    desc3.putInteger(APP.instance.cID("Dstt"), 255)
    list1.putObject(APP.instance.cID("Blnd"), desc3)
    desc2.putList(APP.instance.cID("Blnd"), list1)
    desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
    APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Set
    set_opacity(50)

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 6
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(9, 254)

    # Reset
    reset_colors()

    # Filter Gallery - Cutout
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Ct  ")
    )
    desc1.putInteger(APP.instance.cID("NmbL"), 8)
    desc1.putInteger(APP.instance.cID("EdgS"), 10)
    desc1.putInteger(APP.instance.cID("EdgF"), 1)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Desaturate
    APP.instance.executeAction(
        APP.instance.cID("Dstt"), ps.ActionDescriptor(), dialog_mode
    )

    # Levels - Auto Tone
    auto_tone()

    # Levels - Auto Contrast
    auto_contrast()

    # Color Range
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("Clrs"), APP.instance.cID("Clrs"), APP.instance.cID("Mdtn")
    )
    desc1.putInteger(APP.instance.sID("midtonesFuzziness"), 40)
    desc1.putInteger(APP.instance.sID("midtonesLowerLimit"), 105)
    desc1.putInteger(APP.instance.sID("midtonesUpperLimit"), 150)
    desc1.putInteger(APP.instance.sID("colorModel"), 0)
    APP.instance.executeAction(APP.instance.sID("colorRange"), desc1, dialog_mode)

    # Layer Via Copy - Layer 2
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Find Edges
    APP.instance.executeAction(
        APP.instance.sID("findEdges"), ps.ActionDescriptor(), dialog_mode
    )

    # Hide
    hide_layer("Background copy 6")

    # Hide
    hide_layer()

    # Select
    select_bg()

    # Layer Via Copy - Background copy 8
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(9, 257)

    # Reset
    reset_colors()

    # Filter Gallery - Cutout
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Ct  ")
    )
    desc1.putInteger(APP.instance.cID("NmbL"), 8)
    desc1.putInteger(APP.instance.cID("EdgS"), 8)
    desc1.putInteger(APP.instance.cID("EdgF"), 1)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Desaturate
    APP.instance.executeAction(
        APP.instance.cID("Dstt"), ps.ActionDescriptor(), dialog_mode
    )

    # Levels
    auto_tone()

    # Levels
    auto_contrast()

    # Color Range
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("Clrs"), APP.instance.cID("Clrs"), APP.instance.cID("Mdtn")
    )
    desc1.putInteger(APP.instance.sID("midtonesFuzziness"), 40)
    desc1.putInteger(APP.instance.sID("midtonesLowerLimit"), 105)
    desc1.putInteger(APP.instance.sID("midtonesUpperLimit"), 150)
    desc1.putInteger(APP.instance.sID("colorModel"), 0)
    APP.instance.executeAction(APP.instance.sID("colorRange"), desc1, dialog_mode)

    # Layer Via Copy - Layer 3
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Find Edges
    APP.instance.executeAction(
        APP.instance.sID("findEdges"), ps.ActionDescriptor(), dialog_mode
    )

    # Select
    select_layer("Background copy 8", 257)

    # Select
    select_layers("Background copy 6", [257, 254])

    # Delete
    delete_layers([257, 254])

    # Select
    select_layer("Layer 2", 255)

    # Show
    show_layer()

    # Select
    select_layers("Layer 3", [258, 255])

    # Set
    blend_multiply()

    # Set
    set_opacity(30)

    # Select
    select_layer("Background copy 3", 244)

    # Set
    set_opacity(30)

    # Select
    select_layer("Background copy 7", 250)

    # Move
    move_layer(2, 250)

    # Select
    select_layer("Background copy 5", 252)

    # Move
    move_layer(10, 252)

    # Select
    select_layer("Background copy 7", 250)

    # Set
    set_opacity(50)

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 6
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(11, 261)

    # Filter - Distort Wave
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("Wvtp"), APP.instance.cID("Wvtp"), APP.instance.cID("WvSn")
    )
    desc1.putInteger(APP.instance.cID("NmbG"), 5)
    desc1.putInteger(APP.instance.cID("WLMn"), 10)
    desc1.putInteger(APP.instance.cID("WLMx"), 500)
    desc1.putInteger(APP.instance.cID("AmMn"), 5)
    desc1.putInteger(APP.instance.cID("AmMx"), 35)
    desc1.putInteger(APP.instance.cID("SclH"), 100)
    desc1.putInteger(APP.instance.cID("SclV"), 100)
    desc1.putEnumerated(
        APP.instance.cID("UndA"), APP.instance.cID("UndA"), APP.instance.cID("RptE")
    )
    desc1.putInteger(APP.instance.cID("RndS"), 1260853)
    APP.instance.executeAction(APP.instance.cID("Wave"), desc1, dialog_mode)

    # Reset
    reset_colors()

    # Filter Gallery - Photocopy, Accented Edges
    desc1 = ps.ActionDescriptor()
    list1 = ps.ActionList()
    desc2 = ps.ActionDescriptor()
    desc2.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("AccE")
    )
    desc2.putInteger(APP.instance.cID("EdgW"), 3)
    desc2.putInteger(APP.instance.cID("EdgB"), 20)
    desc2.putInteger(APP.instance.cID("Smth"), 15)
    list1.putObject(APP.instance.cID("GEfc"), desc2)
    desc3 = ps.ActionDescriptor()
    desc3.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Phtc")
    )
    desc3.putInteger(APP.instance.cID("Dtl "), 1)
    desc3.putInteger(APP.instance.cID("Drkn"), 49)
    list1.putObject(APP.instance.cID("GEfc"), desc3)
    desc1.putList(APP.instance.cID("GEfs"), list1)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Levels - Auto Tone
    auto_tone()

    # Levels - Auto Contrast
    auto_contrast()

    # Set - Blending Multiply
    blend_multiply()

    # Set
    set_opacity(50)

    # Move
    move_layer(5, 261)

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 8
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(12, 263)

    # Reset
    reset_colors()

    # Filter Gallery - Photocopy
    filter_photocopy(detail=2, darken=5)

    # Set
    blend_multiply()

    # Layer Via Copy - Background Copy 9
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Transform
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc1.putEnumerated(
        APP.instance.cID("FTcs"),
        APP.instance.cID("QCSt"),
        APP.instance.sID("QCSAverage"),
    )
    desc2 = ps.ActionDescriptor()
    desc2.putUnitDouble(APP.instance.cID("Hrzn"), APP.instance.cID("#Pxl"), 0)
    desc2.putUnitDouble(APP.instance.cID("Vrtc"), APP.instance.cID("#Pxl"), 0)
    desc1.putObject(APP.instance.cID("Ofst"), APP.instance.cID("Ofst"), desc2)
    desc1.putUnitDouble(APP.instance.cID("Wdth"), APP.instance.cID("#Prc"), 110)
    desc1.putUnitDouble(APP.instance.cID("Hght"), APP.instance.cID("#Prc"), 110)
    desc1.putBoolean(APP.instance.cID("Lnkd"), True)
    desc1.putEnumerated(
        APP.instance.cID("Intr"), APP.instance.cID("Intp"), APP.instance.cID("Bcbc")
    )
    APP.instance.executeAction(APP.instance.cID("Trnf"), desc1, dialog_mode)

    # Select
    select_layer("Background copy 8", 263)

    # Transform
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc1.putEnumerated(
        APP.instance.cID("FTcs"),
        APP.instance.cID("QCSt"),
        APP.instance.sID("QCSAverage"),
    )
    desc2 = ps.ActionDescriptor()
    desc2.putUnitDouble(
        APP.instance.cID("Hrzn"), APP.instance.cID("#Pxl"), -2.27373675443232e-13
    )
    desc2.putUnitDouble(APP.instance.cID("Vrtc"), APP.instance.cID("#Pxl"), 0)
    desc1.putObject(APP.instance.cID("Ofst"), APP.instance.cID("Ofst"), desc2)
    desc1.putUnitDouble(APP.instance.cID("Wdth"), APP.instance.cID("#Prc"), 90)
    desc1.putUnitDouble(APP.instance.cID("Hght"), APP.instance.cID("#Prc"), 90)
    desc1.putBoolean(APP.instance.cID("Lnkd"), True)
    desc1.putEnumerated(
        APP.instance.cID("Intr"), APP.instance.cID("Intp"), APP.instance.cID("Bcbc")
    )
    APP.instance.executeAction(APP.instance.cID("Trnf"), desc1, dialog_mode)

    # Select
    select_layers("Background copy 9", [263, 264])

    # Set
    set_opacity(10)

    # Move
    move_layer(8, [263, 264])

    # Select
    select_layer("Background copy 7", 250)

    # Select
    select_layers("Layer 2", [250, 240, 242, 261, 244, 246, 263, 264, 258, 255])

    # Set
    blend_linear_burn()

    # Select
    select_layer("Color Fill 1", 238)

    # Make
    new_layer(268)

    # Fill - 50% Gray
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("Usng"), APP.instance.cID("FlCn"), APP.instance.cID("Gry ")
    )
    desc1.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 100)
    desc1.putEnumerated(
        APP.instance.cID("Md  "), APP.instance.cID("BlnM"), APP.instance.cID("Nrml")
    )
    APP.instance.executeAction(APP.instance.cID("Fl  "), desc1, dialog_mode)

    # Filter Gallery - Texturizer
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Txtz")
    )
    desc1.putEnumerated(
        APP.instance.cID("TxtT"), APP.instance.cID("TxtT"), APP.instance.cID("TxSt")
    )
    desc1.putInteger(APP.instance.cID("Scln"), 200)
    desc1.putInteger(APP.instance.cID("Rlf "), 4)
    desc1.putEnumerated(
        APP.instance.cID("LghD"), APP.instance.cID("LghD"), APP.instance.cID("LDTp")
    )
    desc1.putBoolean(APP.instance.cID("InvT"), False)
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Set - Blending Soft Light
    blend_soft_light()

    # Select
    select_layer("Layer 4", 268)

    # Make
    new_layer(269)

    # Fill - Foreground Color
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("Usng"), APP.instance.cID("FlCn"), APP.instance.cID("FrgC")
    )
    desc1.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 100)
    desc1.putEnumerated(
        APP.instance.cID("Md  "), APP.instance.cID("BlnM"), APP.instance.cID("Nrml")
    )
    APP.instance.executeAction(APP.instance.cID("Fl  "), desc1, dialog_mode)

    # Add Noise
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("Dstr"), APP.instance.cID("Dstr"), APP.instance.cID("Gsn ")
    )
    desc1.putUnitDouble(APP.instance.cID("Nose"), APP.instance.cID("#Prc"), 25)
    desc1.putBoolean(APP.instance.cID("Mnch"), True)
    desc1.putInteger(APP.instance.cID("FlRs"), 1315132)
    APP.instance.executeAction(APP.instance.sID("addNoise"), desc1, dialog_mode)
    APP.instance.activeDocument.activeLayer.opacity = 40

    # Set
    blend_screen()

    # Levels Adjustment
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.sID("presetKind"),
        APP.instance.sID("presetKindType"),
        APP.instance.sID("presetKindCustom"),
    )
    list1 = ps.ActionList()
    desc2 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("Chnl"), APP.instance.cID("Chnl"), APP.instance.cID("Cmps")
    )
    desc2.putReference(APP.instance.cID("Chnl"), ref1)
    list2 = ps.ActionList()
    list2.putInteger(0)
    list2.putInteger(90)
    desc2.putList(APP.instance.cID("Inpt"), list2)
    list1.putObject(APP.instance.cID("LvlA"), desc2)
    desc1.putList(APP.instance.cID("Adjs"), list1)
    APP.instance.executeAction(APP.instance.cID("Lvls"), desc1, dialog_mode)

    # Select
    select_layer("Background copy 4", 246)

    # Move
    move_layer(6, 246)

    # Select
    select_layer("Background copy 3", 244)

    # Set
    set_opacity(20)

    # Select
    select_layer("Layer 3", 258)

    # Select
    select_layers("Layer 2", [258, 255])

    # Set
    set_opacity(40)

    # Select
    select_layer("Background copy 5", 252)

    # Reset
    reset_colors()

    # Make - Gradient Map
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putClass(APP.instance.cID("AdjL"))
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    desc3 = ps.ActionDescriptor()
    desc4 = ps.ActionDescriptor()
    desc4.putString(APP.instance.cID("Nm  "), "Foreground to Background")
    desc4.putEnumerated(
        APP.instance.cID("GrdF"), APP.instance.cID("GrdF"), APP.instance.cID("CstS")
    )
    desc4.putDouble(APP.instance.cID("Intr"), 4096)
    list1 = ps.ActionList()
    desc5 = ps.ActionDescriptor()
    desc6 = ps.ActionDescriptor()
    desc6.putDouble(APP.instance.cID("Rd  "), 0)
    desc6.putDouble(APP.instance.cID("Grn "), 0)
    desc6.putDouble(APP.instance.cID("Bl  "), 0)
    desc5.putObject(APP.instance.cID("Clr "), APP.instance.sID("RGBColor"), desc6)
    desc5.putEnumerated(
        APP.instance.cID("Type"), APP.instance.cID("Clry"), APP.instance.cID("UsrS")
    )
    desc5.putInteger(APP.instance.cID("Lctn"), 0)
    desc5.putInteger(APP.instance.cID("Mdpn"), 50)
    list1.putObject(APP.instance.cID("Clrt"), desc5)
    desc7 = ps.ActionDescriptor()
    desc8 = ps.ActionDescriptor()
    desc8.putDouble(APP.instance.cID("Rd  "), 255)
    desc8.putDouble(APP.instance.cID("Grn "), 255)
    desc8.putDouble(APP.instance.cID("Bl  "), 255)
    desc7.putObject(APP.instance.cID("Clr "), APP.instance.sID("RGBColor"), desc8)
    desc7.putEnumerated(
        APP.instance.cID("Type"), APP.instance.cID("Clry"), APP.instance.cID("UsrS")
    )
    desc7.putInteger(APP.instance.cID("Lctn"), 4096)
    desc7.putInteger(APP.instance.cID("Mdpn"), 50)
    list1.putObject(APP.instance.cID("Clrt"), desc7)
    desc4.putList(APP.instance.cID("Clrs"), list1)
    list2 = ps.ActionList()
    desc9 = ps.ActionDescriptor()
    desc9.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 100)
    desc9.putInteger(APP.instance.cID("Lctn"), 0)
    desc9.putInteger(APP.instance.cID("Mdpn"), 50)
    list2.putObject(APP.instance.cID("TrnS"), desc9)
    desc10 = ps.ActionDescriptor()
    desc10.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 100)
    desc10.putInteger(APP.instance.cID("Lctn"), 4096)
    desc10.putInteger(APP.instance.cID("Mdpn"), 50)
    list2.putObject(APP.instance.cID("TrnS"), desc10)
    desc4.putList(APP.instance.cID("Trns"), list2)
    desc3.putObject(APP.instance.cID("Grad"), APP.instance.cID("Grdn"), desc4)
    desc2.putObject(APP.instance.cID("Type"), APP.instance.cID("GdMp"), desc3)
    desc1.putObject(APP.instance.cID("Usng"), APP.instance.cID("AdjL"), desc2)
    APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)

    # Set
    blend_soft_light()

    # Set
    set_opacity(20)

    # Make - Levels Adjustment Layer
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putClass(APP.instance.cID("AdjL"))
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    desc3 = ps.ActionDescriptor()
    desc3.putEnumerated(
        APP.instance.sID("presetKind"),
        APP.instance.sID("presetKindType"),
        APP.instance.sID("presetKindDefault"),
    )
    desc2.putObject(APP.instance.cID("Type"), APP.instance.cID("Lvls"), desc3)
    desc1.putObject(APP.instance.cID("Usng"), APP.instance.cID("AdjL"), desc2)
    APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)

    # Set - Levels Adjustment Layer Settings
    desc1 = ps.ActionDescriptor()
    ref1 = ps.ActionReference()
    ref1.putEnumerated(
        APP.instance.cID("AdjL"), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("null"), ref1)
    desc2 = ps.ActionDescriptor()
    desc2.putEnumerated(
        APP.instance.sID("presetKind"),
        APP.instance.sID("presetKindType"),
        APP.instance.sID("presetKindCustom"),
    )
    list1 = ps.ActionList()
    desc3 = ps.ActionDescriptor()
    ref2 = ps.ActionReference()
    ref2.putEnumerated(
        APP.instance.cID("Chnl"), APP.instance.cID("Chnl"), APP.instance.cID("Cmps")
    )
    desc3.putReference(APP.instance.cID("Chnl"), ref2)
    desc3.putDouble(APP.instance.cID("Gmm "), 0.8)
    list2 = ps.ActionList()
    list2.putInteger(30)
    list2.putInteger(250)
    desc3.putList(APP.instance.cID("Inpt"), list2)
    list1.putObject(APP.instance.cID("LvlA"), desc3)
    desc2.putList(APP.instance.cID("Adjs"), list1)
    desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lvls"), desc2)
    APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Select
    select_layer("Background copy 6", 112)

    # Set
    set_opacity(40)

    # Select
    select_bg()

    # Layer Via Copy - Background Copy 10
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(18, 121)

    # Reset
    reset_colors()

    # Filter Gallery - Graphic Pen
    desc1 = ps.ActionDescriptor()
    desc1.putEnumerated(
        APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("GraP")
    )
    desc1.putInteger(APP.instance.cID("StrL"), 15)
    desc1.putInteger(APP.instance.cID("LgDr"), 50)
    desc1.putEnumerated(
        APP.instance.cID("SDir"), APP.instance.cID("StrD"), APP.instance.cID("SDRD")
    )
    APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Set
    blend_overlay()

    # Set
    set_opacity(30)

    # Move
    move_layer(5, 121)

    # Select
    select_bg()

    # Layer Via Copy - Background copy 11
    APP.instance.executeAction(
        APP.instance.sID("copyToLayer"), ps.ActionDescriptor(), dialog_mode
    )

    # Move
    move_layer(16, 127)

    # Set
    blend_color()

    """

	# Make - Hue/Saturation Adjustment
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(APP.instance.cID('AdjL'))
	desc1.putReference(APP.instance.cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(APP.instance.sID("presetKind"), APP.instance.sID("presetKindType"), APP.instance.sID("presetKindDefault"))
	desc3.putBoolean(APP.instance.cID('Clrz'), False)
	desc2.putObject(APP.instance.cID('Type'), APP.instance.cID('HStr'), desc3)
	desc1.putObject(APP.instance.cID('Usng'), APP.instance.cID('AdjL'), desc2)
	APP.instance.executeAction(APP.instance.cID('Mk  '), desc1, dialog_mode)

	# Create Clipping Mask
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(APP.instance.cID('Lyr '), APP.instance.cID('Ordn'), APP.instance.cID('Trgt'))
	desc1.putReference(APP.instance.cID('null'), ref1)
	APP.instance.executeAction(APP.instance.sID('groupEvent'), desc1, dialog_mode)

	# Select
	select_layers("Background copy 11", [127, 128])

	# Move
	move_layer(16, [127, 128])

	# Select
	select_layer("Levels 1", 119)

	# Make - Hue/Saturation Adjustment Layer
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(APP.instance.cID('AdjL'))
	desc1.putReference(APP.instance.cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(APP.instance.sID("presetKind"), APP.instance.sID("presetKindType"), APP.instance.sID("presetKindDefault"))
	desc3.putBoolean(APP.instance.cID('Clrz'), False)
	desc2.putObject(APP.instance.cID('Type'), APP.instance.cID('HStr'), desc3)
	desc1.putObject(APP.instance.cID('Usng'), APP.instance.cID('AdjL'), desc2)
	APP.instance.executeAction(APP.instance.cID('Mk  '), desc1, dialog_mode)

	# Merge Visible
	desc1 = ps.ActionDescriptor()
	desc1.putBoolean(APP.instance.cID('Dplc'), True)
	APP.instance.executeAction(APP.instance.sID('mergeVisible'), desc1, dialog_mode)

	# Desaturate
	def step182():

		APP.instance.executeAction(APP.instance.cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# High Pass
	def step183():

		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(APP.instance.cID('Rds '), APP.instance.cID('#Pxl'), 1)
		APP.instance.executeAction(APP.instance.sID('highPass'), desc1, dialog_mode)

	# Set
	def step184():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(APP.instance.cID('Lyr '), APP.instance.cID('Ordn'), APP.instance.cID('Trgt'))
		desc1.putReference(APP.instance.cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(APP.instance.cID('Md  '), APP.instance.cID('BlnM'), APP.instance.sID("vividLight"))
		desc1.putObject(APP.instance.cID('T   '), APP.instance.cID('Lyr '), desc2)
		APP.instance.executeAction(APP.instance.cID('setd'), desc1, dialog_mode)

	# Select
	def step185():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(APP.instance.cID('Lyr '), "Color Fill 1")
		desc1.putReference(APP.instance.cID('null'), ref1)
		desc1.putBoolean(APP.instance.cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(90)
		desc1.putList(APP.instance.cID('LyrI'), list1)
		APP.instance.executeAction(APP.instance.cID('slct'), desc1, dialog_mode)

	# Select
	def step186():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(APP.instance.cID('Lyr '), "Layer 6")
		desc1.putReference(APP.instance.cID('null'), ref1)
		desc1.putEnumerated(APP.instance.sID("selectionModifier"), APP.instance.sID("selectionModifierType"), APP.instance.sID("addToSelectionContinuous"))
		desc1.putBoolean(APP.instance.cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(90)
		list1.putInteger(116)
		list1.putInteger(117)
		list1.putInteger(102)
		list1.putInteger(121)
		list1.putInteger(92)
		list1.putInteger(98)
		list1.putInteger(94)
		list1.putInteger(112)
		list1.putInteger(96)
		list1.putInteger(114)
		list1.putInteger(115)
		list1.putInteger(110)
		list1.putInteger(107)
		list1.putInteger(104)
		list1.putInteger(127)
		list1.putInteger(128)
		list1.putInteger(118)
		list1.putInteger(119)
		list1.putInteger(130)
		list1.putInteger(131)
		desc1.putList(APP.instance.cID('LyrI'), list1)
		APP.instance.executeAction(APP.instance.cID('slct'), desc1, dialog_mode)

	# Make
	def step187():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(APP.instance.sID("layerSection"))
		desc1.putReference(APP.instance.cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putEnumerated(APP.instance.cID('Lyr '), APP.instance.cID('Ordn'), APP.instance.cID('Trgt'))
		desc1.putReference(APP.instance.cID('From'), ref2)
		desc2 = ps.ActionDescriptor()
		desc2.putString(APP.instance.cID('Nm  '), "Pencil Sketch")
		desc1.putObject(APP.instance.cID('Usng'), APP.instance.sID("layerSection"), desc2)
		desc1.putInteger(APP.instance.sID("layerSectionStart"), 136)
		desc1.putInteger(APP.instance.sID("layerSectionEnd"), 137)
		desc1.putString(APP.instance.cID('Nm  '), "Pencil Sketch")
		APP.instance.executeAction(APP.instance.cID('Mk  '), desc1, dialog_mode)

	# Make
	def step188():

		desc1 = ps.ActionDescriptor()
		desc1.putClass(APP.instance.cID('Nw  '), APP.instance.cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(APP.instance.cID('Chnl'), APP.instance.cID('Chnl'), APP.instance.cID('Msk '))
		desc1.putReference(APP.instance.cID('At  '), ref1)
		desc1.putEnumerated(APP.instance.cID('Usng'), APP.instance.cID('UsrM'), APP.instance.cID('RvlA'))
		APP.instance.executeAction(APP.instance.cID('Mk  '), desc1, dialog_mode)

	# Set
	def step189():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(APP.instance.cID('Lyr '), APP.instance.cID('Ordn'), APP.instance.cID('Trgt'))
		desc1.putReference(APP.instance.cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(APP.instance.cID('Usrs'), False)
		desc1.putObject(APP.instance.cID('T   '), APP.instance.cID('Lyr '), desc2)
		APP.instance.executeAction(APP.instance.cID('setd'), desc1, dialog_mode)

	# Select
	def step190():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(APP.instance.cID('Lyr '), "Layer 1")
		desc1.putReference(APP.instance.cID('null'), ref1)
		desc1.putBoolean(APP.instance.cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(139)
		desc1.putList(APP.instance.cID('LyrI'), list1)
		APP.instance.executeAction(APP.instance.cID('slct'), desc1, dialog_mode)

	# Delete
	def step191():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(APP.instance.cID('Lyr '), APP.instance.cID('Ordn'), APP.instance.cID('Trgt'))
		desc1.putReference(APP.instance.cID('null'), ref1)
		list1 = ps.ActionList()
		list1.putInteger(139)
		desc1.putList(APP.instance.cID('LyrI'), list1)
		APP.instance.executeAction(APP.instance.cID('Dlt '), desc1, dialog_mode)

	# Select Background
	def step343(): select_bg()
	
	"""

    if not draft_sketch:
        hide_layer("Layer 2")
        hide_layer("Layer 3")

    if not rough_sketch:
        hide_layer("Background copy 3")
        hide_layer("Background copy 6")
        hide_layer("Background copy 8")
        hide_layer("Background copy 9")

    if black_and_white:
        hide_layer("Background copy 11")

    # Flatten
    if manual_editing:
        render_operation.pause_sync("Sketch Action complete.")
    APP.instance.executeAction(APP.instance.cID("FltI"), None, dialog_mode)
