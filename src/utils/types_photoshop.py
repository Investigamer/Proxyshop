"""
Types for Photoshop Actions
"""
# Standard Library Imports
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
    """
    Layer Effect - Stroke
    """
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
    """
    Layer Effect - Drop Shadow
    """
    type: Literal['drop-shadow']
    opacity: NotRequired[int]
    rotation: NotRequired[int]
    distance: NotRequired[int]
    spread: NotRequired[int]
    size: NotRequired[int]


class EffectGradientColor(TypedDict):
    """
    An individual color within a Gradient Layer Effect.
    """
    color: SolidColor
    location: NotRequired[int]
    midpoint: NotRequired[int]


class EffectGradientOverlay(TypedDict):
    """
    Layer Effect - Drop Shadow
    """
    type: Literal['gradient-overlay']
    size: NotRequired[int]
    scale: NotRequired[int]
    rotation: NotRequired[int]
    opacity: NotRequired[int]
    colors: list[EffectGradientColor]


class EffectColorOverlay(TypedDict):
    """
    Layer Effect - Color Overlay
    """
    type: Literal['color-overlay']
    opacity: NotRequired[int]
    color: SolidColor


LayerEffects = Union[EffectStroke, EffectDropShadow, EffectGradientOverlay, EffectColorOverlay]


"""
LAYER TYPES
"""


LayerContainer = LayerSet, Document, Dispatch
LayerObject = LayerSet, ArtLayer, Dispatch
