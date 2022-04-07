"""
GLOBAL CONSTANTS
Keep all global variables here.
"""
import os
from pathlib import Path
from proxyshop.helpers import ps
from proxyshop import settings
cfg = settings.config()
cwd = os.getcwd()
version = "v1.0.9"

# PATHS
json_custom_path = os.path.join(cwd, "tmp\\custom.json")
scryfall_scan_path = os.path.join(cwd, "tmp\\card.jpg")
Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(cwd, "tmp")).mkdir(mode=511, parents=True, exist_ok=True)

# Card classes - finer grained than Scryfall layouts
normal_class = "normal"
transform_front_class = "transform_front"
transform_back_class = "transform_back"
ixalan_class = "ixalan"
mdfc_front_class = "mdfc_front"
mdfc_back_class = "mdfc_back"
mutate_class = "mutate"
adventure_class = "adventure"
leveler_class = "leveler"
saga_class = "saga"
miracle_class = "miracle"
planeswalker_class = "planeswalker"
pw_tf_front_class = "pw_tf_front"
pw_tf_back_class = "pw_tf_back"
pw_mdfc_front_class = "pw_mdfc_front"
pw_mdfc_back_class = "pw_mdfc_back"
snow_class = "snow"
basic_class = "basic"
planar_class = "planar"

# LAYER NAMES
layers = {
    "WHITE": "W",
    "BLUE": "U",
    "BLACK": "B",
    "RED": "R",
    "GREEN": "G",
    "WU": "WU",
    "UB": "UB",
    "BR": "BR",
    "RG": "RG",
    "GW": "GW",
    "WB": "WB",
    "BG": "BG",
    "GU": "GU",
    "UR": "UR",
    "RW": "RW",
    "ARTIFACT": "Artifact",
    "COLORLESS": "Colorless",
    "NONLAND": "Nonland",
    "LAND": "Land",
    "GOLD": "Gold",
    "VEHICLE": "Vehicle",

    # frame layer group names
    "PT_BOX": "PT Box",
    "PT_AND_LEVEL_BOXES": "PT and Level Boxes",
    "TWINS": "Name & Title Boxes",
    "LEGENDARY_CROWN": "Legendary Crown",
    "PINLINES_TEXTBOX": "Pinlines & Textbox",
    "PINLINES_AND_SAGA_STRIPE": "Pinlines & Saga Stripe",
    "PINLINES": "Pinlines",
    "LAND_PINLINES_TEXTBOX": "Land Pinlines & Textbox",
    "COMPANION": "Companion",
    "BACKGROUND": "Background",
    "NYX": "Nyx",

    # borders
    "BORDER": "Border",
    "NORMAL_BORDER": "Normal Border",
    "LEGENDARY_BORDER": "Legendary Border",

    # shadows
    "SHADOWS": "Shadows",
    "HOLLOW_CROWN_SHADOW": "Hollow Crown Shadow",

    # legal
    "LEGAL": "Legal",
    "ARTIST": "Artist",
    "SET": "Set",
    "COLLECTOR": "Collector",
    "TOP_LINE": "Top",
    "BOTTOM_LINE": "Bottom",

    # text and icons
    "TEXT_AND_ICONS": "Text and Icons",
    "NAME": "Card Name",
    "NAME_SHIFT": "Card Name Shift",
    "NAME_ADVENTURE": "Card Name - Adventure",
    "TYPE_LINE": "Typeline",
    "TYPE_LINE_SHIFT": "Typeline Shift",
    "TYPE_LINE_ADVENTURE": "Typeline - Adventure",
    "MANA_COST": "Mana Cost",
    "MANA_COST_ADVENTURE": "Mana Cost - Adventure",
    "EXPANSION_SYMBOL": "Expansion Symbol",
    "EXPANSION_REFERENCE": "Expansion Reference",
    "COLOR_INDICATOR": "Color Indicator",
    "POWER_TOUGHNESS": "Power / Toughness",
    "FLIPSIDE_POWER_TOUGHNESS": "Flipside Power / Toughness",
    "RULES_TEXT": "Rules Text",
    "RULES_TEXT_NONCREATURE": "Rules Text - Noncreature",
    "RULES_TEXT_NONCREATURE_FLIP": "Rules Text - Noncreature Flip",
    "RULES_TEXT_CREATURE": "Rules Text - Creature",
    "RULES_TEXT_CREATURE_FLIP": "Rules Text - Creature Flip",
    "RULES_TEXT_ADVENTURE": "Rules Text - Adventure",
    "MUTATE": "Mutate",

    # planar text and icons
    "STATIC_ABILITY": "Static Ability",
    "CHAOS_ABILITY": "Chaos Ability",
    "CHAOS_SYMBOL": "Chaos Symbol",
    "PHENOMENON": "Phenomenon",
    "TEXTBOX": "Textbox",

    # textbox references
    "TEXTBOX_REFERENCE": "Textbox Reference",
    "TEXTBOX_REFERENCE_LAND": "Textbox Reference Land",
    "TEXTBOX_REFERENCE_ADVENTURE": "Textbox Reference - Adventure",
    "MUTATE_REFERENCE": "Mutate Reference",
    "PT_REFERENCE": "PT Adjustment Reference",
    "PT_TOP_REFERENCE": "PT Top Reference",

    # planeswalker
    "FIRST_ABILITY": "First Ability",
    "SECOND_ABILITY": "Second Ability",
    "THIRD_ABILITY": "Third Ability",
    "FOURTH_ABILITY": "Fourth Ability",
    "STARTING_LOYALTY": "Starting Loyalty",
    "LOYALTY_GRAPHICS": "Loyalty Graphics",
    "STATIC_TEXT": "Static Text",
    "ABILITY_TEXT": "Ability Text",
    "TEXT": "Text",
    "COST": "Cost",

    # art frames
    "ART_FRAME": "Art Frame",
    "FULL_ART_FRAME": "Full Art Frame",
    "BASIC_ART_FRAME": "Basic Art Frame",
    "PLANESWALKER_ART_FRAME": "Planeswalker Art Frame",
    "SCRYFALL_SCAN_FRAME": "Scryfall Scan Frame",

    # transform
    "TF_FRONT": "tf-front",
    "TF_BACK": "tf-back",
    "MDFC_FRONT": "mdfc-front",
    "MDFC_BACK": "mdfc-back",
    "MOON_ELDRAZI_DFC": "mooneldrazidfc",

    # mdfc
    "TOP": "Top",
    "BOTTOM": "Bottom",
    "LEFT": "Left",
    "RIGHT": "Right",
}

default_layer = "Layer 1"

basic_land_names = [
    "Plains",
    "Island",
    "Swamp",
    "Mountain",
    "Forest",
    "Wastes",
    "Snow-Covered Plains",
    "Snow-Covered Island",
    "Snow-Covered Swamp",
    "Snow-Covered Mountain",
    "Snow-Covered Forest"
]

# Card faces
Faces = {
    "FRONT": 0,
    "BACK": 1,
}

# Font names
font_name_mplantin = "MPlantin"
font_name_mplantin_italic = "MPlantin-Italic"
font_name_ndpmtg = "NDPMTG"
font_name_beleren_smallcaps = "Beleren Small Caps Bold"
font_name_relay_medium = "Relay-Medium"

# Font spacing
modal_indent = 5.7
line_break_lead = 2.4
flavor_text_lead = 4.4

# Symbol colors
rgb_c = ps.SolidColor()
rgb_c.rgb.red = 204
rgb_c.rgb.green = 194
rgb_c.rgb.blue = 193

rgb_w = ps.SolidColor()
rgb_w.rgb.red = 255
rgb_w.rgb.green = 251
rgb_w.rgb.blue = 214

rgb_u = ps.SolidColor()
rgb_u.rgb.red = 170
rgb_u.rgb.green = 224
rgb_u.rgb.blue = 250

rgb_b = ps.SolidColor()
rgb_b.rgb.red = 159
rgb_b.rgb.green = 146
rgb_b.rgb.blue = 143

rgb_r = ps.SolidColor()
rgb_r.rgb.red = 249
rgb_r.rgb.green = 169
rgb_r.rgb.blue = 143

rgb_g = ps.SolidColor()
rgb_g.rgb.red = 154
rgb_g.rgb.green = 211
rgb_g.rgb.blue = 175

# NDPMTG font dictionary to translate Scryfall symbols to font character sequences
symbols = {
    "{W/P}": "Qp",
    "{U/P}": "Qp",
    "{B/P}": "Qp",
    "{R/P}": "Qp",
    "{G/P}": "Qp",
    "{W/U/P}": "Qqp",
    "{U/B/P}": "Qqp",
    "{B/R/P}": "Qqp",
    "{R/G/P}": "Qqp",
    "{G/W/P}": "Qqp",
    "{W/B/P}": "Qqp",
    "{B/G/P}": "Qqp",
    "{G/U/P}": "Qqp",
    "{U/R/P}": "Qqp",
    "{R/W/P}": "Qqp",
    "{E}": "e",
    "{T}": "ot",
    "{X}": "ox",
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

# Ability words which should be italicised in formatted text
ability_words = [
    "Adamant",
    "Addendum",
    "Battalion",
    "Bloodrush",
    "Channel",
    "Chroma",
    "Cohort",
    "varellation",
    "Converge",
    "Council's dilemma",
    "Delirium",
    "Domain",
    "Eminence",
    "Enrage",
    "Fateful hour",
    "Ferocious",
    "Formidable",
    "Grandeur",
    "Hellbent",
    "Heroic",
    "Imprint",
    "Inspired",
    "Join forces",
    "Kinship",
    "Landfall",
    "Lieutenant",
    "Metalcraft",
    "Morbid",
    "Parley",
    "Radiance",
    "Raid",
    "Rally",
    "Revolt",
    "Spell mastery",
    "Strive",
    "Sweep",
    "Tempting offer",
    "Threshold",
    "Undergrowth",
    "Will of the council",
    "Magecraft",

    # AFR ability words
    "Antimagic Cone",
    "Fear Ray",
    "Pack tactics",
    "Acid Breath",
    "Teleport",
    "Lightning Breath",
    "Wild Magic Surge",
    "Two-Weapon Fighting",
    "Archery",
    "Bear Form",
    "Mage Hand",
    "Cure Wounds",
    "Dispel Magic",
    "Gentle Reprise",
    "Beacon of Hope",
    "Displacement",
    "Drag Below",
    "Siege Monster",
    "Dark One's Own Luck",
    "Climb Over",
    "Tie Up",
    "Rappel Down",
    "Rejuvenation",
    "Engulf",
    "Dissolve",
    "Poison Breath",
    "Tragic Backstory",
    "Cunning Action",
    "Stunning Strike",
    "Circle of Death",
    "Bardic Inspiration",
    "Song of Rest",
    "Sneak Attack",
    "Tail Spikes",
    "Dominate Monster",
    "Flurry of Blows",
    "Divine Intervention",
    "Split",
    "Magical Tinkering",
    "Keen Senses",
    "Grant an Advantage",
    "Smash the Chest",
    "Pry It Open",
    "Fire Breath",
    "Cone of Cold",
    "Brave the Stench",
    "Search the Body",
    "Bewitching Whispers",
    "Whispers of the Grave",
    "Animate Walking Statue",
    "Trapped!",
    "Invoke Duplicity",
    "Combat Inspiration",
    "Cold Breath",
    "Life Drain",
    "Fight the Current",
    "Find a Crossing",
    "Intimidate Them",
    "Fend Them Off",
    "Smash It",
    "Lift the Curse",
    "Steal Its Eyes",
    "Break Their Chains",
    "Interrogate Them",
    "Foil Their Scheme",
    "Learn Their Secrets",
    "Journey On",
    "Make Camp",
    "Rouse the Party",
    "Set Off Traps",
    "Form a Party",
    "Start a Brawl",
    "Make a Retreat",
    "Stand and Fight",
    "Distract the Guards",
    "Hide",
    "Charge Them",
    "Befriend Them",
    "Negative Energy Cone",

    # Midnight Hunt words
    "Coven",
]

# Card rarities
rarity_common = "common"
rarity_uncommon = "uncommon"
rarity_rare = "rare"
rarity_mythic = "mythic"
rarity_special = "special"
rarity_bonus = "bonus"

# SET SYMBOL LIBRARY
set_symbol_library = {
    "MTG": "", # Default for not found
    "LEA": "",
    "LEB": "",
    "2ED": "",
    "ARN": "",
    "ATQ": "",
    "3ED": "",
    "LEG": "",
    "DRK": "",
    "FEM": "",
    "4ED": "",
    "ICE": "",
    "CHR": "",
    "HML": "",
    "ALL": "",
    "MIR": "",
    "VIS": "",
    "5ED": "",
    "POR": "",
    "WTH": "",
    "TMP": "",
    "STH": "",
    "EXO": "",
    "P02": "",
    "UGL": "",
    "USG": "",
    "ATH": "",
    "ULG": "",
    "6ED": "",
    "PTK": "",
    "UDS": "",
    "S99": "",
    "MMQ": "",
    "BRB": "",
    "NEM": "",
    "S00": "",
    "PCY": "",
    "INV": "",
    "BTD": "",
    "PLS": "",
    "7ED": "",
    "APC": "",
    "ODY": "",
    "DKM": "",
    "TOR": "",
    "JUD": "",
    "ONS": "",
    "LGN": "",
    "SCG": "",
    "8ED": "",
    "MRD": "",
    "DST": "",
    "5DN": "",
    "CHK": "",
    "UNH": "",
    "BOK": "",
    "SOK": "",
    "9ED": "",
    "RAV": "",
    "GPT": "",
    "DIS": "",
    "CSP": "",
    "TSP": "",
    "PLC": "",
    "FUT": "",
    "10E": "",
    "LRW": "",
    "EVG": "",
    "MOR": "",
    "SHM": "",
    "EVE": "",
    "DRB": "",
    "ME2": "",
    "ALA": "",
    "DD2": "",
    "CON": "",
    "DDC": "",
    "ARB": "",
    "M10": "",
    "V09": "",
    "HOP": "",
    "ME3": "",
    "ZEN": "",
    "DDD": "",
    "H09": "",
    "WWK": "",
    "DDE": "",
    "ROE": "",
    "DPA": "",
    "ARC": "",
    "M11": "",
    "V10": "",
    "DDF": "",
    "SOM": "",
    #"TD0": "", MTGO
    "PD2": "",
    "ME4": "",
    "MBS": "",
    "DDG": "",
    "NPH": "",
    "CMD": "",
    "M12": "",
    "V11": "",
    "DDH": "",
    "ISD": "",
    "PD3": "",
    "DKA": "",
    "DDI": "",
    "AVR": "",
    "PC2": "",
    "M13": "",
    "V12": "",
    "DDJ": "",
    "RTR": "",
    "CM1": "",
    "TD2": "",
    "GTC": "",
    "DDK": "",
    "DGM": "",
    "MMA": "",
    "M14": "",
    "V13": "",
    "DDL": "",
    "THS": "",
    "C13": "",
    "BNG": "",
    "DDM": "",
    "JOU": "",
    "MD1": "",
    "CNS": "",
    "VMA": "",
    "M15": "",
    "V14": "",
    "DDN": "",
    "KTK": "",
    "C14": "",
    "FRF": "",
    "DDO": "",
    "DTK": "",
    "TPR": "",
    "MM2": "",
    "ORI": "",
    "V15": "",
    "DDP": "",
    "BFZ": "",
    "EXP": "",
    "C15": "",
    "PZ1": "",
    "OGW": "",
    "DDQ": "",
    "W16": "",
    "SOI": "",
    "EMA": "",
    "EMN": "",
    "V16": "",
    "CN2": "",
    "DDR": "",
    "KLD": "",
    "MPS": "",
    "PZ2": "",
    "C16": "",
    "PCA": "",
    "AER": "",
    "MM3": "",
    "DDS": "",
    "W17": "",
    "AKH": "",
    "MP2": "",
    "CMA": "",
    "E01": "",
    "HOU": "",
    "C17": "",
    "XLN": "",
    "DDT": "",
    "IMA": "",
    "E02": "",
    "V17": "",
    "UST": "",
    "RIX": "",
    "A25": "",
    "DDU": "",
    "DOM": "",
    "CM2": "",
    "BBD": "",
    "SS1": "",
    "GS1": "",
    "M19": "",
    "C18": "",
    "GRN": "",
    "GNT": "",
    "UMA": "",
    "MED": "",
    "RNA": "",
    "WAR": "",
    "MH1": "",
    "SS2": "",
    "M20": "",
    "C19": "",
    "ELD": "",
    "GN2": "",
    "THB": "",
    "UND": "",
    "IKO": "",
    "C20": "",
    "SS3": "",
    "M21": "",
    "JMP": "",
    "2XM": "",
    "AKR": "",
    "ZNR": "",
    "ZNE": "",
    "ZNC": "",
    "KLR": "",
    "CMR": "",
    "CMC": "",
    "CC1": "",
    "KHM": "",
    "KHC": "",
    "TSR": "",
    "STX": "",
    "STA": "",
    "C21": "",
    "MH2": "",
    "AFR": "",
    "AFC": "",
    "SLD": "",
    "J21": "",
    "MID": "",
    "MIC": "",
    "DCI": "", #Judge Promo
    "VOW": "",
    "VOC": "",
    "NEO": "",
    "NEC": "",
    "UNF": "",
    "Y22": "",
    "CC2": "",
    "HED": ""
}
