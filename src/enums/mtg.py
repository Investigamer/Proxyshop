"""
MTG ENUMS
"""
from src.utils.strings import StrEnum


"""
NAMING CONVENTIONS
"""


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
    UPSIDEDOWN = "upsidedowndfc"
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


# Abilities that aren't italicize, despite fitting the pattern
non_italics_abilities = [
    "Boast",  # Kaldheim
    "Forecast",  # Dissension
    "Gotcha",  # Unhinged
    "Visit",  # Unfinity
    "Whack", "Doodle", "Buzz"  # Unstable
]


"""
DEFAULT COLOR MAPS
"""

mana_color_map = {
    # Default mana symbol colors
    'primary': [0, 0, 0],
    'secondary': [255, 255, 255],
    'c': [204, 194, 193],
    'w': [255, 251, 214],
    'u': [170, 224, 250],
    'b': [204, 194, 193],
    'r': [249, 169, 143],
    'g': [154, 211, 175],
    'bh': [159, 146, 143],
    'c_i': [0, 0, 0],
    'w_i': [0, 0, 0],
    'u_i': [0, 0, 0],
    'b_i': [0, 0, 0],
    'r_i': [0, 0, 0],
    'g_i': [0, 0, 0],
    'bh_i': [0, 0, 0]
}

watermark_color_map = {
    # Default watermark colors
    'W': [183, 157, 88],
    'U': [140, 172, 197],
    'B': [94, 94, 94],
    'R': [198, 109, 57],
    'G': [89, 140, 82],
    'Gold': [202, 179, 77],
    'Land': [94, 84, 72],
    'Artifact': [100, 125, 134],
    'Colorless': [100, 125, 134]
}

pinline_color_map = {
    # Default pinline colors
    'W': [246, 246, 239],
    'U': [0, 117, 190],
    'B': [39, 38, 36],
    'R': [239, 56, 39],
    'G': [0, 123, 67],
    'Gold': [246, 210, 98],
    'Land': [174, 151, 135],
    'Artifact': [230, 236, 242],
    'Colorless': [230, 236, 242],
    'Vehicle': [77, 45, 5]
}

indicator_color_map = {
    # Default color indicator colors
    'W': [248, 244, 240],
    'U': [0, 109, 174],
    'B': [57, 52, 49],
    'R': [222, 60, 35],
    'G': [0, 109, 66],
    'Artifact': [181, 197, 205],
    'Colorless': [214, 214, 220],
    'Land': [165, 150, 132]
}

crown_color_map = {
    # Legendary crown colors
    # TODO: Validate these
    'W': [248, 244, 240],
    'U': [0, 109, 174],
    'B': [57, 52, 49],
    'R': [222, 60, 35],
    'G': [0, 109, 66],
    'Gold': [239, 209, 107],
    'Land': [165, 150, 132],
    'Artifact': [181, 197, 205],
    'Colorless': [214, 214, 220]
}

saga_banner_color_map = {
    # Saga banner colors
    'W': [241, 225, 193],
    'U': [37, 89, 177],
    'B': [59, 51, 48],
    'R': [218, 56, 44],
    'G': [1, 99, 58],
    'Gold': [204, 173, 116],
    'Artifact': [200, 205, 234],
    'Land': [106, 89, 81]
}

saga_stripe_color_map = {
    # Saga stripe colors
    'W': [235, 209, 156],
    'U': [34, 72, 153],
    'B': [30, 24, 18],
    'R': [197, 41, 30],
    'G': [2, 84, 46],
    'Gold': [135, 107, 45],
    'Artifact': [163, 171, 202],
    'Land': [55, 47, 41],
    'Dual': [42, 42, 42]
}
