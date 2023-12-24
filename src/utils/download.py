"""
* Utils: Downloads and Updates
"""
# Standard Library Imports
import os
from pathlib import Path
import sys
import shutil
from tempfile import NamedTemporaryFile
from typing import Callable, Optional

# Third Party Imports
import requests

# Local Imports
from src.utils.compression import unpack_archive


"""
* Download Utils
"""


def get_temporary_file(path: Path, ext: str = '.drive') -> tuple[Path, int]:
    """Check for an existing temporary file representing a provided file path and ext.

    Args:
        path: Path to the file we plan to download.
        ext: Temporary file extension to use, e.g. '.drive' or '.amazon'

    Returns:
        A tuple containing a path to the temporary file and the current size of that file.
    """

    # Look for an existing temporary file
    temp = path.with_suffix(ext)
    for p in os.listdir(path.parent):
        file = path.parent / p
        if file.is_dir():
            continue
        if temp.name in file.name:
            return file, file.stat().st_size

    # Create a new temporary file
    with NamedTemporaryFile(prefix=temp.name, dir=temp.parent, delete=False) as f:
        return f, 0


def download_file(
    file: Path,
    res: requests.Response,
    sess: requests.Session,
    path: Path = None,
    callback: Optional[Callable] = None,
    chunk_size = 1024 * 1024
) -> bool:
    """Download file from streamed response as a temporary file, then rename to its final path.

    Args:
        file: Path of the temporary file.
        res: Download request.
        sess: Download session.
        path: Final path to save the completed temporary file.
        callback: Callback to update download progress.
        chunk_size: Amount of bytes to download before calling `callback`.

    Returns:
        True if download completed successfully, otherwise False.
    """
    # Try to download the file
    total = int(res.headers.get("Content-Length") or 1)
    current = file.stat().st_size
    try:
        with open(file, "ab") as f:
            # Write each chunk and call the progress callback
            for chunk in res.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                if callback:
                    current += int(chunk_size)
                    callback(current, total)
        if path and str(file) != str(path):
            # Rename TMP file
            shutil.move(file, path)
            # Decompress zipped file
            if path.suffix == '.7z':
                unpack_archive(path)
    except IOError as e:
        print(e, file=sys.stderr)
        sess.close()
        return False
    sess.close()
    return True
