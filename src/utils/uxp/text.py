from _ctypes import COMError
from typing import Literal, NotRequired, TypedDict, Unpack

from photoshop.api import SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api.enumerations import AutoKernType, PointKind
from photoshop.api.path_item import PathItem

from src import APP
from src.helpers.effects import copy_layer_fx
from src.helpers.layers import select_layer

from .batch_play import ActionDescriptor, batch_play

FromToDescriptor = TypedDict(
    "FromToDescriptor",
    {
        "from": int,
        "to": int,
    },
)


class UnitDescriptor(TypedDict):
    _unit: Literal["pixelsUnit", "pointsUnit"]
    _value: float | int


class OrientationDescriptor(TypedDict):
    _enum: Literal["orientation"]
    _value: Literal["horizontal", "vertical"]


class AlignmentTypeDescriptor(TypedDict):
    _enum: Literal["alignmentType"]
    _value: Literal["left", "right"]


class DirectionTypeDescriptor(TypedDict):
    _enum: Literal["directionType"]
    _value: Literal["dirLeftToRight", "dirRightToLeft"]


class ParagraphStyleDescriptor(TypedDict):
    _obj: Literal["paragraphStyle"]
    align: NotRequired[AlignmentTypeDescriptor]
    directionType: NotRequired[DirectionTypeDescriptor]
    spaceBefore: NotRequired[UnitDescriptor]
    impliedSpaceBefore: NotRequired[UnitDescriptor]
    spaceAfter: NotRequired[UnitDescriptor]
    impliedSpaceAfter: NotRequired[UnitDescriptor]


class ParagraphStyleRangeDescriptor(FromToDescriptor):
    _obj: Literal["paragraphStyleRange"]
    paragraphStyle: ParagraphStyleDescriptor


class AnchorDescriptor(TypedDict):
    _obj: Literal["paint"]
    horizontal: UnitDescriptor
    vertical: UnitDescriptor


class PathPointDescriptor(TypedDict):
    _obj: Literal["pathPoint"]
    anchor: AnchorDescriptor
    backward: NotRequired[AnchorDescriptor]
    forward: NotRequired[AnchorDescriptor]
    smooth: NotRequired[bool]


class SubpathsListDescriptor(TypedDict):
    _obj: Literal["subpathsList"]
    closedSubpath: bool
    points: list[PathPointDescriptor]


class ShapeOperationDescriptor(TypedDict):
    _enum: Literal["shapeOperation"]
    _value: Literal["xor"]


class PathComponentDescriptor(TypedDict):
    _obj: Literal["pathComponent"]
    shapeOperation: ShapeOperationDescriptor
    subpathListKey: list[SubpathsListDescriptor]


class CharDescriptor(TypedDict):
    _enum: Literal["char"]
    _value: Literal["box"]


class PathClassDescriptor(TypedDict):
    _obj: Literal["pathClass"]
    pathComponents: list[PathComponentDescriptor]


class TextShapeDescriptor(TypedDict):
    _obj: Literal["textShape"]
    char: CharDescriptor
    path: PathClassDescriptor


class ColorDescriptor(TypedDict):
    _obj: Literal["RGBColor"]
    blue: float | int
    grain: float | int
    red: float | int


class KerningDescriptor(TypedDict):
    _enum: Literal["autoKern"]
    _value: Literal["metricsKern", "opticalKern"]


class TextStyleDescriptor(TypedDict):
    _obj: Literal["textStyle"]
    color: NotRequired[ColorDescriptor]
    fontName: NotRequired[str]
    fontPostScriptName: NotRequired[str]
    fontScript: NotRequired[int]
    fontStyleName: NotRequired[str]
    size: NotRequired[UnitDescriptor]
    impliedFontSize: NotRequired[UnitDescriptor]
    autoLeading: NotRequired[bool]
    leading: NotRequired[UnitDescriptor]
    impliedLeading: NotRequired[UnitDescriptor]
    autoKern: NotRequired[KerningDescriptor]


class TextStyleRangeDescriptor(FromToDescriptor):
    _obj: Literal["textStyleRange"]
    textStyle: TextStyleDescriptor


class TextLayerDescriptor(TypedDict):
    _obj: Literal["textLayer"]
    kerningRange: NotRequired[list[None]]
    orientation: NotRequired[OrientationDescriptor]
    paragraphStyleRange: NotRequired[list[ParagraphStyleRangeDescriptor]]
    textKey: NotRequired[str]
    textShape: NotRequired[list[TextShapeDescriptor]]
    textStyleRange: NotRequired[list[TextStyleRangeDescriptor]]


class MakeTextLayerActionDescriptor(ActionDescriptor):
    _obj: Literal["make"]
    using: TextLayerDescriptor


class CreateTextLayerWithPathOptions(TypedDict):
    color: NotRequired[SolidColor]
    size: NotRequired[float]
    leading: NotRequired[float]


# leftDirection -> forward
# rightDirection -> backward
def create_text_layer_with_path(
    reference_path: ArtLayer,
    reference_text: ArtLayer,
    **kwargs: Unpack[CreateTextLayerWithPathOptions],
) -> ArtLayer:
    """Creates a shaped text layer, which aims to mimic the properties of reference_text layer."""
    select_layer(reference_path, make_visible=True)

    layer_path: PathItem | None = None
    for path in APP.instance.activeDocument.pathItems:
        if path.name == f"{reference_path.name} Shape Path":
            layer_path = path

    if not layer_path:
        layer_path = APP.instance.activeDocument.pathItems[-1]

    points: list[PathPointDescriptor] = []
    for sub_path in layer_path.subPathItems:
        for point in sub_path.pathPoints:
            points.append(
                {
                    "_obj": "pathPoint",
                    "smooth": point.kind is PointKind.SmoothPoint,
                    "anchor": {
                        "_obj": "paint",
                        "horizontal": {
                            "_unit": "pixelsUnit",
                            "_value": point.anchor[0],
                        },
                        "vertical": {"_unit": "pixelsUnit", "_value": point.anchor[1]},
                    },
                    "forward": {
                        "_obj": "paint",
                        "horizontal": {
                            "_unit": "pixelsUnit",
                            "_value": point.leftDirection[0],
                        },
                        "vertical": {
                            "_unit": "pixelsUnit",
                            "_value": point.leftDirection[1],
                        },
                    },
                    "backward": {
                        "_obj": "paint",
                        "horizontal": {
                            "_unit": "pixelsUnit",
                            "_value": point.rightDirection[0],
                        },
                        "vertical": {
                            "_unit": "pixelsUnit",
                            "_value": point.rightDirection[1],
                        },
                    },
                }
            )

    reference_path.visible = False

    ref_text = reference_text.textItem
    color = kwargs.get("color", ref_text.color)
    size = kwargs.get("size", ref_text.size)
    leading = kwargs.get("leading", ref_text.leading)
    try:
        space_after = ref_text.spaceAfter
        space_before = ref_text.spaceBefore
    except COMError:
        # Hacky workaround to a value retrieval issue with an unknown cause.
        # This was observed on a duplicated text layer when accessing spaceAfter.
        # https://community.adobe.com/t5/photoshop-ecosystem-discussions/textitem-color-returns-quot-general-photoshop-error-quot/m-p/10900372#M303432
        ref_text.contents = ref_text.contents
        space_after = ref_text.spaceAfter
        space_before = ref_text.spaceBefore
    desc: MakeTextLayerActionDescriptor = {
        "_obj": "make",
        "_target": [{"_ref": "textLayer"}],
        "using": {
            "_obj": "textLayer",
            # If initially empty text is replaced later on that seems
            # to mess up the text size and leading values. At least in my case
            # when rendering a Showcase Adventure card they became very small (< 1 pt).
            # We don't want to use placeholder text either as sometimes no text might
            # be assigned to the layer. Whitespace seems to be an acceptable workaround.
            "textKey": " ",  # text contents
            "textStyleRange": [
                {
                    "_obj": "textStyleRange",
                    "from": 0,
                    "to": 227,
                    "textStyle": {
                        "_obj": "textStyle",
                        "color": {
                            "_obj": "RGBColor",
                            "blue": color.rgb.blue,
                            "grain": color.rgb.green,
                            "red": color.rgb.red,
                        },
                        "fontPostScriptName": ref_text.font,
                        "size": {
                            "_unit": "pointsUnit",
                            "_value": size,
                        },
                        "autoLeading": bool(ref_text.useAutoLeading),
                        "leading": {
                            "_unit": "pointsUnit",
                            "_value": leading,
                        },
                        "autoKern": {
                            "_enum": "autoKern",
                            "_value": "metricsKern"
                            if ref_text.autoKerning is AutoKernType.Metrics
                            else "opticalKern",
                        },
                    },
                }
            ],
            "paragraphStyleRange": [
                {
                    "_obj": "paragraphStyleRange",
                    "from": 0,
                    "to": 227,
                    "paragraphStyle": {
                        "_obj": "paragraphStyle",
                        "spaceBefore": {
                            "_unit": "pointsUnit",
                            "_value": float(space_before),
                        },
                        "spaceAfter": {
                            "_unit": "pointsUnit",
                            "_value": float(space_after),
                        },
                    },
                }
            ],
            "textShape": [
                {
                    "_obj": "textShape",
                    "char": {"_enum": "char", "_value": "box"},
                    "path": {
                        "_obj": "pathClass",
                        "pathComponents": [
                            {
                                "_obj": "pathComponent",
                                "shapeOperation": {
                                    "_enum": "shapeOperation",
                                    "_value": "xor",
                                },
                                "subpathListKey": [
                                    {
                                        "_obj": "subpathsList",
                                        "closedSubpath": True,
                                        "points": points,
                                    }
                                ],
                            }
                        ],
                    },
                }
            ],
        },
    }
    batch_play(desc)

    created_layer = APP.instance.activeDocument.activeLayer
    if not isinstance(created_layer, ArtLayer):
        raise TypeError(
            "Failed to create shaped text layer. Active layer is unexpectedly not an ArtLayer."
        )
    created_layer.name = f"{reference_text.name} - Path"

    try:
        copy_layer_fx(reference_text, created_layer)
    except COMError:
        pass

    return created_layer
