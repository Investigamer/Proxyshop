"""
Enums for Photoshop Actions
"""
# Standard Library Imports
from enum import Enum
from typing import Literal, Union

# Local Imports
from src.constants import con
from src.utils.strings import StrEnum


class DescriptorEnum(Enum):
    def __call__(self, *args, **kwargs) -> int:
        return self.value

    @property
    def value(self) -> int:
        return int(con.app.stringIDToTypeID(self._value_))


class Dimensions(StrEnum):
    """Layer dimension descriptors."""
    Width = 'width'
    Height = 'height'
    CenterX = 'center_x'
    CenterY = 'center_y'
    Left = 'left'
    Right = 'right'
    Top = 'top'
    Bottom = 'bottom'


class Alignment(DescriptorEnum):
    """Selection alignment descriptors."""
    Top: str = 'ADSTops'
    Bottom: str = 'ADSBottoms'
    Left: str = 'ADSLefts'
    Right: str = 'ADSRights'
    CenterHorizontal: str = 'ADSCentersH'
    CenterVertical: str = 'ADSCentersV'


class TextAlignment(DescriptorEnum):
    """Selection alignment descriptors."""
    Left: str = 'left'
    Right: str = 'right'
    Center: str = 'center'


class Stroke(DescriptorEnum):
    """Stroke effect descriptors."""
    Inside: str = 'insetFrame'
    Outside: str = 'outsetFrame'
    Center: str = 'centeredFrame'

    @staticmethod
    def position(
        pos: Literal[
            'in', 'insetFrame',
            'out', 'outsetFrame',
            'center', 'centeredFrame'
        ]
    ) -> Union[
        'Stroke.Inside.value',
        'Stroke.Outside.value',
        'Stroke.Center.value'
    ]:
        """
        Get the proper stroke action enum from canonical user input.
        @param pos: "in", "out", or "center"
        @return: Proper action descriptor ID.
        """
        if pos in ['in', 'insetFrame']:
            return Stroke.Inside.value
        elif pos in ['out', 'outsetFrame']:
            return Stroke.Outside.value
        elif pos in ['center', 'centeredFrame']:
            return Stroke.Center.value
        return Stroke.Outside.value
