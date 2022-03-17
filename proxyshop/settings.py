"""
Process config file into global settings.
"""
import configparser

# Import our config file
cfg = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
cfg.read("config.ini", encoding="utf-8")

# Manual expanson symbol (Keyrune cheatsheet)
symbol_char = cfg['CONF']['Expansion.Symbol']

# Stop after formatting for manual intervention
exit_early = cfg.getboolean('CONF','Manual.Edit')
save_jpeg = cfg.getboolean('CONF','Render.JPEG')
file_ext = cfg['CONF']['Photoshop.Ext']

# Auto symbol, sizing, and outline
auto_symbol = cfg.getboolean('CONF','Auto.Set.Symbol')
auto_symbol_size = cfg.getboolean('CONF','Auto.Symbol.Size')
symbol_stroke = cfg['CONF']['Symbol.Stroke.Size']

# Text options
remove_flavor = cfg.getboolean('CONF','No.Flavor.Text')
remove_reminder = cfg.getboolean('CONF','No.Reminder.Text')
real_collector = cfg.getboolean('CONF','True.Collector.Info')

# Chosen template or multiple templates (comma separated)
template = cfg['CONF']['Template']
