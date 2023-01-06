"""
Borrows from Gdown Project
Source: https://github.com/wkentaro/gdown
License: https://github.com/wkentaro/gdown/blob/main/LICENSE
"""
import json
from pathlib import Path
import os
import os.path as osp
import re
import shutil
import sys
import tempfile
import textwrap
from typing import Callable, Optional
import requests

from proxyshop.constants import con

CHUNK_SIZE = 1024 * 1024  # 1 MB
cwd = os.getcwd()


def get_url_from_gdrive_confirmation(contents: str) -> str:
    """
    Get the correct URL for downloading Google Drive file.
    @param contents: Google Drive page data.
    @return: Correct url for downloading.
    """
    url = ""
    for line in contents.splitlines():
        m = re.search(r'href="(/uc\?export=download[^"]+)', line)
        if m:
            url = "https://docs.google.com" + m.groups()[0]
            url = url.replace("&amp;", "&")
            break
        m = re.search('id="download-form" action="(.+?)"', line)
        if m:
            url = m.groups()[0]
            url = url.replace("&amp;", "&")
            break
        m = re.search('"downloadUrl":"([^"]+)', line)
        if m:
            url = m.groups()[0]
            url = url.replace("\\u003d", "=")
            url = url.replace("\\u0026", "&")
            break
        m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
        if m:
            error = m.groups()[0]
            raise RuntimeError(error)
    if not url:
        raise RuntimeError(
            "Cannot retrieve the public link of the file. "
            "You may need to change the permission to "
            "'Anyone with the link', or have had many accesses."
        )
    return url


def download_google(
    file_id: str,
    path: str,
    callback: Callable,
    use_cookies: bool = True
):
    """
    Download file from Gdrive ID.

    Parameters
    ----------
    file_id: str
        Google Drive's file ID.
    path: str
        Output path.
    callback: any
        Function to call on each chunk downloaded.
    use_cookies: bool
        Use cookies with request.

    Returns
    -------
    output: bool
        True if success, False if failed.
    """
    Path(os.path.dirname(Path(path))).mkdir(mode=511, parents=True, exist_ok=True)
    url = "https://drive.google.com/uc?id={id}".format(id=file_id)
    url_origin = url
    sess = requests.session()
    header = con.http_header.copy()

    # Cookies
    cache_dir = osp.join(cwd, "tmp")
    if not osp.exists(cache_dir):
        os.makedirs(cache_dir)
    cookies_file = osp.join(cache_dir, "cookies.json")
    if osp.exists(cookies_file) and use_cookies:
        with open(cookies_file) as f:
            cookies = json.load(f)
        for k, v in cookies:
            sess.cookies[k] = v

    # Get file resource
    while True:
        res = sess.get(url, headers=header, stream=True, verify=True)
        print(res.headers)

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
    details = get_temp_file(res, sess, path, url)
    file, current, res = details['file'], details['current'], details['res']

    # Let the user know its downloading
    print("Downloading...", file=sys.stderr)
    if current != 0:
        print("Resume:", file, file=sys.stderr)
    print("From:", url_origin, file=sys.stderr)
    print("To:", path, file=sys.stderr)

    # Start the download
    return download_file(file, res, sess, path, callback)


def download_s3(temp: dict, callback: Callable) -> bool:
    """
    Download template from Amazon S3 bucket.
    @param temp: Dict containing template data.
    @param callback: Callback function to update progress.
    @return: True if success, False if failed.
    """
    # Establish this object's key
    key = f"{temp['plugin']}/{temp['filename']}" if temp['plugin'] else temp['filename']
    url = f"{con.cloudfront_url}/{key}"

    # Establish session
    sess = requests.session()
    header = con.http_header.copy()
    res = sess.get(url, headers=header, stream=True, verify=True)

    # Get temp file
    details = get_temp_file(res, sess, temp['path'], url)
    file, current, res = details['file'], details['current'], details['res']

    # Let the user know its downloading
    print("Downloading...", file=sys.stderr)
    if current != 0:
        print("Resume:", file, file=sys.stderr)
    print("From:", url, file=sys.stderr)
    print("To:", temp['path'], file=sys.stderr)

    # Start the download
    return download_file(file, res, sess, temp['path'], callback)


def get_temp_file(
        res: requests.Response,
        sess: requests.Session,
        path: str,
        url: str,
) -> dict:
    # Check for existing Temp file, or setup new one
    existing_tmp_files = []
    header = con.http_header.copy()
    file_name = osp.basename(path)
    for file in os.listdir(osp.dirname(path) or "."):
        if file.startswith(file_name) and file != file_name:
            existing_tmp_files.append(osp.join(osp.dirname(path), file))
    if len(existing_tmp_files) != 0:
        tmp_file = existing_tmp_files[0]
        current = int(os.path.getsize(tmp_file))
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
    return {
        'file': tmp_file,
        'res': res,
        'current': current
    }


def download_file(
        file: str,
        res: requests.Response,
        sess: requests.Session,
        path: Optional[str] = None,
        callback: Optional[Callable] = None
) -> bool:
    # Try to download the file
    total = int(res.headers.get("Content-Length"))
    current = int(os.path.getsize(file))
    try:
        with open(file, "ab") as f:
            for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
                current += int(CHUNK_SIZE)
                if callback:
                    callback(current, total)
        if path and file != path:
            shutil.move(file, path)
    except IOError as e:
        print(e, file=sys.stderr)
        return False
    finally:
        sess.close()
    return True
