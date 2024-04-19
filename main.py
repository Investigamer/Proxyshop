"""
* Proxyshop Application Launcher
"""
# Standard Library Imports
import os
import sys

"""
* Launcher Funcs
"""


def launch_cli():
    """Launch the app in CLI mode."""

    # Enable headless mode, remove cli marker
    os.environ['HEADLESS'] = '1'
    if 'cli' in sys.argv:
        sys.argv.remove('cli')

    # Local Imports
    from src.commands import ProxyshopCLI

    # Run the CLI application
    ProxyshopCLI.main()


def launch_gui():
    """Launch the app in GUI mode."""

    # Local Imports
    from src import (
        APP, CFG, CON, CONSOLE, ENV,
        PLUGINS, TEMPLATES, TEMPLATE_MAP, TEMPLATE_DEFAULTS)
    from src.gui._state import register_kv_classes, load_kv_config
    from src.gui.app import ProxyshopGUIApp

    # Kivy Imported Last
    from kivy.resources import resource_add_path

    # Kivy packaging for PyInstaller
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    # Load KV files and utilities
    load_kv_config()
    register_kv_classes()

    # Run the GUI application
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


if __name__ == '__main__':
    """Route to a qualified launcher."""
    if 'cli' in sys.argv:
        sys.exit(launch_cli())
    launch_gui()
