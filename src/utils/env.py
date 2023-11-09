"""
* ENVIRONMENT VARIABLES
"""
# Standard Library
import sys
from os import environ
from typing import Optional

# Third Party Imports
from dotenv import dotenv_values

# Current app version
from src.__version__ import version as ENV_VERSION
from src.utils.decorators import auto_prop_cached
from src.utils.strings import str_to_bool

# Load environment variables
OS_ENV = dotenv_values('.env')

# Try to import private API keys
try:
    from src.__private__ import GOOGLE_KEY
    from src.__private__ import AMAZON_KEY
except ModuleNotFoundError:
    GOOGLE_KEY = None
    AMAZON_KEY = None


class Env:
    @auto_prop_cached
    def VERSION(self) -> str:
        return ENV_VERSION

    @auto_prop_cached
    def API_GOOGLE(self) -> str:
        return GOOGLE_KEY or environ.get('GOOGLE_KEY', OS_ENV.get('GOOGLE_KEY', ''))

    @auto_prop_cached
    def API_AMAZON(self) -> str:
        return AMAZON_KEY or environ.get('AMAZON_KEY', OS_ENV.get('AMAZON_KEY', ''))

    @auto_prop_cached
    def DEV_MODE(self) -> bool:
        if environ.get('ENV_DEV_MODE', None):
            return str_to_bool(environ['ENV_DEV_MODE'])
        return bool(not hasattr(sys, '_MEIPASS'))

    @auto_prop_cached
    def HEADLESS(self) -> bool:
        return str_to_bool(environ.get('HEADLESS', OS_ENV.get('HEADLESS', 'False')))

    @auto_prop_cached
    def PS_ERROR_DIALOG(self) -> bool:
        return str_to_bool(environ.get('PS_ERROR_DIALOG', OS_ENV.get('PS_ERROR_DIALOG', 'False')))

    @auto_prop_cached
    def PS_VERSION(self) -> Optional[str]:
        return environ.get('PS_VERSION', OS_ENV.get('PS_VERSION', None))


# App-wide environment object
ENV = Env()

# Export all
__all__ = ["ENV"]
