"""
* Manage Global State (non-GUI)
* Only local imports should be `enums`, `utils`, or `cards`.
"""
# Standard Library Imports
import os
from contextlib import suppress
from os import environ
from pathlib import Path
import sys
from threading import Lock
from typing import Optional, Union

# Third Party Imports
from dotenv import dotenv_values

# Local Imports
from src.enums.layers import LAYERS
from src.enums.mtg import (
    mana_symbol_map,
    CardFonts,
    SymbolColorMap,
    ColorObject,
    get_symbol_colors)
from src.utils.exceptions import return_on_exception
from src.utils.files import dump_data_file, load_data_file, get_app_version
from src.utils.properties import auto_prop_cached, Singleton, tracked_prop
from src.utils.strings import str_to_bool_safe


"""
* App Paths
"""

# Establish global root, based on frozen executable or Python
__PATH_CWD__: Path = Path(os.getcwd())
__PATH_ROOT__: Optional[Path] = Path(sys.executable).parent if (
    getattr(sys, 'frozen', False)
) else (Path(__file__).parent.parent if __file__ else __PATH_CWD__)

# Switch to root directory if current directory differs
if str(__PATH_CWD__) != str(__PATH_ROOT__):
    os.chdir(__PATH_ROOT__)


class DefinedPaths:
    """Class for defining reusable named Path objects."""

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.ensure_paths()

    @classmethod
    def ensure_paths(cls):
        """Ensures all directory paths defined exist."""

        # Iterate over all attributes, ignoring built-ins
        for attr in dir(cls):
            if not attr.startswith("__"):
                path = getattr(cls, attr)

                # Generate any directories which don't exist
                if isinstance(path, Path) and not path.suffix and not path.is_dir():
                    path.mkdir(mode=777, parents=True, exist_ok=True)


class PATH(DefinedPaths):
    """Define app-wide paths that are always relational to the root project path."""
    __metaclass__ = Singleton
    CWD = __PATH_ROOT__

    # Root Level Directories
    SRC = CWD / 'src'
    OUT = CWD / 'out'
    ART = CWD / 'art'
    LOGS = CWD / 'logs'
    FONTS = CWD / 'fonts'
    PLUGINS = CWD / 'plugins'
    TEMPLATES = CWD / 'templates'

    # Source Level Directories
    SRC_IMG = SRC / 'img'
    SRC_DATA = SRC / 'data'

    # Data Level Directories
    SRC_DATA_KV = SRC_DATA / 'kv'
    SRC_DATA_TESTS = SRC_DATA / 'tests'
    SRC_DATA_CONFIG = SRC_DATA / 'config'
    SRC_DATA_HEXPROOF = SRC_DATA / 'hexproof'
    SRC_DATA_CONFIG_INI = SRC_DATA / 'config_ini'

    # Data Level Files
    SRC_DATA_WATERMARKS = SRC_DATA / 'watermarks.yml'
    SRC_DATA_MANIFEST = SRC_DATA / 'manifest.yml'
    SRC_DATA_HEXPROOF_SET = (SRC_DATA_HEXPROOF / 'set').with_suffix('.json')
    SRC_DATA_HEXPROOF_META = (SRC_DATA_HEXPROOF / 'meta').with_suffix('.json')

    # Image Level Directories
    SRC_IMG_SYMBOLS = SRC_IMG / 'symbols'
    SRC_IMG_PREVIEWS = SRC_IMG / 'previews'

    # Image Level Files
    SRC_IMG_SYMBOLS_PACKAGE = (SRC_IMG_SYMBOLS / 'package').with_suffix('.zip')
    SRC_IMG_OVERLAY = (SRC_IMG / 'overlay').with_suffix('.jpg')
    SRC_IMG_NOTFOUND = (SRC_IMG / 'notfound').with_suffix('.jpg')

    # Config Level Files
    SRC_DATA_CONFIG_APP = (SRC_DATA_CONFIG / 'app').with_suffix('.toml')
    SRC_DATA_CONFIG_BASE = (SRC_DATA_CONFIG / 'base').with_suffix('.toml')
    SRC_DATA_CONFIG_INI_APP = (SRC_DATA_CONFIG_INI / 'app').with_suffix('.ini')
    SRC_DATA_CONFIG_INI_BASE = (SRC_DATA_CONFIG_INI / 'base').with_suffix('.ini')

    # Logs Level Files
    LOGS_SCAN = (LOGS / 'scan').with_suffix('.jpg')
    LOGS_ERROR = (LOGS / 'error').with_suffix('.txt')
    LOGS_FAILED = (LOGS / 'failed').with_suffix('.txt')
    LOGS_COOKIES = (LOGS / 'cookies').with_suffix('.json')

    # Generated user data files
    SRC_DATA_USER = SRC_DATA / 'user.yml'
    SRC_DATA_VERSIONS = SRC_DATA / 'versions.yml'


"""
* App Environment
"""

# Load environment variables
DOTENV = dotenv_values(Path(PATH.CWD, '.env'))

# KIVY Environment
environ.setdefault('KIVY_LOG_MODE', 'PYTHON')
environ.setdefault('KIVY_NO_FILELOG', '1')
environ.setdefault('HEADLESS', '0')


class AppEnvironment:
    """Tracking and modifying global environment behavior."""
    __metaclass__ = Singleton

    @auto_prop_cached
    def VERSION(self) -> str:
        """str: Current app version."""
        if hasattr(sys, '_MEIPASS'):
            # Use generated version module in Pyinstaller build
            import __VERSION__
            return str(__VERSION__.version)
        return environ.get('VERSION', get_app_version(PATH.CWD / 'pyproject.toml'))

    @auto_prop_cached
    def API_GOOGLE(self) -> str:
        """str: Google Drive API key."""
        return environ.get('GOOGLE_KEY', DOTENV.get('GOOGLE_KEY', ''))

    @auto_prop_cached
    def API_AMAZON(self) -> str:
        """str: Amazon S3 cloudfront URL."""
        return environ.get('AMAZON_KEY', DOTENV.get('AMAZON_KEY', ''))

    @auto_prop_cached
    def DEV_MODE(self) -> bool:
        """bool: Whether the app is running in developer mode."""
        return str_to_bool_safe(environ.get('DEV_MODE', DOTENV.get('DEV_MODE', str(not hasattr(sys, '_MEIPASS')))))

    @auto_prop_cached
    def TEST_MODE(self) -> bool:
        """bool: Whether the app is running in testing mode."""
        return str_to_bool_safe(environ.get('TEST_MODE', DOTENV.get('TEST_MODE', '0')))

    @auto_prop_cached
    def FORCE_RELOAD(self) -> bool:
        """bool: Whether the for plugin template modules to be reloaded on each new render sequence."""
        return str_to_bool_safe(environ.get('FORCE_RELOAD', DOTENV.get('FORCE_RELOAD', '0')))

    @auto_prop_cached
    def HEADLESS(self) -> bool:
        """bool: Whether the app is running in headless mode."""
        return str_to_bool_safe(environ.get('HEADLESS', DOTENV.get('HEADLESS', '0')))

    @auto_prop_cached
    def PS_ERROR_DIALOG(self) -> bool:
        """bool: Whether Photoshop error dialogues are enabled."""
        return str_to_bool_safe(environ.get('PS_ERROR_DIALOG', DOTENV.get('PS_ERROR_DIALOG', '0')))

    @auto_prop_cached
    def PS_VERSION(self) -> Optional[str]:
        """str: Photoshop version to try and load, for use when multiple Photoshop versions are installed."""
        return environ.get('PS_VERSION', DOTENV.get('PS_VERSION', None))


"""
* App Constants
"""


class AppConstants:
    """Stores global constants that control app behavior."""
    __metaclass__ = Singleton
    _changes = set()

    # Thread locking handlers
    lock_decompress = Lock()
    lock_file_save = Lock()

    # Standard HTTP request header
    http_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/39.0.2171.95 Safari/537.36"}

    def __init__(self):
        """Load initial values."""
        self.load_defaults()

    """
    * Loading Default Values
    """

    def load_defaults(self):
        """Loads default values. Called at launch and between renders to remove any changes made by templates."""

        # Define text layer formatting
        self.modal_indent = 5.7
        self.line_break_lead = 2.4
        self.flavor_text_lead = 4.4
        self.flavor_text_lead_divider = 7

        # Define currently selected fonts as defaults
        self.font_rules_text_italic = CardFonts.RULES_ITALIC
        self.font_rules_text_bold = CardFonts.RULES_BOLD
        self.font_rules_text = CardFonts.RULES
        self.font_collector = CardFonts.COLLECTOR
        self.font_artist = CardFonts.ARTIST
        self.font_title = CardFonts.TITLES
        self.font_pt = CardFonts.TITLES
        self.font_mana = CardFonts.MANA

        # Load changed values
        if self._changes:
            for attr in self._changes:
                delattr(self, attr)
            self._changes.clear()
            self.get_user_data()

    def reload(self) -> None:
        """Reloads default attribute values."""
        self.load_defaults()

    """
    * Tracked Properties: Symbols
    """

    @tracked_prop
    def mana_symbols(self) -> dict[str, str]:
        """dict[str, str]: Maps Scryfall symbol strings to their font character representation."""
        return mana_symbol_map.copy()

    """
    * Tracked Properties: Watermarks
    """

    @tracked_prop
    def watermarks(self) -> dict[str, dict]:
        """dict[str, dict]: Maps watermark names to defined formatting rules."""
        with suppress():
            # Ensure file exists
            if not PATH.SRC_DATA_WATERMARKS.is_file():
                dump_data_file({}, PATH.SRC_DATA_WATERMARKS)
            return load_data_file(PATH.SRC_DATA_WATERMARKS)
        return {}

    """
    * Tracked Properties: Colors
    """

    @tracked_prop
    def colors(self) -> dict[str, list[int]]:
        """dict[str, list[int]]: Named reusable colors."""
        return {
            'black': [0, 0, 0],
            'white': [255, 255, 255],
            'silver': [167, 177, 186],
            'gold': [166, 135, 75]
        }

    @tracked_prop
    def mana_colors(self) -> SymbolColorMap:
        """SymbolColorMap: Defined mana symbol colors."""
        return SymbolColorMap()

    @tracked_prop
    def symbol_map(self) -> dict[str, tuple[str, list[ColorObject]]]:
        """dict[str, tuple[str, list[ColorObject]]]: Uses the symbol map and mana_colors to map
            symbol character strings and colors to their Scryfall symbol string."""
        return {sym: (n, get_symbol_colors(sym, n, self.mana_colors)) for sym, n in self.mana_symbols.items()}

    def build_symbol_map(
            self, colors: Optional[SymbolColorMap] = None,
            symbols: Optional[dict[str, str]] = None
    ) -> None:
        """Establishes a new `symbol_color_map` using a provided color map and symbol map.

        Args:
            colors: A `SymbolColorMap`, uses default if not provided.
            symbols: A dictionary mapping font characters to their Scryfall symbol string. Uses default
                if not provided.
        """
        if colors:
            self.mana_colors = colors
        if symbols:
            self.mana_symbols = symbols
        self.symbol_map = {
            sym: (n, get_symbol_colors(sym, n, self.mana_colors))
            for sym, n in self.mana_symbols.items()}

    """
    * Tracked Properties: Masks and Gradients
    """

    @tracked_prop
    def masks(self) -> dict[int, list[str]]:
        """dict[int, list[str]]: Maps mask layer names to a number representing the number of color splits."""
        return {
            2: [LAYERS.HALF],
            3: [LAYERS.THIRD, LAYERS.TWO_THIRDS],
            4: [LAYERS.QUARTER, LAYERS.HALF, LAYERS.THREE_QUARTERS],
            5: [LAYERS.FIFTH, LAYERS.TWO_FIFTHS, LAYERS.THREE_FIFTHS, LAYERS.FOUR_FIFTHS]
        }

    @tracked_prop
    def gradient_locations(self) -> dict[int, list[Union[int, float]]]:
        """dict[int, list[Union[int, float]]: Maps gradient locations to a number representing the number
            of color splits."""
        return {
            2: [.40, .60],
            3: [.26, .36, .64, .74],
            4: [.20, .30, .45, .55, .70, .80],
            5: [.20, .25, .35, .45, .55, .65, .75, .80]
        }

    """
    * Tracked Properties: Template Versions
    """

    @tracked_prop
    def versions(self) -> dict:
        """dict[str, str]: Maps version numbers to template file identifiers."""
        with suppress():
            # Ensure file exists
            if not PATH.SRC_DATA_VERSIONS.is_file():
                dump_data_file({}, PATH.SRC_DATA_VERSIONS)
            return load_data_file(PATH.SRC_DATA_VERSIONS)
        return {}

    def update_version_tracker(self):
        """Updates the version tracker JSON file with current values."""
        dump_data_file(self.versions, PATH.SRC_DATA_VERSIONS)
        if 'versions' in self._changes:
            self._changes.remove('versions')
        delattr(self, 'versions')

    """
    * Tracked Properties: Hexproof.io Data
    """

    @tracked_prop
    def set_data(self) -> dict[str, dict]:
        """dict[str, dict]: Returns set data pulled from Hexproof.io mapped to set codes."""
        return self.get_set_data()

    @tracked_prop
    def metadata(self) -> dict[str, dict]:
        """dict[str, dict]: Returns data pulled from Hexproof.io mapped to resources."""
        return self.get_meta_data()

    """
    * Import: User Custom Definitions
    """

    def get_user_data(self):
        """Loads the user data file and replaces any necessary data."""
        # Write a blank data file if not found
        if not PATH.SRC_DATA_USER.is_file():
            dump_data_file({}, PATH.SRC_DATA_USER)

        # Pull the version tracker
        f = load_data_file(PATH.SRC_DATA_USER)

        # Load user data
        [self.__setattr__(name, f[name]) for name in [
            # Fonts
            'font_rules_text_italic',
            'font_rules_text_bold',
            'font_rules_text',
            'font_collector',
            'font_artist',
            'font_title',
            'font_mana',
            'font_pt',

            # Numeric font values
            'flavor_text_lead_divider',
            'flavor_text_lead',
            'line_break_lead',
            'modal_indent'
        ] if f.get(name)]

    """
    * Import: Hexproof API Data
    """

    @return_on_exception({})
    def get_set_data(self) -> dict[str, dict]:
        """dict: Loaded data from the 'set' data file."""
        if not PATH.SRC_DATA_HEXPROOF_SET.is_file():
            dump_data_file({}, PATH.SRC_DATA_HEXPROOF_SET)

        # Import watermark library
        return load_data_file(PATH.SRC_DATA_HEXPROOF_SET)

    @return_on_exception({})
    def get_meta_data(self) -> dict[str, dict]:
        """dict: Loaded data from the 'meta' data file."""
        if not PATH.SRC_DATA_HEXPROOF_META.is_file():
            dump_data_file({}, PATH.SRC_DATA_HEXPROOF_META)

        # Import watermark library
        return load_data_file(PATH.SRC_DATA_HEXPROOF_META)
