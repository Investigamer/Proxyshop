"""
* Proxyshop GUI Launcher
"""
# Standard Library Imports
import os
import sys

# Third Party Imports
from kivy.resources import resource_add_path

# Local Imports
from src.gui._state import register_kv_classes, load_kv_files, load_kv_config
from src.gui.app import ProxyshopGUIApp


if __name__ == '__main__':
    """Launch GUI application."""

    # Kivy packaging for PyInstaller
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    # Load KV files
    load_kv_config()
    register_kv_classes()
    load_kv_files()
    ProxyshopGUIApp().run()
