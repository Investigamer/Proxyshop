"""
Enums for Photoshop Actions
"""
from enum import Enum
from typing import Literal, Union

import photoshop.api as ps
app = ps.Application()
cID = app.charIDToTypeID
sID = app.stringIDToTypeID


class Alignment(Enum):
    """
    Layer alignment descriptors.
    """
    Top: int = int(sID('ADSTops'))
    Bottom: int = int(sID('ADSBottoms'))
    Left: int = int(sID('ADSLefts'))
    Right: int = int(sID('ADSRights'))
    CenterHorizontal: int = int(sID('ADSCentersH'))
    CenterVertical: int = int(sID('ADSCentersV'))


class Stroke(Enum):
    """
    Stroke effect descriptors.
    """
    Inside: int = int(sID('insetFrame'))
    Outside: int = int(sID('outsetFrame'))
    Center: int = int(sID('centeredFrame'))

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
