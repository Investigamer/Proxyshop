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
		self.file.read(conf, encoding="utf-8")
		self.load()

	def load(self):
		"""
		Load the config values
		"""
		# Manual expansion symbol (Keyrune cheatsheet)
		self.symbol_char = self.file['CONF']['Expansion.Symbol']

		# Stop after formatting for manual intervention
		self.exit_early = self.file.getboolean('CONF', 'Manual.Edit')
		self.save_jpeg = self.file.getboolean('CONF', 'Render.JPEG')
		self.file_ext = self.file['CONF']['Photoshop.Ext']
		self.skip_failed = self.file.getboolean('CONF', 'Skip.Failed')
		self.save_artist_name = self.file.getboolean('CONF', 'Save.Artist.Name')

		# Auto symbol, sizing, and outline
		self.auto_symbol = self.file.getboolean('CONF', 'Auto.Set.Symbol')
		self.auto_symbol_size = self.file.getboolean('CONF', 'Auto.Symbol.Size')
		self.symbol_stroke = self.file['CONF']['Symbol.Stroke.Size']
		self.fill_symbol = self.file.getboolean('CONF', 'Fill.Symbol.Background')

		# Text options
		self.remove_flavor = self.file.getboolean('CONF', 'No.Flavor.Text')
		self.remove_reminder = self.file.getboolean('CONF', 'No.Reminder.Text')
		self.real_collector = self.file.getboolean('CONF', 'True.Collector.Info')

		# Chosen template or multiple templates (comma separated)
		self.template = self.file['CONF']['Template']

	def reload(self, conf=os.path.join(cwd, "config.ini")):
		"""
		Reload the config file and define new values
		"""
		del self.file
		self.file = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
		self.file.read(conf, encoding="utf-8")
		self.load()

cfg = Config()
