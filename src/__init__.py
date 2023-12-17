"""
* Load Global Application State
"""
# Local Imports
from .console import TerminalConsole
from ._loader import get_all_plugins, get_all_templates, get_template_map, get_template_map_defaults
from ._state import AppConstants, AppEnvironment, PATH
from src.utils.adobe import PhotoshopHandler
from settings import AppConfig

"""
* Globally Loaded Objects
"""

# Global environment object
ENV = AppEnvironment()

# Global constants object
CON = AppConstants()

# Global settings object
CFG = AppConfig(env=ENV)

# Global Photoshop handler
APP = PhotoshopHandler(env=ENV)

# Conditionally import the GUI console
if not ENV.HEADLESS:
    from src.gui.console import GUIConsole as Console
else:
    Console = TerminalConsole
CONSOLE = Console(cfg=CFG, env=ENV)

# Global plugins and templates
PLUGINS = get_all_plugins(CON)
TEMPLATES = get_all_templates(CON, PLUGINS)
TEMPLATE_MAP = get_template_map(TEMPLATES)
TEMPLATE_DEFAULTS = get_template_map_defaults(TEMPLATE_MAP)

# Export objects
__all__ = ['APP', 'CFG', 'CON', 'CONSOLE', 'ENV', 'PATH']
