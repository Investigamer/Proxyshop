"""
GLOBAL CONSTANTS MODULE
"""
# Standard Library Imports
import os
from os import path as osp
import json
from threading import Lock

# Local Imports
from src.env import ENV_API_GOOGLE, ENV_API_AMAZON
from src.enums.layers import LAYERS
from src.utils.exceptions import PS_EXCEPTIONS
from src.utils.objects import Singleton, PhotoshopHandler


# Global app-wide constants class
class Constants:
    """
    Stores global constants that affect the behavior of the app.
    Can be changed within a template class to affect rendering behavior.
    """
    __metaclass__ = Singleton

    def __init__(self):
        # Initialize the values
        self.app = None
        self.refresh_photoshop()
        self.load_values()

    def load_values(self):
        """
        Loads default values across the board.
        Called between renders to remove any changes made by templates.
        """
        # Consistent paths used by the app
        self.cwd = os.getcwd()
        self.path_src = osp.join(self.cwd, 'src')
        self.path_logs = osp.join(self.cwd, 'logs')
        self.path_fonts = osp.join(self.cwd, 'fonts')
        self.path_img = osp.join(self.path_src, 'img')
        self.path_data = osp.join(self.path_src, 'data')
        self.path_plugins = osp.join(self.cwd, 'plugins')
        self.path_tests = osp.join(self.path_src, 'tests')
        self.path_configs = osp.join(self.path_src, 'configs')
        self.path_data_sets = osp.join(self.path_data, 'sets')
        self.path_config_json_base = osp.join(self.path_data, 'base_settings.json')
        self.path_config_json_app = osp.join(self.path_data, 'app_settings.json')
        self.path_config_ini_base = os.path.join(self.path_configs, "base_config.ini")
        self.path_config_ini_app = os.path.join(self.cwd, "config.ini")

        # Key files used by the app
        self.path_scryfall_scan = osp.join(self.path_logs, "card.jpg")
        self.path_watermarks = osp.join(self.path_data, 'watermarks.json')
        self.path_version_tracker = osp.join(self.path_data, 'version_tracker.json')
        self.path_expansion_symbols = osp.join(self.path_data, 'expansion_symbols.json')
        self.path_custom_symbols = osp.join(self.path_data, "custom_symbols.json")

        # Locking handlers for multithreading
        self.lock_file_open = Lock()
        self.lock_func_cached = Lock()

        # Import version tracker
        self.versions = self.get_version_tracker()

        # Import API Keys
        self.google_api = ENV_API_GOOGLE
        self.cloudfront_url = ENV_API_AMAZON

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
        self.token_class = "token"

        # Symbol dictionary for NDPMTG font
        self.symbols = {
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
            "{A}": "oj",
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

        # Layer names and transform icons
        self.layers = LAYERS
        self.transform_icons = [
            LAYERS.DFC_COMPASSLAND,
            LAYERS.DFC_MOONELDRAZI,
            LAYERS.DFC_ORIGINPW,
            LAYERS.DFC_CONVERT,
            LAYERS.DFC_SUNMOON,
            LAYERS.DFC_FAN
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

        # Masks
        self.masks = {
            2: [LAYERS.HALF],
            3: [LAYERS.THIRD, LAYERS.TWO_THIRDS],
            4: [LAYERS.QUARTER, LAYERS.HALF, LAYERS.THREE_QUARTERS]
        }

        # Pinline colors
        self.pinline_colors = {
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

        # Mana colors
        self.mana_colors = {
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

        # Import watermark library
        self.watermarks = self.get_watermarks()

        # Import symbol library, update with custom symbols, establish fallback
        self.set_symbols = self.get_expansion_symbols()
        self.set_symbols.update(self.get_custom_symbols())
        self.set_symbol_fallback = ""

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

        # HTTP Header for requests
        self.http_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/39.0.2171.95 Safari/537.36"
        }

        # Run headless
        self.headless = False

        # Track timed checks
        self.times = []

    """
    UTILITY
    """

    def reload(self):
        """
        Reloads default values
        """
        self.load_values()

    def refresh_photoshop(self):
        """
        Attempts to refresh the Photoshop object.
        """
        try:
            if isinstance(self.app, PhotoshopHandler):
                self.app.refresh_app()
                return
            self.app = PhotoshopHandler()
        except PS_EXCEPTIONS as e:
            self.app = None
            if 'busy' in str(e).lower():
                return OSError("Photoshop appears to be busy currently!\n"
                               "Ensure no dialog windows are open in Photoshop and there are no actions "
                               "currently being performed such as using the text tool.")
            return OSError("Make sure Photoshop is installed properly!\n"
                           "If it is installed, check the FAQ for troubleshooting steps.")

    """
    VERSION TRACKER
    """

    def get_version_tracker(self) -> dict:
        """
        Get the current version tracker dict.
        """
        # Write a blank version tracker if not found
        if not osp.isfile(self.path_version_tracker):
            with open(self.path_version_tracker, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

        # Pull the version tracker
        with open(self.path_version_tracker, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                # Data is invalid
                return {}

    def update_version_tracker(self):
        """
        Updates the version tracker json with current dict.
        """
        with open(self.path_version_tracker, "w", encoding="utf-8") as vt:
            json.dump(self.versions, vt, indent=4)

    """
    EXPANSION SYMBOLS
    """

    def get_expansion_symbols(self) -> dict:
        """
        Import the expansion symbol library.
        @return: Dict containing expansion symbol entries.
        """
        # Import expansion symbol library
        with open(self.path_expansion_symbols, "r", encoding="utf-8-sig") as f:
            return json.load(f)

    def get_custom_symbols(self) -> dict:
        """
        Import any custom defined expansion symbols.
        @return: Dict containing custom symbol entries.
        """
        # Check for a custom expansion symbol library
        if not osp.exists(self.path_custom_symbols):
            with open(osp.join(self.path_data, "custom_symbols.json"), "w", encoding="utf-8-sig") as f:
                json.dump({}, f, indent=4)

        # Pull the custom expansion symbol library
        with open(self.path_custom_symbols, "r", encoding="utf-8-sig") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Data is invalid
                return {}

    """
    WATERMARKS
    """

    def get_watermarks(self) -> dict:
        """
        Import the watermark library.
        @return: Dict containing watermark entries.
        """
        # Import expansion symbol library
        with open(self.path_watermarks, "r", encoding="utf-8") as f:
            return json.load(f)


# Global instance tracking our constants
con = Constants()
