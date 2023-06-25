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


class TransformIcons(StrEnum):
    """Transform icon names."""
    MOONELDRAZI = "mooneldrazidfc"
    COMPASSLAND = "compasslanddfc"
    ORIGINPW = "originpwdfc"
    CONVERT = "convertdfc"
    SUNMOON = "sunmoondfc"
    FAN = "fandfc"
    MELD = "meld"


# Basic land dictionary
BASIC_LANDS = {
    "plains": "Basic Land — Plains",
    "island": "Basic Land — Island",
    "swamp": "Basic Land — Swamp",
    "mountain": "Basic Land — Mountain",
    "forest": "Basic Land — Forest",
    "wastes": "Basic Land",
    "snowcoveredplains": "Basic Snow Land — Plains",
    "snowcoveredisland": "Basic Snow Land — Island",
    "snowcoveredswamp": "Basic Snow Land — Swamp",
    "snowcoveredmountain": "Basic Snow Land — Mountain",
    "snowcoveredforest": "Basic Snow Land — Forest"
}