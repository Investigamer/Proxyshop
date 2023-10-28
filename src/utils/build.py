"""
* APP BUILD SCRIPT
"""
# Standard Library
import os
from os import path as osp
import zipfile
from contextlib import suppress
from glob import glob
from pathlib import Path
from typing import Any, Optional
from shutil import (
    copy2,
    copytree,
    rmtree,
    move
)

# Third party imports
import PyInstaller.__main__
import click
import tomli

# Local Imports
from src.constants import con
from src.utils.env import ENV

# Directory definitions
SRC = con.cwd
DST = osp.join(SRC, 'dist')


"""
HANDLING APP FILES
"""


def make_directories(config: dict[str, Any]) -> None:
    """
    Make sure necessary directories exist.
    @param config: TOML config data.
    """
    Path(osp.join(SRC, 'dist')).mkdir(mode=711, parents=True, exist_ok=True)
    for path in config['make']['paths']:
        Path(osp.join(DST, path)).mkdir(mode=711, parents=True, exist_ok=True)


def copy_directory(
        src: str, dst: str,
        x_files: list[str],
        x_dirs: list[str],
        x_ext: Optional[list[str]] = None,
        recursive: bool = True
) -> None:
    """
    Copy a directory from src to dst.
    @param src: Source directory to copy this directory from.
    @param dst: Destination directory to copy this directory to.
    @param x_files: Excluded file names.
    @param x_dirs: Excluded directory names.
    @param x_ext: Excluded extensions.
    @param recursive: Will exclude all subdirectories if False.
    """
    # Set empty lists for None value
    x_files = x_files or []
    x_dirs = x_dirs or []
    x_ext = x_ext or []

    def _ignore(path: str, names: list[str]):
        """
        Return a list of files to ignore based on our exclusion criteria.
        @param path: Path to these files.
        @names: Names of these files.
        """
        ignored: list[str] = []
        for name in names:
            # Ignore certain names and extensions
            if name in x_files or osp.splitext(name)[1] in x_ext:
                ignored.append(name)
            # Ignore certain directories
            elif (name in x_dirs or not recursive) and osp.isdir(osp.join(path, name)):
                ignored.append(name)
        return set(ignored)

    # Copy the directory
    copytree(src, dst, ignore=_ignore)


def copy_app_files(config: dict[str, Any]) -> None:
    """
    Copy necessary app files and directories.
    @param config: TOML config data.
    """
    for _, DIR in config.get('copy', {}).items():
        # Copy directories
        for path in DIR.get('paths', []):
            copy_directory(
                src=osp.join(SRC, path),
                dst=osp.join(DST, path),
                x_files=DIR.get('exclude_files', []),
                x_dirs=DIR.get('exclude_dirs', []),
                x_ext=DIR.get('exclude_ext', []),
                recursive=bool(DIR.get('recursive', True)))
        # Copy files
        for file in DIR.get('files', []):
            copy2(
                src=osp.join(SRC, file),
                dst=osp.join(DST, file))


"""
CLEANING BUILD FILES
"""


def clear_build_files(clear_dist: bool = True) -> None:
    """
    Clean out __pycache__ and venv cache, remove previous build files.
    @param clear_dist: Remove previous dist directory if True, otherwise skip.
    """
    # Run pyclean on main directory and venv
    os.system("pyclean -v .")
    if osp.exists(osp.join(SRC, '.venv')):
        os.system("pyclean -v .venv")

    # Remove build directory
    with suppress(Exception):
        rmtree(osp.join(SRC, 'build'))

    # Optionally remove dist directory
    if clear_dist:
        with suppress(Exception):
            rmtree(osp.join(SRC, 'dist'))


"""
BUILDING APP
"""


def build_zip(filename: str) -> None:
    """
    Create a zip of this release.
    @filename: Filename to use on zip archive.
    """
    ZIP_SRC = osp.join(SRC, filename)
    with zipfile.ZipFile(ZIP_SRC, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fp in glob(osp.join(DST, "**/*"), recursive=True):
            zipf.write(fp, arcname=fp.replace(
                osp.commonpath([DST, fp]), ""))
    move(ZIP_SRC, osp.join(DST, filename))


def build_app(
    version: Optional[str] = None,
    console: bool = False,
    beta: bool = False,
    zipped: bool = True
) -> None:
    """
    Build the app to executable release.
    @param version: Version to use in zip name and GUI display.
    @param console: Whether to enable console window when app is launched.
    @param beta: Whether this is a beta release.
    @param zipped: Whether to create a zip of this release.
    """
    # Load toml config
    with open(osp.join(con.path_data, 'build/dist.toml'), 'rb') as f:
        toml_config = tomli.load(f)

    # Pre-build steps
    clear_build_files()
    make_directories(config=toml_config)

    # Run pyinstaller
    PyInstaller.__main__.run([toml_config['spec']['console' if console else 'release'], '--clean'])

    # Copy our essential app files
    with suppress(Exception):
        copy_app_files(toml_config)

    # Build zip release if requested
    if zipped:
        build_zip(
            filename=toml_config['names']['zip'].format(
                version=version or ENV.VERSION,
                console='-console' if console else '',
                beta='-beta' if beta else ''
            ))

    # Clear build files, except dist
    clear_build_files(clear_dist=False)


"""
COMMANDS
"""


@click.group()
def build_cli():
    """App build tools CLI."""
    pass


@build_cli.command()
@click.argument('version', required=False)
@click.option('-B', '--beta', is_flag=True, default=False, help="Build app as a Beta release.")
@click.option('-C', '--console', is_flag=True, default=False, help="Build app with console enabled.")
@click.option('-R', '--raw', is_flag=True, default=False, help="Build app without creating ZIP.")
def build_app(version: Optional[str] = None, beta: bool = False, console: bool = False, raw: bool = False):
    """Build Proxyshop as an executable release."""
    build_app(version=version, beta=beta, console=console, zipped=not raw)


# Export CLI
__all__ = ['build_cli']
