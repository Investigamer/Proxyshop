"""
Process config file into global settings.
"""
import os
from typing import Optional
from configparser import ConfigParser

from src.constants import con
from src.core import TemplateDetails
from src.utils.files import verify_config_fields


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
		# APP - FILES
		self.output_filetype = self.file['APP.FILES']['Output.Filetype']
		self.save_artist_name = self.file.getboolean('APP.FILES', 'Save.Artist.Name')
		self.overwrite_duplicate = self.file.getboolean('APP.FILES', 'Overwrite.Duplicate')

		# APP - RENDER
		self.skip_failed = self.file.getboolean('APP.RENDER', 'Skip.Failed')
		self.targeted_replace = self.file.getboolean('APP.RENDER', 'Targeted.Replace')
		self.force_english_formatting = self.file.getboolean('APP.RENDER', "Force.English.Formatting")

		# APP - DATA
		self.scry_ascending = self.file.getboolean('APP.DATA', 'Scryfall.Ascending')

		# APP - SYSTEM
		self.dev_mode = self.file.getboolean('APP.SYSTEM', 'Dev.Mode')

		# TEXT settings
		self.lang = self.file['BASE.TEXT']['Language']
		self.flavor_divider = self.file.getboolean('BASE.TEXT', 'Flavor.Divider')
		self.remove_flavor = self.file.getboolean('BASE.TEXT', 'No.Flavor.Text')
		self.remove_reminder = self.file.getboolean('BASE.TEXT', 'No.Reminder.Text')
		self.real_collector = self.file.getboolean('BASE.TEXT', 'True.Collector.Info')

		# SYMBOLS settings
		self.symbol_mode = self.file['BASE.SYMBOLS']['Symbol.Mode']
		self.symbol_default = self.file['BASE.SYMBOLS']['Default.Symbol']
		self.symbol_force_default = self.file.getboolean('BASE.SYMBOLS', 'Force.Default.Symbol')
		self.symbol_stroke = self.file['BASE.SYMBOLS']['Symbol.Stroke.Size']
		self.enable_watermark = self.file.getboolean('BASE.SYMBOLS', 'Enable.Watermark')

		# TEMPLATES settings
		self.exit_early = self.file.getboolean('BASE.TEMPLATES', 'Manual.Edit')
		self.border_color = self.file['BASE.TEMPLATES']['Border.Color']
		self.render_snow = self.file.getboolean('BASE.TEMPLATES', 'Render.Snow')
		self.render_miracle = self.file.getboolean('BASE.TEMPLATES', 'Render.Miracle')
		self.render_basic = self.file.getboolean('BASE.TEMPLATES', 'Render.Basic')

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

		# Check if we're using a template ini file
		template_ini = template['config_path'].replace('json', 'ini').replace('Back', 'Front') if template else None
		template_json = template['config_path'].replace('Back', 'Front') if template else None
		if template_ini and os.path.exists(template_ini) and not self.dev_mode:
			conf = template_ini
		else:
			conf = con.path_config_ini_base

		# Validate ini file contents
		verify_config_fields(conf, con.path_config_json_base)
		verify_config_fields(con.path_config_ini_app, con.path_config_json_app)
		if template_ini and os.path.exists(template_ini) and not self.dev_mode:
			verify_config_fields(conf, template_json)

		# Load necessary files
		self.file = ConfigParser(allow_no_value=True)
		self.file.optionxform = str
		with open(conf, encoding="utf-8") as f:
			self.file.read_file(f)
		with open(con.path_config_ini_app, encoding="utf-8") as f:
			self.file.read_file(f)
		self.update_definitions()


# Global settings object
cfg = Config()
