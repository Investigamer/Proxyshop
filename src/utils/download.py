"""
* Utils: Downloads and Updates
"""
# Standard Library Imports
import os
from pathlib import Path
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
    f = NamedTemporaryFile(prefix=temp.name, dir=temp.parent, delete=False)
    file = f.name
    f.close()
    return Path(file), 0


def download_file(
    file: Path,
    res: requests.Response,
    path: Path = None,
    callback: Optional[Callable] = None,
    chunk_size: int = 1024 * 1024
) -> bool:
    """Download file from streamed response as a temporary file, then rename to its final path.

    Args:
        file: Path of the temporary file.
        res: Download request.
        path: Final path to save the completed temporary file.
        callback: Callback to update download progress.
        chunk_size: Amount of bytes to download before calling `callback`.

    Returns:
        True if download completed successfully, otherwise False.
    """
    # Establish initial progress
    path = path or file
    total = int(res.headers.get("Content-Length") or 1)
    current = file.stat().st_size

    # Open the temporary file and write each chunk
    with open(file, "ab") as f:
        try:
            for chunk in res.iter_content(chunk_size=chunk_size):
                if not chunk:
                    raise OSError('Bad chunk detected!')
                if res.status_code != 200:
                    raise requests.RequestException(
                        request=res.request,
                        response=res)
                f.write(chunk)

                # Execute progress callback if provided
                if callback:
                    current += int(chunk_size)
                    callback(current, total)

        # Download failure
        except Exception as e:
            print(f'Download failed: {file}\n{e}')
            return False
        del res

    # Rename the temporary file, unpack it
    try:
        if file != path:
            shutil.move(file, path)
        unpack_archive(path)
    except Exception as e:
        print(f'Unpacking failed: {path}\n{e}')
        return False
    return True
