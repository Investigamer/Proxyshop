"""
GLOBAL SETTINGS MODULE
"""
# Standard Library Imports
from pathlib import Path
from typing import Optional, Union
from configparser import ConfigParser

# Local Imports
from src.constants import con
from src.enums.settings import (
	ExpansionSymbolMode,
	CollectorMode,
	BorderColor,
	OutputFiletype,
	ScryfallSorting,
	ScryfallUnique,
	CollectorPromo, WatermarkMode
)
from src.utils.env import ENV
from src.utils.objects import Singleton
from src.utils.strings import StrEnum
from src.types.templates import TemplateDetails
from src.utils.files import (
	verify_config_fields,
	get_config_object,
	ensure_path_exists,
	copy_config_or_verify,
	get_kivy_config_from_schema
)


class ConfigManager:
	def __init__(self, template: Optional[str] = None, plugin: Optional[str] = None) -> None:

		# Establish template and plugin naming
		self._template = template.replace('Back', 'Front') if template else None
		self._plugin = plugin

		# Core path where config folders exist
		self._path_toml = Path(con.path_plugins, plugin, 'config') if plugin else con.path_config
		self._path_ini = Path(con.path_plugins, plugin, 'config_ini') if plugin else con.path_config_ini

	"""
	* Path: App settings only modified in Global
	"""

	@property
	def app_path_schema(self) -> Path:
		"""System config schema, in JSON or TOML."""
		return con.path_config_app

	@property
	def app_path_ini(self) -> Path:
		"""System config INI."""
		return con.path_config_ini_app

	@property
	def app_json(self) -> str:
		"""System config as Kivy readable JSON string dump."""
		return get_kivy_config_from_schema(self.app_path_schema)

	@property
	def app_cfg(self) -> ConfigParser:
		"""System ConfigParser instance."""
		return get_config_object(self.app_path_ini)

	"""
	* Path: Settings modifiable by Template
	"""

	@property
	def base_path_schema(self) -> Path:
		"""Main template config schema, in JSON or TOML."""
		return con.path_config_base

	@property
	def base_path_ini(self) -> Path:
		"""Main template config INI."""
		return con.path_config_ini_base

	@property
	def base_json(self) -> str:
		"""Main template config as Kivy readable JSON string dump."""
		return get_kivy_config_from_schema(self.base_path_schema)

	@property
	def base_cfg(self) -> ConfigParser:
		"""Main template ConfigParser instance."""
		return get_config_object(self.base_path_ini)

	"""
	* Path: Template specific settings
	"""

	@property
	def template_path_schema(self) -> Optional[Path]:
		"""Template specific config schema, in JSON or TOML."""
		if self._template:
			for n in ['.json', '.toml']:
				path = Path(self._path_toml, self._template).with_suffix(n)
				if path.is_file():
					return path
		return

	@property
	def template_path_ini(self) -> Optional[Path]:
		"""Template specific config INI."""
		if self._template:
			return Path(self._path_ini, self._template).with_suffix('.ini')
		return

	@property
	def template_json(self) -> Optional[str]:
		"""Template specific config as Kivy readable JSON string dump."""
		if self.template_path_schema:
			return get_kivy_config_from_schema(self.template_path_schema)
		return

	@property
	def template_cfg(self) -> Optional[ConfigParser]:
		"""Template specific ConfigParser instance."""
		if self.template_path_ini:
			return get_config_object(self.template_path_ini)
		return

	"""
	* Bool Checks
	"""

	@property
	def has_template_ini(self) -> bool:
		"""Returns True if a template has a separate INI file."""
		return bool(self.template_path_ini and self.template_path_ini.is_file())

	"""
	* Utility Methods
	"""

	def get_config(self) -> ConfigParser:
		"""Return a ConfigParser instance with all relevant config data loaded."""
		self.validate_configs()
		if self.has_template_ini:
			# Load template INI file instead of base
			self.validate_template_configs()
			return get_config_object([
				self.app_path_ini,
				self.template_path_ini])
		# Load app and base only
		return get_config_object([
			self.app_path_ini,
			self.base_path_ini])

	"""
	* Validate Methods
	"""

	def validate_configs(self) -> None:
		"""Validate app and base configs against data schemas."""
		verify_config_fields(
			ini_file=self.app_path_ini,
			data_file=self.app_path_schema)
		verify_config_fields(
			ini_file=self.base_path_ini,
			data_file=self.base_path_schema)

	def validate_template_configs(self) -> None:
		"""Validate template configs against data schemas."""
		if not self.template_path_ini:
			return

		# Validate base template configs
		ensure_path_exists(self.template_path_ini)
		copy_config_or_verify(
			path_from=self.base_path_ini,
			path_to=self.template_path_ini,
			data_file=self.base_path_schema)

		# Validate template specific configs
		if self.template_path_schema:
			verify_config_fields(
				ini_file=self.template_path_ini,
				data_file=self.template_path_schema)


class Config:
	"""
	Stores the current state of app and template settings.
	Can be changed within a template class to affect rendering behavior.
	"""
	__metaclass__ = Singleton

	def __init__(self):
		self.load()

	def update_definitions(self):
		"""Load config values."""

		# APP - FILES
		self.save_artist_name = self.file.getboolean('APP.FILES', 'Save.Artist.Name', fallback=False)
		self.overwrite_duplicate = self.file.getboolean('APP.FILES', 'Overwrite.Duplicate', fallback=True)
		self.output_filetype = self.get_option('APP.FILES', 'Output.Filetype', OutputFiletype)

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
		self.generative_fill = self.file.getboolean('APP.RENDER', 'Generative.Fill', fallback=False)
		self.vertical_fullart = self.file.getboolean('APP.RENDER', 'Vertical.Fullart', fallback=False)

		# APP - SYSTEM
		self.refresh_plugins = self.file.getboolean('APP.SYSTEM', 'Refresh.Plugins', fallback=False)
		self.test_mode = self.file.getboolean('APP.SYSTEM', 'Test.Mode', fallback=False)
		if self.test_mode:
			ENV.PS_ERROR_DIALOG = False

		# BASE - TEXT
		self.flavor_divider = self.file.getboolean('BASE.TEXT', 'Flavor.Divider', fallback=True)
		self.remove_flavor = self.file.getboolean('BASE.TEXT', 'No.Flavor.Text', fallback=False)
		self.remove_reminder = self.file.getboolean('BASE.TEXT', 'No.Reminder.Text', fallback=False)
		self.collector_mode = self.get_option('BASE.TEXT', 'Collector.Mode', CollectorMode)
		self.collector_promo = self.get_option('BASE.TEXT', "Collector.Promo", CollectorPromo)

		# BASE - SYMBOLS
		self.symbol_mode = self.get_option('BASE.SYMBOLS', 'Symbol.Mode', ExpansionSymbolMode)
		self.symbol_default = self.file.get('BASE.SYMBOLS', 'Default.Symbol', fallback='MTG')
		self.symbol_force_default = self.file.getboolean('BASE.SYMBOLS', 'Force.Default.Symbol', fallback=False)
		self.symbol_stroke = self.file.getint('BASE.SYMBOLS', 'Symbol.Stroke.Size', fallback=6)

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
	METHODS
	"""

	def get_option(self, section: str, key: str, enum_class: type[StrEnum], default: str = None) -> str:
		"""
		Returns the current value of an "options" setting if that option exists in its StrEnum class.
		Otherwise, returns the default value of that StrEnum class.
		@param section: Group (section) to access within the config file.
		@param key: Key to access within the setting group (section).
		@param enum_class: StrEnum class representing the options of this setting.
		@param default: Default value to return if current value is invalid.
		@return: Validated current value, or default value.
		"""
		default = default or enum_class.Default
		if self.file.has_section(section):
			option = self.file[section].get(key, fallback=default)
			if option in enum_class:
				return option
		return default

	def get_setting(self, section: str, key: str, default: Optional[str] = None, is_bool: bool = True):
		"""
		Check if the setting exists and return it. Default will be returned if missing.
		@param section: Section to look for.
		@param key: Key to look for within section.
		@param default: Default value to return if section/key missing.
		@param is_bool
		@return: Value or default
		"""
		if self.file.has_section(section):
			if self.file.has_option(section, key):
				if is_bool:
					return self.file.getboolean(section, key, fallback=default)
				return self.file[section].get(key, fallback=default)
		return default

	def get_default_symbol(self) -> Union[str, dict, list[dict]]:
		"""
		Gets the default expansion symbol set by the user, or the 'MTG' fallback symbol if not found.
		@return: Symbol character string or dict/list notation.
		"""
		return con.set_symbols.get(
			self.symbol_default, con.set_symbols.get(
				'MTG', con.set_symbol_fallback))

	"""
	LOAD SETTINGS
	"""

	def load(self, template: Optional[TemplateDetails] = None) -> None:
		"""
		Reload the config file and define new values
		@param template: Template data if provided.
		"""

		# Was template provided?
		template = template or {}

		# Invalidate file cache
		if hasattr(self, 'file'):
			del self.file

		# Check if we're using a template config
		config = ConfigManager(
			template=template.get('class_name'),
			plugin=template.get('plugin_name'))

		# Validate and load config data, then refresh values
		self.file = config.get_config()
		self.update_definitions()


"""
* Global settings instance
"""

cfg = Config()
