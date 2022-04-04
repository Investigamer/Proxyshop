"""
Process config file into global settings.
"""
# pylint: disable=R0902
import configparser
import os
cwd = os.getcwd()

class config():
	"""
	Build our config info
	"""
	def __init__(self, conf=os.path.join(cwd, "config.ini")):
		self.conf = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
		self.conf.read(conf, encoding="utf-8")
		self.load()

	def load(self):
		"""
		Load the config values
		"""
		# Manual expanson symbol (Keyrune cheatsheet)
		self.symbol_char = self.conf['CONF']['Expansion.Symbol']

		# Stop after formatting for manual intervention
		self.exit_early = self.conf.getboolean('CONF','Manual.Edit')
		self.save_jpeg = self.conf.getboolean('CONF','Render.JPEG')
		self.file_ext = self.conf['CONF']['Photoshop.Ext']

		# Auto symbol, sizing, and outline
		self.auto_symbol = self.conf.getboolean('CONF','Auto.Set.Symbol')
		self.auto_symbol_size = self.conf.getboolean('CONF','Auto.Symbol.Size')
		self.symbol_stroke = self.conf['CONF']['Symbol.Stroke.Size']
		self.fill_symbol = self.conf.getboolean('CONF','Fill.Symbol.Background')

		# Text options
		self.remove_flavor = self.conf.getboolean('CONF','No.Flavor.Text')
		self.remove_reminder = self.conf.getboolean('CONF','No.Reminder.Text')
		self.real_collector = self.conf.getboolean('CONF','True.Collector.Info')

		# Chosen template or multiple templates (comma separated)
		self.template = self.conf['CONF']['Template']

	def reload(self, conf=os.path.join(cwd, "config.ini")):
		"""
		Reload the config file and define new values
		"""
		del self.conf
		self.conf = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
		self.conf.read(conf, encoding="utf-8")
		self.load()
