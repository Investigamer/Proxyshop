from collections.abc import Iterable

from photoshop.api import ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import DialogModes, ElementPlacement

from src import APP
from src.helpers.colors import get_color, rgb_black
from src.schema.colors import ColorObject
from src.utils.uxp.path import PathPointConf, create_path


def create_shape_layer(
    points: Iterable[PathPointConf],
    name: str = "",
    relative_layer: ArtLayer | LayerSet | None = None,
    placement: ElementPlacement = ElementPlacement.PlaceAfter,
    hide: bool = False,
    color: ColorObject | None = None,
) -> ArtLayer:
    solid_color = get_color(color) if color else rgb_black()
    docref = APP.instance.activeDocument

    create_path(points)

    # Convert path to a layer
    ref1 = ActionReference()
    desc1 = ActionDescriptor()
    desc2 = ActionDescriptor()
    desc3 = ActionDescriptor()
    desc4 = ActionDescriptor()
    ref1.putClass(APP.instance.sID("contentLayer"))
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc4.putDouble(APP.instance.sID("red"), solid_color.rgb.red)
    desc4.putDouble(APP.instance.sID("green"), solid_color.rgb.green)
    desc4.putDouble(APP.instance.sID("blue"), solid_color.rgb.blue)
    desc3.putObject(APP.instance.sID("color"), APP.instance.sID("RGBColor"), desc4)
    desc2.putObject(
        APP.instance.sID("type"), APP.instance.sID("solidColorLayer"), desc3
    )
    desc1.putObject(APP.instance.sID("using"), APP.instance.sID("contentLayer"), desc2)
    APP.instance.executeAction(
        APP.instance.sID("make"), desc1, DialogModes.DisplayNoDialogs
    )

    layer = docref.activeLayer
    if not isinstance(layer, ArtLayer):
        raise TypeError(
            "Failed to create shape layer. Active layer is unexpectedly not an ArtLayer."
        )
    if name:
        layer.name = name
    if hide:
        layer.visible = False
    if relative_layer:
        layer.move(relative_layer, placement)

    return layer
