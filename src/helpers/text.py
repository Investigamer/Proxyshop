"""
* Helpers: Text Items
"""

from collections.abc import Iterable, Sequence
from logging import getLogger
from math import fabs
from typing import Literal, overload

from photoshop.api import ActionDescriptor, ActionList, ActionReference, SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api._selection import Selection
from photoshop.api.enumerations import DialogModes, ElementPlacement, LayerKind
from photoshop.api.text_item import TextItem

from src import APP
from src.helpers.bounds import (
    get_layer_height,
    get_layer_width,
    get_textbox_width,
    get_width_no_effects,
)
from src.helpers.descriptors import (
    set_or_copy_color,
    set_or_copy_enumerated,
    set_or_copy_integer,
    set_or_copy_string,
    set_or_copy_unit_double,
)
from src.helpers.document import pixels_to_points
from src.helpers.position import (
    RefSide,
    check_bounds_overlap,
    check_reference_overlap,
    spread_layers_over_reference,
)
from src.helpers.shapes import create_shape_layer
from src.utils.adobe import PS_EXCEPTIONS, ReferenceLayer
from src.utils.uxp.shape import ShapeOperation, merge_shapes
from src.utils.uxp.text import create_text_layer_with_path

_logger = getLogger(__name__)

"""
* Text Utils
"""


def get_font_size(layer: ArtLayer, raw_size: float | None = None) -> float:
    """Get scale factor adjusted font size of a given text layer.

    Args:
        layer: Text layer to get size of.
    """
    return round(
        (layer.textItem.size if raw_size is None else raw_size)
        * get_text_scale_factor(layer),
        2,
    )


def get_text_key(layer: ArtLayer) -> ActionDescriptor:
    """Get the textKey action reference from a TextLayer.

    Args:
        layer: ArtLayer which must be a TextLayer kind.
    """
    reference = ActionReference()
    reference.putIdentifier(APP.instance.sID("layer"), layer.id)
    descriptor = APP.instance.executeActionGet(reference)
    return descriptor.getObjectValue(APP.instance.sID("textKey"))


def apply_text_key(text_layer: ArtLayer, text_key: ActionDescriptor) -> None:
    """Applies a TextKey action descriptor to a given TextLayer.

    Args:
        text_layer: ArtLayer which must be a TextLayer kind.
        text_key: TextKey extracted from a TextLayer that has been modified.
    """
    action, ref = ActionDescriptor(), ActionReference()
    ref.putIdentifier(APP.instance.sID("layer"), text_layer.id)
    action.putReference(APP.instance.sID("target"), ref)
    action.putObject(APP.instance.sID("to"), APP.instance.sID("textLayer"), text_key)
    APP.instance.executeAction(
        APP.instance.sID("set"), action, DialogModes.DisplayNoDialogs
    )


def get_line_count(layer: ArtLayer, docref: Document | None = None) -> int:
    """Get the number of lines in a paragraph text layer.

    Args:
        layer: Text layer that contains a paragraph TextItem.
        docref: Reference document, use active if not provided.

    Returns:
        Number of lines in the TextItem.
    """
    docref = docref or APP.instance.activeDocument
    return round(
        pixels_to_points(number=get_layer_height(layer), docref=docref)
        / layer.textItem.leading
    )


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
    idTextKey = APP.instance.sID("textKey")
    text_key: ActionDescriptor = get_text_key(layer)
    current_text = text_key.getString(idTextKey)

    # Check if our target text exists
    if find not in current_text:
        _logger.warning(f"Couldn't find the text '{find}' in layer: '{layer.name}'")
        return

    # Reusable ID's
    idTo = APP.instance.sID("to")
    idFrom = APP.instance.sID("from")
    idTextStyleRange = APP.instance.sID("textStyleRange")

    # Track length difference and whether replacement was made
    offset = len(replace) - len(find)
    replaced = False

    # Find the range where target text exists
    style_ranges = text_key.getList(idTextStyleRange)
    for i in range(style_ranges.count):
        style_range = style_ranges.getObjectValue(i)
        idxFrom = style_range.getInteger(idFrom)
        idxTo = style_range.getInteger(idTo)
        if not replaced and find in current_text[idxFrom:idxTo]:
            # Found the text to replace
            replaced = True
            style_range.putInteger(idTo, idxTo + offset)
            style_ranges.putObject(idTextStyleRange, style_range)
        elif replaced:
            # Replacement already made, offset the remaining ranges
            style_range.putInteger(idFrom, idxFrom + offset)
            style_range.putInteger(idTo, idxTo + offset)
            style_ranges.putObject(idTextStyleRange, style_range)

    # Skip applying changes if no replacement could be made
    if not replaced:
        _logger.warning(f"Couldn't replace the text '{find}' in layer: {layer.name}")
        return

    # Apply changes
    text_key.putString(idTextKey, current_text.replace(find, replace))
    text_key.putList(idTextStyleRange, style_ranges)
    apply_text_key(layer, text_key)


def replace_text_legacy(
    find: str,
    replace: str,
    layer: ArtLayer | None = None,
    targeted_replace: bool = True,
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
        APP.instance.activeDocument.activeLayer = layer

    # Find and replace
    idFindReplace = APP.instance.sID("findReplace")
    desc31 = ActionDescriptor()
    ref3 = ActionReference()
    desc32 = ActionDescriptor()
    ref3.putProperty(APP.instance.sID("property"), idFindReplace)
    ref3.putEnumerated(
        APP.instance.sID("textLayer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    desc31.putReference(APP.instance.sID("target"), ref3)
    desc32.putString(APP.instance.sID("find"), find)
    desc32.putString(APP.instance.sID("replace"), replace)
    desc32.putBoolean(
        APP.instance.sID(
            "checkAll"
        ),  # Targeted replace doesn't work on old PS versions
        not (targeted_replace and APP.instance.supports_target_text_replace),
    )
    desc32.putBoolean(APP.instance.sID("forward"), True)
    desc32.putBoolean(APP.instance.sID("caseSensitive"), True)
    desc32.putBoolean(APP.instance.sID("wholeWord"), False)
    desc32.putBoolean(APP.instance.sID("ignoreAccents"), True)
    desc31.putObject(APP.instance.sID("using"), idFindReplace, desc32)
    try:
        APP.instance.executeAction(idFindReplace, desc31, DialogModes.DisplayNoDialogs)
    except PS_EXCEPTIONS:
        replace_text_legacy(
            find=find, replace=replace, layer=layer, targeted_replace=False
        )


def remove_trailing_text(layer: ArtLayer, idx: int) -> None:
    """Remove text after certain index from a TextLayer.

    Args:
        layer: TextLayer containing the text to modify.
        idx: Index to remove after.
    """
    # Action Descriptor ID's
    idTextKey = APP.instance.sID("textKey")
    idFrom = APP.instance.sID("from")
    idTo = APP.instance.sID("to")

    # Establish our text key and descriptor ID's
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(idTextKey)
    new_text = current_text[0 : idx - 1]

    # Find the range where target text exists
    for n in [
        APP.instance.sID("textStyleRange"),
        APP.instance.sID("paragraphStyleRange"),
    ]:
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
    idTextKey = APP.instance.sID("textKey")
    idFrom = APP.instance.sID("from")
    idTo = APP.instance.sID("to")

    # Establish our text key and descriptor ID's
    key: ActionDescriptor = get_text_key(layer)
    current_text = key.getString(idTextKey)
    new_text = current_text[idx + 1 :]
    offset = idx + 1

    # Find the range where target text exists
    for n in [
        APP.instance.sID("textStyleRange"),
        APP.instance.sID("paragraphStyleRange"),
    ]:
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


def set_text_style_values(
    text_style: ActionDescriptor,
    source: ActionDescriptor | None = None,
    font: str | None = None,
    size: float | None = None,
    leading: float | None = None,
    kerning: Literal["metricsKern", "opticalKern", "manual"] | None = None,
    tracking: int | None = None,
    color: SolidColor | None = None,
    language: str | None = None,
    reference_layer: ArtLayer | None = None,
) -> None:
    """Set text style descriptor values."""
    set_or_copy_string(APP.instance.sID("fontPostScriptName"), text_style, source, font)
    set_or_copy_unit_double(
        APP.instance.sID("size"),
        text_style,
        source,
        unit_type=APP.instance.sID("pointsUnit"),
        unit_value=size,
        source_value_hook=(lambda value: get_font_size(reference_layer, value))
        if reference_layer
        else None,
    )
    set_or_copy_unit_double(
        APP.instance.sID("leading"),
        text_style,
        source,
        unit_type=APP.instance.sID("pointsUnit"),
        unit_value=leading,
    )
    kern_id = APP.instance.sID("autoKern")
    set_or_copy_enumerated(
        kern_id,
        text_style,
        source,
        enum_type=kern_id,
        enum_value=APP.instance.sID(kerning) if kerning else None,
    )
    set_or_copy_integer(APP.instance.sID("tracking"), text_style, source, tracking)
    set_or_copy_color("color", text_style, source, color)
    lang_id = APP.instance.sID("textLanguage")
    set_or_copy_enumerated(
        lang_id,
        text_style,
        source,
        enum_type=lang_id,
        enum_value=APP.instance.sID(language) if language else None,
    )


def override_text_style_ranges(
    layer: ArtLayer,
    ranges: Iterable[tuple[int, int]],
    font: str | None = None,
    size: float | None = None,
    leading: float | None = None,
    kerning: Literal["metricsKern", "opticalKern", "manual"] | None = None,
    tracking: int | None = None,
    color: SolidColor | None = None,
    language: str | None = None,
) -> None:
    """Override style properties in specified character ranges of a text layer.

    Existing style ranges are split and adjusted as necessary. New ranges inherit
    the existing style from the portions they replace, then apply the overrides.

    Args:
        layer: Text layer to modify.
        ranges: List of (start, end) tuples, where end is exclusive (0-based indices).
        font: Font post script name.
        size: Text size in points.
    """
    # Get IDs
    text_key_id = APP.instance.sID("textKey")
    text_style_range_id = APP.instance.sID("textStyleRange")
    from_id = APP.instance.sID("from")
    to_id = APP.instance.sID("to")
    text_style_id = APP.instance.sID("textStyle")

    # Get text key and current text
    text_key = get_text_key(layer)
    current_text = text_key.getString(text_key_id)
    text_len = len(current_text)

    # Get existing style ranges
    style_ranges = text_key.getList(text_style_range_id)

    # Collect all split positions
    positions = {0, text_len}
    for start, end in ranges:
        positions.add(max(0, start))
        positions.add(min(text_len, end))
    positions = sorted(positions)

    # Create new style ranges
    new_style_ranges = ActionList()
    for i in range(len(positions) - 1):
        start = positions[i]
        end = positions[i + 1]

        # Find the original range containing this start
        orig_range = None
        for j in range(style_ranges.count):
            r = style_ranges.getObjectValue(j)
            if r.getInteger(from_id) <= start < r.getInteger(to_id):
                orig_range = r
                break
        if not orig_range:
            continue

        # Create new range
        new_range = ActionDescriptor()
        new_range.putInteger(from_id, start)
        new_range.putInteger(to_id, end)

        orig_style = orig_range.getObjectValue(text_style_id)

        overridden = any(ov_start <= start < ov_end for ov_start, ov_end in ranges)
        if overridden:
            # Create new range if values require overriding,
            # as editing the original range's text style
            # doesn't allow changing unit values, such as size,
            # because the Photoshop API doesn't seem to support it.
            # The values can be successfully set to the original text
            # style descriptor but they just won't come into effect when
            # the action is applied.
            text_style = ActionDescriptor()
            set_text_style_values(
                text_style,
                orig_style,
                font=font,
                size=size,
                leading=leading,
                kerning=kerning,
                tracking=tracking,
                color=color,
                language=language,
                reference_layer=layer,
            )
        else:
            # Use original range's text style if no overriding should be done
            text_style = orig_style

        new_range.putObject(text_style_id, text_style_id, text_style)
        new_style_ranges.putObject(text_style_range_id, new_range)

    # Update the text key
    text_key.putList(text_style_range_id, new_style_ranges)
    apply_text_key(layer, text_key)


"""
* Text Item Size
"""

ScaleAxis = Literal["tx", "ty", "xx", "yy", "xy", "yx"]


@overload
def get_text_scale_factor(
    layer: ArtLayer, axis: list[ScaleAxis], text_key: ActionDescriptor | None = None
) -> list[float]: ...


@overload
def get_text_scale_factor(
    layer: ArtLayer, axis: ScaleAxis = "yy", text_key: ActionDescriptor | None = None
) -> float: ...


def get_text_scale_factor(
    layer: ArtLayer,
    axis: ScaleAxis | list[ScaleAxis] = "yy",
    text_key: ActionDescriptor | None = None,
) -> float | list[float]:
    """Gets a transform value from text layer.

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
    idTransform = APP.instance.sID("transform")

    # Check for the "transform" descriptor
    if text_key.hasKey(idTransform):
        transform = text_key.getObjectValue(idTransform)
        # Check list of axis
        if isinstance(axis, list):
            return [transform.getUnitDoubleValue(APP.instance.sID(n)) for n in axis]
        # String axis
        return transform.getUnitDoubleValue(APP.instance.sID(axis))
    if isinstance(axis, list):
        return [1.0] * len(axis)
    return 1.0


def get_text_click_point(
    layer: ArtLayer,
    document_width: float | None = None,
    document_height: float | None = None,
    text_key: ActionDescriptor | None = None,
) -> tuple[float, float]:
    if not text_key:
        text_key = get_text_key(layer)
    if document_width is None or document_height is None:
        doc = APP.instance.activeDocument
        document_width = doc.width
        document_height = doc.height
    id_text_click_point = APP.instance.sID("textClickPoint")
    desc = text_key.getObjectValue(id_text_click_point)
    return (
        desc.getUnitDoubleValue(APP.instance.sID("horizontal")) / 100 * document_width,
        desc.getUnitDoubleValue(APP.instance.sID("vertical")) / 100 * document_height,
    )


"""
* Text Alignment
"""


def align_text(
    action_list: ActionList,
    start: int,
    end: int,
    alignment: Literal["left", "center", "right"] = "right",
) -> ActionList:
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
    paraStyle = APP.instance.sID("paragraphStyle")
    d1.putInteger(APP.instance.sID("from"), start)
    d1.putInteger(APP.instance.sID("to"), end)
    d2.putBoolean(APP.instance.sID("styleSheetHasParent"), True)
    d2.putEnumerated(
        APP.instance.sID("align"),
        APP.instance.sID("alignmentType"),
        APP.instance.sID(alignment),
    )
    d1.putObject(paraStyle, paraStyle, d2)
    action_list.putObject(APP.instance.sID("paragraphStyleRange"), d1)
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


def set_space_after(space: float) -> None:
    """Manually assign the 'space after' property for a paragraph text layer.

    Args:
        space: The 'space after' value to set.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    deesc2 = ActionDescriptor()
    ref1.putProperty(APP.instance.sID("property"), APP.instance.sID("paragraphStyle"))
    ref1.putEnumerated(
        APP.instance.sID("textLayer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    desc1.putReference(APP.instance.sID("target"), ref1)
    deesc2.putInteger(APP.instance.sID("textOverrideFeatureName"), 808464438)
    deesc2.putUnitDouble(
        APP.instance.sID("spaceAfter"), APP.instance.sID("pointsUnit"), space
    )
    desc1.putObject(APP.instance.sID("to"), APP.instance.sID("paragraphStyle"), deesc2)
    APP.instance.executeAction(
        APP.instance.sID("set"), desc1, DialogModes.DisplayNoDialogs
    )


def set_text_leading(layer: ArtLayer, leading: float) -> None:
    """Manually assign font leading to a text layer using action descriptors.

    Args:
        layer: Layer containing TextItem to change leading of.
        leading: New TextItem font leading.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    ref1.putProperty(APP.instance.sID("property"), APP.instance.sID("textStyle"))
    ref1.putIdentifier(APP.instance.sID("textLayer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc2.putUnitDouble(
        APP.instance.sID("leading"), APP.instance.sID("pointsUnit"), leading
    )
    desc1.putObject(APP.instance.sID("to"), APP.instance.sID("textStyle"), desc2)
    APP.instance.executeAction(
        APP.instance.sID("set"), desc1, DialogModes.DisplayNoDialogs
    )


def set_text_size(layer: ArtLayer, size: float) -> None:
    """Manually assign font size to a text layer using action descriptors.

    Args:
        layer: Layer containing TextItem to change size of.
        size: New TextItem font size.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    textStyle = APP.instance.sID("textStyle")
    ref1.putProperty(APP.instance.sID("property"), textStyle)
    ref1.putIdentifier(APP.instance.sID("textLayer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc2.putUnitDouble(APP.instance.sID("size"), APP.instance.sID("pointsUnit"), size)
    desc1.putObject(APP.instance.sID("to"), textStyle, desc2)
    APP.instance.executeAction(
        APP.instance.sID("set"), desc1, DialogModes.DisplayNoDialogs
    )


def set_text_size_and_leading(layer: ArtLayer, size: float, leading: float) -> None:
    """Manually assign font size and leading space to a text layer using action descriptors.

    Args:
        layer: Layer containing TextItem to change size of.
        size: New TextItem font size.
        leading: New TextItem font leading.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    desc2 = ActionDescriptor()
    textStyle = APP.instance.sID("textStyle")
    ptUnit = APP.instance.sID("pointsUnit")
    ref1.putProperty(APP.instance.sID("property"), textStyle)
    ref1.putIdentifier(APP.instance.sID("textLayer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc2.putUnitDouble(APP.instance.sID("size"), ptUnit, size)
    desc2.putUnitDouble(APP.instance.sID("leading"), ptUnit, leading)
    desc1.putObject(APP.instance.sID("to"), textStyle, desc2)
    APP.instance.executeAction(
        APP.instance.sID("set"), desc1, DialogModes.DisplayNoDialogs
    )


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
    paraStyle = APP.instance.sID("paragraphStyle")
    ref1.putProperty(APP.instance.sID("property"), paraStyle)
    ref1.putIdentifier(APP.instance.sID("textLayer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc2.putBoolean(APP.instance.sID("textEveryLineComposer"), every)
    desc1.putObject(APP.instance.sID("to"), paraStyle, desc2)
    APP.instance.executeAction(
        APP.instance.sID("set"), desc1, DialogModes.DisplayNoDialogs
    )


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
    if font := APP.instance.fonts.getByName(font_name):
        layer.textItem.font = font.postScriptName


"""
* Scaling Font Down
"""


def ensure_visible_reference(reference: ArtLayer) -> TextItem | None:
    """Ensures that a layer used for reference has bounds if it is a text layer.

    Args:
        reference: Reference layer that might be a TextLayer.

    Returns:
        TextItem if reference is an empty text layer, otherwise None.
    """
    if isinstance(reference, LayerSet):
        return None
    if (reference.kind is LayerKind.TextLayer) and reference.bounds == (0, 0, 0, 0):
        TI = reference.textItem
        TI.contents = "."
        return TI
    return None


def scale_text_right_overlap(
    layer: ArtLayer,
    reference: ArtLayer,
    reference_side: RefSide,
    step_sizes: Sequence[float] | None = None,
    gap: float = 30,
) -> None:
    """Scales a text layer down (in 0.2 pt increments) until it
    doesn't overlap with the reference layer's `reference_side` bound.

    Args:
        layer: The text item layer to scale.
        reference: Reference layer we need to avoid.
        reference_side: Which side of reference to check overlap with.
        gap: Minimum gap to ensure between the layer and reference (DPI adjusted).
    """
    # Ensure a valid and visible reference layer
    if not reference:
        return
    ref_TI = ensure_visible_reference(reference)

    # Set starting variables
    font_size = old_size = get_font_size(layer)
    scaled_gap = APP.instance.scale_by_dpi(gap)
    ref_bounds = reference.bounds
    ref_bounds = (
        ref_bounds[0] - scaled_gap,
        ref_bounds[1] - scaled_gap,
        ref_bounds[2] + scaled_gap,
        ref_bounds[3] + scaled_gap,
    )
    layer_bounds = layer.bounds
    step_sizes = step_sizes or (0.4, 0.2)

    # Guard against reference being left of the layer
    if (
        ref_bounds[0] < layer_bounds[0]
        if reference_side == RefSide.LEFT
        else ref_bounds[1] < layer_bounds[1]
        if reference_side == RefSide.TOP
        else ref_bounds[2] > layer_bounds[2]
        if reference_side == RefSide.RIGHT
        else ref_bounds[3] > layer_bounds[3]
    ):
        # Reset reference
        if ref_TI:
            ref_TI.contents = ""
        return

    uneven_round = False
    # Adjust text size down and up in decreasing steps
    for idx, step_size in enumerate(step_sizes):
        uneven_round = bool(idx % 2)

        # Check overlap
        while check_bounds_overlap(layer_bounds, ref_bounds, reference_side):
            if uneven_round:
                font_size += step_size
            else:
                font_size -= step_size

            set_text_size(layer, font_size)

            layer_bounds = layer.bounds

    # If the last round was uneven we have to go one step down
    if uneven_round:
        font_size -= step_sizes[-1]
        set_text_size(layer, font_size)

    # Shift baseline up to keep text centered vertically
    layer.textItem.baselineShift = (old_size * 0.3) - (font_size * 0.3)

    # Fix corrected reference layer
    if ref_TI:
        # Reset reference
        ref_TI.contents = ""


def scale_text_left_overlap(
    layer: ArtLayer, reference: ArtLayer, gap: int = 30
) -> None:
    """Scales a text layer down (in 0.2 pt increments) until its left bound
    has a 30 px~ (based on DPI) clearance from a reference layer's right bound.

    Args:
        layer: The text item layer to scale.
        reference: Reference layer we need to avoid.
        gap: Minimum gap to ensure between the layer and reference (DPI adjusted).
    """
    # Ensure a valid and visible reference layer
    if not reference or reference.bounds == (0, 0, 0, 0):
        return
    ref_TI = ensure_visible_reference(reference)

    # Set starting variables
    font_size = old_size = get_font_size(layer)
    ref_right_bound = reference.bounds[2] + APP.instance.scale_by_dpi(gap)
    step, half_step = 0.4, 0.2

    # Guard against reference being right of the layer
    if layer.bounds[0] < reference.bounds[0]:
        # Reset reference
        if ref_TI:
            ref_TI.contents = ""
        return

    # Make our first check if scaling is necessary
    if continue_scaling := bool(ref_right_bound > layer.bounds[0]):
        # Step down the font till it clears the reference
        while continue_scaling:
            font_size -= step
            set_text_size(layer, font_size)
            continue_scaling = bool(ref_right_bound > layer.bounds[0])

        # Go up a half step
        font_size += half_step
        set_text_size(layer, font_size)

        # If text not in bounds, revert half step
        if ref_right_bound > layer.bounds[0]:
            font_size -= half_step
            set_text_size(layer, font_size)

        # Shift baseline up to keep text centered vertically
        layer.textItem.baselineShift = (old_size * 0.3) - (font_size * 0.3)

    # Fix corrected reference layer
    if ref_TI:
        ref_TI.contents = ""


def scale_text_to_width(
    layer: ArtLayer,
    width: float,
    spacing: int = 64,
    step: float = 0.4,
    font_size: float | None = None,
) -> float | None:
    """Resize a given text layer's font size/leading until it fits inside a reference width.

    Args:
        layer: Text layer to scale.
        width: Width the text layer must fit (after spacing added).
        spacing: Amount of DPI adjusted spacing to pad the width.
        step: Amount to step font size down by in each check.
        font_size: The starting font size if pre-calculated.

    Returns:
        Font size if font size is calculated during operation, otherwise None.
    """
    # Cancel if we're already within expected bounds
    width = width - APP.instance.scale_by_dpi(spacing)
    continue_scaling = bool(width < get_layer_width(layer))
    if not continue_scaling:
        return

    # Establish starting size and half step
    if font_size is None:
        font_size = get_font_size(layer)
    half_step = step / 2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    while continue_scaling:
        font_size -= step
        set_text_size_and_leading(layer, font_size, font_size)
        continue_scaling = bool(width < get_layer_width(layer))

    # Increase by a half step
    font_size += half_step
    set_text_size_and_leading(layer, font_size, font_size)

    # Revert if half step still exceeds reference
    if width < get_layer_width(layer):
        font_size -= half_step
        set_text_size_and_leading(layer, font_size, font_size)
    return font_size


def scale_text_to_height(
    layer: ArtLayer,
    height: float,
    spacing: float = 64,
    step: float = 0.4,
    font_size: float | None = None,
) -> float | None:
    """Resize a given text layer's font size/leading until it fits inside a reference height.

    Args:
        layer: Text layer to scale.
        height: Width the text layer must fit (after spacing added).
        spacing: Amount of DPI adjusted spacing to pad the height.
        step: Amount to step font size down by in each check.
        font_size: The starting font size if pre-calculated.

    Returns:
        Font size if font size is calculated during operation, otherwise None.
    """
    # Cancel if we're already within expected bounds
    height = height - APP.instance.scale_by_dpi(spacing)
    continue_scaling = bool(height < get_layer_height(layer))
    if not continue_scaling:
        return

    # Establish starting size and half step
    if font_size is None:
        font_size = get_font_size(layer)
    half_step = step / 2

    # Step down font and lead sizes by the step size, and update those sizes in the layer
    while continue_scaling:
        font_size -= step
        set_text_size_and_leading(layer, font_size, font_size)
        continue_scaling = bool(height < get_layer_height(layer))

    # Increase by a half step
    font_size += half_step
    set_text_size_and_leading(layer, font_size, font_size)

    # Revert if half step still exceeds reference
    if height < get_layer_height(layer):
        font_size -= half_step
        set_text_size_and_leading(layer, font_size, font_size)
    return font_size


def scale_text_to_width_textbox(
    layer: ArtLayer, font_size: float | None = None, step: float = 0.1
) -> None:
    """Check if the text in a TextLayer exceeds its bounding box.

    Args:
        layer: ArtLayer with "kind" of TextLayer.
        font_size: Starting font size, calculated if not provided (slower execution time).
        step: Amount of points to step down each iteration.
    """
    # Get the starting font size
    if font_size is None:
        font_size = get_font_size(layer)
    ref = get_textbox_width(layer) + 1

    # Continue to reduce the size until within the bounding box
    while get_width_no_effects(layer) > ref:
        font_size -= step
        set_text_size_and_leading(layer, font_size, font_size)


def scale_text_layers_to_height(
    text_layers: list[ArtLayer],
    ref_height: float,
    font_size: float | None = None,
    step_sizes: Sequence[float] | None = None,
) -> float | None:
    """Scale multiple text layers until they all can fit within the same given height dimension.

    Args:
        text_layers: List of TextLayers to check.
        ref_height: Height to fit inside.
        font_size: Starting font size of the text layers, calculated if not provided.
        step_sizes: Descending sequence, which determines the increments used for text scaling.
    """
    step_sizes = step_sizes or (0.4, 0.2)

    # Check initial fit
    total_layer_height = sum([get_layer_height(layer) for layer in text_layers])
    if total_layer_height <= ref_height:
        return

    # Establish font size
    if font_size is None:
        font_size = get_font_size(text_layers[0])

    uneven_round = False
    # Adjust text size down and up in decreasing steps
    for idx, step_size in enumerate(step_sizes):
        uneven_round = bool(idx % 2)

        # Compare height of all 3 elements vs total reference height
        while (
            total_layer_height < ref_height
            if uneven_round
            else total_layer_height > ref_height
        ):
            total_layer_height = 0

            if uneven_round:
                font_size += step_size
            else:
                font_size -= step_size

            for layer in text_layers:
                set_text_size_and_leading(layer, font_size, font_size)
                total_layer_height += get_layer_height(layer)

    # If the last round was uneven we have to go one step down,
    # because we are over the reference height
    if uneven_round:
        font_size -= step_sizes[-1]
        for layer in text_layers:
            set_text_size_and_leading(layer, font_size, font_size)

    return font_size


def clear_reference_vertical_multi(
    text_layers: list[ArtLayer],
    ref: ReferenceLayer,
    loyalty_ref: ReferenceLayer,
    space: float,
    uniform_gap: bool = False,
    font_size: float | None = None,
    step: float = 0.2,
    docsel: Selection | None = None,
    bottom_ref: ReferenceLayer | None = None,
) -> None:
    """Shift or resize multiple text layers to prevent vertical collision with a reference area.

    Note:
        Used on Planeswalker cards to allow multiple text abilities to clear the loyalty box.

    Args:
        text_layers: Ability text layers to nudge or resize.
        ref: Reference area ability text layers must fit inside.
        loyalty_ref: Reference area that covers the loyalty box.
        space: Minimum space between planeswalker abilities.
        uniform_gap: Whether the gap between abilities should be the same between each ability.
        font_size: The current font size of the text layers, if known. Otherwise, calculate automatically.
        step: The amount of font size and leading to step down each iteration.
        docsel: Selection object, pull from document if not provided (improves performance).
        bottom_ref: Reference layer used to check text overflow at bottom.
    """
    # Return if adjustments weren't provided
    if not loyalty_ref:
        return

    # Establish fresh data
    if font_size is None:
        font_size = get_font_size(text_layers[0])
    layers = text_layers.copy()
    movable = len(layers) - 1

    # Calculate inside gap
    total_space = ref.dims["height"] - sum(
        [get_layer_height(layer) for layer in text_layers]
    )
    if not uniform_gap:
        inside_gap = (
            (total_space - space) - (ref.bounds[3] - layers[-1].bounds[1])
        ) / movable
    else:
        inside_gap = total_space / (len(layers) + 1)
    leftover = (inside_gap - space) * movable

    # Does the bottom layer overlap with the loyalty box?
    delta = check_reference_overlap(layer=layers[-1], ref=loyalty_ref, docsel=docsel)
    if delta >= 0:
        return

    outer_gap = space if not uniform_gap else 0

    if APP.instance.supports_uxp_scripts and bottom_ref:
        keep_adjusting: bool = True
        ref_right = ref.bounds[2]
        bottom_ref_bounds = bottom_ref.bounds
        bottom_layer = text_layers[-1]
        bottom_layer_top = bottom_layer.bounds[1]
        bottom_layer_contents = bottom_layer.textItem.contents
        x, _ = get_text_click_point(bottom_layer)
        min_inside_gap = outer_gap

        while keep_adjusting:
            # Avoid overlapping the loyalty box using a shaped text layer
            bottom_layer = text_layers[-1]
            # TODO Get the "actual" transform x and y, which are visible in Photoshop UI,
            # in order to precisely align the shaped text layer with the others. The current
            # implementation uses text click point which seems to precisely match the x value
            # but not the y value. Bounds and boundsNoEffects don't give the transform values
            # and as such can't be used here.
            base_shape = create_shape_layer(
                (
                    {"x": x, "y": bottom_layer_top},
                    {"x": ref_right, "y": bottom_layer_top},
                    {"x": ref_right, "y": bottom_ref_bounds[3] + 500},
                    {"x": x, "y": bottom_ref_bounds[3] + 500},
                ),
                relative_layer=bottom_layer,
                placement=ElementPlacement.PlaceBefore,
            )
            loyalty_box_cutout = loyalty_ref.duplicate(
                base_shape, ElementPlacement.PlaceBefore
            )
            merged_shape = merge_shapes(
                loyalty_box_cutout, base_shape, operation=ShapeOperation.SubtractFront
            )
            shaped_text = create_text_layer_with_path(
                reference_path=merged_shape,
                reference_text=bottom_layer,
                size=font_size,
                leading=font_size,
            )
            shaped_text.textItem.contents = bottom_layer_contents
            bottom_layer.visible = False
            text_layers[-1] = shaped_text

            inside_gap = spread_layers_over_reference(
                layers=text_layers,
                ref=ref,
                gap=outer_gap,
                outside_matching=True,
            )

            if keep_adjusting := inside_gap < min_inside_gap or (
                text_layers[-1].bounds[3] >= bottom_ref_bounds[1]
            ):
                font_size -= step
                for lyr in text_layers:
                    set_text_size_and_leading(
                        layer=lyr, size=font_size, leading=font_size
                    )

                spread_layers_over_reference(
                    layers=text_layers,
                    ref=ref,
                    gap=outer_gap,
                    outside_matching=True,
                )
            else:
                # Ensure uniform gaps between pinlines and all text layers
                spread_layers_over_reference(
                    layers=text_layers,
                    ref=ref,
                    outside_matching=True,
                )
    else:
        # Calculate the total distance needing to be covered
        total_move = 0
        layers.pop(0)
        for n, lyr in enumerate(layers):
            total_move += fabs(delta) * ((len(layers) - n) / len(layers))

        # Text layers can just be shifted upwards
        if total_move < leftover:
            layers.reverse()
            for n, lyr in enumerate(layers):
                move_y = delta * ((len(layers) - n) / len(layers))
                lyr.translate(0, move_y)
            return

        # Layer gap would be too small, need to resize text then shift upward
        font_size -= step
        for lyr in text_layers:
            set_text_size_and_leading(layer=lyr, size=font_size, leading=font_size)

        # Space apart planeswalker text evenly
        spread_layers_over_reference(
            layers=text_layers,
            ref=ref,
            gap=outer_gap,
            outside_matching=False,
        )

        # Check for another iteration
        clear_reference_vertical_multi(
            text_layers=text_layers,
            ref=ref,
            loyalty_ref=loyalty_ref,
            space=space,
            uniform_gap=uniform_gap,
            font_size=font_size,
            docsel=docsel,
        )
