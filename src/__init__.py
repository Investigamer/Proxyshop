"""
* Load Global Application State
"""

from src._config import AppConfig
from src._state import AppConstants, AppEnvironment
from src.utils.adobe import PhotoshopHandler
from src.utils.threading import ThreadInitializedInstance

# Global environment object
ENV = AppEnvironment()

DEFAULT_HEADERS = {"User-Agent": f"Proxyshop/{ENV.VERSION}"}

# Global constants object
CON = AppConstants()

# Global settings object
CFG = AppConfig()

# Global Photoshop handler
APP = ThreadInitializedInstance(lambda: PhotoshopHandler(env=ENV))

# Export objects
__all__ = ["APP", "CFG", "CON", "ENV"]
