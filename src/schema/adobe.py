"""
* Schema: Photoshop
"""
# Standard Library Imports
from typing import Union, Literal

# Third Party Imports
from omnitils.schema import ArbitrarySchema, Schema

# Local Imports
from src.schema.colors import ColorObject, GradientColor

"""
* Layer Details
"""


class LayerDimensions(Schema):
    """Calculated layer dimension info for a layer."""
    width: int
    height: int
    center_x: int
    center_y: int
    left: int
    right: int
    top: int
    bottom: int


"""
* Layer Effects
"""


class EffectBevel(ArbitrarySchema):
    """Layer Effect: Bevel"""
    highlight_color: ColorObject = [255, 255, 255]
    highlight_opacity: float | int = 70
    shadow_color: ColorObject = [0, 0, 0]
    shadow_opacity: float | int = 72
    global_light: bool = False
    rotation: float | int = 45
    altitude: float | int = 22
    depth: float | int = 100
    size: float | int = 30
    softness: float | int = 14


class EffectColorOverlay(ArbitrarySchema):
    """Layer Effect: Color Overlay"""
    color: ColorObject = [0, 0, 0]
    opacity: float | int = 100


class EffectDropShadow(ArbitrarySchema):
    """Layer Effect: Drop Shadow"""
    color: ColorObject = [0, 0, 0]
    opacity: float | int = 100
    rotation: float | int = 45
    distance: float | int = 10
    spread: float | int = 0
    size: float | int = 0
    noise: float | int = 0


class EffectGradientOverlay(ArbitrarySchema):
    """Layer Effect: Drop Shadow"""
    colors: list[GradientColor] = []
    opacity: int | float = 100
    rotation: int | float = 45
    scale: int | float = 70
    size: int | float = 4096


class EffectStroke(ArbitrarySchema):
    """Layer Effect: Stroke"""
    color: ColorObject = [0, 0, 0]
    weight: int | float = 6
    opacity: int | float = 100
    style: Literal['in', 'insetFrame', 'out', 'outsetFrame', 'center', 'centeredFrame'] = 'out'


# Type: Any layer effect
LayerEffects = Union[
    EffectBevel,
    EffectColorOverlay,
    EffectDropShadow,
    EffectGradientOverlay,
    EffectStroke
]
