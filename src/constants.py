"""
GLOBAL CONSTANTS MODULE
"""
# Standard Library Imports
import os
import sys
import json
from os import path as osp
from pathlib import Path
from threading import Lock
from typing import Optional

# Third Party Imports
import yaml

# Establish global root, based on Python or frozen EXE environment
__PATH_CWD__ = os.getcwd()
__PATH_ROOT__ = None
if getattr(sys, 'frozen', False):
    __PATH_ROOT__ = os.path.dirname(sys.executable)
elif __file__:
    __PATH_ROOT__ = os.path.dirname(Path(__file__).parent)
__PATH_ROOT__ = __PATH_ROOT__ or __PATH_CWD__

# Switch to root directory if current directory differs
if __PATH_CWD__ != __PATH_ROOT__:
    os.chdir(__PATH_ROOT__)

# Local Imports
from src.utils.objects import Singleton, PhotoshopHandler
from src.enums.mtg import mana_color_map
from src.enums.layers import LAYERS
from src.utils.env import ENV


# Global app-wide constants class
class Constants:
    """
    Stores global constants that control app behavior.
    Can be modified within a template class to adjust rendering behavior.
    """
    __metaclass__ = Singleton
    app = PhotoshopHandler(version=ENV.PS_VERSION)

    '''Named card layouts mapped to raw layouts.'''
    card_type_map = {
        "Normal": ["normal"],
        "MDFC": ["mdfc_front", "mdfc_back"],
        "Transform": ["transform_front", "transform_back"],
        "Planeswalker": ["planeswalker"],
        "PW MDFC": ["pw_mdfc_front", "pw_mdfc_back"],
        "PW TF": ["pw_tf_front", "pw_tf_back"],
        "Basic": ["basic"],
        "Ixalan": ["ixalan"],
        "Mutate": ["mutate"],
        "Prototype": ["prototype"],
        "Adventure": ["adventure"],
        "Leveler": ["leveler"],
        "Saga": ["saga"],
        "Split": ["split"],
        "Class": ["class"],
        "Battle": ["battle"],
        "Token": ["token"],
        "Miracle": ["miracle"],
        "Snow": ["snow"],
        "Planar": ["planar"]
    }

    '''Raw card layouts mapped to named layouts.'''
    card_type_map_raw = {
        raw: named for named, raw in sum([
            [(k, n) for n in names] for k, names in card_type_map.items()
        ], [])}

    def __init__(self):
        # Initialize the values
        self.refresh_photoshop()
        self.load_values()

    def load_values(self):
        """Loads default values. Called at launch and between renders to remove any changes made by templates."""

        # Consistent paths used by the app
        self.cwd = __PATH_ROOT__
        self.path_src = osp.join(self.cwd, 'src')
        self.path_logs = osp.join(self.cwd, 'logs')
        self.path_fonts = osp.join(self.cwd, 'fonts')
        self.path_img = osp.join(self.path_src, 'img')
        self.path_data = osp.join(self.path_src, 'data')
        self.path_kv = osp.join(self.path_data, 'kv')
        self.path_plugins = osp.join(self.cwd, 'plugins')
        self.path_tests = osp.join(self.path_data, 'tests')
        self.path_configs = osp.join(self.path_src, 'configs')
        self.path_templates = osp.join(self.cwd, 'templates')
        self.path_data_sets = osp.join(self.path_data, 'sets')
        self.path_config_json_base = osp.join(self.path_data, 'base_settings.json')
        self.path_config_json_app = osp.join(self.path_data, 'app_settings.json')
        self.path_config_ini_base = os.path.join(self.path_configs, "base_config.ini")
        self.path_config_ini_app = os.path.join(self.cwd, "config.ini")

        # Key files used by the app
        self.path_scryfall_scan = osp.join(self.path_logs, "card.jpg")
        self.path_watermarks = osp.join(self.path_data, 'watermarks.json')
        self.path_version_tracker = osp.join(self.path_data, 'version_tracker.json')
        self.path_expansion_symbols = osp.join(self.path_data, 'symbols.yaml')
        self.path_custom_symbols = osp.join(self.path_data, "custom_symbols.yaml")

        # Locking handlers for multithreading
        self.lock_file_open = Lock()
        self.lock_func_cached = Lock()
        self.lock_decompress = Lock()

        # Import version tracker
        self.versions = self.get_version_tracker()

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
        self.split_class = "split"
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
        self.battle_class = "battle"

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

        # Layer names
        self.layers = LAYERS

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

        # Masks
        self.masks = {
            2: [LAYERS.HALF],
            3: [LAYERS.THIRD, LAYERS.TWO_THIRDS],
            4: [LAYERS.QUARTER, LAYERS.HALF, LAYERS.THREE_QUARTERS]
        }

        # Gradients
        self.gradient_locations = {
            2: [.40, .60],
            3: [.26, .36, .64, .74],
            4: [.20, .30, .45, .55, .70, .80],
            5: [.20, .25, .35, .45, .55, .65, .75, .80]
        }

        # Mana colors
        self.mana_colors = mana_color_map.copy()

        # Import watermark library
        self.watermarks = self.get_watermarks()

        # Import symbol library, update with custom symbols, establish fallback
        self.set_symbols = self.get_expansion_symbols()
        self.set_symbols.update(self.get_custom_symbols())
        self.set_symbol_fallback = ""

        # Font names
        self.font_mana = "Proxyglyph"
        self.font_rules_text = "PlantinMTPro-Regular"
        self.font_rules_text_bold = "PlantinMTPro-Bold"
        self.font_rules_text_italic = "PlantinMTPro-Italic"
        self.font_subtext = "BelerenSmallCaps-Bold"
        self.font_collector = "Gotham-Medium"

        # Text Layer formatting
        self.modal_indent = 5.7
        self.line_break_lead = 2.4
        self.flavor_text_lead = 4.4
        self.flavor_text_lead_divider = 7

        # HTTP Header for requests
        self.http_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/39.0.2171.95 Safari/537.36"
        }

    """
    UTILITY
    """

    def reload(self):
        """Reloads default attribute values."""
        self.load_values()

    def refresh_photoshop(self) -> Optional[Exception]:
        """Attempts to refresh the Photoshop object."""
        return self.app.refresh_app()

    """
    VERSION TRACKER
    """

    def get_version_tracker(self) -> dict:
        """Get the current version tracker dict."""
        if not osp.isfile(self.path_version_tracker):
            # Write a blank version tracker if not found
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
        """Updates the version tracker json with current dict."""
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
            return yaml.load(f, yaml.Loader)

    def get_custom_symbols(self) -> dict:
        """
        Import any custom defined expansion symbols.
        @return: Dict containing custom symbol entries.
        """
        # Check for a custom expansion symbol library
        if not osp.exists(self.path_custom_symbols):
            with open(self.path_custom_symbols, "w", encoding="utf-8-sig") as f:
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
