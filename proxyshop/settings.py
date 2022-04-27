"""
Process config file into global settings.
"""
# pylint: disable=R0902
import configparser
import os
cwd = os.getcwd()


class Config:
	"""
	Build our config info
	"""
	def __init__(self, conf=os.path.join(cwd, "config.ini")):
		self.symbol_char = None
		self.exit_early = None
		self.save_jpeg = None
		self.file_ext = None
		self.skip_failed = None
		self.auto_symbol = None
		self.auto_symbol_size = None
		self.symbol_stroke = None
		self.fill_symbol = None
		self.remove_flavor = None
		self.remove_reminder = None
		self.real_collector = None
		self.template = None
		self.save_artist_name = None
		self.file = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
		self.file.optionxform = str
		self.file.read(conf, encoding="utf-8")
		self.load()

	def load(self):
		"""
		Load the config values
		"""
		# CONF section
		self.exit_early = self.file.getboolean('CONF', 'Manual.Edit')
		self.skip_failed = self.file.getboolean('CONF', 'Skip.Failed')

		# FILE section
		self.save_jpeg = self.file.getboolean('FILES', 'Render.JPEG')
		self.file_ext = self.file['FILES']['Photoshop.Ext']
		self.save_artist_name = self.file.getboolean('FILES', 'Save.Artist.Name')

		# TEXT section
		self.remove_flavor = self.file.getboolean('TEXT', 'No.Flavor.Text')
		self.remove_reminder = self.file.getboolean('TEXT', 'No.Reminder.Text')
		self.real_collector = self.file.getboolean('TEXT', 'True.Collector.Info')

		# SYMBOLS section
		self.symbol_char = self.file['SYMBOLS']['Default.Symbol']
		self.auto_symbol = self.file.getboolean('SYMBOLS', 'Auto.Set.Symbol')
		self.auto_symbol_size = self.file.getboolean('SYMBOLS', 'Auto.Symbol.Size')
		self.symbol_stroke = self.file['SYMBOLS']['Symbol.Stroke.Size']
		self.fill_symbol = self.file.getboolean('SYMBOLS', 'Fill.Symbol.Background')

	def update(self, c):
		self.file.set("SYMBOLS", "Auto.Set.Symbol", str(c['auto_set_symbol']))
		self.file.set("SYMBOLS", "Auto.Symbol.Size", str(c['auto_symbol_size']))
		self.file.set("SYMBOLS", "Fill.Symbol.Background", str(c['fill_symbol']))
		self.file.set("FILES", "Render.JPEG", str(c['save_JPEG']))
		self.file.set("TEXT", "No.Flavor.Text", str(c['no_flavor']))
		self.file.set("TEXT", "No.Reminder.Text", str(c['no_reminder']))
		self.file.set("CONF", "Manual.Edit", str(c['manual_edit']))
		self.file.set("CONF", "Skip.Failed", str(c['skip_failed']))
		with open("config.ini", "w", encoding="utf-8") as config_file:
			self.file.write(config_file)

	def reload(self, conf=os.path.join(cwd, "config.ini")):
		"""
		Reload the config file and define new values
		"""
		del self.file
		self.file = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
		self.file.optionxform = str
		self.file.read(conf, encoding="utf-8")
		self.load()

cfg = Config()
