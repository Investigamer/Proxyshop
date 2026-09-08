"""
* Schema: Photoshop
"""

from typing import Literal

from pydantic import BaseModel

from src.schema.colors import ColorObject, GradientColor

"""
* Layer Details
"""


class LayerDimensions(BaseModel):
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

BlendMode = Literal[
    "normal",
    "dissolve",
    "darken",
    "multiply",
    "colorBurn",
    "linearBurn",
    "darkerColor",
    "lighten",
    "screen",
    "colorDodge",
    "linearDodge",
    "lighterColor",
    "overlay",
    "softLight",
    "hardLight",
    "vividLight",
    "linearLight",
    "pinLight",
    "hardMix",
    "difference",
    "exclusion",
    "subtract",
    "divide",
    "hue",
    "saturation",
    "color",
    "luminosity",
]
GradientMethod = Literal["perceptual", "linear", "classic", "smooth", "stripes"]


class EffectBevel(BaseModel):
    """Layer Effect: Bevel"""

    highlight_color: ColorObject = (255, 255, 255)
    highlight_opacity: float | int = 70
    shadow_color: ColorObject = (0, 0, 0)
    shadow_opacity: float | int = 72
    global_light: bool = False
    rotation: float | int = 45
    altitude: float | int = 22
    depth: float | int = 100
    size: float | int = 30
    softness: float | int = 14


class EffectColorOverlay(BaseModel):
    """Layer Effect: Color Overlay"""

    color: ColorObject = (0, 0, 0)
    opacity: float | int = 100


class EffectDropShadow(BaseModel):
    """Layer Effect: Drop Shadow"""

    color: ColorObject = (0, 0, 0)
    opacity: float | int = 100
    rotation: float | int = 45
    distance: float | int = 10
    spread: float | int = 0
    size: float | int = 0
    noise: float | int = 0


class EffectGradientOverlay(BaseModel):
    """Layer Effect: Drop Shadow"""

    colors: list[GradientColor] = []
    blend_mode: BlendMode = "normal"
    dither: bool = False
    opacity: int | float = 100
    rotation: int | float = 45
    scale: int | float = 70
    size: int | float = 4096
    method: GradientMethod = "classic"


class EffectStroke(BaseModel):
    """Layer Effect: Stroke"""

    color: ColorObject = (0, 0, 0)
    weight: int | float = 6
    opacity: int | float = 100
    style: Literal[
        "in", "insetFrame", "out", "outsetFrame", "center", "centeredFrame"
    ] = "out"


# Type: Any layer effect
LayerEffects = (
    EffectBevel
    | EffectColorOverlay
    | EffectDropShadow
    | EffectGradientOverlay
    | EffectStroke
)
