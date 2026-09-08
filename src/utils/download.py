"""
* Utils: Downloads and Updates
"""

import shutil
from collections.abc import Callable
from pathlib import Path

import requests
import yarl
from omnitils.fetch import download_file
from omnitils.files import get_temporary_file
from omnitils.files.archive import unpack_archive

from src import DEFAULT_HEADERS


def download_cloudfront(
    url: yarl.URL, path: Path, callback: Callable[[int, int], None] | None = None
) -> bool:
    """Download a template from cloudfront cached Amazon S3 bucket.

    Args:
        url: URL to S3/cloudfront hosted file.
        path: Path to save the archive.
        callback: Callback function to update progress.

    Returns:
        True if download is successful, otherwise False.
    """
    # Get a temp file
    temp_path = get_temporary_file(path=path, ext=".amzn")

    # Start the download
    try:
        download_file(
            url=url, path=temp_path, callback=callback, header=DEFAULT_HEADERS
        )
        shutil.move(temp_path, path)
        unpack_archive(path)
    except requests.RequestException, FileExistsError, FileNotFoundError:
        return False
    return True
