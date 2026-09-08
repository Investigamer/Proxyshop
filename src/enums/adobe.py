"""
* Enums for Photoshop Actions
"""

from enum import Enum, StrEnum
from typing import Literal

from src import APP

"""
* Action Descriptors
"""


class DescriptorEnum(Enum):
    def __call__(self) -> int:
        return self.value

    @property
    def value(self) -> int:
        return int(APP.instance.sID(self._value_))


class Dimensions(StrEnum):
    """Layer dimension descriptors."""

    Width = "width"
    Height = "height"
    CenterX = "center_x"
    CenterY = "center_y"
    Left = "left"
    Right = "right"
    Top = "top"
    Bottom = "bottom"


class Alignment(DescriptorEnum):
    """Selection alignment descriptors."""

    Top = "ADSTops"
    Bottom = "ADSBottoms"
    Left = "ADSLefts"
    Right = "ADSRights"
    CenterHorizontal = "ADSCentersH"
    CenterVertical = "ADSCentersV"


class TextAlignment(DescriptorEnum):
    """Selection alignment descriptors."""

    Left = "left"
    Right = "right"
    Center = "center"


class Stroke(DescriptorEnum):
    """Stroke effect descriptors."""

    Inside = "insetFrame"
    Outside = "outsetFrame"
    Center = "centeredFrame"

    @staticmethod
    def position(
        pos: Literal[
            "in", "insetFrame", "out", "outsetFrame", "center", "centeredFrame"
        ],
    ) -> int:
        """
        Get the proper stroke action enum from canonical user input.
        @param pos: "in", "out", or "center"
        @return: Proper action descriptor ID.
        """
        if pos in ["in", "insetFrame"]:
            return Stroke.Inside.value
        elif pos in ["center", "centeredFrame"]:
            return Stroke.Center.value
        return Stroke.Outside.value
