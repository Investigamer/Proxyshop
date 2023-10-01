"""
GLOBAL SETTINGS MODULE
"""
# Standard Library Imports
import os
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
	CollectorPromo
)
from src.utils.objects import Singleton
from src.utils.strings import StrEnum
from src.types.templates import TemplateDetails
from src.utils.files import verify_config_fields


class Config:
	"""
	Stores the current state of app and template settings.
	Can be changed within a template class to affect rendering behavior.
	"""
	__metaclass__ = Singleton

	def __init__(self):
		self.load()

	def update_definitions(self):
		"""
		Load the config values
		"""
		# APP - FILES
		self.save_artist_name = self.file.getboolean('APP.FILES', 'Save.Artist.Name')
		self.overwrite_duplicate = self.file.getboolean('APP.FILES', 'Overwrite.Duplicate')
		self.output_filetype = self.get_option('APP.FILES', 'Output.Filetype', OutputFiletype)

		# APP - DATA
		self.lang = self.file['APP.DATA'].get('Scryfall.Language', 'en')
		self.scry_ascending = self.file.getboolean('APP.DATA', 'Scryfall.Ascending')
		self.scry_sorting = self.get_option('APP.DATA', 'Scryfall.Sorting', ScryfallSorting)
		self.scry_extras = self.file.getboolean('APP.DATA', 'Scryfall.Extras')
		self.scry_unique = self.get_option('APP.DATA', 'Scryfall.Unique', ScryfallUnique)

		# APP - TEXT
		self.force_english_formatting = self.file.getboolean('APP.TEXT', "Force.English.Formatting")

		# APP - RENDER
		self.skip_failed = self.file.getboolean('APP.RENDER', 'Skip.Failed')
		self.render_snow = self.file.getboolean('APP.RENDER', 'Render.Snow')
		self.render_miracle = self.file.getboolean('APP.RENDER', 'Render.Miracle')
		self.render_basic = self.file.getboolean('APP.RENDER', 'Render.Basic')
		self.generative_fill = self.file.getboolean('APP.RENDER', 'Generative.Fill')
		self.vertical_fullart = self.file.getboolean('APP.RENDER', 'Vertical.Fullart')

		# APP - SYSTEM
		self.refresh_plugins = self.file.getboolean('APP.SYSTEM', 'Refresh.Plugins')
		self.test_mode = self.file.getboolean('APP.SYSTEM', 'Test.Mode')

		# BASE - TEXT
		self.flavor_divider = self.file.getboolean('BASE.TEXT', 'Flavor.Divider')
		self.remove_flavor = self.file.getboolean('BASE.TEXT', 'No.Flavor.Text')
		self.remove_reminder = self.file.getboolean('BASE.TEXT', 'No.Reminder.Text')
		self.collector_mode = self.get_option('BASE.TEXT', 'Collector.Mode', CollectorMode)
		self.collector_promo = self.get_option('BASE.TEXT', "Collector.Promo", CollectorPromo)

		# BASE - SYMBOLS
		self.symbol_default = self.file['BASE.SYMBOLS']['Default.Symbol']
		self.symbol_force_default = self.file.getboolean('BASE.SYMBOLS', 'Force.Default.Symbol')
		self.symbol_stroke = int(self.file['BASE.SYMBOLS']['Symbol.Stroke.Size'])
		self.enable_watermark = self.file.getboolean('BASE.SYMBOLS', 'Enable.Watermark')
		self.watermark_opacity = int(self.file['BASE.SYMBOLS']['Watermark.Opacity'])
		self.symbol_mode = self.get_option('BASE.SYMBOLS', 'Symbol.Mode', ExpansionSymbolMode)

		# BASE - TEMPLATES
		self.exit_early = self.file.getboolean('BASE.TEMPLATES', 'Manual.Edit')
		self.import_scryfall_scan = self.file.getboolean('BASE.TEMPLATES', 'Import.Scryfall.Scan')
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
				'MTG', con.set_symbol_fallback
			)
		)

	"""
	LOAD SETTINGS
	"""

	def load(self, template: Optional[TemplateDetails] = None):
		"""
		Reload the config file and define new values
		"""
		# Invalidate file cache
		if hasattr(self, 'file'):
			del self.file

		# Check if we're using a template config
		conf = con.path_config_ini_base
		if hasattr(self, 'test_mode') and not self.test_mode and template:
			# Check if the template config exists
			template_ini = template['config_path'].replace('json', 'ini').replace('Back', 'Front') if template else None
			template_json = template['config_path'].replace('Back', 'Front') if template else None
			if template_ini and os.path.isfile(template_ini):
				# Use template ini and validate its contents
				verify_config_fields(template_ini, template_json)
				conf = template_ini

		# Validate app and base ini contents
		verify_config_fields(con.path_config_ini_app, con.path_config_json_app)
		verify_config_fields(conf, con.path_config_json_base)

		# Load necessary files
		self.file = ConfigParser(allow_no_value=True)
		self.file.optionxform = str
		with open(conf, encoding="utf-8") as f:
			self.file.read_file(f)
		with open(con.path_config_ini_app, encoding="utf-8") as f:
			self.file.read_file(f)
		self.update_definitions()


# Global instance tracking our settings
cfg = Config()
