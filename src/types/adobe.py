"""
Types for Photoshop Actions
"""
# Standard Library Imports
from __future__ import absolute_import
from typing import TypedDict, Literal, Union

# Third Party Imports
from photoshop.api import SolidColor
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document
from comtypes.client.lazybind import Dispatch
from typing_extensions import NotRequired

"""
LAYER EFFECTS
"""


class EffectStroke(TypedDict):
    """Layer Effect: Stroke"""
    type: Literal['stroke']
    weight: NotRequired[int]
    color: SolidColor
    opacity: NotRequired[int]
    style: Literal[
        'in', 'insetFrame',
        'out', 'outsetFrame',
        'center', 'centeredFrame'
    ]


class EffectDropShadow(TypedDict):
    """Layer Effect: Drop Shadow"""
    type: Literal['drop-shadow']
    opacity: NotRequired[Union[float, int]]
    rotation: NotRequired[Union[float, int]]
    distance: NotRequired[Union[float, int]]
    spread: NotRequired[Union[float, int]]
    size: NotRequired[Union[float, int]]
    noise: NotRequired[Union[float, int]]


class EffectGradientColor(TypedDict):
    """An individual color within a EffectGradientOverlay."""
    color: SolidColor
    location: NotRequired[int]
    midpoint: NotRequired[int]


class EffectGradientOverlay(TypedDict):
    """Layer Effect: Drop Shadow"""
    type: Literal['gradient-overlay']
    size: NotRequired[int]
    scale: NotRequired[int]
    rotation: NotRequired[int]
    opacity: NotRequired[int]
    colors: list[EffectGradientColor]


class EffectColorOverlay(TypedDict):
    """Layer Effect: Color Overlay"""
    type: Literal['color-overlay']
    opacity: NotRequired[Union[float, int]]
    color: Union[SolidColor, list[int]]


class EffectBevel(TypedDict):
    """Layer Effect: Bevel"""
    type: Literal['bevel']
    highlight_opacity: NotRequired[Union[float, int]]
    highlight_color: NotRequired[Union[SolidColor, list[int]]]
    shadow_opacity: NotRequired[Union[float, int]]
    shadow_color: NotRequired[Union[SolidColor, list[int]]]
    rotation: NotRequired[Union[float, int]]
    altitude: NotRequired[Union[float, int]]
    depth: NotRequired[Union[float, int]]
    size: NotRequired[Union[float, int]]
    softness: NotRequired[Union[float, int]]


"""
* Types
"""

# Check against: isinstance
LayerContainer = LayerSet, Document, Dispatch
LayerObject = LayerSet, ArtLayer, Dispatch

# Type: Any layer effect
LayerEffects = Union[
    EffectStroke,
    EffectDropShadow,
    EffectGradientOverlay,
    EffectColorOverlay,
    EffectBevel
]
