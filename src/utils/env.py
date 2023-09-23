"""
* ENVIRONMENT VARIABLES
"""
# Standard Library
import sys
from os import environ
from distutils.util import strtobool
from typing import Optional

# Third Party Imports
from dotenv import dotenv_values

# Current app version
from src.__version__ import version as ENV_VERSION

# Load environment variables
ENV = dotenv_values('.env')

# Disable development flag if building executable release
ENV_DEV_MODE: bool = True if not hasattr(sys, '_MEIPASS') else False

# Try to import private API keys
try:
    from src.__private__ import GOOGLE_KEY
    from src.__private__ import AMAZON_KEY
except ModuleNotFoundError:
    GOOGLE_KEY = None
    AMAZON_KEY = None

# Load OS environment or .env variables
ENV_API_GOOGLE: str = GOOGLE_KEY or environ.get('GOOGLE_KEY', ENV.get('GOOGLE_KEY', ''))
ENV_API_AMAZON: str = AMAZON_KEY or environ.get('AMAZON_KEY', ENV.get('AMAZON_KEY', ''))
ENV_HEADLESS: bool = bool(strtobool(environ.get('HEADLESS', ENV.get('HEADLESS', 'False'))))
PS_VERSION: Optional[str] = environ.get('PS_VERSION', ENV.get('PS_VERSION', None))
PS_VERSION = str(PS_VERSION) if PS_VERSION else None

# Export all
__all__ = ["ENV_VERSION", "ENV_API_GOOGLE", "ENV_API_AMAZON", "ENV_DEV_MODE", "ENV_HEADLESS", "PS_VERSION"]
