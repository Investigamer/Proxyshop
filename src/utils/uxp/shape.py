from enum import StrEnum
from typing import Literal, TypedDict

from photoshop.api._artlayer import ArtLayer

from src import APP
from src.helpers.layers import select_layers

from .batch_play import ActionDescriptor, batch_play


class ShapeOperation(StrEnum):
    Unite = "add"
    SubtractFront = "subtract"
    UniteAtOverlap = "interfaceIconFrameDimmed"
    SubtractAtOverlap = "xor"


class ShapeOperationDescriptor(TypedDict):
    _enum: Literal["shapeOperation"]
    _value: ShapeOperation


class MergeShapesDescriptor(ActionDescriptor):
    _obj: Literal["mergeLayersNew"]
    shapeOperation: ShapeOperationDescriptor


class CombineShapeComponentsDescriptor(ActionDescriptor):
    _obj: Literal["combine"]


def merge_shapes(*args: ArtLayer, operation: ShapeOperation) -> ArtLayer:
    """Merges shapes, consuming the shapes that are earlier in the document order."""
    for layer in args:
        layer.visible = True
    select_layers([*args])
    desc: MergeShapesDescriptor = {
        "_obj": "mergeLayersNew",
        "shapeOperation": {"_enum": "shapeOperation", "_value": operation},
    }
    comb_desc: CombineShapeComponentsDescriptor = {
        "_obj": "combine",
        "_target": [{"_ref": "path", "_enum": "ordinal"}],
    }
    batch_play(desc, comb_desc)
    active_layer = APP.instance.activeDocument.activeLayer
    if not isinstance(active_layer, ArtLayer):
        raise TypeError(
            "Failed to merge shapes. Active layer is unexpectedly not an ArtLayer."
        )
    return active_layer
