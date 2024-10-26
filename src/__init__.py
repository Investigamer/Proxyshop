"""
* Load Global Application State
"""
# Standard Library Imports
import sys

# Third Party Imports
from dynaconf import Validator
from omnitils.files import get_project_version

# Local Imports
from .console import TerminalConsole
from ._config import AppConfig
from ._loader import get_all_plugins, get_all_templates, get_template_map, get_template_map_defaults
from ._state import AppConstants, AppEnvironment, PATH
from src.utils.adobe import PhotoshopHandler

"""
* Globally Loaded Objects
"""

# Global environment object (dynaconf)
ENV = AppEnvironment(
    envvar_prefix='PROXYSHOP',
    settings_files=[PATH.SRC_DATA_ENV, PATH.SRC_DATA_ENV_DEFAULT],
    validators=[
        Validator('API_GOOGLE', cast=str, default=''),
        Validator('API_AMAZON', cast=str, default=''),
        Validator('PS_ERROR_DIALOG', cast=bool, default=False),
        Validator('PS_VERSION', cast=AppEnvironment.string_or_none, default=None),
        Validator('HEADLESS', cast=bool, default=False),
        Validator('DEV_MODE', cast=bool, default=bool(not hasattr(sys, '_MEIPASS'))),
        Validator('TEST_MODE', cast=bool, default=False),
        Validator('VERSION', cast=str, default=get_project_version(PATH.PROJECT_FILE)),
        Validator('FORCE_RELOAD', cast=bool, default=False)
    ],
    apply_default_on_none=True
)

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
PLUGINS = get_all_plugins(con=CON, env=ENV)
TEMPLATES = get_all_templates(con=CON, env=ENV, plugins=PLUGINS)
TEMPLATE_MAP = get_template_map(templates=TEMPLATES)
TEMPLATE_DEFAULTS = get_template_map_defaults(TEMPLATE_MAP)

# Export objects
__all__ = ['APP', 'CFG', 'CON', 'CONSOLE', 'ENV', 'PATH']
