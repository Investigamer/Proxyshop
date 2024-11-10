"""
* Global Settings Module
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from omnitils.metaclass import Singleton
from omnitils.enums import StrConstant

# Local Imports
from src._state import AppEnvironment
from src.enums.settings import (
    CollectorMode,
    BorderColor,
    OutputFileType,
    ScryfallSorting,
    ScryfallUnique,
    CollectorPromo,
    WatermarkMode
)
from src._loader import ConfigManager


class AppConfig:
    """Stores the current state of app and template settings. Can be changed within a template
    class to affect rendering behavior."""
    __metaclass__ = Singleton

    def __init__(self, env: AppEnvironment):
        """Load initial settings values."""
        self.ENV = env
        self.load()

    def update_definitions(self):
        """Updates the defined settings values using the currently loaded ConfigParser object."""

        # APP - FILES
        self.overwrite_duplicate = self.file.getboolean('APP.FILES', 'Overwrite.Duplicate', fallback=True)
        self.output_file_type = self.get_option('APP.FILES', 'Output.File.Type', OutputFileType)
        self.output_file_name = self.file.get(
            section='APP.FILES', option='Output.File.Name',
            fallback='#name (#frame<, #suffix>) [#set] {#num}')

        # APP - DATA
        self.lang = self.file.get('APP.DATA', 'Scryfall.Language', fallback='en')
        self.scry_sorting = self.get_option('APP.DATA', 'Scryfall.Sorting', ScryfallSorting)
        self.scry_ascending = self.file.getboolean('APP.DATA', 'Scryfall.Ascending', fallback=False)
        self.scry_extras = self.file.getboolean('APP.DATA', 'Scryfall.Extras', fallback=False)
        self.scry_unique = self.get_option('APP.DATA', 'Scryfall.Unique', ScryfallUnique)

        # APP - TEXT
        self.force_english_formatting = self.file.getboolean('APP.TEXT', "Force.English.Formatting", fallback=False)

        # APP - RENDER
        self.skip_failed = self.file.getboolean('APP.RENDER', 'Skip.Failed', fallback=False)
        self.generative_fill = False if self.ENV.TEST_MODE else self.file.getboolean(
            'APP.RENDER', 'Generative.Fill', fallback=False)
        self.select_variation = self.file.getboolean('APP.RENDER', 'Select.Variation', fallback=False)
        self.feathered_fill = self.file.getboolean('APP.RENDER', 'Feathered.Fill', fallback=False)
        self.vertical_fullart = self.file.getboolean('APP.RENDER', 'Vertical.Fullart', fallback=False)

        # BASE - TEXT
        self.flavor_divider = self.file.getboolean('BASE.TEXT', 'Flavor.Divider', fallback=True)
        self.remove_flavor = self.file.getboolean('BASE.TEXT', 'No.Flavor.Text', fallback=False)
        self.remove_reminder = self.file.getboolean('BASE.TEXT', 'No.Reminder.Text', fallback=False)
        self.collector_mode = self.get_option('BASE.TEXT', 'Collector.Mode', CollectorMode)
        self.collector_promo = self.get_option('BASE.TEXT', "Collector.Promo", CollectorPromo)

        # BASE - SYMBOLS
        self.symbol_enabled = self.file.getboolean('BASE.SYMBOLS', 'Enable.Expansion.Symbol', fallback=True)
        self.symbol_default = self.file.get('BASE.SYMBOLS', 'Default.Symbol', fallback='MTG')
        self.symbol_force_default = self.file.getboolean('BASE.SYMBOLS', 'Force.Default.Symbol', fallback=False)

        # BASE - WATERMARKS
        self.watermark_mode = self.get_option('BASE.WATERMARKS', 'Watermark.Mode', WatermarkMode)
        self.watermark_default = self.file.get('BASE.WATERMARKS', 'Default.Watermark', fallback='WOTC')
        self.watermark_opacity = self.file.getint('BASE.WATERMARKS', 'Watermark.Opacity', fallback=30)
        self.enable_basic_watermark = self.file.getboolean('BASE.WATERMARKS', 'Enable.Basic.Watermark', fallback=True)

        # BASE - TEMPLATES
        self.exit_early = self.file.getboolean('BASE.TEMPLATES', 'Manual.Edit', fallback=False)
        self.import_scryfall_scan = self.file.getboolean('BASE.TEMPLATES', 'Import.Scryfall.Scan', fallback=False)
        self.border_color = self.get_option('BASE.TEMPLATES', 'Border.Color', BorderColor)

    """
    * Setting Utils
    """

    def get_option(self, section: str, key: str, enum_class: type[StrConstant], default: str = None) -> str:
        """Returns the current value of an "options" setting if that option exists in its StrEnum class.
        Otherwise, returns the default value of that StrEnum class.

        Args:
            section: Group (section) to access within the config file.
            key: Key to access within the setting group (section).
            enum_class: StrEnum class representing the options of this setting.
            default: Default value to return if current value is invalid.

        Returns:
            Validated current value, or default value.
        """
        default = default or enum_class.Default
        if self.file.has_section(section):
            option = self.file[section].get(key, fallback=default)
            if option in enum_class:
                return option
        return default

    def get_setting(self, section: str, key: str, default: Optional[str] = None, is_bool: bool = True):
        """Check if the setting exists and return it. Default will be returned if missing.

        Args:
            section: Section to look for.
            key: Key to look for within section.
            default: Default value to return if section/key missing.
            is_bool: Whether this value is a boolean.

        Returns:
            Value or default
        """
        if self.file.has_section(section):
            if self.file.has_option(section, key):
                if is_bool:
                    return self.file.getboolean(section, key, fallback=default)
                return self.file[section].get(key, fallback=default)
        return default

    """
    * Load ConfigParser Object
    """

    def load(self, config: Optional[ConfigManager] = None) -> None:
        """Reload the config file and define new values

        Args:
            config: ConfigManager to load from if provided, otherwise use app-wide configuration.
        """
        # Invalidate file cache
        if hasattr(self, 'file'):
            del self.file

        # Load provided or load fresh
        config = config or ConfigManager()
        self.file = config.get_config()
        self.update_definitions()
