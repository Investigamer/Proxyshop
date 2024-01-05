"""
* Headless CLI Application
"""
# Standard Library Imports
from os import environ

# Third Party Imports
from click import CommandCollection
environ["HEADLESS"] = "True"

# Local Imports
from src.commands.build import build_cli
from src.commands.files import compress_cli
from src.commands.render import render_cli
from src.commands.test import test_cli

"""
* CLI Application
"""

# Add supported commands
ProxyshopCLI = CommandCollection(
    sources=[  # type: ignore
        test_cli,
        compress_cli,
        build_cli,
        render_cli
    ])

# Export CLI
__all__ = ['ProxyshopCLI']
