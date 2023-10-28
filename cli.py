"""
* Headless CLI Application
"""
# Standard Library Imports
from os import environ

# Third Party Imports
from click import CommandCollection
environ["HEADLESS"] = "True"

# Local Imports
from src.tests import test_cli
from src.utils.compression import compress_cli
from src.utils.build import build_cli

# Add supported commands
cli = CommandCollection(
    sources=[  # type: ignore
        test_cli,
        compress_cli,
        build_cli
    ])


if __name__ == '__main__':
    cli()
