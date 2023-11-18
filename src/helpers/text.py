"""
TEXT HELPERS
"""
# Standard Library Imports
from typing import Union, Optional, Any

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference, ActionList
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.constants import con
from src.helpers import pixels_to_points, get_layer_dimensions
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
TEXT UTILITIES
"""


def get_font_size(layer: ArtLayer) -> float:
    """
    Get scale factor adjusted font size of a given text layer.
    @param layer: Text layer to get size of.
    """
    return round(layer.textItem.size * get_text_scale_factor(layer), 2)


def get_text_key(layer: ArtLayer) -> Any:
    """
    Get the textKey action reference from a TextLayer.
    @param layer: ArtLayer which must be a TextLayer kind.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = app.executeActionGet(reference)
    return descriptor.getObjectValue(sID('textKey'))


def apply_text_key(text_layer, text_key) -> None:
    """
    Applies a TextKey action descriptor to a given TextLayer.
    @param text_layer: ArtLayer which must be a TextLayer kind.
    @param text_key: TextKey extracted from a TextLayer that has been modified.
    """
    action, ref = ActionDescriptor(), ActionReference()
    ref.putIdentifier(sID("layer"), text_layer.id)
    action.putReference(sID("target"), ref)
    action.putObject(sID("to"), sID("textLayer"), text_key)
    app.executeAction(sID("set"), action, DialogModes.DisplayNoDialogs)


def get_line_count(layer: Optional[ArtLayer] = None) -> int:
    """
    Get the number of lines in a paragraph text layer.
    @param layer: Text layer that contains a paragraph TextItem.
    @return: Number of lines in the TextItem.
    """
    return round(pixels_to_points(get_layer_dimensions(layer)['height']) / layer.textItem.leading)


"""
MODIFYING TEXT
"""


def replace_text(layer: ArtLayer, find: str, replace: str) -> None:
    """
    Replaces target "find" text with "replace" text in a given TextLayer.
    @param layer: ArtLayer which must be a TextLayer kind.
    @param find: Text to find in the layer.
    @param replace: Text to replace the found text with.
    """
    # Establish our text key and reference text
    text_key: ActionDescriptor = get_text_key(layer)
    current_text = text_key.getString(sID("textKey"))

    # Check if our target text exists
    if find not in current_text:
        print(f"Text replacement couldn't find the text '{find}' "
              f"in layer with name '{layer.name}'!")
        return

    # Track length difference and whether replacement was made
    offset = len(replace) - len(find)
    replaced = False

    # Find the range where target text exists
    style_range = text_key.getList(sID("textStyleRange"))
    for i in range(style_range.count):
        style = style_range.getObjectValue(i)
        id_from = style.getInteger(sID("from"))
        id_to = style.getInteger(sID("to"))
        text = current_text[id_from: id_to]
        if not replaced and find in text:
            replaced = True
            style.putInteger(sID("to"), id_to + offset)
            style_range.putObject(sID("textStyleRange"), style)
        elif replaced:
            style.putInteger(sID("from"), id_from + offset)
            style.putInteger(sID("to"), id_to + offset)
            style_range.putObject(sID("textStyleRange"), style)

    # Skip applying changes if no replacement could be made
    if not replaced:
        print(f"Text replacement couldn't find the text '{find}' "
              f"in layer with name '{layer.name}'!")
        return

    # Apply changes
    text_key.putString(sID("textKey"), current_text.replace(find, replace))
    text_key.putList(sID("textStyleRange"), style_range)
    apply_text_key(layer, text_key)


def replace_text_robust(layer: ArtLayer, find: str, replace: str, targeted_replace: bool = True) -> None:
    """
    Replace all instances of `replace_this` in the specified layer with `replace_with`, using Photoshop's
    built-in search and replace feature. Slower than `replace_text`, but can handle multi-style strings.
    @param layer: Layer object to search through.
    @param find: Text string to search for.
    @param replace: Text string to replace matches with.
    @param targeted_replace: Disables layer targeting if False, if True may cause a crash on older PS versions.
    """
    # Set the active layer
    app.activeDocument.activeLayer = layer

    # Find and replace
    desc31 = ActionDescriptor()
    ref3 = ActionReference()
    desc32 = ActionDescriptor()
    ref3.putProperty(sID("property"), sID("findReplace"))
    ref3.putEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc31.putReference(sID("target"), ref3)
    desc32.putString(sID("find"), f"""{find}""")
    desc32.putString(sID("replace"), f"""{replace}""")
    desc32.putBoolean(
        sID("checkAll"),  # Targeted replace doesn't work on old PS versions
        False if targeted_replace and app.supports_target_text_replace() else True
    )
    desc32.putBoolean(sID("forward"), True)
    desc32.putBoolean(sID("caseSensitive"), True)
    desc32.putBoolean(sID("wholeWord"), False)
    desc32.putBoolean(sID("ignoreAccents"), True)
    desc31.putObject(sID("using"), sID("findReplace"), desc32)
    try:
        app.executeAction(sID("findReplace"), desc31, NO_DIALOG)
    except PS_EXCEPTIONS:
        replace_text_robust(layer, find, replace, False)


def remove_trailing_text(layer: ArtLayer, idx: int) -> None:
    """
    Remove text after certain index from a TextLayer.
    @param layer: TextLayer containing the text to modify.
    @param idx: Index to remove after.
    """
    # Establish our text key and descriptor ID's
    app.activeDocument.activeLayer = layer
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(sID("textKey"))
    new_text = current_text[0:idx - 1]
    idFrom = sID("from")
    idTo = sID("to")

    # Find the range where target text exists
    for n in [sID("textStyleRange"), sID("paragraphStyleRange")]:

        # Iterate over list of style ranges
        style_ranges: list[ActionDescriptor] = []
        text_range = key.getList(n)
        for i in range(text_range.count):

            # Get position of this style range
            style = text_range.getObjectValue(i)
            i_left = style.getInteger(idFrom)
            i_right = style.getInteger(idTo)

            if idx <= i_left:
                # Skip text ouf bounds
                continue
            elif i_left < idx <= i_right:
                # Reduce "end" position
                style.putInteger(idTo, idx - 1)
            style_ranges.append(style)

        # Apply changes
        style_range = ActionList()
        for r in style_ranges:
            style_range.putObject(n, r)
        key.putList(n, style_range)
        key.putString(sID("textKey"), new_text)
    apply_text_key(layer, key)


def remove_leading_text(layer: ArtLayer, idx: int) -> None:
    """
    Remove text up to a certain index from a TextLayer.
    @param layer: TextLayer containing the text to modify.
    @param idx: Index to remove up to.
    """
    # Establish our text key and descriptor ID's
    app.activeDocument.activeLayer = layer
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(sID("textKey"))
    new_text = current_text[idx + 1:]
    idFrom = sID("from")
    idTo = sID("to")
    offset = idx + 1

    # Find the range where target text exists
    for n in [sID("textStyleRange"), sID("paragraphStyleRange")]:

        # Iterate over list of style ranges
        style_ranges: list[ActionDescriptor] = []
        text_range = key.getList(n)
        for i in range(text_range.count):

            # Get position of this style range
            style = text_range.getObjectValue(i)
            i_left = style.getInteger(idFrom)
            i_right = style.getInteger(idTo)

            # Compare position to excluded indexes
            if i_right < idx:
                # Remove entirely
                continue
            elif i_left < idx <= i_right:
                # Zero "to" position
                style.putInteger(idTo, 0)
            else:
                # Offset "to" position
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


"""
GETTING TEXT ITEM SIZE
"""


def get_text_scale_factor(
    layer: Optional[ArtLayer] = None,
    axis: Optional[Union[str, list]] = 'yy',
    text_key = None
) -> Union[int, float, list[Union[int, float]]]:
    """
    Get the scale factor of the document for changing text size.
    @param layer: The layer to make active and run the check on.
    @param axis: Scale axis or list of scale axis to check
                 (xx: horizontal, yy: vertical)
    @param text_key: textKey action descriptor
    @return: Float scale factor
    """
    # Get the textKey if not provided
    if not text_key:
        # Get text key
        text_key = get_text_key(layer)

    # Check for the "transform" descriptor
    if text_key.hasKey(sID('transform')):
        transform = text_key.getObjectValue(sID('transform'))
        # Check list of axis
        if isinstance(axis, list):
            return [transform.getUnitDoubleValue(sID(n)) for n in axis]
        # Check string axis
        if isinstance(axis, str):
            return transform.getUnitDoubleValue(sID(axis))
    return 1 if not isinstance(axis, list) else [1] * len(axis)


"""
APPLYING TEXT CHANGES
"""


def set_text_leading(layer: ArtLayer, size: Union[float, int]) -> None:
    """
    Manually assign font leading to a layer using action descriptors.
    @param layer: Layer containing TextItem to change leading of.
    @param size: New textItem font leading.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    ref1.putProperty(sID("property"), sID("textStyle"))
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putInteger(sID("textOverrideFeatureName"), 808465461)
    desc2.putInteger(sID("typeStyleOperationType"), 3)
    desc2.putUnitDouble(sID("leading"), sID("pointsUnit"), size)
    desc1.putObject(sID("to"), sID("textStyle"), desc2)
    app.executeaction(sID("set"), desc1, NO_DIALOG)


def set_text_size(layer: ArtLayer, size: Union[float, int]) -> None:
    """
    Manually assign font size to a layer using action descriptors.
    @param layer: Layer containing TextItem to change size of.
    @param size: New textItem font size.
    """
    # Set the new size
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    ref1.putProperty(sID("property"), sID("textStyle"))
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putInteger(sID("textOverrideFeatureName"), 808465458)
    desc2.putInteger(sID("typeStyleOperationType"), 3)
    desc2.putUnitDouble(sID("size"), sID("pointsUnit"), size)
    desc1.putObject(sID("to"), sID("textStyle"), desc2)
    app.ExecuteAction(sID("set"), desc1, NO_DIALOG)


def set_composer_single_line(layer: ArtLayer) -> None:
    """
    Set text layer to single line composer.
    @param layer: Layer containing TextItem to set composer for.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    ref1.putProperty(sID("property"), sID("textStyle"))
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.PutInteger(sID("textOverrideFeatureName"),  808464691)
    desc2.PutBoolean(sID("textEveryLineComposer"), False)
    desc1.PutObject(sID("to"), sID("paragraphStyle"),  desc2)
    app.Executeaction(sID("set"), desc1,  NO_DIALOG)


"""
FONTS
"""


def set_font(layer: ArtLayer, font_name: str) -> None:
    """
    Set the font of a given TextItem layer using a given name.
    @param layer: ArtLayer containing TextItem.
    @param font_name:  Name of the font to set.
    """
    layer.textItem.font = app.fonts.getByName(font_name).postScriptName
