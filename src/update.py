"""
Borrows from Gdown Project
Source: https://github.com/wkentaro/gdown
License: https://github.com/wkentaro/gdown/blob/main/LICENSE
"""
# Standard Library Imports
import os
import sys
import json
import shutil
import tempfile
import textwrap
import os.path as osp
from pathlib import Path
from typing import Callable, Optional

# Third Party Imports
import requests

# Local Imports
from src.constants import con
from src.utils.regex import Reg


def get_url_from_gdrive_confirmation(contents: str) -> str:
    """
    Get the correct URL for downloading Google Drive file.
    @param contents: Google Drive page data.
    @return: Correct url for downloading.
    """
    for line in contents.splitlines():
        if m := Reg.GDOWN_EXPORT.search(line):
            # Google Docs URL
            return f"https://docs.google.com{m.groups()[0]}".replace("&amp;", "&")
        if m := Reg.GDOWN_FORM.search(line):
            # Download URL from Form
            return m.groups()[0].replace("&amp;", "&")
        if m := Reg.GDOWN_URL.search(line):
            # Download URL from JSON
            return m.groups()[0].replace("\\u003d", "=").replace("\\u0026", "&")
        if m := Reg.GDOWN_ERROR.search(line):
            # Error Returned
            error = m.groups()[0]
            raise RuntimeError(error)
    raise RuntimeError(
        "Cannot retrieve a public link of the file. "
        "You may need to change access permission, "
        "or have reached the daily limit."
    )


def download_google(
    file_id: str,
    path: str,
    callback: Callable,
    use_cookies: bool = True
) -> bool:
    """
    Download a file from Google Drive using its file ID.
    @param file_id: Google Drive file ID.
    @param path: Path to save downloaded file.
    @param callback: Function to call on each chunk downloaded.
    @param use_cookies: Use cookies with request if True.
    @return: True if successful, otherwise False.
    """
    Path(osp.dirname(Path(path))).mkdir(mode=511, parents=True, exist_ok=True)
    url = "https://drive.google.com/uc?id={id}".format(id=file_id)
    url_origin = url
    sess = requests.session()
    header = con.http_header.copy()

    # Cookies
    cookies_file = osp.join(con.path_logs, "cookies.json")
    if osp.exists(cookies_file) and use_cookies:
        with open(cookies_file) as f:
            cookies = json.load(f)
        for k, v in cookies:
            sess.cookies[k] = v

    # Get file resource
    while True:
        res = sess.get(url, headers=header, stream=True, verify=True)

        # Save cookies
        with open(cookies_file, "w") as f:
            cookies = [
                (k, v)
                for k, v in sess.cookies.items()
                if not k.startswith("download_warning_")
            ]
            json.dump(cookies, f, indent=2)

        # Is this the right file?
        if "Content-Disposition" in res.headers:
            break

        # Need to redirect with confirmation
        try:
            url = get_url_from_gdrive_confirmation(res.text)
        except RuntimeError as e:
            print("Access denied with the following error:")
            error = "\n".join(textwrap.wrap(str(e)))
            print("\n", error, "\n", file=sys.stderr)
            print(
                "You may still be able to access the file from the browser:",
                file=sys.stderr,
            )
            print("\n\t", url_origin, "\n", file=sys.stderr)
            return False

    # Get temp file
    file, current, res = get_temp_file(res, sess, path, url)

    # Let the user know its downloading
    print_download(url_origin, path, file if current != 0 else None)

    # Start the download
    return download_file(file, res, sess, path, callback)


def download_s3(save_path: str, s3_path: str, callback: Optional[Callable] = None) -> bool:
    """
    Download template from Amazon S3 bucket.
    @param save_path: Path to save the file to.
    @param s3_path: Filepath key on S3 bucket.
    @param callback: Callback function to update progress.
    @return: True if success, False if failed.
    """
    # Establish this object's cloudfront URL
    url = f"{con.cloudfront_url}/{s3_path}"

    # Establish session
    sess = requests.session()
    header = con.http_header.copy()
    res = sess.get(url, headers=header, stream=True, verify=True)

    # Get temp file
    file, current, res = get_temp_file(res, sess, save_path, url)

    # Let the user know its downloading
    print_download(url, save_path, file if current != 0 else None)

    # Start the download
    return download_file(file, res, sess, save_path, callback)


def get_temp_file(
    res: requests.Response,
    sess: requests.Session,
    path: str,
    url: str,
) -> tuple:
    """
    Check for an existing temporary file or create a new one.
    @param res: Planned download request.
    @param sess: Current download session.
    @param path: Planned path name to the completed download.
    @param url: If resumable, url to generate a new download request.
    @return: Tuple containing temp file path, total bytes downloaded, new download request.
    """
    existing_tmp_files = []
    header = con.http_header.copy()
    file_name = osp.basename(path)
    for file in os.listdir(osp.dirname(path) or "."):
        if file.startswith(file_name) and file != file_name:
            existing_tmp_files.append(osp.join(osp.dirname(path), file))
    if len(existing_tmp_files) != 0:
        tmp_file = existing_tmp_files[0]
        current = int(osp.getsize(tmp_file))
    else:
        current = 0
        # mkstemp is preferred, but does not work on Windows
        # https://github.com/wkentaro/gdown/issues/153
        tmp_file = tempfile.mktemp(
            suffix=tempfile.template,
            prefix=osp.basename(path),
            dir=osp.dirname(path),
        )

    # Resumable temp file found, update request with Range header
    with open(tmp_file, "ab") as f:
        if tmp_file is not None and f.tell() != 0:
            header["Range"] = "bytes={}-".format(f.tell())
            res = sess.get(url, headers=header, stream=True, verify=True)
    return tmp_file, current, res


def print_download(url: str, path: str, resume: str = None) -> None:
    """
    Print the details of an initiated download.
    @param url: Url file is being received from.
    @param path: Path the file is being saved to.
    @param resume: Temporary file we're resuming download on, if provided.
    """
    print("Downloading...", file=sys.stderr)
    if resume:
        print("Resume:", resume, file=sys.stderr)
    print("From:", url, file=sys.stderr)
    print("To:", path, file=sys.stderr)


def download_file(
    file: str,
    res: requests.Response,
    sess: requests.Session,
    path: Optional[str] = None,
    callback: Optional[Callable] = None,
    chunk_size = 1024 * 1024
) -> bool:
    """
    Download file as a temporary file, then rename to its correct filename.
    @param file: File path to download to.
    @param res: Download request.
    @param sess: Download session.
    @param path: Final path to save the completed temporary file.
    @param callback: Callback to update download progress.
    @param chunk_size: Amount of bytes to download before processing the callback.
    @return: True if download completed without error, otherwise False.
    """
    # Ensure a proper chunk_size
    if not chunk_size or not isinstance(chunk_size, int):
        chunk_size = 1024 * 1024

    # Try to download the file
    total = int(res.headers.get("Content-Length") or 1)
    current = int(osp.getsize(file))
    try:
        with open(file, "ab") as f:
            for chunk in res.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                if callback:
                    current += int(chunk_size)
                    callback(current, total)
        if path and file != path:
            shutil.move(file, path)
    except IOError as e:
        print(e, file=sys.stderr)
        return False
    finally:
        # Close the session
        sess.close()
    return True
