"""
* Proxyshop GUI Launcher
"""
# Standard Library Imports
import os
import sys
from pprint import pprint
from traceback import format_exception

# Local Imports
from src import (
    APP, CFG, CON, CONSOLE, ENV,
    PLUGINS, TEMPLATES, TEMPLATE_MAP, TEMPLATE_DEFAULTS
)
from src.gui._state import register_kv_classes, load_kv_config
from src.gui.app import ProxyshopGUIApp

# Kivy Imported Last
from kivy.resources import resource_add_path


if __name__ == '__main__':
    """Launch GUI application."""

    # Kivy packaging for PyInstaller
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    # Load KV files
    load_kv_config()
    register_kv_classes()
    try:
        ProxyshopGUIApp(
            app=APP,
            con=CON,
            cfg=CFG,
            env=ENV,
            console=CONSOLE,
            plugins=PLUGINS,
            templates=TEMPLATES,
            template_map=TEMPLATE_MAP,
            templates_default=TEMPLATE_DEFAULTS,
        ).run()
    except Exception as e:
        pprint(format_exception(e))
