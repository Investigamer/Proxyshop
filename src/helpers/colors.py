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
from src.enums.layers import LAYERS
from src.enums.mtg import pinline_color_map

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
    Convert a hexadecimal color code into RGB value list.
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


def get_rgb_from_hex(hex_code: str) -> SolidColor:
    """
    Creates an RGB SolidColor object with the given hex value. Allows prepending # or without.
    @param hex_code: Hexadecimal color code.
    @return: SolidColor object.
    """
    # Remove hashtag
    hex_code = hex_code[1:] if hex_code.startswith('#') else hex_code
    # Hexadecimal abbreviated
    if len(hex_code) == 3:
        hex_code = "".join([n * 2 for n in hex_code])
    # Convert to RGB
    color = SolidColor()
    color.rgb.hexValue = hex_code
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
            return get_rgb_from_hex(color)
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


def apply_rgb_from_list(action: ActionDescriptor, color: list[int], color_type: str = 'color') -> None:
    """
    Applies RGB color to action descriptor from a list of values.
    @param action: ActionDescriptor object.
    @param color: List of integers for R, G, B.
    @param color_type: Color action descriptor type, defaults to 'color'.
    """
    ad = ActionDescriptor()
    ad.putDouble(sID("red"), color[0])
    ad.putDouble(sID("green"), color[1])
    ad.putDouble(sID("blue"), color[2])
    action.putObject(sID(color_type), sID("RGBColor"), ad)


def apply_cmyk_from_list(action: ActionDescriptor, color: list[int], color_type: str = 'color') -> None:
    """
    Applies CMYK color to action descriptor from a list of values.
    @param action: ActionDescriptor object.
    @param color: List of integers for R, G, B.
    @param color_type: Color action descriptor type, defaults to 'color'.
    """
    ad = ActionDescriptor()
    ad.putDouble(sID("cyan"), color[0])
    ad.putDouble(sID("magenta"), color[1])
    ad.putDouble(sID("yellowColor"), color[2])
    ad.putDouble(sID("black"), color[3])
    action.putObject(sID(color_type), sID("CMYKColorClass"), ad)


def apply_rgb(action: ActionDescriptor, c: SolidColor, color_type: str = 'color') -> None:
    """
    Apply RGB SolidColor object to action descriptor.
    @param action: ActionDescriptor object.
    @param c: SolidColor object matching RGB model.
    @param color_type: Color action descriptor type, defaults to 'color'.
    """
    apply_rgb_from_list(action, [c.rgb.red, c.rgb.green, c.rgb.blue], color_type)


def apply_cmyk(action: ActionDescriptor, c: SolidColor, color_type: str = 'color') -> None:
    """
    Apply CMYK SolidColor object to action descriptor.
    @param action: ActionDescriptor object.
    @param c: SolidColor object matching CMYK model.
    @param color_type: Color action descriptor type, defaults to 'color'.
    """
    apply_cmyk_from_list(action, [c.cmyk.cyan, c.cmyk.magenta, c.cmyk.yellow, c.cmyk.black], color_type)


def apply_color(action: ActionDescriptor, color: Union[list[int], SolidColor], color_type: str = 'color') -> None:
    """
    Applies color to the specified action descriptor.
    @param action: ActionDescriptor object.
    @param color: RGB/CMYK SolidColor object, or list of RGB/CMYK values.
    @param color_type: Color action descriptor type, defaults to 'color'.
    """
    if isinstance(color, list):
        # List notation
        return apply_rgb_from_list(action, color, color_type) if (
            len(color) < 4
        ) else apply_cmyk_from_list(action, color, color_type)
    if color.model == ColorModel.RGBModel:
        # RGB SolidColor object
        return apply_rgb(action, color, color_type)
    if color.model == ColorModel.CMYKModel:
        # CMYK SolidColor object
        return apply_cmyk(action, color, color_type)
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


def get_pinline_gradient(
        colors: str,
        color_map: Optional[dict] = None,
        location_map: dict = None
) -> Union[SolidColor, list[dict]]:
    """
    Return a gradient color list notation for some given pinline colors.
    @param colors: Pinline colors to produce a gradient.
    @param color_map: Color map to color the pinlines.
    @param location_map: Location map to position gradients.
    @return: Gradient color list notation.
    """
    # Establish the color_map
    if not color_map:
        color_map = pinline_color_map

    # Establish the location map
    if not location_map:
        location_map = con.gradient_locations

    # Return our colors
    if not colors:
        return get_color(color_map.get('Artifact', [0, 0, 0]))
    if len(colors) == 1:
        return get_color(color_map.get(colors, [0, 0, 0]))
    if len(colors) == 2:
        return [
            {
                'color': get_color(color_map.get(colors[0], [0, 0, 0])),
                'location': location_map[2][0] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': location_map[2][1] * 4096, 'midpoint': 50,
            }
        ]
    if len(colors) == 3:
        return [
            {
                'color': get_color(color_map.get(colors[0], [0, 0, 0])),
                'location': location_map[3][0] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': location_map[3][1] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': location_map[3][2] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[2], [0, 0, 0])),
                'location': location_map[3][3] * 4096, 'midpoint': 50
            }
        ]
    if len(colors) == 4 and colors not in [LAYERS.LAND, LAYERS.GOLD]:
        return [
            {
                'color': get_color(color_map.get(colors[0], [0, 0, 0])),
                'location': location_map[4][0] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': location_map[4][1] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[1], [0, 0, 0])),
                'location': location_map[4][2] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[2], [0, 0, 0])),
                'location': location_map[4][3] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[2], [0, 0, 0])),
                'location': location_map[4][4] * 4096, 'midpoint': 50
            },
            {
                'color': get_color(color_map.get(colors[3], [0, 0, 0])),
                'location': location_map[4][5] * 4096, 'midpoint': 50
            }
        ]
    return get_color(color_map.get(colors, [0, 0, 0]))
