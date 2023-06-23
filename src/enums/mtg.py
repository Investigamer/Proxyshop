"""
MTG ENUMS
"""
from src.utils.strings import StrEnum


class Rarity(StrEnum):
    """Card rarities."""
    C = "common"
    U = "uncommon"
    R = "rare"
    M = "mythic"
    S = "special"
    B = "bonus"
    T = "timeshifted"
