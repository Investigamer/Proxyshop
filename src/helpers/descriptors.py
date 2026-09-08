"""
* Helpers: PS Object Descriptors
"""

from collections.abc import Callable
from ctypes import COMError
from logging import getLogger
from os import PathLike

from photoshop.api import ActionDescriptor, ActionList, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import DescValueType

from src import APP
from src.helpers.colors import apply_color
from src.schema.colors import ColorObject

_logger = getLogger(__name__)

"""
* Layer Action Descriptors
"""


def get_layer_action_descriptor(layer: ArtLayer | LayerSet) -> ActionDescriptor:
    """Gets action descriptor info object using layer as a reference.

    Args:
        layer: Layer or layer group to get action descriptor info for.

    Returns:
        Action descriptor info object about the layer.
    """
    ref = ActionReference()
    ref.putIdentifier(APP.instance.sID("layer"), layer.id)
    return APP.instance.executeActionGet(ref)


# region Copying


def copy_descriptor(
    source: ActionDescriptor, recursive: bool = False
) -> ActionDescriptor:
    """Creates a copy of an ActionDescriptor by copying all properties from source.

    Args:
        source: Descriptor to copy from.
        recursive: Whether to create copies of nested descriptors or not.

    Returns:
        New descriptor with all properties copied from source.
    """
    copy = ActionDescriptor()

    for i in range(source.count):
        copy_descriptor_value(
            source.getKey(i), source=source, target=copy, recursive=recursive
        )

    return copy


def copy_descriptor_value(
    key: int,
    source: ActionDescriptor,
    target: ActionDescriptor,
    recursive: bool = False,
) -> None:
    """Copies value at key from source to target descriptor."""
    if source.hasKey(key):
        value_type = source.getType(key)
        try:
            if value_type == DescValueType.AliasType:
                target.putPath(key, source.getPath(key))
            elif value_type == DescValueType.BooleanType:
                target.putBoolean(key, source.getBoolean(key))
            elif value_type == DescValueType.ClassType:
                target.putClass(key, source.getClass(key))
            elif value_type == DescValueType.DoubleType:
                target.putDouble(key, source.getDouble(key))
            elif value_type == DescValueType.EnumeratedType:
                enum_type = source.getEnumerationType(key)
                enum_value = source.getEnumerationValue(key)
                target.putEnumerated(key, enum_type, enum_value)
            elif value_type == DescValueType.IntegerType:
                target.putInteger(key, source.getInteger(key))
            elif value_type == DescValueType.LargeIntegerType:
                target.putLargeInteger(key, source.getLargeInteger(key))
            elif value_type == DescValueType.ListType:
                target.putList(key, source.getList(key))
            elif value_type == DescValueType.ObjectType:
                obj_type = source.getObjectType(key)
                obj_desc = source.getObjectValue(key)
                # Recursive copy for nested objects
                target.putObject(
                    key, obj_type, copy_descriptor(obj_desc) if recursive else obj_desc
                )
            elif value_type == DescValueType.RawType:
                target.putData(key, source.getData(key))
            elif value_type == DescValueType.ReferenceType:
                target.putReference(key, source.getReference(key))
            elif value_type == DescValueType.StringType:
                target.putString(key, source.getString(key))
            elif value_type == DescValueType.UnitDoubleType:
                unit_type = source.getUnitDoubleType(key)
                unit_value = source.getUnitDoubleValue(key)
                target.putUnitDouble(key, unit_type, unit_value)
            else:
                _logger.warning(
                    f"ActionDescriptor value at key '{key}' has an unknown type '{value_type}'"
                )
        except COMError:
            # Skip properties that cannot be copied
            _logger.warning(
                f"Can't copy key '{key}' of type '{value_type}' from ActionDescriptor"
            )


# endregion Copying

# region Descriptor Value Setters


def set_or_copy_alias(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: str | PathLike[str] | None = None,
) -> None:
    """Set alias (path) value or copy from source if value is None."""
    if value is not None:
        target.putPath(key, value)
    elif source is not None and source.hasKey(key):
        target.putPath(key, source.getPath(key))


def set_or_copy_boolean(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: bool | None = None,
) -> None:
    """Set boolean value or copy from source if value is None."""
    if value is not None:
        target.putBoolean(key, value)
    elif source is not None and source.hasKey(key):
        target.putBoolean(key, source.getBoolean(key))


def set_or_copy_class(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: int | None = None,
) -> None:
    """Set class value or copy from source if value is None."""
    if value is not None:
        target.putClass(key, value)
    elif source is not None and source.hasKey(key):
        target.putClass(key, source.getClass(key))


def set_or_copy_double(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: float | None = None,
) -> None:
    """Set double value or copy from source if value is None."""
    if value is not None:
        target.putDouble(key, value)
    elif source is not None and source.hasKey(key):
        target.putDouble(key, source.getDouble(key))


def set_or_copy_enumerated(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    enum_type: int | None = None,
    enum_value: int | None = None,
) -> None:
    """Set enumerated value or copy from source if both enum_type and enum_value are None."""
    if enum_type is not None and enum_value is not None:
        target.putEnumerated(key, enum_type, enum_value)
    elif source is not None and source.hasKey(key):
        source_enum_type = source.getEnumerationType(key)
        source_enum_value = source.getEnumerationValue(key)
        target.putEnumerated(key, source_enum_type, source_enum_value)


def set_or_copy_integer(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: int | None = None,
) -> None:
    """Set integer value or copy from source if value is None."""
    if value is not None:
        target.putInteger(key, value)
    elif source is not None and source.hasKey(key):
        target.putInteger(key, source.getInteger(key))


def set_or_copy_large_integer(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: int | None = None,
) -> None:
    """Set large integer value or copy from source if value is None."""
    if value is not None:
        target.putLargeInteger(key, value)
    elif source is not None and source.hasKey(key):
        target.putLargeInteger(key, source.getLargeInteger(key))


def set_or_copy_list(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: ActionList | None = None,
) -> None:
    """Set list value or copy from source if value is None."""
    if value is not None:
        target.putList(key, value)
    elif source is not None and source.hasKey(key):
        target.putList(key, source.getList(key))


def set_or_copy_object(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    obj_type: int | None = None,
    obj_desc: ActionDescriptor | None = None,
) -> None:
    """Set object value or copy from source if both obj_type and obj_desc are None."""
    if obj_type is not None and obj_desc is not None:
        target.putObject(key, obj_type, obj_desc)
    elif source is not None and source.hasKey(key):
        source_obj_type = source.getObjectType(key)
        source_obj_desc = source.getObjectValue(key)
        target.putObject(key, source_obj_type, source_obj_desc)


def set_or_copy_raw(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: str | None = None,
) -> None:
    """Set raw (data) value or copy from source if value is None."""
    if value is not None:
        target.putData(key, value)
    elif source is not None and source.hasKey(key):
        target.putData(key, source.getData(key))


def set_or_copy_reference(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: ActionReference | None = None,
) -> None:
    """Set reference value or copy from source if value is None."""
    if value is not None:
        target.putReference(key, value)
    elif source is not None and source.hasKey(key):
        target.putReference(key, source.getReference(key))


def set_or_copy_string(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    value: str | None = None,
) -> None:
    """Set string value or copy from source if value is None."""
    if value is not None:
        target.putString(key, value)
    elif source is not None and source.hasKey(key):
        target.putString(key, source.getString(key))


def set_or_copy_unit_double(
    key: int,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    unit_type: int | None = None,
    unit_value: float | None = None,
    source_value_hook: Callable[[float], float] | None = None,
) -> None:
    """Set unit double value or copy from source if both unit_type and unit_value are None."""
    if unit_type is not None and unit_value is not None:
        target.putUnitDouble(key, unit_type, unit_value)
    elif source is not None and source.hasKey(key):
        source_unit_type = source.getUnitDoubleType(key)
        source_unit_value = source.getUnitDoubleValue(key)
        target.putUnitDouble(
            key,
            source_unit_type,
            source_value_hook(source_unit_value)
            if source_value_hook
            else source_unit_value,
        )


def set_or_copy_color(
    color_str_id: str,
    target: ActionDescriptor,
    source: ActionDescriptor | None = None,
    color: ColorObject | None = None,
) -> None:
    """Set object value or copy from source if both obj_type and obj_desc are None."""
    if color is not None:
        return apply_color(target, color, color_type=color_str_id)

    key = APP.instance.sID(color_str_id)
    if source is not None and source.hasKey(key):
        source_obj_type = source.getObjectType(key)
        source_obj_desc = source.getObjectValue(key)
        target.putObject(key, source_obj_type, source_obj_desc)


# endregion Descriptor Value Setters
