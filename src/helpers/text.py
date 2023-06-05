"""
TEXT HELPERS
"""
# Standard Library Imports
from typing import Union, Optional

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.constants import con
from src.settings import cfg

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
TEXT UTILITIES
"""


def get_text_key(layer: ArtLayer) -> ActionDescriptor:
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


def replace_text_robust(layer: ArtLayer, find: str, replace: str) -> None:
    """
    Replace all instances of `replace_this` in the specified layer with `replace_with`, using Photoshop's
    built-in search and replace feature. Slower than `replace_text`, but can handle multi-style strings.
    @param layer: Layer object to search through.
    @param find: Text string to search for.
    @param replace: Text string to replace matches with.
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
        False if cfg.targeted_replace and app.supports_target_text_replace() else True
    )
    desc32.putBoolean(sID("forward"), True)
    desc32.putBoolean(sID("caseSensitive"), True)
    desc32.putBoolean(sID("wholeWord"), False)
    desc32.putBoolean(sID("ignoreAccents"), True)
    desc31.putObject(sID("using"), sID("findReplace"), desc32)
    app.executeAction(sID("findReplace"), desc31, NO_DIALOG)


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
        # Get the activeLayer if not provided
        if not layer:
            layer = app.activeDocument.activeLayer
        ref = ActionReference()
        ref.putIdentifier(sID("layer"), layer.id)
        text_key = app.executeActionGet(ref).getObjectValue(sID('textKey'))

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
APPLYING TEXT ITEM SIZE
"""


def set_text_size(size: int, layer: Optional[ArtLayer] = None) -> None:
    """
    Manually assign font size to a layer using action descriptors.
    @param layer: Layer containing TextItem
    @param size: New size of layer
    """
    # Set the active layer if needed
    if layer:
        app.activeDocument.activeLayer = layer

    # Set the new size
    desc2361 = ActionDescriptor()
    ref68 = ActionReference()
    desc2362 = ActionDescriptor()
    ref68.putProperty(sID("property"), sID("textStyle"))
    ref68.putEnumerated(sID("textLayer"), sID("ordinal"), sID("targetEnum"))
    desc2361.putReference(sID("target"), ref68)
    desc2362.putInteger(sID("textOverrideFeatureName"), 808465458)
    desc2362.putInteger(sID("typeStyleOperationType"), 3)
    desc2362.putUnitDouble(sID("size"), sID("pointsUnit"), size)
    desc2361.putObject(sID("to"), sID("textStyle"), desc2362)
    app.ExecuteAction(sID("set"), desc2361, NO_DIALOG)


def update_text_layer_size(
    layer: ArtLayer,
    change: float,
    factor: Optional[float] = None,
) -> None:
    """
    Sets the text item size while ensuring proper scaling.
    @param layer: Layer containing TextItem object.
    @param change: Difference in size (+/-).
    @param factor: Scale factor of text item.
    """
    # Set the active layer if needed
    if not factor:
        factor = get_text_scale_factor()

    # Increase the size
    set_text_size(size=(factor*layer.textItem.size)+change)
