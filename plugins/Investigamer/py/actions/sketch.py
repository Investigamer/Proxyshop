"""
* Sketchify Action Module
"""

from photoshop.api import ActionDescriptor, ActionList, ActionReference
from photoshop.api.enumerations import DialogModes

from src import APP


def run():
    """Trix old sketchify Steps."""

    # Duplicate
    def step1(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putProperty(APP.instance.cID("Lyr "), APP.instance.cID("Bckg"))
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putString(APP.instance.cID("Nm  "), "Layer 1 copy")
        desc1.putInteger(APP.instance.cID("Vrsn"), 5)
        APP.instance.executeAction(APP.instance.cID("Dplc"), desc1, dialog_mode)

    # Invert
    def step2(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        APP.instance.executeAction(
            APP.instance.cID("Invr"), ActionDescriptor(), dialog_mode
        )

    # Gaussian Blur
    def step3(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        desc1.putUnitDouble(APP.instance.cID("Rds "), APP.instance.cID("#Pxl"), 65)
        APP.instance.executeAction(APP.instance.sID("gaussianBlur"), desc1, dialog_mode)

    # Set
    def step4(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putEnumerated(
            APP.instance.cID("Md  "), APP.instance.cID("BlnM"), APP.instance.cID("CDdg")
        )
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Make
    def step5(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putClass(APP.instance.cID("AdjL"))
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc3 = ActionDescriptor()
        desc3.putEnumerated(
            APP.instance.sID("presetKind"),
            APP.instance.sID("presetKindType"),
            APP.instance.sID("presetKindDefault"),
        )
        desc2.putObject(APP.instance.cID("Type"), APP.instance.cID("Lvls"), desc3)
        desc1.putObject(APP.instance.cID("Usng"), APP.instance.cID("AdjL"), desc2)
        APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)

    # Set
    def step6(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("AdjL"), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putEnumerated(
            APP.instance.sID("presetKind"),
            APP.instance.sID("presetKindType"),
            APP.instance.sID("presetKindCustom"),
        )
        list1 = ActionList()
        desc3 = ActionDescriptor()
        ref2 = ActionReference()
        ref2.putEnumerated(
            APP.instance.cID("Chnl"), APP.instance.cID("Chnl"), APP.instance.cID("Cmps")
        )
        desc3.putReference(APP.instance.cID("Chnl"), ref2)
        list2 = ActionList()
        list2.putInteger(91)
        list2.putInteger(255)
        desc3.putList(APP.instance.cID("Inpt"), list2)
        desc3.putDouble(APP.instance.cID("Gmm "), 0.66)
        list1.putObject(APP.instance.cID("LvlA"), desc3)
        desc2.putList(APP.instance.cID("Adjs"), list1)
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lvls"), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Make
    def step7(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putClass(APP.instance.cID("AdjL"))
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc3 = ActionDescriptor()
        desc3.putEnumerated(
            APP.instance.sID("presetKind"),
            APP.instance.sID("presetKindType"),
            APP.instance.sID("presetKindDefault"),
        )
        desc3.putInteger(APP.instance.cID("Rd  "), 40)
        desc3.putInteger(APP.instance.cID("Yllw"), 60)
        desc3.putInteger(APP.instance.cID("Grn "), 40)
        desc3.putInteger(APP.instance.cID("Cyn "), 60)
        desc3.putInteger(APP.instance.cID("Bl  "), 20)
        desc3.putInteger(APP.instance.cID("Mgnt"), 80)
        desc3.putBoolean(APP.instance.sID("useTint"), False)
        desc4 = ActionDescriptor()
        desc4.putDouble(APP.instance.cID("Rd  "), 225)
        desc4.putDouble(APP.instance.cID("Grn "), 211)
        desc4.putDouble(APP.instance.cID("Bl  "), 179)
        desc3.putObject(
            APP.instance.sID("tintColor"), APP.instance.sID("RGBColor"), desc4
        )
        desc2.putObject(APP.instance.cID("Type"), APP.instance.cID("BanW"), desc3)
        desc1.putObject(APP.instance.cID("Usng"), APP.instance.cID("AdjL"), desc2)
        APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)

    # Set
    def step8(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putProperty(APP.instance.cID("Chnl"), APP.instance.sID("selection"))
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putEnumerated(
            APP.instance.cID("T   "), APP.instance.cID("Ordn"), APP.instance.cID("Al  ")
        )
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Copy Merged
    def step9(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        APP.instance.executeAction(
            APP.instance.sID("copyMerged"), ActionDescriptor(), dialog_mode
        )

    # Paste
    def step10(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        desc1.putEnumerated(
            APP.instance.cID("AntA"), APP.instance.cID("Annt"), APP.instance.cID("Anno")
        )
        desc1.putClass(APP.instance.cID("As  "), APP.instance.cID("Pxel"))
        APP.instance.executeAction(APP.instance.cID("past"), desc1, dialog_mode)

    # Filter Gallery
    def step11(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        desc1.putEnumerated(
            APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("GlwE")
        )
        desc1.putInteger(APP.instance.cID("EdgW"), 1)
        desc1.putInteger(APP.instance.cID("EdgB"), 20)
        desc1.putInteger(APP.instance.cID("Smth"), 15)
        APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Invert
    def step12(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        APP.instance.executeAction(
            APP.instance.cID("Invr"), ActionDescriptor(), dialog_mode
        )

    # Blend mode "Multiply"
    # Step 13 and Step 20
    def blend_mode_multiply(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putEnumerated(
            APP.instance.cID("Md  "), APP.instance.cID("BlnM"), APP.instance.cID("Mltp")
        )
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Set
    def step14(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 60)
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Select
    def step15(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putName(APP.instance.cID("Lyr "), "Black & White 1")
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putBoolean(APP.instance.cID("MkVs"), False)
        list1 = ActionList()
        list1.putInteger(6)
        desc1.putList(APP.instance.cID("LyrI"), list1)
        APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)

    # Make
    def step16(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putClass(APP.instance.cID("Lyr "))
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putInteger(APP.instance.cID("LyrI"), 8)
        APP.instance.executeAction(APP.instance.cID("Mk  "), desc1, dialog_mode)

    # Select
    def step17(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putName(APP.instance.cID("Lyr "), "Layer 2")
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putBoolean(APP.instance.cID("MkVs"), False)
        list1 = ActionList()
        list1.putInteger(7)
        desc1.putList(APP.instance.cID("LyrI"), list1)
        APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)

    # Fill
    def step18(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        desc1.putEnumerated(
            APP.instance.cID("Usng"), APP.instance.cID("FlCn"), APP.instance.cID("BckC")
        )
        APP.instance.executeAction(APP.instance.cID("Fl  "), desc1, dialog_mode)

    # Filter Gallery
    def step19(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        desc1.putEnumerated(
            APP.instance.cID("GEfk"), APP.instance.cID("GEft"), APP.instance.cID("Txtz")
        )
        desc1.putEnumerated(
            APP.instance.cID("TxtT"), APP.instance.cID("TxtT"), APP.instance.cID("TxSt")
        )
        desc1.putInteger(APP.instance.cID("Scln"), 100)
        desc1.putInteger(APP.instance.cID("Rlf "), 4)
        desc1.putEnumerated(
            APP.instance.cID("LghD"), APP.instance.cID("LghD"), APP.instance.cID("LDTp")
        )
        desc1.putBoolean(APP.instance.cID("InvT"), False)
        APP.instance.executeAction(1195730531, desc1, dialog_mode)

    # Set
    def step21(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 70)
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Select
    def step22(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putName(APP.instance.cID("Lyr "), "Black & White 1")
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putBoolean(APP.instance.cID("MkVs"), False)
        list1 = ActionList()
        list1.putInteger(6)
        desc1.putList(APP.instance.cID("LyrI"), list1)
        APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)

    # Set
    def step23(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 50)
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Select
    def step24(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putName(APP.instance.cID("Lyr "), "Background")
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putBoolean(APP.instance.cID("MkVs"), False)
        list1 = ActionList()
        list1.putInteger(1)
        desc1.putList(APP.instance.cID("LyrI"), list1)
        APP.instance.executeAction(APP.instance.cID("slct"), desc1, dialog_mode)

    # Duplicate
    def step25(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc1.putString(APP.instance.cID("Nm  "), "top adjustment")
        desc1.putInteger(APP.instance.cID("Vrsn"), 5)
        list1 = ActionList()
        list1.putInteger(35)
        desc1.putList(APP.instance.cID("Idnt"), list1)
        APP.instance.executeAction(APP.instance.cID("Dplc"), desc1, dialog_mode)

    # Move
    def step26(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        ref2 = ActionReference()
        ref2.putIndex(APP.instance.cID("Lyr "), 7)
        desc1.putReference(APP.instance.cID("T   "), ref2)
        desc1.putBoolean(APP.instance.cID("Adjs"), False)
        desc1.putInteger(APP.instance.cID("Vrsn"), 5)
        list1 = ActionList()
        list1.putInteger(35)
        desc1.putList(APP.instance.cID("LyrI"), list1)
        APP.instance.executeAction(APP.instance.cID("move"), desc1, dialog_mode)

    # Set
    def step27(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putUnitDouble(APP.instance.cID("Opct"), APP.instance.cID("#Prc"), 40)
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Set
    def step28(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        desc1 = ActionDescriptor()
        ref1 = ActionReference()
        ref1.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc1.putReference(APP.instance.cID("null"), ref1)
        desc2 = ActionDescriptor()
        desc2.putEnumerated(
            APP.instance.cID("Md  "), APP.instance.cID("BlnM"), APP.instance.cID("HrdL")
        )
        desc1.putObject(APP.instance.cID("T   "), APP.instance.cID("Lyr "), desc2)
        APP.instance.executeAction(APP.instance.cID("setd"), desc1, dialog_mode)

    # Merge Visible
    def step29(enabled: bool = True, dialog: bool = False):
        if not enabled:
            return
        dialog_mode = (
            DialogModes.DisplayAllDialogs if dialog else DialogModes.DisplayNoDialogs
        )
        APP.instance.executeAction(
            APP.instance.sID("mergeVisible"), ActionDescriptor(), dialog_mode
        )

    # Run each step
    step1()  # Duplicate
    step2()  # Invert
    step3()  # Gaussian Blur
    step4()  # Set
    step5()  # Make
    step6()  # Set
    step7()  # Make
    step8()  # Set
    step9()  # Copy Merged
    step10()  # Paste
    step11()  # Filter Gallery
    step12()  # Invert
    blend_mode_multiply()  # Set
    step14()  # Set
    step15()  # Select
    step16()  # Make
    step17()  # Select
    step18()  # Fill
    step19()  # Filter Gallery
    blend_mode_multiply()  # Set
    step21()  # Set
    step22()  # Select
    step23()  # Set
    step24()  # Select
    step25()  # Duplicate
    step26()  # Move
    step27()  # Set
    step28()  # Set
    step29()  # Merge
