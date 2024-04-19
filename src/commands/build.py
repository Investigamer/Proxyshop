"""
* CLI Commands: Build
"""
# Standard Library
from typing import Optional

# Third party imports
import click

# Local Imports
from src.utils.build import build_release

"""
* Command Groups
"""


@click.group(
    name='build',
    help='Command utilities for building and managing release files.'
)
def build_cli() -> None:
    """App build tools CLI."""
    pass


"""
* Commands
"""


@build_cli.command(
    name='app',
    help='Build executable app release and distributable zip.'
)
@click.argument('version', required=False)
@click.option('-B', '--beta', is_flag=True, default=False, help="Build app as a Beta release.")
@click.option('-C', '--console', is_flag=True, default=False, help="Build app with console enabled.")
@click.option('-R', '--raw', is_flag=True, default=False, help="Build app without creating zip release archive.")
def build_app(version: Optional[str] = None, beta: bool = False, console: bool = False, raw: bool = False) -> None:
    """Build Proxyshop as an executable release.

    Args:
        version: Version number to build with, if not provided use latest.
        beta: Build as beta release if True.
        console: Build with console window if True.
        raw: Build app without creating zip if True.
    """
    build_release(version=version, beta=beta, console=console, zipped=not raw)


# Export CLI
__all__ = ['build_cli']
