"""
* Helpers: Text Items
"""
# Standard Library Imports
from typing import Union, Optional, Any

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference, ActionList
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document

# Local Imports
from src import APP
from src.helpers.bounds import get_layer_height
from src.helpers.document import pixels_to_points
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
* Text Utils
"""


def get_font_size(layer: ArtLayer) -> float:
    """Get scale factor adjusted font size of a given text layer.

    Args:
        layer: Text layer to get size of.
    """
    return round(layer.textItem.size * get_text_scale_factor(layer), 2)


def get_text_key(layer: ArtLayer) -> Any:
    """Get the textKey action reference from a TextLayer.

    Args:
        layer: ArtLayer which must be a TextLayer kind.
    """
    reference = ActionReference()
    reference.putIdentifier(sID('layer'), layer.id)
    descriptor = APP.executeActionGet(reference)
    return descriptor.getObjectValue(sID('textKey'))


def apply_text_key(text_layer, text_key) -> None:
    """Applies a TextKey action descriptor to a given TextLayer.

    Args:
        text_layer: ArtLayer which must be a TextLayer kind.
        text_key: TextKey extracted from a TextLayer that has been modified.
    """
    action, ref = ActionDescriptor(), ActionReference()
    ref.putIdentifier(sID("layer"), text_layer.id)
    action.putReference(sID("target"), ref)
    action.putObject(sID("to"), sID("textLayer"), text_key)
    APP.executeAction(sID("set"), action, NO_DIALOG)


def get_line_count(layer: Optional[ArtLayer] = None, docref: Optional[Document] = None) -> int:
    """Get the number of lines in a paragraph text layer.

    Args:
        layer: Text layer that contains a paragraph TextItem.
        docref: Reference document, use active if not provided.

    Returns:
        Number of lines in the TextItem.
    """
    docref = docref or APP.activeDocument
    return round(pixels_to_points(
        number=get_layer_height(layer),
        docref=docref
    ) / layer.textItem.leading)


"""
* Modifying Text
"""


def replace_text(layer: ArtLayer, find: str, replace: str) -> None:
    """Replaces target "find" text with "replace" text in a given TextLayer.

    Args:
        layer: ArtLayer which must be a TextLayer kind.
        find: Text to find in the layer.
        replace: Text to replace the found text with.
    """
    # Establish our text key and reference text
    idTextKey = sID("textKey")
    text_key: ActionDescriptor = get_text_key(layer)
    current_text = text_key.getString(idTextKey)

    # Check if our target text exists
    if find not in current_text:
        print(f"Text replacement couldn't find the text '{find}' "
              f"in layer with name '{layer.name}'!")
        return

    # Reusable ID's
    idTo = sID('to')
    idFrom = sID('from')
    idTextStyleRange = sID('textStyleRange')

    # Track length difference and whether replacement was made
    offset = len(replace) - len(find)
    replaced = False

    # Find the range where target text exists
    style_range = text_key.getList(idTextStyleRange)
    for i in range(style_range.count):
        style = style_range.getObjectValue(i)
        idxFrom = style.getInteger(idFrom)
        idxTo = style.getInteger(idTo)
        if not replaced and find in current_text[idxFrom: idxTo]:
            # Found the text to replace
            replaced = True
            style.putInteger(idTo, idxTo + offset)
            style_range.putObject(idTextStyleRange, style)
        elif replaced:
            # Replacement already made, offset the remaining ranges
            style.putInteger(idFrom, idxFrom + offset)
            style.putInteger(idTo, idxTo + offset)
            style_range.putObject(idTextStyleRange, style)

    # Skip applying changes if no replacement could be made
    if not replaced:
        print(f"Text replacement couldn't find the text '{find}' "
              f"in layer with name '{layer.name}'!")
        return

    # Apply changes
    text_key.putString(idTextKey, current_text.replace(find, replace))
    text_key.putList(idTextStyleRange, style_range)
    apply_text_key(layer, text_key)


def replace_text_legacy(
    find: str,
    replace: str,
    layer: Optional[ArtLayer] = None,
    targeted_replace: bool = True
) -> None:
    """Replace all instances of `replace_this` in the specified layer with `replace_with`, using Photoshop's
    built-in search and replace feature. Slower than `replace_text`, but can handle strings broken into
    multiple textStyle ranges.

    Args:
        find: Text string to search for.
        replace: Text string to replace matches with.
        layer: Layer object to search through, use active if not provided.
        targeted_replace: Disables layer targeting if False, if True may cause a crash on older PS versions.
    """
    # Set the active layer
    if layer:
        APP.activeDocument.activeLayer = layer

    # Find and replace
    idFindReplace = sID("findReplace")
    desc31 = ActionDescriptor()
    ref3 = ActionReference()
    desc32 = ActionDescriptor()
    ref3.putProperty(sID("property"), idFindReplace)
    ref3.putEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc31.putReference(sID("target"), ref3)
    desc32.putString(sID("find"), f"""{find}""")
    desc32.putString(sID("replace"), f"""{replace}""")
    desc32.putBoolean(
        sID("checkAll"),  # Targeted replace doesn't work on old PS versions
        False if targeted_replace and APP.supports_target_text_replace() else True
    )
    desc32.putBoolean(sID("forward"), True)
    desc32.putBoolean(sID("caseSensitive"), True)
    desc32.putBoolean(sID("wholeWord"), False)
    desc32.putBoolean(sID("ignoreAccents"), True)
    desc31.putObject(sID("using"), idFindReplace, desc32)
    try:
        APP.executeAction(idFindReplace, desc31, NO_DIALOG)
    except PS_EXCEPTIONS:
        replace_text_legacy(
            find=find,
            replace=replace,
            layer=layer,
            targeted_replace=False)


def remove_trailing_text(layer: ArtLayer, idx: int) -> None:
    """Remove text after certain index from a TextLayer.

    Args:
        layer: TextLayer containing the text to modify.
        idx: Index to remove after.
    """
    # Action Descriptor ID's
    idTextKey = sID("textKey")
    idFrom = sID("from")
    idTo = sID("to")

    # Establish our text key and descriptor ID's
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(idTextKey)
    new_text = current_text[0:idx - 1]

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
        key.putString(idTextKey, new_text)
    apply_text_key(layer, key)


def remove_leading_text(layer: ArtLayer, idx: int) -> None:
    """Remove text up to a certain index from a TextLayer.

    Args:
        layer: TextLayer containing the text to modify.
        idx: Index to remove up to.
    """
    # Action Descriptor ID's
    idTextKey = sID("textKey")
    idFrom = sID("from")
    idTo = sID("to")

    # Establish our text key and descriptor ID's
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(idTextKey)
    new_text = current_text[idx + 1:]
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
        key.putString(idTextKey, new_text)
    apply_text_key(layer, key)


"""
* Text Item Size
"""


def get_text_scale_factor(
    layer: Optional[ArtLayer] = None,
    axis: Optional[Union[str, list]] = 'yy',
    text_key = None
) -> Union[int, float, list[Union[int, float]]]:
    """Get the scale factor of the document for changing text size.

    Args:
        layer: The layer to make active and run the check on.
        axis: Scale axis or list of scale axis to check (xx: horizontal, yy: vertical).
        text_key: textKey action descriptor

    Returns:
        Float scale factor
    """
    # Get the textKey if not provided
    if not text_key:
        # Get text key
        text_key = get_text_key(layer)
    idTransform = sID('transform')

    # Check for the "transform" descriptor
    if text_key.hasKey(idTransform):
        transform = text_key.getObjectValue(idTransform)
        # Check list of axis
        if isinstance(axis, list):
            return [transform.getUnitDoubleValue(sID(n)) for n in axis]
        # Check string axis
        if isinstance(axis, str):
            return transform.getUnitDoubleValue(sID(axis))
    return 1 if not isinstance(axis, list) else [1] * len(axis)


"""
* Text Alignment
"""


def align_text(action_list: ActionList, start: int, end: int, alignment: str = "right") -> ActionList:
    """Align a slice of text in an action using given alignment.

    Examples:
        Used to align the quote credit of --Name to the right on some classic cards.

    Args:
        action_list: Action list to add this action to
        start: Starting index of the quote string
        end: Ending index of the quote string
        alignment: left, right, or center

    Returns:
        Returns the existing ActionDescriptor with changes applied
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    paraStyle = sID("paragraphStyle")
    d1.putInteger(sID("from"), start)
    d1.putInteger(sID("to"), end)
    d2.putBoolean(sID("styleSheetHasParent"), True)
    d2.putEnumerated(sID("align"), sID("alignmentType"), sID(alignment))
    d1.putObject(paraStyle, paraStyle, d2)
    action_list.putObject(sID("paragraphStyleRange"), d1)
    return action_list


def align_text_right(action_list: ActionList, start: int, end: int) -> None:
    """Utility shorthand to call `align_text` with 'right' alignment."""
    align_text(action_list, start, end, "right")


def align_text_left(action_list: ActionList, start: int, end: int) -> None:
    """Utility shorthand to call `align_text` with 'left' alignment."""
    align_text(action_list, start, end, "left")


def align_text_center(action_list: ActionList, start: int, end: int) -> None:
    """Utility shorthand to call `align_text` with 'center' alignment."""
    align_text(action_list, start, end, "center")


"""
* Setting Text Properties
"""


def set_space_after(space: Union[int, float]) -> None:
    """Manually assign the 'space after' property for a paragraph text layer.

    Args:
        space: The 'space after' value to set.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    deesc2 = ActionDescriptor()
    ref1.PutProperty(sID("property"), sID("paragraphStyle"))
    ref1.PutEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc1.PutReference(sID("target"), ref1)
    deesc2.PutInteger(sID("textOverrideFeatureName"), 808464438)
    deesc2.PutUnitDouble(sID("spaceAfter"), sID("pointsUnit"), space)
    desc1.PutObject(sID("to"), sID("paragraphStyle"), deesc2)
    APP.executeAction(sID("set"), desc1, NO_DIALOG)


def set_text_leading(layer: ArtLayer, leading: Union[float, int]) -> None:
    """Manually assign font leading to a text layer using action descriptors.

    Args:
        layer: Layer containing TextItem to change leading of.
        leading: New TextItem font leading.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    ref1.putProperty(sID("property"), sID("textStyle"))
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putUnitDouble(sID("leading"), sID("pointsUnit"), leading)
    desc1.putObject(sID("to"), sID("textStyle"), desc2)
    APP.executeaction(sID("set"), desc1, NO_DIALOG)


def set_text_size(layer: ArtLayer, size: Union[float, int]) -> None:
    """Manually assign font size to a text layer using action descriptors.

    Args:
        layer: Layer containing TextItem to change size of.
        size: New TextItem font size.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    textStyle = sID("textStyle")
    ref1.putProperty(sID("property"), textStyle)
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putUnitDouble(sID("size"), sID("pointsUnit"), size)
    desc1.putObject(sID("to"), textStyle, desc2)
    APP.executeAction(sID("set"), desc1, NO_DIALOG)


def set_text_size_and_leading(layer: ArtLayer, size: Union[int, float], leading: Union[int, float]) -> None:
    """Manually assign font size and leading space to a text layer using action descriptors.

    Args:
        layer: Layer containing TextItem to change size of.
        size: New TextItem font size.
        leading: New TextItem font leading.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    textStyle = sID("textStyle")
    ptUnit = sID("pointsUnit")
    ref1.putProperty(sID("property"), textStyle)
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putUnitDouble(sID("size"), ptUnit, size)
    desc2.putUnitDouble(sID("leading"), ptUnit, leading)
    desc1.putObject(sID("to"), textStyle, desc2)
    APP.executeAction(sID("set"), desc1, NO_DIALOG)


def set_composer(layer: ArtLayer, every: bool = False) -> None:
    """Set text layer composer to single line or multi line.

    Args:
        layer: Layer containing TextItem to set composer for.
        every: Set to 'Every-line Composer' if True, otherwise 'Single-line Composer'.
            By default, set to 'Single-line Composer'.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    paraStyle = sID("paragraphStyle")
    ref1.putProperty(sID("property"), paraStyle)
    ref1.putIdentifier(sID("textLayer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc2.putBoolean(sID("textEveryLineComposer"), every)
    desc1.putObject(sID("to"), paraStyle, desc2)
    APP.executeaction(sID("set"), desc1, NO_DIALOG)


def set_composer_single_line(layer: ArtLayer) -> None:
    """Shorthand redirect to 'set_composer' applying 'Single-line Composer'."""
    set_composer(layer)


def set_composer_every_line(layer: ArtLayer) -> None:
    """Shorthand redirect to 'set_composer' applying 'Every-line Composer'."""
    set_composer(layer, every=True)


"""
* Fonts
"""


def set_font(layer: ArtLayer, font_name: str) -> None:
    """Set the font of a given TextItem layer using a font's ordinary name.

    Note:
        Setting font using the 'postScriptName' is faster. For example:
            layer.textItem.font = 'Beleren-Bold'

    Args:
        layer: ArtLayer containing TextItem.
        font_name:  Name of the font to set.
    """
    layer.textItem.font = APP.fonts.getByName(font_name).postScriptName
