"""
Process config file into global settings.
"""
# pylint: disable=R0902
import configparser
import os
cwd = os.getcwd()


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

	def __init__(self, conf=os.path.join(cwd, "config.ini")):
		self.reload(conf)

	def load(self):
		"""
		Load the config values
		"""
		# CONF section
		self.exit_early = self.file.getboolean('CONF', 'Manual.Edit')
		self.skip_failed = self.file.getboolean('CONF', 'Skip.Failed')
		self.scry_ascending = self.file.getboolean('CONF', 'Scryfall.Ascending')

		# FILE section
		self.output_filetype = self.file['FILES']['Output.Filetype']
		self.save_artist_name = self.file.getboolean('FILES', 'Save.Artist.Name')

		# TEXT section
		self.remove_flavor = self.file.getboolean('TEXT', 'No.Flavor.Text')
		self.remove_reminder = self.file.getboolean('TEXT', 'No.Reminder.Text')
		self.real_collector = self.file.getboolean('TEXT', 'True.Collector.Info')
		self.lang = self.file['TEXT']['Language']
		self.force_english_formatting = self.file.getboolean('TEXT', "Force.English.Formatting")

		# SYMBOLS section
		self.symbol_char = self.file['SYMBOLS']['Default.Symbol']
		self.auto_symbol = self.file.getboolean('SYMBOLS', 'Auto.Set.Symbol')
		self.auto_symbol_size = self.file.getboolean('SYMBOLS', 'Auto.Symbol.Size')
		self.symbol_stroke = self.file['SYMBOLS']['Symbol.Stroke.Size']
		self.fill_symbol = self.file.getboolean('SYMBOLS', 'Fill.Symbol.Background')

		# EXPERIMENTAL section
		self.targeted_replace = self.file.getboolean('EXPERIMENTAL', 'Targeted.Replace')
		self.flavor_divider = self.file.getboolean('EXPERIMENTAL', 'Flavor.Divider')
		self.dev_mode = self.file.getboolean('EXPERIMENTAL', 'Dev.Mode')

	def update(self):
		self.file.set("SYMBOLS", "Auto.Set.Symbol", str(self.auto_symbol))
		self.file.set("SYMBOLS", "Auto.Symbol.Size", str(self.auto_symbol_size))
		self.file.set("EXPERIMENTAL", "Flavor.Divider", str(self.flavor_divider))
		self.file.set("FILES", "Output.Filetype", str(self.output_filetype))
		self.file.set("TEXT", "No.Flavor.Text", str(self.remove_flavor))
		self.file.set("TEXT", "No.Reminder.Text", str(self.remove_reminder))
		self.file.set("CONF", "Manual.Edit", str(self.exit_early))
		self.file.set("CONF", "Skip.Failed", str(self.skip_failed))
		self.file.set("CONF", "Scryfall.Ascending", str(self.scry_ascending))
		with open("config.ini", "w", encoding="utf-8") as config_file:
			self.file.write(config_file)

	def update_setting(self, state, setting):
		if state == "down": setattr(self, setting, True)
		else: setattr(self, setting, False)

	def reload(self, conf=os.path.join(cwd, "config.ini")):
		"""
		Reload the config file and define new values
		"""
		if hasattr(self, 'file'): del self.file
		self.file = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
		self.file.optionxform = str
		with open(conf, encoding="utf-8") as file:
			self.file.read_file(file)
		self.load()

# Global settings object
cfg = Config()
