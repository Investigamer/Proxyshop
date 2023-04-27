"""
DEVELOPMENT ENVIRONMENT FLAG
"""
import sys
from os import environ

# Disable development flag if building executable release
development = True if not hasattr(sys, '_MEIPASS') else False

# Disable Kivy output outside development environment
if not development:
    environ["KIVY_NO_CONSOLELOG"] = "1"
