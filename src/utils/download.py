"""
* Utils: Downloads and Updates
"""
# Standard Library Imports
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

# Third Party Imports
import requests
import yarl
from omnitils.fetch import download_file
from omnitils.files import get_temporary_file
from omnitils.files.archive import unpack_archive


@dataclass
class HEADERS:
    """Stores defined HTTP request headers."""

    Default = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/39.0.2171.95 Safari/537.36"}


"""
* Download Utils
"""


def download_cloudfront(url: yarl.URL, path: Path, callback: Optional[Callable] = None) -> bool:
    """Download a template from cloudfront cached Amazon S3 bucket.

    Args:
        url: URL to S3/cloudfront hosted file.
        path: Path to save the archive.
        callback: Callback function to update progress.

    Returns:
        True if download is successful, otherwise False.
    """
    # Get a temp file
    temp_path = get_temporary_file(path=path, ext='.amzn')

    # Start the download
    try:
        download_file(
            url=url,
            path=temp_path,
            callback=callback)
        shutil.move(temp_path, path)
        unpack_archive(path)
    except (requests.RequestException, FileExistsError, FileNotFoundError):
        return False
    return True
