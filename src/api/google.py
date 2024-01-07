"""
* API: Google Drive
"""
# Standard Library Imports
from contextlib import suppress
import json
from pathlib import Path
import textwrap
from typing import Optional, Callable, TypedDict, NotRequired

# Third Party Imports
import requests
import yarl

# Local Imports
from src.enums.api import HEADERS
from src.utils.download import get_temporary_file, download_file
from src.utils.regex import Reg
from src.utils.strings import decode_url


"""
* Types
"""


class GoogleDriveMetadata(TypedDict):
    """Relevant metadata for a file hosted on Google Drive."""
    description: NotRequired[str]
    name: str
    size: int


"""
* Google Drive Utils
"""


def get_url_from_gdrive_confirmation(contents: str) -> yarl.URL:
    """Get the correct URL for downloading Google Drive file.

    Args:
        contents: Google Drive page data.

    Returns:
        URL object pointing to the hosted file resource.
    """
    for line in contents.splitlines():
        if m := Reg.GDOWN_EXPORT.search(line):
            # Google Docs URL
            return decode_url(f'https://docs.google.com{m.groups()[0]}')
        if m := Reg.GDOWN_FORM.search(line):
            # Download URL from Form
            return decode_url(m.groups()[0])
        if m := Reg.GDOWN_URL.search(line):
            # Download URL from JSON
            return decode_url(m.groups()[0])
        if m := Reg.GDOWN_ERROR.search(line):
            # Error Returned
            raise OSError(m.groups()[0])
    raise OSError(
        "Google Drive file has been made private or has reached its daily request limit.")


"""
* Request Funcs
"""


def get_google_drive_metadata(file_id: str, api_key: str) -> Optional[GoogleDriveMetadata]:
    """Get the metadata of a given template file.

    Args:
        file_id: ID of the Google Drive file.
        api_key: Google Drive API key.

    Returns:
        Metadata of the Google Drive file.
    """
    with suppress(Exception):
        with requests.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            headers=HEADERS.Default.copy(),
            params={
                'alt': 'json',
                'fields': 'description,name,size',
                'key': api_key}
        ) as req:
            if not req.status_code == 200:
                return
            result = req.json()
            if 'name' in result and 'size' in result:
                return result

    # Request was unsuccessful
    return


def download_google_drive(
    url: yarl.URL,
    path: Path,
    callback: Callable,
    path_cookies: Optional[Path] = None
) -> bool:
    """
    Download a file from Google Drive using its file ID.

    Note:
        URL: https://drive.google.com/uc?id={file_id}

    Args:
        url: Google Drive file ID.
        path: Path to save downloaded file.
        callback: Function to call on each chunk downloaded.
        path_cookies: Path to cookies file, don't use cookies if not provided.

    Returns:
        True if download successful, otherwise False.
    """

    # Ensure path and load a temporary file
    path.parent.mkdir(mode=777, parents=True, exist_ok=True)
    file, size = get_temporary_file(path=path, ext='.drive')

    # Add range header if file is partially downloaded
    header = HEADERS.Default.copy()
    if size > 0:
        header["Range"] = f"bytes={str(size)}-"

    # Create initial session
    sess = requests.session()

    # Load cookies if provided and exists
    if path_cookies and path_cookies.is_file():
        with open(path_cookies, 'r', encoding='utf-8') as f:
            for k, v in json.load(f):
                sess.cookies[k] = v

    # Get file resource
    while True:
        res = sess.get(url, headers=header, stream=True)

        # Save cookies
        if path_cookies:
            with open(path_cookies, "w") as f:
                json.dump([
                    (k, v) for k, v in sess.cookies.items()
                    if not k.startswith("download_warning_")
                ], fp=f, indent=2)

        # Is this the right file?
        if "Content-Disposition" in res.headers:
            break

        # Need to redirect with confirmation
        try:
            url = get_url_from_gdrive_confirmation(res.text)
        except Exception as e:
            sess.close()
            err = '\n'.join(textwrap.wrap(str(e)))
            print(f'Access denied with the following error:\n{err}')
            return False

    # Start the download
    result = download_file(
        file=file,
        res=res,
        path=path,
        callback=callback)
    sess.close()
    return result
