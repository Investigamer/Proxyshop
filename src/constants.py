"""
GLOBAL CONSTANTS MODULE
"""
# Standard Library Imports
import os
import sys
from pathlib import Path
from threading import Lock
from typing import Optional

# Establish global root, based on frozen executable or Python
__PATH_CWD__: Path = Path(os.getcwd())
__PATH_ROOT__: Optional[Path] = Path(os.path.dirname(sys.executable)) if (
    getattr(sys, 'frozen', False)
) else (Path(os.path.dirname(Path(__file__).parent)) if __file__ else __PATH_CWD__)

# Switch to root directory if current directory differs
if str(__PATH_CWD__) != str(__PATH_ROOT__):
    os.chdir(__PATH_ROOT__)

# Local Imports
from src.utils.decorators import suppress_and_return
from src.utils.files import dump_data_file, load_data_file
from src.utils.objects import Singleton, PhotoshopHandler
from src.enums.mtg import mana_color_map, mana_symbol_map, rarity_gradient_map, main_color_map, CardFonts
from src.enums.layers import LAYERS
from src.utils.env import ENV


class Constants:
    """Stores global constants that control app behavior."""
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
        "Ixalan": ["ixalan"],
        "Mutate": ["mutate"],
        "Prototype": ["prototype"],
        "Adventure": ["adventure"],
        "Leveler": ["leveler"],
        "Split": ["split"],
        "Class": ["class"],
        "Saga": ["saga"],
        "Battle": ["battle"],
        "Token": ["token"],
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

        # Main app paths
        self.cwd = __PATH_ROOT__
        self.path_src = Path(self.cwd, 'src')
        self.path_out = Path(self.cwd, 'out')
        self.path_art = Path(self.cwd, 'art')
        self.path_logs = Path(self.cwd, 'logs')
        self.path_fonts = Path(self.cwd, 'fonts')
        self.path_plugins = Path(self.cwd, 'plugins')
        self.path_templates = Path(self.cwd, 'templates')

        # Source paths
        self.path_img = Path(self.path_src, 'img')
        self.path_data = Path(self.path_src, 'data')

        # Data paths
        self.path_kv = Path(self.path_data, 'kv')
        self.path_tests = Path(self.path_data, 'tests')
        self.path_data_sets = Path(self.path_data, 'mtg/sets')
        self.path_data_cards = Path(self.path_data, 'mtg/cards')

        # Config paths
        self.path_config = Path(self.path_data, 'config')
        self.path_config_ini = Path(self.path_data, 'config_ini')
        self.path_config_app = Path(self.path_config, 'app.toml')
        self.path_config_base = Path(self.path_config, 'base.toml')
        self.path_config_ini_app = Path(self.path_config_ini, "app.ini")
        self.path_config_ini_base = Path(self.path_config_ini, "base.ini")

        # Key files used by the app
        self.path_scryfall_scan = Path(self.path_logs, "card.jpg")
        self.path_watermarks = Path(self.path_data, 'watermarks.yml')
        self.path_version_tracker = Path(self.path_data, 'version_tracker.json')
        self.path_expansion_symbols = Path(self.path_data, 'symbols.yml')
        self.path_custom_symbols = Path(self.path_data, "symbols.user.yml")

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
        self.split_class = "split"
        self.planeswalker_class = "planeswalker"
        self.pw_tf_front_class = "pw_tf_front"
        self.pw_tf_back_class = "pw_tf_back"
        self.pw_mdfc_front_class = "pw_mdfc_front"
        self.pw_mdfc_back_class = "pw_mdfc_back"
        self.planar_class = "planar"
        self.prototype_class = "prototype"
        self.token_class = "token"
        self.battle_class = "battle"

        # Symbol dictionary for NDPMTG font
        self.symbols = mana_symbol_map.copy()

        # Layer names
        self.layers = LAYERS

        # Main color dictionary
        self.colors = main_color_map.copy()

        # Rarity gradient dictionary
        self.rarity_gradients = rarity_gradient_map.copy()

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
        self.font_rules_text_italic = CardFonts.RULES_ITALIC
        self.font_rules_text_bold = CardFonts.RULES_BOLD
        self.font_rules_text = CardFonts.RULES
        self.font_collector = CardFonts.COLLECTOR
        self.font_artist = CardFonts.ARTIST
        self.font_title = CardFonts.TITLES
        self.font_pt = CardFonts.TITLES
        self.font_mana = CardFonts.MANA

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
    * Utilities
    """

    def reload(self):
        """Reloads default attribute values."""
        self.load_values()

    """
    * Handle: Photoshop
    """

    def refresh_photoshop(self) -> Optional[Exception]:
        """Attempts to refresh the Photoshop object."""
        return self.app.refresh_app()

    """
    * Handle: Version Tracker
    """

    @suppress_and_return({})
    def get_version_tracker(self) -> dict:
        """Get the current version tracker dict."""
        # Write a blank version tracker if not found
        if not self.path_version_tracker.is_file():
            dump_data_file({}, self.path_version_tracker)

        # Pull the version tracker
        return load_data_file(self.path_version_tracker)

    def update_version_tracker(self):
        """Updates the version tracker json with current dict."""
        dump_data_file(self.versions, self.path_version_tracker)

    """
    Handle: Expansion Symbols
    """

    @suppress_and_return({})
    def get_expansion_symbols(self) -> dict:
        """
        Import the expansion symbol library (YAML data).
        @return: Dict containing expansion symbol entries.
        """
        # Check for expansion symbol library
        if not self.path_expansion_symbols.is_file():
            dump_data_file({}, self.path_expansion_symbols)

        # Import expansion symbol library
        return load_data_file(self.path_expansion_symbols)

    @suppress_and_return({})
    def get_custom_symbols(self) -> dict:
        """
        Import any custom defined expansion symbols (YAML data).
        @return: Dict containing custom symbol entries.
        """
        # Check for a custom expansion symbol library
        if not self.path_custom_symbols.is_file():
            dump_data_file({}, self.path_custom_symbols)

        # Pull the custom expansion symbol library
        return load_data_file(self.path_custom_symbols)

    """
    Handle: Watermarks
    """

    @suppress_and_return({})
    def get_watermarks(self) -> dict:
        """
        Import the watermark library (YAML data).
        @return: Dict containing watermark entries.
        """
        # Check for a watermark library
        if not self.path_watermarks.is_file():
            dump_data_file({}, self.path_watermarks)

        # Import watermark library
        return load_data_file(self.path_watermarks)


# Global instance tracking our constants
con = Constants()
