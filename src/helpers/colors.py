"""
COLOR HELPERS
"""
# Standard Library Imports
from typing import Union, Optional

# Third Party Imports
from photoshop.api import SolidColor, DialogModes, ActionList, ActionDescriptor, ColorModel, LayerKind
from photoshop.api._artlayer import ArtLayer

# Local Imports
from src.constants import con

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
CONVERTING COLOR
"""


def hex_to_rgb(color: str) -> list[int]:
    """
    Convert a hexadecimal color code into RGB values.
    @param color: Hexadecimal color code, e.g. #F5D676
    @return: Color in RGB list notation.
    """
    if '#' in color:
        color = color[1:]
    return [int(color[i:i+2], 16) for i in (0, 2, 4)]


"""
GETTING COLOR
"""


def rgb_black() -> SolidColor:
    """
    Creates a black SolidColor object.
    @return: SolidColor object.
    """
    return get_rgb(0, 0, 0)


def rgb_grey() -> SolidColor:
    """
    Creates a grey SolidColor object.
    @return: SolidColor object.
    """
    return get_rgb(170, 170, 170)


def rgb_white() -> SolidColor:
    """
    Creates a white SolidColor object.
    @return: SolidColor object.
    """
    return get_rgb(255, 255, 255)


def get_rgb(r: int, g: int, b: int) -> SolidColor:
    """
    Creates a SolidColor object with the given RGB values.
    @param r: Integer from 0 to 255 for red spectrum.
    @param g: Integer from 0 to 255 for green spectrum.
    @param b: Integer from 0 to 255 for blue spectrum.
    @return: SolidColor object.
    """
    color = SolidColor()
    color.rgb.red = r
    color.rgb.green = g
    color.rgb.blue = b
    return color


def get_cmyk(c: float, m: float, y: float, k: float) -> SolidColor:
    """
    Creates a SolidColor object with the given CMYK values.
    @param c: Float from 0.0 to 100.0 for Cyan component.
    @param m: Float from 0.0 to 100.0 for Magenta component.
    @param y: Float from 0.0 to 100.0 for Yellow component.
    @param k: Float from 0.0 to 100.0 for black component.
    @return: SolidColor object.
    """
    color = SolidColor()
    color.cmyk.cyan = c
    color.cmyk.magenta = m
    color.cmyk.yellow = y
    color.cmyk.black = k
    return color


def get_color(color: Union[SolidColor, list[int], str, dict]) -> SolidColor:
    """
    Automatically get either cmyk or rgb color given a range of
    @param color: Array containing 3 (RGB) or 4 (CMYK) numbers between 0 and 255, or the name of a known color.
    @return: SolidColor object.
    """
    try:
        if isinstance(color, SolidColor):
            # Solid color given
            return color
        if isinstance(color, dict):
            # Color dictionary
            if 'r' in color.keys():
                # RGB
                return get_rgb(color['r'], color['g'], color['b'])
            elif 'c' in color.keys():
                # CMYK
                return get_cmyk(color['c'], color['m'], color['y'], color['k'])
        if isinstance(color, str):
            # Named color
            if color in con.colors:
                return get_color(con.colors[color])
            # Hexadecimal
            return get_rgb(*hex_to_rgb(color))
        if isinstance(color, list):
            # List notation
            if len(color) == 3:
                # RGB
                return get_rgb(*color)
            elif len(color) == 4:
                # CMYK
                return get_cmyk(*color)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid color notation given: {color}")
    raise ValueError(f"Unrecognized color notation given: {color}")


def get_text_layer_color(layer: ArtLayer) -> SolidColor:
    """
    Occasionally, Photoshop has issues with retrieving the color of a text layer. This helper guards
    against errors and null values by defaulting to rgb_black() in the event of a problem.
    @param layer: Layer object that must be TextLayer
    @return: SolidColor object representing the color of the text item.
    """
    if isinstance(layer, ArtLayer) and layer.kind == LayerKind.TextLayer:
        if hasattr(layer.textItem, 'color'):
            return layer.textItem.color
        print(f"Couldn't retrieve color of layer: {layer.name}")
    return rgb_black()


"""
APPLYING COLOR
"""


def apply_rgb(action: ActionDescriptor, color: SolidColor) -> None:
    """
    Apply RGB SolidColor object to action descriptor.
    @param action: ActionDescriptor object.
    @param color: SolidColor object matching RGB model.
    """
    ad = ActionDescriptor()
    ad.putDouble(sID("red"), color.rgb.red)
    ad.putDouble(sID("green"), color.rgb.green)
    ad.putDouble(sID("blue"), color.rgb.blue)
    action.putObject(sID("color"), sID("RGBColor"), ad)


def apply_cmyk(action: ActionDescriptor, color: SolidColor) -> None:
    """
    Apply CMYK SolidColor object to action descriptor.
    @param action: ActionDescriptor object.
    @param color: SolidColor object matching CMYK model.
    """
    ad = ActionDescriptor()
    ad.putDouble(sID("cyan"), color.cmyk.cyan)
    ad.putDouble(sID("magenta"), color.cmyk.magenta)
    ad.putDouble(sID("yellowColor"), color.cmyk.yellow)
    ad.putDouble(sID("black"), color.cmyk.black)
    action.putObject(sID("color"), sID("CMYKColorClass"), ad)


def apply_color(action: ActionDescriptor, color: SolidColor) -> None:
    """
    Applies color to the specified action descriptor.
    @param action: ActionDescriptor object.
    @param color: CMYK or RGB SolidColor object.
    """
    if color.model == ColorModel.RGBModel:
        return apply_rgb(action, color)
    if color.model == ColorModel.CMYKModel:
        return apply_cmyk(action, color)
    raise ValueError(f"Received unsupported color object: {color}")


def add_color_to_gradient(
    action_list: ActionList,
    color: SolidColor,
    location: int,
    midpoint: int
) -> None:
    """

    @param action_list: Action list to add this color to.
    @param color: SolidColor object
    @param location: Location of the color along the track.
    @param midpoint: Percentage midpoint between this color and the next.
    """
    action = ActionDescriptor()
    apply_color(action, color)
    action.putEnumerated(sID("type"), sID("colorStopType"), sID("userStop"))
    action.putInteger(sID("location"), location)
    action.putInteger(sID("midpoint"), midpoint)
    action_list.putObject(sID("colorStop"), action)


def fill_layer_primary():
    """Fill active layer using foreground color."""
    desc1 = ActionDescriptor()
    desc1.putEnumerated(sID("using"), sID("fillContents"), sID("foregroundColor"))
    app.executeAction(sID("fill"), desc1, NO_DIALOG)


def get_pinline_gradient(colors: str, color_map: Optional[dict] = None) -> Union[SolidColor, list[dict]]:
    """
    Return a gradient color list notation for some given pinline colors.
    @param colors: Pinline colors to produce a gradient.
    @param color_map: Color map to color the pinlines.
    @return: Gradient color list notation.
    """
    # Establish the color_map
    if not color_map:
        color_map = con.pinline_colors

    # Return our colors
    if not colors:
        return get_color(color_map.get('Artifact', [0, 0, 0]))
    if len(colors) == 1:
        return get_color(color_map.get(colors, [0, 0, 0]))
    if len(colors) == 2:
        return [
            {
                'color': get_color(color_map.get(colors[0], [0, 0, 0])),
                'location': 1638, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': 2458, 'midpoint': 50,
            }
        ]
    if len(colors) == 3:
        return [
            {
                'color': get_color(color_map.get(colors[0], [0, 0, 0])),
                'location': 1065, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': 1475, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': 2621, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[2], [0, 0, 0])),
                'location': 3031, 'midpoint': 50
            }
        ]
    return get_color(color_map.get(colors, [0, 0, 0]))
