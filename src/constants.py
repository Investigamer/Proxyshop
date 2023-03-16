"""
GLOBAL CONSTANTS
Keep all global variables here.
"""
import os
from os import path as osp
import json
from dataclasses import dataclass
try:
    from src.__env__ import google
    from src.__env__ import cloudfront
except ModuleNotFoundError:
    google = ""
    cloudfront = ""


@dataclass
class Layers:
    """
    Layer Names
    """
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    WU = "WU"
    UB = "UB"
    BR = "BR"
    RG = "RG"
    GW = "GW"
    WB = "WB"
    BG = "BG"
    GU = "GU"
    UR = "UR"
    RW = "RW"
    ARTIFACT = "Artifact"
    COLORLESS = "Colorless"
    NONLAND = "Nonland"
    LAND = "Land"
    GOLD = "Gold"
    VEHICLE = "Vehicle"

    # frame layer group names
    PT_BOX = "PT Box"
    PT_AND_LEVEL_BOXES = "PT and Level Boxes"
    TWINS = "Name & Title Boxes"
    LEGENDARY_CROWN = "Legendary Crown"
    PINLINES_TEXTBOX = "Pinlines & Textbox"
    PINLINES_AND_SAGA_STRIPE = "Pinlines & Saga Stripe"
    PINLINES = "Pinlines"
    LAND_PINLINES_TEXTBOX = "Land Pinlines & Textbox"
    COMPANION = "Companion"
    BACKGROUND = "Background"
    NYX = "Nyx"

    # borders
    BORDER = "Border"
    NORMAL_BORDER = "Normal Border"
    LEGENDARY_BORDER = "Legendary Border"

    # shadows
    SHADOWS = "Shadows"
    HOLLOW_CROWN_SHADOW = "Hollow Crown Shadow"

    # legal
    LEGAL = "Legal"
    ARTIST = "Artist"
    SET = "Set"
    COLLECTOR = "Collector"
    TOP_LINE = "Top"
    BOTTOM_LINE = "Bottom"

    # text and icons
    TEXT_AND_ICONS = "Text and Icons"
    NAME = "Card Name"
    NAME_SHIFT = "Card Name Shift"
    NAME_ADVENTURE = "Card Name - Adventure"
    TYPE_LINE = "Typeline"
    TYPE_LINE_SHIFT = "Typeline Shift"
    TYPE_LINE_ADVENTURE = "Typeline - Adventure"
    MANA_COST = "Mana Cost"
    MANA_COST_ADVENTURE = "Mana Cost - Adventure"
    EXPANSION_SYMBOL = "Expansion Symbol"
    EXPANSION_REFERENCE = "Expansion Reference"
    COLOR_INDICATOR = "Color Indicator"
    POWER_TOUGHNESS = "Power / Toughness"
    FLIPSIDE_POWER_TOUGHNESS = "Flipside Power / Toughness"
    RULES_TEXT = "Rules Text"
    RULES_TEXT_NONCREATURE = "Rules Text - Noncreature"
    RULES_TEXT_NONCREATURE_FLIP = "Rules Text - Noncreature Flip"
    RULES_TEXT_CREATURE = "Rules Text - Creature"
    RULES_TEXT_CREATURE_FLIP = "Rules Text - Creature Flip"
    RULES_TEXT_ADVENTURE = "Rules Text - Adventure"
    MUTATE = "Mutate"
    DIVIDER = "Divider"

    # prototype
    PROTO_TEXTBOX = "Prototype Textbox"
    PROTO_MANABOX_SMALL = "Prototype Manabox 2"
    PROTO_MANABOX_MEDIUM = "Prototype Manabox 3"
    PROTO_PTBOX = "Prototype PT Box"
    PROTO_MANA_COST = "Prototype Mana Cost"
    PROTO_RULES = "Prototype Rules Text"
    PROTO_PT = "Prototype Power / Toughness"

    # planar text and icons
    STATIC_ABILITY = "Static Ability"
    CHAOS_ABILITY = "Chaos Ability"
    CHAOS_SYMBOL = "Chaos Symbol"
    PHENOMENON = "Phenomenon"
    TEXTBOX = "Textbox"

    # textbox references
    TEXTBOX_REFERENCE = "Textbox Reference"
    TEXTBOX_REFERENCE_LAND = "Textbox Reference Land"
    TEXTBOX_REFERENCE_ADVENTURE = "Textbox Reference - Adventure"
    MUTATE_REFERENCE = "Mutate Reference"
    PT_REFERENCE = "PT Adjustment Reference"
    PT_TOP_REFERENCE = "PT Top Reference"

    # planeswalker
    FIRST_ABILITY = "First Ability"
    SECOND_ABILITY = "Second Ability"
    THIRD_ABILITY = "Third Ability"
    FOURTH_ABILITY = "Fourth Ability"
    STARTING_LOYALTY = "Starting Loyalty"
    LOYALTY_GRAPHICS = "Loyalty Graphics"
    STATIC_TEXT = "Static Text"
    ABILITY_TEXT = "Ability Text"
    PW_ADJUSTMENT_REFERENCE = "PW Adjustment Reference"
    PW_TOP_REFERENCE = "PW Top Reference"
    COLON = "Colon"
    TEXT = "Text"
    COST = "Cost"

    # art frames
    ART_FRAME = "Art Frame"
    FULL_ART_FRAME = "Full Art Frame"
    BASIC_ART_FRAME = "Basic Art Frame"
    PLANESWALKER_ART_FRAME = "Planeswalker Art Frame"
    SCRYFALL_SCAN_FRAME = "Scryfall Scan Frame"

    # transform
    TF_FRONT = "tf-front"
    TF_BACK = "tf-back"
    MDFC_FRONT = "mdfc-front"
    MDFC_BACK = "mdfc-back"
    MOON_ELDRAZI_DFC = "mooneldrazidfc"

    # mdfc
    TOP = "Top"
    BOTTOM = "Bottom"
    LEFT = "Left"
    RIGHT = "Right"


# For object permanence
class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Global app-wide constants class
class Constants:
    __metaclass__ = Singleton

    def __init__(self):
        self.load_values()

    def load_values(self):

        # Key file paths
        self.cwd = os.getcwd()
        self.path_src = osp.join(self.cwd, 'src')
        self.path_logs = osp.join(self.cwd, 'logs')
        self.path_plugins = osp.join(self.cwd, 'plugins')
        self.path_img = osp.join(self.path_src, 'img')
        self.path_data = osp.join(self.path_src, 'data')
        self.path_tests = osp.join(self.path_src, 'tests')
        self.path_data_sets = osp.join(self.path_data, 'sets')
        self.path_scryfall_scan = osp.join(self.path_logs, "card.jpg")
        self.path_version_tracker = osp.join(self.path_data, 'version_tracker.json')
        self.path_config_json = osp.join(self.path_data, 'app_settings.json')

        # Import version tracker
        if not osp.exists(self.path_version_tracker):
            with open(self.path_version_tracker, "w", encoding="utf-8") as tr:
                json.dump({}, tr, indent=4)
        with open(self.path_version_tracker, "r", encoding="utf-8") as tr:
            try:
                self.versions = json.load(tr)
            except json.decoder.JSONDecodeError:
                self.versions = {}

        # Import API Keys
        self.google_api = google
        self.cloudfront_url = cloudfront

        # Card classes - finer grained than Scryfall layouts
        self.normal_class = "normal"
        self.transform_front_class = "transform_front"
        self.transform_back_class = "transform_back"
        self.ixalan_class = "ixalan"
        self.mdfc_front_class = "mdfc_front"
        self.mdfc_back_class = "mdfc_back"
        self.mutate_class = "mutate"
        self.adventure_class = "adventure"
        self.leveler_class = "leveler"
        self.saga_class = "saga"
        self.class_class = "class"
        self.miracle_class = "miracle"
        self.planeswalker_class = "planeswalker"
        self.pw_tf_front_class = "pw_tf_front"
        self.pw_tf_back_class = "pw_tf_back"
        self.pw_mdfc_front_class = "pw_mdfc_front"
        self.pw_mdfc_back_class = "pw_mdfc_back"
        self.snow_class = "snow"
        self.basic_class = "basic"
        self.planar_class = "planar"
        self.prototype_class = "prototype"

        # Layer names
        self.layers = Layers()
        self.default_layer = "Layer 1"

        # Symbol dictionary for NDPMTG font
        self.symbols = {
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

        # Basic land dictionary
        self.basic_land_names = [
            "plains",
            "island",
            "swamp",
            "mountain",
            "forest",
            "wastes",
            "snowcoveredplains",
            "snowcoveredisland",
            "snowcoveredswamp",
            "snowcoveredmountain",
            "snowcoveredforest"
        ]

        # Color reference dictionary
        self.colors = {
            'black': [0, 0, 0],
            'white': [255, 255, 255],
            'silver': [167, 177, 186],
            'gold': [166, 135, 75]
        }

        # Rarity gradient dictionary
        self.rarity_gradients = {
            'c': None,
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
            ]
        }

        # Watermark colors
        self.watermark_colors = {
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

        # Import watermark library
        with open(osp.join(self.path_data, 'watermarks.json'), "r", encoding="utf-8-sig") as js:
            self.watermarks = json.load(js)

        # Import set symbol library
        with open(osp.join(self.path_data, "symbols.json"), "r", encoding="utf-8-sig") as js:
            self.set_symbols = json.load(js)
        if not osp.exists(osp.join(self.path_data, "custom_symbols.json")):
            with open(osp.join(self.path_data, "custom_symbols.json"), "w", encoding="utf-8") as cs:
                json.dump({}, cs, indent=4)
        with open(osp.join(self.path_data, "custom_symbols.json"), "r", encoding="utf-8-sig") as js:
            self.set_symbols.update(json.load(js))

        # Font names
        self.font_rules_text = "PlantinMTPro-Regular"
        self.font_rules_text_bold = "PlantinMTPro-Bold"
        self.font_rules_text_italic = "PlantinMTPro-Italic"
        self.font_mana = "NDPMTG"
        self.font_subtext = "Beleren Small Caps Bold"
        self.font_collector = "Relay-Medium"

        # Text Layer formatting
        self.modal_indent = 5.7
        self.line_break_lead = 2.4
        self.flavor_text_lead = 4.4
        self.flavor_text_lead_divider = 7

        # Card rarities
        self.rarity_common = "common"
        self.rarity_uncommon = "uncommon"
        self.rarity_rare = "rare"
        self.rarity_mythic = "mythic"
        self.rarity_special = "special"
        self.rarity_bonus = "bonus"

        # Symbol colors
        self.clr_primary = {'r': 0, 'g': 0, 'b': 0}
        self.clr_secondary = {'r': 255, 'g': 255, 'b': 255}
        self.clr_c = {'r': 204, 'g': 194, 'b': 193}
        self.clr_w = {'r': 255, 'g': 251, 'b': 214}
        self.clr_u = {'r': 170, 'g': 224, 'b': 250}
        self.clr_b = {'r': 204, 'g': 194, 'b': 193}
        self.clr_bh = {'r': 159, 'g': 146, 'b': 143}
        self.clr_r = {'r': 249, 'g': 169, 'b': 143}
        self.clr_g = {'r': 154, 'g': 211, 'b': 175}

        # Inner Symbol colors
        self.clri_c = self.clr_primary.copy()
        self.clri_w = self.clr_primary.copy()
        self.clri_u = self.clr_primary.copy()
        self.clri_b = self.clr_primary.copy()
        self.clri_bh = self.clr_primary.copy()
        self.clri_r = self.clr_primary.copy()
        self.clri_g = self.clr_primary.copy()

        # HTTP Header for requests
        self.http_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/39.0.2171.95 Safari/537.36"
        }

        # Run headless
        self.headless = False

        # Version compatibility features
        self.version_webp = '23.2.0'
        self.version_targeted_replace = '22.0.0'

        # Console message colors
        self.console_message_error = "#a84747"
        self.console_message_warning = "#d4c53d"
        self.console_message_success = "#59d461"

    def reload(self):
        """
        Reloads default values
        """
        self.load_values()

    def update_version_tracker(self):
        """
        Updates the version tracker json with current dict.
        """
        with open(self.path_version_tracker, "w", encoding="utf-8") as vt:
            json.dump(self.versions, vt, indent=4)


# Global instance
con = Constants()
