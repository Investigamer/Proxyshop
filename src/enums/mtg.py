"""
* Enums: MTG Related Data
"""
# Standard Library Imports
from typing import Union

# Third Party Imports
from photoshop.api import SolidColor

# Local Imports
from src.utils.schema import DictSchema, Schema
from src.utils.strings import StrEnum
from src.utils.regex import Reg

"""
* Card Layout Nomenclature
"""


class LayoutCategory(StrEnum):
    """Card layout category, broad naming used for displaying on GUI elements."""
    Adventure = 'Adventure'
    Battle = 'Battle'
    Class = 'Class'
    Ixalan = 'Ixalan'
    Leveler = 'Leveler'
    MDFC = 'MDFC'
    Mutate = 'Mutate'
    Normal = 'Normal'
    Planar = 'Planar'
    Planeswalker = 'Planeswalker'
    PlaneswalkerMDFC = 'PW MDFC'
    PlaneswalkerTransform = 'PW Transform'
    Prototype = 'Prototype'
    Saga = 'Saga'
    Split = 'Split'
    Token = 'Token'
    Transform = 'Transform'


class LayoutType(StrEnum):
    """Card layout type, fine-grained naming separated by front/back where applicable."""
    Adventure = 'adventure'
    Battle = 'battle'
    Class = 'class'
    Ixalan = 'ixalan'
    Leveler = 'leveler'
    MDFCBack = 'mdfc_back'
    MDFCFront = 'mdfc_front'
    Mutate = 'mutate'
    Normal = 'normal'
    Planar = 'planar'
    Planeswalker = 'planeswalker'
    PlaneswalkerMDFCBack = 'pw_mdfc_back'
    PlaneswalkerMDFCFront = 'pw_mdfc_front'
    PlaneswalkerTransformBack = 'pw_tf_back'
    PlaneswalkerTransformFront = 'pw_tf_front'
    Prototype = 'prototype'
    Saga = 'saga'
    Split = 'split'
    TransformBack = 'transform_back'
    TransformFront = 'transform_front'


class LayoutScryfall(StrEnum):
    """Card layout type, according to Scryfall data."""
    Normal = 'normal'
    Split = 'split'
    Flip = 'flip'
    Transform = 'transform'
    MDFC = 'modal_dfc'
    Meld = 'meld'
    Leveler = 'leveler'
    Class = 'class'
    Saga = 'saga'
    Adventure = 'adventure'
    Mutate = 'mutate'
    Prototype = 'prototype'
    Battle = 'battle'
    Planar = 'planar'
    Scheme = 'scheme'
    Vanguard = 'vanguard'
    Token = 'token'
    DoubleFacedToken = 'double_faced_token'
    Emblem = 'emblem'
    Augment = 'augment'
    Host = 'host'
    ArtSeries = 'art_series'
    ReversibleCard = 'reversible_card'

    # Definitions added to Scryfall data in postprocessing
    Planeswalker = 'planeswalker'
    PlaneswalkerMDFC = 'planeswalker_mdfc'
    PlaneswalkerTransform = 'planeswalker_tf'


"""Maps Layout categories to a list of equivalent Layout types."""
layout_map_category: dict[LayoutCategory, list[LayoutType]] = {
    LayoutCategory.Normal: [LayoutType.Normal],
    LayoutCategory.MDFC: [LayoutType.MDFCFront, LayoutType.MDFCBack],
    LayoutCategory.Transform: [LayoutType.TransformFront, LayoutType.TransformBack],
    LayoutCategory.Planeswalker: [LayoutType.Planeswalker],
    LayoutCategory.PlaneswalkerMDFC: [LayoutType.PlaneswalkerMDFCFront, LayoutType.PlaneswalkerMDFCBack],
    LayoutCategory.PlaneswalkerTransform: [LayoutType.PlaneswalkerTransformFront, LayoutType.PlaneswalkerTransformBack],
    LayoutCategory.Saga: [LayoutType.Saga],
    LayoutCategory.Class: [LayoutType.Class],
    LayoutCategory.Ixalan: [LayoutType.Ixalan],
    LayoutCategory.Mutate: [LayoutType.Mutate],
    LayoutCategory.Prototype: [LayoutType.Prototype],
    LayoutCategory.Adventure: [LayoutType.Adventure],
    LayoutCategory.Leveler: [LayoutType.Leveler],
    LayoutCategory.Split: [LayoutType.Split],
    LayoutCategory.Battle: [LayoutType.Battle],
    LayoutCategory.Planar: [LayoutType.Planar]
}


"""Maps Layout types to their equivalent Layout category."""
layout_map_types = {
    raw: named for named, raw in sum([
        [(k, n) for n in names] for k, names in layout_map_category.items()
    ], [])
}


"""Maps display formatted layout types to a singular layout type.."""
layout_map_display_condition = {
    f'{LayoutCategory.Transform} Front': LayoutType.TransformFront,
    f'{LayoutCategory.Transform} Back': LayoutType.TransformBack,
    f'{LayoutCategory.MDFC} Front': LayoutType.MDFCFront,
    f'{LayoutCategory.MDFC} Back': LayoutType.MDFCBack,
    f'{LayoutCategory.PlaneswalkerTransform} Front': LayoutType.PlaneswalkerTransformFront,
    f'{LayoutCategory.PlaneswalkerTransform} Back': LayoutType.PlaneswalkerTransformBack,
    f'{LayoutCategory.PlaneswalkerMDFC} Front': LayoutType.PlaneswalkerMDFCFront,
    f'{LayoutCategory.PlaneswalkerMDFC} Back': LayoutType.PlaneswalkerMDFCBack
}


"""Maps display formatted layout types to a combined group of two layout types."""
layout_map_display_condition_dual = {
    LayoutCategory.Transform: [
        LayoutType.TransformFront,
        LayoutType.TransformBack],
    LayoutCategory.MDFC: [
        LayoutType.MDFCFront,
        LayoutType.MDFCBack],
    LayoutCategory.PlaneswalkerTransform: [
        LayoutType.PlaneswalkerTransformFront,
        LayoutType.PlaneswalkerTransformBack],
    LayoutCategory.PlaneswalkerMDFC: [
        LayoutType.PlaneswalkerMDFCFront,
        LayoutType.PlaneswalkerMDFCBack],
}


"""Maps Layout types to a display formatted Layout category (with Back or Front)."""
layout_map_types_display = {
    raw: (
        f'{named} Front' if 'front' in raw else (
            f'{named} Back' if 'back' in raw else named)
    ) for raw, named in layout_map_types.items()
}


"""
* Card Typeline Types
"""


class CardTypes(StrEnum):
    """Represents main card types."""
    Artifact = 'Artifact'
    Battle = 'Battle'
    Conspiracy = 'Conspiracy'
    Creature = 'Creature'
    Enchantment = 'Enchantment'
    Instant = 'Instant'
    Land = 'Land'
    Phenomenon = 'Phenomenon'
    Plane = 'Plane'
    Planeswalker = 'Planeswalker'
    Scheme = 'Scheme'
    Sorcery = 'Sorcery'
    Tribal = 'Tribal'
    Vanguard = 'Vanguard'


class CardTypesSuper(StrEnum):
    """Represents card supertypes."""
    Basic = 'Basic'
    Elite = 'Elite'
    Host = 'Host'
    Legendary = 'Legendary'
    Ongoing = 'Ongoing'
    Snow = 'Snow'
    World = 'World'


"""
* Symbol Libraries
"""

mana_symbol_map = {
    "{W/P}": "Qp",
    "{U/P}": "Qp",
    "{B/P}": "Qp",
    "{R/P}": "Qp",
    "{G/P}": "Qp",
    "{W/U/P}": "Qqyz",
    "{U/B/P}": "Qqyz",
    "{B/R/P}": "Qqyz",
    "{R/G/P}": "Qqyz",
    "{G/W/P}": "Qqyz",
    "{W/B/P}": "Qqyz",
    "{B/G/P}": "Qqyz",
    "{G/U/P}": "Qqyz",
    "{U/R/P}": "Qqyz",
    "{R/W/P}": "Qqyz",
    "{A}": "oi",
    "{E}": "e",
    "{T}": "ot",
    "{X}": "ox",
    "{Y}": "oY",
    "{Z}": "oZ",
    "{∞}": "o∞",
    "{0}": "o0",
    "{1}": "o1",
    "{2}": "o2",
    "{3}": "o3",
    "{4}": "o4",
    "{5}": "o5",
    "{6}": "o6",
    "{7}": "o7",
    "{8}": "o8",
    "{9}": "o9",
    "{10}": "oA",
    "{11}": "oB",
    "{12}": "oC",
    "{13}": "oD",
    "{14}": "oE",
    "{15}": "oF",
    "{16}": "oG",
    "{17}": "oÅ",
    "{18}": "oÆ",
    "{19}": "oÃ",
    "{20}": "oK",
    "{W}": "ow",
    "{U}": "ou",
    "{B}": "ob",
    "{R}": "or",
    "{G}": "og",
    "{C}": "oc",
    "{W/U}": "QqLS",
    "{U/B}": "QqMT",
    "{B/R}": "QqNU",
    "{R/G}": "QqOV",
    "{G/W}": "QqPR",
    "{W/B}": "QqLT",
    "{B/G}": "QqNV",
    "{G/U}": "QqPS",
    "{U/R}": "QqMU",
    "{R/W}": "QqOR",
    "{2/W}": "QqWR",
    "{2/U}": "QqWS",
    "{2/B}": "QqWT",
    "{2/R}": "QqWU",
    "{2/G}": "QqWV",
    "{S}": "omn",
    "{Q}": "ol",
    "{CHAOS}": "?"
}

"""
* Naming Conventions
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


"""
* Text Formatting Cases
"""

# Abilities that aren't italicize, despite fitting the pattern
non_italics_abilities = [
    "Boast",  # Kaldheim
    "Forecast",  # Dissension
    "Gotcha",  # Unhinged
    "Visit",  # Unfinity
    "Whack", "Doodle", "Buzz"  # Unstable
]

# Edge case Planeswalkers with tall ability box
planeswalkers_tall = [
    "Gideon Blackblade",
    "Comet, Stellar Pup"
]

"""
* Colors & Gradient Maps
"""

# Represents a color value
ColorObject = Union[str, list[int], type[SolidColor]]


class ColorMap(DictSchema):
    """Defines RGB or CMYK color values mapped to string keys."""
    W: ColorObject = [246, 246, 239]
    U: ColorObject = [0, 117, 190]
    B: ColorObject = [39, 38, 36]
    R: ColorObject = [239, 56, 39]
    G: ColorObject = [0, 123, 67]
    Gold: ColorObject = [246, 210, 98]
    Land: ColorObject = [174, 151, 135]
    Artifact: ColorObject = [230, 236, 242]
    Colorless: ColorObject = [230, 236, 242]
    Vehicle: ColorObject = [77, 45, 5]


class ManaColors(DictSchema):
    """Defines the mana colors for a specific symbol map (inner, outer, hybrid)."""
    C: ColorObject = [204, 194, 193]
    W: ColorObject = [255, 251, 214]
    U: ColorObject = [170, 224, 250]
    B: ColorObject = [204, 194, 193]
    R: ColorObject = [249, 169, 143]
    G: ColorObject = [154, 211, 175]

    def __new__(cls, **data):
        d = super().__new__(cls, **data)
        d['2'] = d.pop('C', [0, 0, 0])
        return d


class ManaColorsInner(ManaColors):
    """Default mana colors."""
    C: ColorObject = [0, 0, 0]
    W: ColorObject = [0, 0, 0]
    U: ColorObject = [0, 0, 0]
    B: ColorObject = [0, 0, 0]
    R: ColorObject = [0, 0, 0]
    G: ColorObject = [0, 0, 0]


class SymbolColorMap(Schema):
    """Color map schema."""
    primary: ColorObject = [0, 0, 0]
    secondary: ColorObject = [255, 255, 255]
    colorless: ColorObject = [204, 194, 193]
    colors: dict[str, ColorObject] = ManaColors()
    hybrid: dict[str, ColorObject] = ManaColors(B=[159, 146, 143])
    colors_inner: dict[str, ColorObject] = ManaColorsInner()
    hybrid_inner: dict[str, ColorObject] = ManaColorsInner()


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

basic_watermark_color_map = {
    # Basic land watermark colors
    'W': [248, 249, 243],
    'U': [0, 115, 178],
    'B': [6, 0, 0],
    'R': [212, 39, 44],
    'G': [1, 131, 69],
    'Land': [165, 150, 132],
    'Snow': [255, 255, 255]
}

pinlines_color_map = {
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

rarity_gradient_map = {
    'c': [],
    'u': [
        {
            "color": [98, 110, 119],
            "location": 0,
            "midpoint": 50
        },
        {
            "color": [199, 225, 241],
            "location": 2048,
            "midpoint": 50
        },
        {
            "color": [98, 110, 119],
            "location": 4096,
            "midpoint": 50
        }
    ],
    'r': [
        {
            "color": [146, 116, 67],
            "location": 0,
            "midpoint": 50
        },
        {
            "color": [213, 180, 109],
            "location": 2048,
            "midpoint": 50
        },
        {
            "color": [146, 116, 67],
            "location": 4096,
            "midpoint": 50
        }
    ],
    'm': [
        {
            "color": [192, 55, 38],
            "location": 0,
            "midpoint": 50
        },
        {
            "color": [245, 149, 29],
            "location": 2048,
            "midpoint": 50
        },
        {
            "color": [192, 55, 38],
            "location": 4096,
            "midpoint": 50
        }
    ],
    't': [
        {
            "color": [98, 45, 118],
            "location": 0,
            "midpoint": 50
        },
        {
            "color": [191, 153, 195],
            "location": 2048,
            "midpoint": 50
        },
        {
            "color": [98, 45, 118],
            "location": 4096,
            "midpoint": 50
        }
    ]
}

"""
* Fonts & Characters
"""


class CardFonts(StrEnum):
    """Fonts used for card text."""
    RULES = "PlantinMTPro-Regular"
    RULES_BOLD = "PlantinMTPro-Bold"
    RULES_ITALIC = "PlantinMTPro-Italic"
    NICKNAME = "PlantinMTPro-SemiboldIt"
    TITLES = "BelerenProxy-Bold"
    PT = "BelerenProxy-Bold"
    TITLES_CLASSIC = "Magic:theGathering"
    MANA = "Proxyglyph"
    ARTIST = "BelerenSmallCaps-Bold"
    ARTIST_CLASSIC = "Matrix-Bold"
    COLLECTOR = "Gotham-Medium"
    SYMBOL = "Keyrune"


class MagicIcons:
    # Proxyglyph font
    PAINTBRUSH_MODERN = "a"
    PAINTBRUSH_CLASSIC = "ýþ"
    # Gotham-Medium font
    COLLECTOR_STAR = "¬"


"""
* Util Funcs
"""


def get_symbol_colors(symbol: str, chars: str, color_map: SymbolColorMap) -> list[ColorObject]:
    """Determines the colors of a symbol (represented as Scryfall string) and returns an array Symbol colors.

    Args:
        symbol: Symbol to determine the colors of.
        chars: Character representation of the symbol.
        color_map: Maps colors to symbol strings.

    Returns:
        List of SolidColor objects to color the symbol's characters.
    """

    # Special Symbols
    if symbol in ("{E}", "{CHAOS}"):
        # Energy or chaos symbols
        return [color_map.primary]
    elif symbol == "{S}":
        # Snow symbol
        return [color_map.colorless, color_map.primary, color_map.secondary]
    elif symbol == "{Q}":
        # Untap symbol
        return [color_map.primary, color_map.secondary]

    # Normal mana symbol
    if normal_symbol_match := Reg.MANA_NORMAL.match(symbol):
        return [
            color_map.colors[normal_symbol_match[1]],
            color_map.colors_inner[normal_symbol_match[1]]
        ]

    # Hybrid
    if hybrid_match := Reg.MANA_HYBRID.match(symbol):
        # Use the darker color for black's symbols for 2/B hybrid symbols
        colors = color_map.hybrid if hybrid_match[1] == "2" else color_map.colors
        return [
            colors[hybrid_match[2]],
            colors[hybrid_match[1]],
            color_map.colors_inner[hybrid_match[1]],
            color_map.colors_inner[hybrid_match[2]]
        ]

    # Phyrexian
    if phyrexian_match := Reg.MANA_PHYREXIAN.match(symbol):
        return [
            color_map.hybrid[phyrexian_match[1]],
            color_map.hybrid_inner[phyrexian_match[1]]
        ]

    # Phyrexian hybrid
    if phyrexian_hybrid_match := Reg.MANA_PHYREXIAN_HYBRID.match(symbol):
        return [
            color_map.colors[phyrexian_hybrid_match[2]],
            color_map.colors[phyrexian_hybrid_match[1]],
            color_map.colors_inner[phyrexian_hybrid_match[1]],
            color_map.colors_inner[phyrexian_hybrid_match[2]]
        ]

    # Weird situation?
    if len(chars) == 2:
        return [color_map.colorless, color_map.primary]

    # Nothing matching found!
    raise Exception(f"Encountered a symbol that I don't know how to color: {symbol}")
