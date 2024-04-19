"""
* CLI Commands: Build
"""
# Third party imports
import click

# Local Imports
from src.utils.build import generate_mkdocs, generate_nav, update_mkdocs_yml

"""
* Command Groups
"""


@click.group(
    name="docs",
    help="Command utilities for managing the app's documentation."
)
def docs_cli() -> None:
    """App docs tools CLI."""
    pass


"""
* Commands
"""


@docs_cli.command(
    name="update",
    help="Updates MKDocs files for the current app version."
)
def generate_docs() -> None:
    """Build the docs."""
    headers = ['Template Classes', 'Photoshop Helpers', 'App Utilities']
    paths = ['templates', 'helpers', 'utils']
    [generate_mkdocs(p) for p in paths]
    nav = generate_nav(headers, paths)
    update_mkdocs_yml(nav)


# Export CLI
__all__ = ['docs_cli']
