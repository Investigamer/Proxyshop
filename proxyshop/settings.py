"""
Process config file into global settings.
"""
import configparser
import os
from typing import Optional

from proxyshop.constants import con
from proxyshop.core import TemplateDetails


# For object permanence
class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


# Global app-wide settings configuration
class Config:
	"""
	Build our config info
	"""
	__metaclass__ = Singleton

	def __init__(self):
		self.load()

	def update_definitions(self):
		"""
		Load the config values
		"""
		# FILE section
		self.output_filetype = self.file['FILES']['Output.Filetype']
		self.save_artist_name = self.file.getboolean('FILES', 'Save.Artist.Name')
		self.overwrite_duplicate = self.file.getboolean('FILES', 'Overwrite.Duplicate')

		# TEXT section
		self.remove_flavor = self.file.getboolean('TEXT', 'No.Flavor.Text')
		self.remove_reminder = self.file.getboolean('TEXT', 'No.Reminder.Text')
		self.real_collector = self.file.getboolean('TEXT', 'True.Collector.Info')
		self.lang = self.file['TEXT']['Language']
		self.force_english_formatting = self.file.getboolean('TEXT', "Force.English.Formatting")
		self.flavor_divider = self.file.getboolean('TEXT', 'Flavor.Divider')

		# SYMBOLS section
		self.symbol_char = self.file['SYMBOLS']['Default.Symbol']
		self.auto_symbol = self.file.getboolean('SYMBOLS', 'Auto.Set.Symbol')
		self.auto_symbol_size = self.file.getboolean('SYMBOLS', 'Auto.Symbol.Size')
		self.symbol_stroke = self.file['SYMBOLS']['Symbol.Stroke.Size']
		self.fill_symbol = self.file.getboolean('SYMBOLS', 'Fill.Symbol.Background')
		self.classic_expansion_symbol = self.file.getboolean('SYMBOLS', 'Classic.Symbol.Rendering')

		# APP section
		self.exit_early = self.file.getboolean('APP', 'Manual.Edit')
		self.skip_failed = self.file.getboolean('APP', 'Skip.Failed')
		self.scry_ascending = self.file.getboolean('APP', 'Scryfall.Ascending')
		self.targeted_replace = self.file.getboolean('APP', 'Targeted.Replace')
		self.color_identity_max = int(self.file['APP']['Color.Identity.Max'])
		self.dev_mode = self.file.getboolean('APP', 'Dev.Mode')
		self.color_identity_max = int(self.file['APP']['Color.Identity.Max'])

		# TEMPLATES section
		self.render_snow = self.file.getboolean('TEMPLATES', 'Render.Snow')
		self.render_miracle = self.file.getboolean('TEMPLATES', 'Render.Miracle')
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
					return self.file.getboolean(section, key)
				return self.file[section][key]
		return default

	def load(self, template: Optional[TemplateDetails] = None):
		"""
		Reload the config file and define new values
		"""
		# Invalidate file cache
		if hasattr(self, 'file'):
			del self.file

		# Choose the file
		conf = os.path.join(con.cwd, "config.ini")
		if template and os.path.exists(template['config_path'].replace('json', 'ini')):
			conf = template['config_path'].replace('json', 'ini')

		# Load necessary file
		self.file = configparser.ConfigParser(allow_no_value=True)
		self.file.optionxform = str
		with open(conf, encoding="utf-8") as f:
			self.file.read_file(f)
		self.update_definitions()


# Global settings object
cfg = Config()
