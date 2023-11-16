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
from src.utils.strings import str_to_bool_safe
from src.utils.api import get_api_key

# Load environment variables
OS_ENV = dotenv_values('.env')

# KIVY Environment
environ.setdefault('KIVY_LOG_MODE', 'PYTHON')
environ.setdefault('KIVY_NO_FILELOG', '1')
environ.setdefault('HEADLESS', '0')


class Env:
    @auto_prop_cached
    def VERSION(self) -> str:
        return ENV_VERSION

    @auto_prop_cached
    def API_GOOGLE(self) -> str:
        return environ.get('GOOGLE_KEY', OS_ENV.get('GOOGLE_KEY', get_api_key('proxyshop.google.drive')))

    @auto_prop_cached
    def API_AMAZON(self) -> str:
        return environ.get('AMAZON_KEY', OS_ENV.get('AMAZON_KEY', get_api_key('proxyshop.amazon.s3')))

    @auto_prop_cached
    def DEV_MODE(self) -> bool:
        if environ.get('ENV_DEV_MODE'):
            return str_to_bool_safe(environ['ENV_DEV_MODE'])
        return bool(not hasattr(sys, '_MEIPASS'))

    @auto_prop_cached
    def HEADLESS(self) -> bool:
        return str_to_bool_safe(environ.get('HEADLESS', OS_ENV.get('HEADLESS', '0')))

    @auto_prop_cached
    def PS_ERROR_DIALOG(self) -> bool:
        return str_to_bool_safe(environ.get('PS_ERROR_DIALOG', OS_ENV.get('PS_ERROR_DIALOG', '0')))

    @auto_prop_cached
    def PS_VERSION(self) -> Optional[str]:
        return environ.get('PS_VERSION', OS_ENV.get('PS_VERSION', None))


# App-wide environment object
ENV = Env()

# Export all
__all__ = ["ENV"]
