"""
* Enums: MTG Related Data
"""
# Standard Library Imports
import re
from dataclasses import dataclass

# Third Party Imports
from omnitils.enums import StrConstant

"""
* Card Layouts
"""


class LayoutCategory(StrConstant):
    """Card layout category, broad naming used for displaying on GUI elements."""
    Adventure = 'Adventure'
    Battle = 'Battle'
    Class = 'Class'
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


class LayoutType(StrConstant):
    """Card layout type, fine-grained naming separated by front/back where applicable."""
    Adventure = 'adventure'
    Battle = 'battle'
    Class = 'class'
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


class LayoutScryfall(StrConstant):
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

    # Definitions added to Scryfall built-ins
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

"""Maps Layout types to a display formatted Layout category (with Back or Front)."""
layout_map_types_display = {
    raw: (
        f'{named} Front' if 'front' in raw else (
            f'{named} Back' if 'back' in raw else named)
    ) for raw, named in layout_map_types.items()
}

"""Maps multimodal display formatted layout types to a singular layout type."""
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
        LayoutType.TransformBack
    ],
    LayoutCategory.MDFC: [
        LayoutType.MDFCFront,
        LayoutType.MDFCBack
    ],
    LayoutCategory.PlaneswalkerTransform: [
        LayoutType.PlaneswalkerTransformFront,
        LayoutType.PlaneswalkerTransformBack
    ],
    LayoutCategory.PlaneswalkerMDFC: [
        LayoutType.PlaneswalkerMDFCFront,
        LayoutType.PlaneswalkerMDFCBack
    ],
}


"""
* Card Types
"""


class CardTypes(StrConstant):
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


class CardTypesSuper(StrConstant):
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


class Rarity(StrConstant):
    """Card rarities."""
    C = "common"
    U = "uncommon"
    R = "rare"
    M = "mythic"
    S = "special"
    B = "bonus"
    T = "timeshifted"


class TransformIcons(StrConstant):
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
    "Boast",                   # Kaldheim
    "Forecast",                # Dissension
    "Gotcha",                  # Unhinged
    "Visit",                   # Unfinity
    "Whack", "Doodle", "Buzz"  # Unstable
]

# Edge case Planeswalkers with tall ability box
planeswalkers_tall = [
    "Gideon Blackblade",
    "Comet, Stellar Pup"
]

"""
* Fonts & Characters
"""


class CardFonts(StrConstant):
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


class MagicIcons(StrConstant):
    # Proxyglyph font
    PAINTBRUSH_MODERN = "a"
    PAINTBRUSH_CLASSIC = "ýþ"
    # Gotham-Medium font
    COLLECTOR_STAR = "¬"


"""
* Regex Patterns
"""


@dataclass
class CardTextPatterns:
    """Defined card data regex patterns."""

    # Rules Text - Special Card Types
    LEVELER: re.Pattern = re.compile(r"(?s)(.*?)\nLEVEL (\d*-\d*)\n(\d*/\d*)\n(.*?)(?:\n|)LEVEL (\d*\+)\n(\d*/\d*)\n(.*?)$", re.DOTALL)
    PROTOTYPE: re.Pattern = re.compile(r"Prototype (.+) [—\-] ([0-9]{0,2}/[0-9]{0,2}) \((.+)\)")
    PLANESWALKER: re.Pattern = re.compile(r"(^[^:]*$|^.*:.*$)", re.MULTILINE)
    CLASS: re.Pattern = re.compile(r"(.+?): Level (\d)\n(.+)")

    # Filename - Card Art
    PATH_ARTIST: re.Pattern = re.compile(r"\(+(.*?)\)")
    PATH_SPLIT: re.Pattern = re.compile(r"[\[({$]")
    PATH_SET: re.Pattern = re.compile(r"\[(.*)]")
    PATH_NUM: re.Pattern = re.compile(r"\{(.*)}")
    PATH_CONDITION: re.Pattern = re.compile(r'<([^>]*)>')

    # Mana - Symbols
    SYMBOL: re.Pattern = re.compile(r"(\{.*?})")
    MANA_NORMAL: re.Pattern = re.compile(r"{([WUBRG])}")
    MANA_PHYREXIAN: re.Pattern = re.compile(r"{([WUBRG])/P}")
    MANA_HYBRID: re.Pattern = re.compile(r"{([2WUBRG])/([WUBRG])}")
    MANA_PHYREXIAN_HYBRID: re.Pattern = re.compile(r"{([WUBRG])/([WUBRG])/P}")

    # Text - Extra Spaces
    EXTRA_SPACE: re.Pattern = re.compile(r"  +")

    # Text - Reminder
    TEXT_REMINDER: re.Pattern = re.compile(r"\([^()]*\)")

    # Text - Italicised Ability
    TEXT_ABILITY: re.Pattern = re.compile(r"(?:^|\r)+(?:• )*([^\r]+) — ", re.MULTILINE)
