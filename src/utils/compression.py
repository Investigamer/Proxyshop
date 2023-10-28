# Standard Library
import os
import logging
import subprocess
from glob import glob
from os import path as osp, makedirs
from time import perf_counter
from typing import Optional

# Third Party Imports
from tqdm import tqdm
import py7zr
import click

# Local Imports
from src.constants import con
from src.utils.strings import StrEnum
from src.utils.files import get_file_size_mb


class WordSize(StrEnum):
    """Word Size for 7z compression."""
    WS16 = "16"
    WS24 = "24"
    WS32 = "32"
    WS48 = "48"
    WS64 = "64"
    WS96 = "96"
    WS128 = "128"


class DictionarySize(StrEnum):
    """Dictionary Size for 7z compression."""
    DS32 = "32"
    DS48 = "48"
    DS64 = "64"
    DS96 = "96"
    DS128 = "128"
    DS192 = "192"
    DS256 = "256"
    DS384 = "384"
    DS512 = "512"
    DS768 = "768"
    DS1024 = "1024"
    DS1536 = "1536"


"""
UTILITY FUNCS
"""


def compress_file(file_path: str, output_dir: str) -> bool:
    """
    Compress a target file and save it as a 7z archive to the output directory.
    @param file_path: File to compress.
    @param output_dir: Directory to save archive to.
    @return: True if compression succeeded, otherwise False.
    """
    # Define the output file path
    filename = osp.basename(file_path).replace('.psd', '.7z')
    out_file = osp.join(output_dir, filename)
    null_device = open(os.devnull, 'w')

    # Compress the file
    try:
        subprocess.run([
                "7z", "a", "-t7z", "-m0=LZMA", "-mx=9",
                f"-md={DictionarySize.DS96}M",
                f"-mfb={WordSize.WS24}",
                out_file, file_path
            ], stdout=null_device, stderr=null_device)
    except Exception as e:
        logging.error("An error occurred compressing file!", exc_info=e)
        return False
    return True


def compress_template(
    file_name: str,
    plugin: Optional[str] = None,
    word_size: WordSize = WordSize.WS16,
    dict_size: DictionarySize = DictionarySize.DS1536
):
    """
    Compress a given template from an optional given plugin.
    @param file_name: Template PSD/PSB file name.
    @param plugin: Plugin containing the template, assume a base template if not provided.
    @param word_size: Word size value to use for the compression.
    @param dict_size: Dictionary size value to use for the compression.
    @return:
    """
    # Build the template path
    from_dir = osp.join(con.cwd, f'plugins\\{plugin}\\templates' if plugin else 'templates')
    to_dir = osp.join(con.cwd, f'plugins\\{plugin}\\templates\\compressed' if plugin else 'templates\\compressed')
    from_file = osp.join(from_dir, file_name)
    to_file = osp.join(to_dir, file_name.replace('.psd', '.7z').replace('.psb', '.7z'))
    null_device = open(os.devnull, 'w')

    # Compress the file
    s = perf_counter()
    try:
        subprocess.run(
            ["7z", "a", "-t7z", "-m0=LZMA", "-mx=9", f"-md={dict_size}M", f"-mfb={word_size}", to_file, from_file],
            stdout=null_device, stderr=null_device)
    except Exception as e:
        logging.error("An error occurred compressing file!", exc_info=e)
    return get_file_size_mb(to_file), perf_counter()-s


def compress_plugin(plugin: str) -> None:
    """
    Compress all PSD files in a plugin.
    @param plugin: Name of the plugin folder.
    """
    compress_all(directory=osp.join(con.path_plugins, f"{plugin}\\templates"))


def compress_all(directory: Optional[str] = None) -> None:
    """
    Compress all PSD files in a directory.
    @param directory: Directory containing PSD files to compress.
    """
    # Create "compressed" subdirectory if it doesn't exist
    directory = directory or con.path_templates
    output_dir = osp.join(directory, 'compressed')
    makedirs(output_dir, exist_ok=True)

    # Get a list of all .psd files in the directory
    files = glob(osp.join(directory, '*.psd'))

    # Compress each file
    with tqdm(total=len(files), desc="Compressing files", unit="file") as pbar:
        for f in files:
            pbar.set_description(osp.basename(f))
            compress_file(f, output_dir)
            pbar.update()


def compress_all_templates():
    """Compress all app templates."""
    # Compress base templates
    compress_all(con.path_templates)

    # Compress plugin templates
    _ = [compress_plugin(p) for p in ['MrTeferi', 'SilvanMTG']]


"""
ARCHIVE DECOMPRESSION
"""


def decompress_file(file_path: str) -> None:
    """
    Decompress target 7z archive.
    @param file_path: Path to the 7z archive.
    """
    with py7zr.SevenZipFile(file_path, 'r') as archive:
        archive.extractall(path=osp.dirname(file_path))
    os.remove(file_path)


"""
CLI COMMANDS
"""


@click.group()
def compress_cli():
    """File utilities CLI."""
    pass


@click.command()
@click.argument('template')
@click.argument('plugin', required=False)
def compress_template(template: str, plugin: Optional[str] = None) -> None:
    compress_template(
        file_name=template,
        plugin=plugin)


@click.command()
@click.argument('plugin')
def compress_plugin(plugin: str) -> None:
    compress_plugin(plugin=plugin)


@click.command()
def compress_all() -> None:
    compress_all()


# Export CLI
__all__ = ['compress_cli']
