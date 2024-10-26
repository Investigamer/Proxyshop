"""
* Enums: Layer Names
"""
# Third Party Imports
from omnitils.enums import StrConstant

"""
* Enums
"""


class LAYERS (StrConstant):
    """Layer name definitions."""

    # Default art layer
    DEFAULT = 'Layer 1'

    # Colors
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'
    WU = 'WU'
    UB = 'UB'
    BR = 'BR'
    RG = 'RG'
    GW = 'GW'
    WB = 'WB'
    BG = 'BG'
    GU = 'GU'
    UR = 'UR'
    RW = 'RW'
    GWU = 'GWU'
    WUB = 'WUB'
    UBR = 'UBR'
    BRG = 'BRG'
    RGW = 'RGW'
    WBG = 'WBG'
    URW = 'URW'
    BGU = 'BGU'
    RWB = 'RWB'
    GUR = 'GUR'
    WUBR = 'WUBR'
    UBRG = 'UBRG'
    BRGW = 'BRGW'
    RGWU = 'RGWU'
    GWUB = 'GWUB'
    WUBRG = 'WUBRG'
    ARTIFACT = 'Artifact'
    COLORLESS = 'Colorless'
    NONLAND = 'Nonland'
    LAND = 'Land'
    GOLD = 'Gold'
    VEHICLE = 'Vehicle'
    HYBRID = 'Hybrid'

    # Frame layer group names
    PT_BOX = 'PT Box'
    PT_AND_LEVEL_BOXES = 'PT and Level Boxes'
    TWINS = 'Name & Title Boxes'
    LEGENDARY_CROWN = 'Legendary Crown'
    PINLINES_TEXTBOX = 'Pinlines & Textbox'
    PINLINES = 'Pinlines'
    LAND_PINLINES_TEXTBOX = 'Land Pinlines & Textbox'
    COMPANION = 'Companion'
    BACKGROUND = 'Background'
    NYX = 'Nyx'
    FRAME = 'Frame'
    LEGENDARY = 'Legendary'
    NON_LEGENDARY = 'Non-Legendary'
    CREATURE = 'Creature'
    NON_CREATURE = 'Non-Creature'
    NONE = 'None'
    ONE_LINE = 'One Line'
    FULL = 'Full'
    NORMAL = 'Normal'
    SNOW = 'Snow'

    # Borders
    BORDER = 'Border'
    OUTLINE = 'Outline'
    NORMAL_BORDER = 'Normal Border'
    LEGENDARY_BORDER = 'Legendary Border'

    # Shadows
    SHADOWS = 'Shadows'
    HOLLOW_CROWN_SHADOW = 'Hollow Crown Shadow'

    # Vectors
    SHAPE = 'Shape'
    TEXTLESS = 'Textless'

    # Effects
    EFFECTS = 'Effects'
    LIGHTEN = 'Lighten'
    DARKEN = 'Darken'
    CONTRAST = 'Contrast'

    # Masks
    MASKS = 'Masks'
    HALF = '1/2'
    THIRD = '1/3'
    TWO_THIRDS = '2/3'
    QUARTER = '1/4'
    THREE_QUARTERS = '3/4'
    FIFTH = '1/5'
    TWO_FIFTHS = '2/5'
    THREE_FIFTHS = '3/5'
    FOUR_FIFTHS = '4/5'

    # Legal / Collector Info
    LEGAL = 'Legal'
    ARTIST = 'Artist'
    SET = 'Set'
    COLLECTOR = 'Collector'
    NFS = 'NFS'
    NFS_CREATURE = 'NFS - Creature'

    # Text and Icons
    TEXT_AND_ICONS = 'Text and Icons'
    NAME = 'Card Name'
    NAME_SHIFT = 'Card Name Shift'
    NICKNAME = 'Nickname'
    TYPE_LINE = 'Typeline'
    TYPE_LINE_SHIFT = 'Typeline Shift'
    MANA_COST = 'Mana Cost'
    EXPANSION_SYMBOL = 'Expansion Symbol'
    COLOR_INDICATOR = 'Color Indicator'
    POWER_TOUGHNESS = 'Power / Toughness'
    FLIPSIDE_POWER_TOUGHNESS = 'Flipside Power / Toughness'
    RULES_TEXT = 'Rules Text'
    RULES_TEXT_FLIP = 'Rules Text - Flip'
    RULES_TEXT_NONCREATURE = 'Rules Text - Noncreature'
    RULES_TEXT_NONCREATURE_FLIP = 'Rules Text - Noncreature Flip'
    RULES_TEXT_CREATURE = 'Rules Text - Creature'
    RULES_TEXT_CREATURE_FLIP = 'Rules Text - Creature Flip'
    MUTATE = 'Mutate'
    DIVIDER = 'Divider'
    CREATOR = 'Creator'

    # Prototype
    PROTO_TEXTBOX = 'Prototype Textbox'
    PROTO_MANABOX = 'Prototype Manabox'
    PROTO_PTBOX = 'Prototype PT Box'
    PROTO_MANA_COST = 'Prototype Mana Cost'
    PROTO_RULES = 'Prototype Rules Text'
    PROTO_PT = 'Prototype Power / Toughness'

    # Planar text and icons
    STATIC_ABILITY = 'Static Ability'
    CHAOS_ABILITY = 'Chaos Ability'
    CHAOS_SYMBOL = 'Chaos Symbol'
    PHENOMENON = 'Phenomenon'
    TEXTBOX = 'Textbox'

    # Text References
    TEXTBOX_REFERENCE = 'Textbox Reference'
    TEXTBOX_REFERENCE_LAND = 'Textbox Reference Land'
    MUTATE_REFERENCE = 'Mutate Reference'
    PT_REFERENCE = 'PT Reference'
    EXPANSION_REFERENCE = 'Expansion Reference'
    NAME_REFERENCE_NON_LEGENDARY = 'Name Reference Non-Legendary'
    NAME_REFERENCE_LEGENDARY = 'Name Reference Legendary'
    NAME_REFERENCE = 'Name Reference'
    TYPE_LINE_REFERENCE = 'Typeline Reference'
    COLLECTOR_REFERENCE = 'Collector Reference'

    # Saga
    SAGA = 'Saga'
    PINLINES_AND_SAGA_STRIPE = 'Pinlines & Saga Stripe'
    BANNER = 'Banner'
    STRIPE = 'Stripe'

    # Class
    CLASS = 'Class'
    STAGE = 'Stage'

    # Token
    TOKEN = 'Token'

    # Planeswalker
    PLANESWALKER = 'Planeswalker'
    FIRST_ABILITY = 'First Ability'
    SECOND_ABILITY = 'Second Ability'
    THIRD_ABILITY = 'Third Ability'
    FOURTH_ABILITY = 'Fourth Ability'
    STARTING_LOYALTY = 'Starting Loyalty'
    LOYALTY_GRAPHICS = 'Loyalty Graphics'
    LOYALTY_REFERENCE = 'Loyalty Reference'
    STATIC_TEXT = 'Static Text'
    ABILITY_TEXT = 'Ability Text'
    COLON = 'Colon'
    TEXT = 'Text'
    COST = 'Cost'

    # Art Frames
    ART_FRAME = 'Art Frame'
    FULL_ART_FRAME = 'Full Art Frame'
    BORDERLESS_FRAME = 'Borderless Frame'
    BASIC_ART_FRAME = 'Basic Art Frame'
    PLANESWALKER_ART_FRAME = 'Planeswalker Art Frame'
    SCRYFALL_SCAN_FRAME = 'Scryfall Scan Frame'

    # Double Faced
    MDFC = 'MDFC'
    TRANSFORM = 'Transform'
    TRANSFORM_FRONT = 'TF Front'
    TRANSFORM_BACK = 'TF Back'
    MDFC_FRONT = 'mdfc-front'
    MDFC_BACK = 'mdfc-back'
    MODAL_FRONT = 'MDFC Front'
    MODAL_BACK = 'MDFC Back'

    # Orientation
    TOP = 'Top'
    BOTTOM = 'Bottom'
    LEFT = 'Left'
    RIGHT = 'Right'
    BACK = 'Back'
    FRONT = 'Front'

    # Sizes
    TALL = 'Tall'
    MEDIUM = 'Medium'
    SHORT = 'Short'
    MINI = 'Mini'

    # Frame types
    BORDERLESS = 'Borderless'
    EXTENDED = 'Extended'
    CLASSIC = 'Classic'
    FULLART = 'Fullart'

    # Adventure
    ADVENTURE = 'Adventure'
    STORYBOOK = 'Storybook'
    ADVENTURE_NAME = 'Adventure Name'
    ADVENTURE_TYPELINE = 'Adventure Typeline'
    ADVENTURE_TYPELINE_ACCENT = 'Adventure Typeline Accent'
    NAME_ADVENTURE = 'Card Name - Adventure'
    TYPE_LINE_ADVENTURE = 'Typeline - Adventure'
    MANA_COST_ADVENTURE = 'Mana Cost - Adventure'
    RULES_TEXT_ADVENTURE = 'Rules Text - Adventure'
    TEXTBOX_REFERENCE_ADVENTURE = 'Textbox Reference - Adventure'
    DIVIDER_ADVENTURE = 'Divider - Adventure'
    WINGS = 'Wings'

    # Battles
    DEFENSE = 'Defense'
    DEFENSE_REFERENCE = 'Defense Reference'
