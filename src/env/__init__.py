"""
ENVIRONMENT MODULE
"""

# Current app version
from src.env.__version__ import version

# Development environment flag
try:
    from src.env.__dev__ import development
except ModuleNotFoundError:
    development = False

# Protected environment variables
try:
    from src.env.__private__ import google_key
    from src.env.__private__ import amazon_key
except ModuleNotFoundError:
    google_key = ""
    amazon_key = ""

# Establish ENV variables
ENV_API_GOOGLE = google_key
ENV_API_AMAZON = amazon_key
ENV_DEV_MODE = development
ENV_VERSION = version

__all__ = ["ENV_API_GOOGLE", "ENV_API_AMAZON", "ENV_DEV_MODE", "ENV_VERSION"]
