"""
* CLI Commands: Files
"""
# Standard Library
from pathlib import Path
from typing import Optional

# Third Party Imports
import click

# Local Imports
from src import PATH
from src.utils.compression import compress_7z, compress_7z_all

"""
* Commands: Compression
"""


@click.group(
    name='compress',
    help='Command utilities for compressing files.'
)
def compress_cli():
    """File utilities CLI."""
    pass


@compress_cli.command(
    name='template',
    help='Compress a Photoshop template file (PSD/PSB).'
)
@click.argument('template')
@click.argument('plugin', required=False)
def compress_template(template: str, plugin: Optional[str] = None) -> None:
    """Compress a template by name and optionally plugin name.

    Args:
        template: Filename of the template, e.g. `normal.psd`
        plugin: Name of the plugin containing the template if required, e.g. MrTeferi
    """
    path = Path(PATH.PLUGINS, plugin, 'templates') if plugin else PATH.TEMPLATES
    path = path / template
    if not path.is_file():
        print(f"I couldn't find a template named '{template}' at this path:\n{str(path)}")
        return
    compress_7z(path)


@compress_cli.command(
    name='plugin',
    help='Compress all Photoshop template files (PSD/PSB) in a given plugin.'
)
@click.argument('plugin')
def compress_plugin(plugin: str) -> None:
    """Compress all templates in a specific plugin.

    Args:
        plugin: Name of the plugin, e.g. MrTeferi
    """
    path = PATH.PLUGINS / plugin / 'templates'
    if not path.is_dir():
        print(f"I couldn't find a plugin named '{plugin}'")
        return
    compress_7z_all(path)


@compress_cli.command(
    name='all',
    help='Compress all Photoshop template files (PSD/PSB) in the entire app, plugins optional.'
)
@click.option('-P', '--plugins', is_flag=True, default=False, help="Compress built-in plugins as well.")
def compress_all(plugins: bool = False) -> None:
    """Compress all templates.

    Args:
        plugins: Compress built-in plugins as well if True, otherwise skip them.
    """
    # Compress main templates folder
    compress_7z_all(PATH.TEMPLATES)

    # Compress plugins if requested
    if plugins:
        plugins = [
            Path(PATH.PLUGINS, p, 'templates')
            for p in ['Investigamer', 'SilvanMTG']]
        [compress_7z_all(p) for p in plugins]


# Export CLI
__all__ = ['compress_cli']
