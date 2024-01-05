"""
* API: Amazon (Cloudfront / S3)
"""
# Standard Library Imports
from pathlib import Path
from typing import Callable, Optional

# Third Party Imports
import requests
import yarl

# Local Imports
from src.enums.api import HEADERS
from src.utils.download import get_temporary_file, download_file


"""
* Request Funcs
"""


def download_cloudfront(url: yarl.URL, path: Path, callback: Optional[Callable] = None) -> bool:
    """Download template from cloudfront cached Amazon S3 bucket.

    Args:
        url: Amazon Cloudfront URL.
        path: Filepath key on S3 bucket.
        callback: Callback function to update progress.

    Returns:
        True if download is successful, otherwise False.
    """
    # Get a temp file
    file, size = get_temporary_file(path=path, ext='.amzn')

    # Add range header if file is partially downloaded
    header = HEADERS.Default.copy()
    if size is not 0:
        header["Range"] = f"bytes={str(size)}-"

    # Establish session
    sess = requests.session()
    res = sess.get(url, headers=header, stream=True, verify=True)

    # Start the download
    return download_file(file, res, sess, path, callback)
