"""
Types for Photoshop Actions
"""
from typing import TypedDict, Literal, Union
from photoshop.api import SolidColor

"""
LAYER EFFECTS
"""


class EffectStroke(TypedDict):
    """
    Layer Effect - Stroke
    """
    type: Literal['stroke']
    weight: int
    color: SolidColor
    opacity: int
    style: Literal[
        'in', 'insetFrame',
        'out', 'outsetFrame',
        'center', 'centeredFrame'
    ]


class EffectDropShadow(TypedDict):
    """
    Layer Effect - Drop Shadow
    """
    type: Literal['drop-shadow']
    opacity: int
    rotation: int
    distance: int
    spread: int
    size: int


class EffectGradientColor(TypedDict):
    """
    An individual color within a Gradient Layer Effect.
    """
    color: SolidColor
    location: int
    midpoint: int


class EffectGradientOverlay(TypedDict):
    """
    Layer Effect - Drop Shadow
    """
    type: Literal['gradient-overlay']
    size: int
    scale: int
    rotation: int
    opacity: int
    colors: list[EffectGradientColor]


class EffectColorOverlay(TypedDict):
    """
    Layer Effect - Color Overlay
    """
    type: Literal['color-overlay']
    opacity: int
    color: SolidColor


LayerEffects = Union[EffectStroke, EffectDropShadow, EffectGradientOverlay, EffectColorOverlay]
