"""
* Manage Global State (non-GUI)
* Only local imports should be `utils`.
"""
# Standard Library Imports
import os
from os import environ
from pathlib import Path
import sys
from threading import Lock
from typing import Optional

# Third Party Imports
from dotenv import dotenv_values

# Local Imports
from src.enums.layers import LAYERS
from src.enums.mtg import (
    mana_color_map,
    mana_symbol_map,
    rarity_gradient_map,
    main_color_map,
    CardFonts)
from src.utils.exceptions import return_on_exception
from src.utils.files import dump_data_file, load_data_file, get_app_version
from src.utils.properties import auto_prop_cached, Singleton
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
DOTENV = dotenv_values('.env')

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
        if ver := DOTENV.get('VERSION'):
            return ver
        return get_app_version(Path(__file__).parent.parent.parent / 'pyproject.toml')

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
        if environ.get('DEV_MODE'):
            return str_to_bool_safe(environ['DEV_MODE'])
        return bool(not hasattr(sys, '_MEIPASS'))

    @auto_prop_cached
    def TEST_MODE(self) -> bool:
        """bool: Whether the app is running in testing mode."""
        if environ.get('TEST_MODE'):
            return str_to_bool_safe(environ['TEST_MODE'])
        return False

    @auto_prop_cached
    def FORCE_RELOAD(self) -> bool:
        """bool: Whether the for plugin template modules to be reloaded on each new render sequence."""
        if environ.get('FORCE_RELOAD'):
            return str_to_bool_safe(environ['FORCE_RELOAD'])
        return False

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
        self.load_values()

    def load_values(self):
        """Loads default values. Called at launch and between renders to remove any changes made by templates."""

        # Define blending layer mask map
        self.masks = {
            2: [LAYERS.HALF],
            3: [LAYERS.THIRD, LAYERS.TWO_THIRDS],
            4: [LAYERS.QUARTER, LAYERS.HALF, LAYERS.THREE_QUARTERS]
        }

        # Define named colors
        self.colors = main_color_map.copy()

        # Define mana colors map
        self.mana_colors = mana_color_map.copy()

        # Define rarity gradient map
        self.rarity_gradients = rarity_gradient_map.copy()

        # Define rarity gradient location map
        self.gradient_locations = {
            2: [.40, .60],
            3: [.26, .36, .64, .74],
            4: [.20, .30, .45, .55, .70, .80],
            5: [.20, .25, .35, .45, .55, .65, .75, .80]
        }

        # Define card symbol dictionary
        self.symbols = mana_symbol_map.copy()

        # Define currently selected fonts as defaults
        self.font_rules_text_italic = CardFonts.RULES_ITALIC
        self.font_rules_text_bold = CardFonts.RULES_BOLD
        self.font_rules_text = CardFonts.RULES
        self.font_collector = CardFonts.COLLECTOR
        self.font_artist = CardFonts.ARTIST
        self.font_title = CardFonts.TITLES
        self.font_pt = CardFonts.TITLES
        self.font_mana = CardFonts.MANA

        # Define text layer formatting
        self.modal_indent = 5.7
        self.line_break_lead = 2.4
        self.flavor_text_lead = 4.4
        self.flavor_text_lead_divider = 7

        # Import Hexproof.io Cached Data
        self.set_data = self.get_set_data()
        self.metadata = self.get_meta_data()

        # Import watermark library
        self.watermarks = self.get_watermarks()

        # Import user version tracker
        self.versions = self.get_version_tracker()

        # Import user custom definitions
        self.get_user_data()

    def reload(self) -> None:
        """Reloads default attribute values."""
        self.load_values()

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
    * Import: User Version Tracker
    """

    @return_on_exception({})
    def get_version_tracker(self) -> dict:
        """Get the current version tracker dict."""
        # Write a blank version tracker if not found
        if not PATH.SRC_DATA_VERSIONS.is_file():
            dump_data_file({}, PATH.SRC_DATA_VERSIONS)

        # Pull the version tracker
        return load_data_file(PATH.SRC_DATA_VERSIONS)

    def update_version_tracker(self):
        """Updates the version tracker json with current dict."""
        dump_data_file(self.versions, PATH.SRC_DATA_VERSIONS)

    """
    * Import: Watermark Config
    """

    @return_on_exception({})
    def get_watermarks(self) -> dict:
        """Import the watermark configuration map (YAML).

        Returns:
            Dict containing watermark configuration map.
        """
        # Check for a watermark library
        if not PATH.SRC_DATA_WATERMARKS.is_file():
            dump_data_file({}, PATH.SRC_DATA_WATERMARKS)

        # Import watermark library
        return load_data_file(PATH.SRC_DATA_WATERMARKS)

    """
    * Import: Hexproof API Data
    """

    @return_on_exception({})
    def get_set_data(self) -> dict:
        """dict: Loaded data from the 'set' data file."""
        if not PATH.SRC_DATA_HEXPROOF_SET.is_file():
            dump_data_file({}, PATH.SRC_DATA_HEXPROOF_SET)

        # Import watermark library
        return load_data_file(PATH.SRC_DATA_HEXPROOF_SET)

    @return_on_exception({})
    def get_meta_data(self) -> dict:
        """dict: Loaded data from the 'meta' data file."""
        if not PATH.SRC_DATA_HEXPROOF_META.is_file():
            dump_data_file({}, PATH.SRC_DATA_HEXPROOF_META)

        # Import watermark library
        return load_data_file(PATH.SRC_DATA_HEXPROOF_META)
