"""
* Utils: Compressing and Decompressing Archives
"""
# Standard Library
from contextlib import suppress
import gzip
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from threading import Lock
from typing import Optional, Callable
import zipfile

# Third Party Imports
from tqdm import tqdm
import py7zr

# Local Imports
from src.utils.strings import StrEnum

# Locking mechanism
ARCHIVE_LOCK = Lock()

"""
* Enums
"""


class ArchiveExt(StrEnum):
    """Recognized archive extensions."""
    Zip = '.zip'
    GZip = '.gz'
    XZip = '.xz'
    SevenZip = '.7z'
    TarZip = '.tar.zip'
    TarGZip = '.tar.gz'
    TarXZip = '.tar.xz'
    TarSevenZip = '.tar.xz'


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
* Compression Utils
"""


def compress_7z(
    path_in: Path,
    path_out: Optional[Path] = None,
    word_size: WordSize = WordSize.WS16,
    dict_size: DictionarySize = DictionarySize.DS1536
) -> Path:
    """Compress a target file and save it as a 7z archive to the output directory.

    Args:
        path_in: File to compress.
        path_out: Path to the archive to be saved. Use 'compressed' subdirectory if not provided.
        word_size: Word size value to use for the compression.
        dict_size: Dictionary size value to use for the compression.
    """
    # Define the output file path
    path_out = path_out or Path(path_in.parent, 'compressed', path_in.name)
    path_out = path_out.with_suffix('.7z')
    null_device = open(os.devnull, 'w')

    # Compress the file
    with suppress(Exception):
        subprocess.run([
            "7z", "a", "-t7z", "-m0=LZMA", "-mx=9",
            f"-md={dict_size}M",
            f"-mfb={word_size}",
            str(path_out),
            str(path_in)
        ], stdout=null_device, stderr=null_device)
    return path_out


def compress_7z_all(
    path_in: Path,
    path_out: Path = None,
    word_size: WordSize = WordSize.WS16,
    dict_size: DictionarySize = DictionarySize.DS1536
) -> None:
    """Compress every file inside `path_in` directory as 7z archives, then output
    those archives in the `path_out`.

    Args:
        path_in: Directory containing files to compress.
        path_out: Directory to place the archives. Use a subdirectory 'compressed' if not provided.
        word_size: Word size value to use for the compression.
        dict_size: Dictionary size value to use for the compression.
    """
    # Use "compressed" subdirectory if not provided, ensure output directory exists
    path_out = path_out or Path(path_out, 'compressed')
    path_out.mkdir(mode=777, parents=True, exist_ok=True)

    # Get a list of all .psd files in the directory
    files = [
        Path(path_in, n) for n in os.listdir(path_in)
        if Path(path_in, n).is_file()]

    # Compress each file
    with tqdm(total=len(files), desc="Compressing files", unit="file") as pbar:
        for f in files:
            p = (path_out / f.name).with_suffix('.7z')
            pbar.set_description(f.name)
            compress_7z(
                path_in=f,
                path_out=p,
                word_size=word_size,
                dict_size=dict_size)
            pbar.update()


"""
* Decompression Utils
"""


def unpack_zip(path: Path) -> None:
    """Unpack target 'zip' archive.

    Args:
        path: Path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(path=path.parent)


def unpack_gz(path: Path) -> None:
    """Unpack target 'gz' archive.

    Args:
        path: Path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    output = path.parent / path.name.replace('.gz', '')
    with gzip.open(path, 'rb') as arch:
        with open(output, 'wb') as f:
            shutil.copyfileobj(arch, f)


def unpack_xz(path: Path) -> None:
    """Unpack target 'xz' archive.

    Args:
        path: Path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    output = path.parent / path.name.replace('.xz', '')
    with lzma.open(path, mode='r') as arch:
        with open(output, 'wb') as f:
            shutil.copyfileobj(arch, f)


def unpack_7z(path: Path) -> None:
    """Unpack target '7z' archive.

    Args:
        path: path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with py7zr.SevenZipFile(path, 'r') as arch:
        arch.extractall(path=path.parent)


def unpack_tar_zip(path: Path) -> None:
    """Unpack target `tar.gz` archive.

    Args:
        path: Path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(path=path)
    with tarfile.open(path.with_suffix('.tar'), 'r') as tar:
        tar.extractall(path=path.parent)


def unpack_tar_gz(path: Path) -> None:
    """Unpack target `tar.gz` archive.

    Args:
        path: Path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with tarfile.open(path, 'r:gz') as tar:
        tar.extractall(path=path.parent)


def unpack_tar_xz(path: Path) -> None:
    """Unpack target `tar.xz` archive.

    Args:
        path: Path to the archive.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with tarfile.open(path, 'r:xz') as tar:
        tar.extractall(path=path.parent)


def unpack_archive(path: Path, remove: bool = True) -> None:
    """Unpack an archive using the correct methodology based on its extension.

    Args:
        path: Path to the archive.
        remove: Whether to remove the archive after unpacking.

    Raises:
        FileNotFoundError: If archive couldn't be located.
        Not
    """
    action_map: dict[str, Callable] = {
        ArchiveExt.Zip: unpack_zip,
        ArchiveExt.GZip: unpack_gz,
        ArchiveExt.XZip: unpack_xz,
        ArchiveExt.TarZip: unpack_tar_zip,
        ArchiveExt.TarGZip: unpack_tar_gz,
        ArchiveExt.TarXZip: unpack_tar_xz,
        ArchiveExt.SevenZip: unpack_7z,
        ArchiveExt.TarSevenZip: unpack_7z
    }
    if path.suffix not in action_map:
        raise NotImplementedError(
            f"File extension '{path.suffix}' not a supported archive type!")
    with ARCHIVE_LOCK:
        action_map[path.suffix](path)
    if remove:
        os.remove(path)
