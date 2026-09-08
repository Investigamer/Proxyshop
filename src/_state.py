"""
* Manage Global State (non-GUI)
"""

import os
import sys
from logging import INFO, getLogger
from pathlib import Path
from threading import Lock
from typing import TypedDict

from hexproof.hexapi.schema.meta import Meta
from omnitils.files import get_project_version
from omnitils.properties import tracked_prop
from pydantic import BaseModel, RootModel, ValidationError
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from src.enums.layers import LAYERS
from src.enums.mtg import CardFonts, mana_symbol_map
from src.schema.colors import ColorObject, SymbolColorMap
from src.utils.data_structures import parse_model
from src.utils.mtg import get_symbol_colors

_logger = getLogger(__name__)


class HexproofSet(BaseModel):
    """Cached 'Set' object data from Hexproof.io."""

    code_symbol: str = "default"
    code_parent: str | None = None
    count_cards: int
    count_tokens: int
    count_printed: int | None = None


HexproofSets = RootModel[dict[str, HexproofSet]]

HexproofMetas = RootModel[dict[str, Meta]]

"""
* App Paths
"""

# Establish global root, based on frozen executable or Python
__PATH_CWD__: Path = Path(os.getcwd())
__PATH_ROOT__: Path = (
    # Path handling for PyInstalller build
    Path(sys.executable).parent
    if (getattr(sys, "frozen", False))
    # Path handling for regular Python
    else (Path(__file__).parent.parent)
)

# Switch to root directory if current directory differs
if str(__PATH_CWD__) != str(__PATH_ROOT__):
    os.chdir(__PATH_ROOT__)


class DefinedPaths:
    """Class for defining reusable named Path objects."""

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
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

    CWD = __PATH_ROOT__

    # Root Level Directories
    SRC = CWD / "src"
    OUT = CWD / "out"
    TMP = CWD / "tmp"
    LOGS = CWD / "logs"
    FONTS = CWD / "fonts"
    PLUGINS = CWD / "plugins"
    TEMPLATES = CWD / "templates"
    JS_SCRIPTS = CWD / "dist_js"
    PROJECT_FILE = CWD / "pyproject.toml"

    # Source Level Directories
    SRC_IMG = SRC / "img"
    SRC_DATA = SRC / "data"

    # Data Level Directories
    SRC_DATA_TESTS = SRC_DATA / "tests"
    SRC_DATA_CONFIG = SRC_DATA / "config"
    SRC_DATA_HEXPROOF = SRC_DATA / "hexproof"
    SRC_DATA_CONFIG_INI = SRC_DATA / "config_ini"
    SRC_DATA_PREFERENCES = SRC_DATA / "preferences"

    # Data Level Files
    SRC_DATA_ENV = SRC_DATA / "env.yml"
    SRC_DATA_ENV_DEFAULT = SRC_DATA / "env.default.yml"
    SRC_DATA_WATERMARKS = SRC_DATA / "watermarks.yml"
    SRC_DATA_MANIFEST = SRC_DATA / "manifest.yml"
    SRC_DATA_HEXPROOF_SET = SRC_DATA_HEXPROOF / "set.json"
    SRC_DATA_HEXPROOF_META = SRC_DATA_HEXPROOF / "meta.json"
    SRC_DATA_PREDEFINED_PLUGINS = SRC_DATA / "predefined_plugins.yml"

    # Test Data Files
    SRC_DATA_TEMPLATE_RENDER_TEST_CASES = SRC_DATA_TESTS / "template_renders.toml"

    # Image Level Directories
    SRC_IMG_SYMBOLS = SRC_IMG / "symbols"
    SRC_IMG_PREVIEWS = SRC_IMG / "previews"

    # Image Level Files
    SRC_IMG_SYMBOLS_PACKAGE = SRC_IMG_SYMBOLS / "package.zip"
    SRC_IMG_SYMBOLS_MANIFEST = SRC_IMG_SYMBOLS / "manifest.json"
    SRC_IMG_OVERLAY = SRC_IMG / "overlay.jpg"
    SRC_IMG_NOTFOUND = SRC_IMG / "notfound.jpg"
    SRC_IMG_TEST = SRC_IMG / "test.jpg"
    SRC_IMG_TEST_FULL_ART = SRC_IMG / "test-fa.jpg"

    # Config Level Files
    SRC_DATA_CONFIG_APP = SRC_DATA_CONFIG / "app.toml"
    SRC_DATA_CONFIG_BASE = SRC_DATA_CONFIG / "base.toml"
    SRC_DATA_CONFIG_INI_APP = SRC_DATA_CONFIG_INI / "app.ini"
    SRC_DATA_CONFIG_INI_BASE = SRC_DATA_CONFIG_INI / "base.ini"

    # Logs Level Files
    LOGS_SCAN = LOGS / "scan.jpg"
    LOGS_ERROR = LOGS / "error.txt"
    LOGS_FAILED = LOGS / "failed.txt"
    LOGS_COOKIES = LOGS / "cookies.json"

    # Generated user data files
    SRC_DATA_USER = SRC_DATA / "user.yml"
    SRC_DATA_VERSIONS = SRC_DATA / "versions.yml"
    SRC_DATA_PLUGIN_VERSIONS = SRC_DATA / "plugin_versions.yml"
    SRC_DATA_ADDED_PLUGINS = SRC_DATA / "added_plugins.yml"
    SRC_DATA_PREVIOUS_UPDATE_CHECK = SRC_DATA / "previous_update_check.json"


"""
* App Environment
"""


def _get_proj_version(path: Path) -> str:
    if hasattr(sys, "_MEIPASS"):
        # Build with Pyinstaller generated module
        import __VERSION__

        return str(__VERSION__.version)
    try:
        return get_project_version(path)
    except Exception:  # noqa: BLE001
        return "0.0.0"


class AppEnvironment(BaseSettings):
    API_GOOGLE: str = ""
    API_AMAZON: str = ""
    PS_ERROR_DIALOG: bool = False
    PS_VERSION: str | None = None
    HEADLESS: bool = False
    LOG_LEVEL: int = INFO
    APP_UPDATES_REPO: str = ""
    SYMBOL_UPDATES_REPO: str = ""
    FORCE_RELOAD: bool = False
    VERSION: str = _get_proj_version(PATH.PROJECT_FILE)
    UPDATE_CHECK_INTERVAL: float = 2.0

    model_config = SettingsConfigDict(env_prefix="PROXYSHOP_")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # First entry has highest priority
        return (
            env_settings,
            YamlConfigSettingsSource(settings_cls, PATH.SRC_DATA_ENV),
            YamlConfigSettingsSource(settings_cls, PATH.SRC_DATA_ENV_DEFAULT),
        )


"""
* App Constants
"""


class WatermarkFormat(TypedDict):
    scale: float


WatermarkFormats = RootModel[dict[str, WatermarkFormat]]


class CustomUserDefinitions(BaseModel):
    # Fonts
    font_rules_text_italic: str | None = None
    font_rules_text_bold: str | None = None
    font_rules_text: str | None = None
    font_collector: str | None = None
    font_artist: str | None = None
    font_title: str | None = None
    font_mana: str | None = None
    font_pt: str | None = None
    # Numeric font values
    flavor_text_lead_divider: float | None = None
    flavor_text_lead: float | None = None
    line_break_lead: float | None = None
    modal_indent: float | None = None


class AppConstants:
    """Stores global constants that control app behavior."""

    # Thread locking handlers
    lock_decompress = Lock()
    lock_file_save = Lock()

    def __init__(self):
        """Load initial values."""
        self._changes: set[str] = set()
        self.load_defaults()

    """
    * Loading Default Values
    """

    def load_defaults(self):
        """Loads default values. Called at launch and between renders to remove any changes made by templates."""

        # Define text layer formatting
        self.modal_indent: float = 5.7
        self.line_break_lead: float = 2.4
        self.flavor_text_lead: float = 4.4
        self.flavor_text_lead_divider: float = 7

        # Define currently selected fonts as defaults
        self.font_rules_text_italic: str = CardFonts.RULES_ITALIC
        self.font_rules_text_bold: str = CardFonts.RULES_BOLD
        self.font_rules_text: str = CardFonts.RULES
        self.font_collector: str = CardFonts.COLLECTOR
        self.font_artist: str = CardFonts.ARTIST
        self.font_title: str = CardFonts.TITLES
        self.font_pt: str = CardFonts.TITLES
        self.font_mana: str = CardFonts.MANA

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
    def watermarks(self) -> dict[str, WatermarkFormat]:
        """dict[str, dict]: Maps watermark names to defined formatting rules."""
        try:
            # Ensure file exists
            if not PATH.SRC_DATA_WATERMARKS.is_file():
                return parse_model(PATH.SRC_DATA_WATERMARKS, WatermarkFormats).root
        except OSError, ValidationError:
            pass
        except Exception:
            _logger.exception("Failed to get watermark mapping")
        return {}

    """
    * Tracked Properties: Colors
    """

    @tracked_prop
    def colors(self) -> dict[str, tuple[float, float, float]]:
        """dict[str, list[int]]: Named reusable colors."""
        return {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "silver": (167, 177, 186),
            "gold": (166, 135, 75),
        }

    @tracked_prop
    def mana_colors(self) -> SymbolColorMap:
        """SymbolColorMap: Defined mana symbol colors."""
        return SymbolColorMap()

    @tracked_prop
    def symbol_map(self) -> dict[str, tuple[str, list[ColorObject | None]]]:
        """Uses the symbol map and mana_colors to map
        symbol character strings and colors to their Scryfall symbol string."""
        return {
            sym: (n, get_symbol_colors(sym, n, self.mana_colors))
            for sym, n in self.mana_symbols.items()
        }

    def build_symbol_map(
        self,
        colors: SymbolColorMap | None = None,
        symbols: dict[str, str] | None = None,
    ) -> None:
        """Sets a new mapping for symbol colors. Affects e.g. mana colors.

        Args:
            colors: A model mapping color names to colors, uses default if not provided.
            symbols: A dictionary mapping font characters to their Scryfall symbol string. Uses default
                if not provided.
        """
        if colors:
            self.mana_colors = colors
        if symbols:
            self.mana_symbols = symbols
        self.symbol_map = {
            sym: (n, get_symbol_colors(sym, n, self.mana_colors))
            for sym, n in self.mana_symbols.items()
        }

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
            5: [
                LAYERS.FIFTH,
                LAYERS.TWO_FIFTHS,
                LAYERS.THREE_FIFTHS,
                LAYERS.FOUR_FIFTHS,
            ],
        }

    @tracked_prop
    def gradient_locations(self) -> dict[int, list[int | float]]:
        """dict[int, list[Union[int, float]]: Maps gradient locations to a number representing the number
        of color splits."""
        return {
            2: [0.40, 0.60],
            3: [0.26, 0.36, 0.64, 0.74],
            4: [0.20, 0.30, 0.45, 0.55, 0.70, 0.80],
            5: [0.20, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.80],
        }

    """
    * Tracked Properties: Hexproof.io Data
    """

    @tracked_prop
    def set_data(self) -> dict[str, HexproofSet]:
        """Returns set data pulled from Hexproof.io mapped to set codes."""
        return self.get_set_data()

    @tracked_prop
    def metadata(self) -> dict[str, Meta]:
        """Returns data pulled from Hexproof.io mapped to resources."""
        return self.get_meta_data()

    """
    * Import: User Custom Definitions
    """

    def get_user_data(self):
        """Loads the user data file and replaces any necessary data."""
        if PATH.SRC_DATA_USER.is_file():
            data = parse_model(PATH.SRC_DATA_USER, CustomUserDefinitions)

            for field in data.model_fields_set:
                if (value := getattr(data, field, None)) is not None:
                    setattr(self, field, value)

    """
    * Import: Hexproof API Data
    """

    def get_set_data(self) -> dict[str, HexproofSet]:
        """Loaded data from the 'set' data file."""
        try:
            if not PATH.SRC_DATA_HEXPROOF_SET.is_file():
                return {}

            # Read set data
            return HexproofSets.model_validate_json(
                PATH.SRC_DATA_HEXPROOF_SET.read_bytes()
            ).root
        except OSError, ValidationError:
            pass
        except Exception:
            _logger.exception("Failed to load data from Hexproof set file")
        return {}

    def get_meta_data(self) -> dict[str, Meta]:
        """Loaded data from the 'meta' data file."""
        try:
            if not PATH.SRC_DATA_HEXPROOF_META.is_file():
                return {}

            return HexproofMetas.model_validate_json(
                PATH.SRC_DATA_HEXPROOF_META.read_bytes()
            ).root
        except OSError, ValidationError:
            pass
        except Exception:
            _logger.exception("Failed to load data from Hexproof meta file")
        return {}
