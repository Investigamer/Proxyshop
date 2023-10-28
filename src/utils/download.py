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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional, Iterator

# Third Party Imports
import requests

# Local Imports
from src.types.templates import TemplateDetails, TemplateUpdate
from src.utils.compression import decompress_file
from src.core import get_templates
from src.utils.regex import Reg
from src.constants import con
from src.utils.env import ENV


"""
DOWNLOAD UTILS
"""


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
            # Rename TMP file
            shutil.move(file, path)
            # Decompress zipped file
            if path[-3:] == '.7z':
                with con.lock_decompress:
                    decompress_file(path)
    except IOError as e:
        print(e, file=sys.stderr)
        return False
    finally:
        # Close the session
        sess.close()
    return True


"""
GDRIVE UTILS
"""


def gdrive_metadata(file_id: str) -> dict:
    """
    Get the metadata of a given template file.
    @param file_id: ID of the Google Drive file
    @return: Dict of metadata
    """
    result = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}",
        headers=con.http_header,
        params={
            'alt': 'json',
            'fields': 'description,name,size',
            'key': ENV.API_GOOGLE
        }
    ).json()
    return result if 'name' in result and 'size' in result else None


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
    Path(osp.dirname(Path(path))).mkdir(mode=711, parents=True, exist_ok=True)
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


"""
AMAZON S3 UTILS
"""


def download_s3(save_path: str, s3_path: str, callback: Optional[Callable] = None) -> bool:
    """
    Download template from Amazon S3 bucket.
    @param save_path: Path to save the file to.
    @param s3_path: Filepath key on S3 bucket.
    @param callback: Callback function to update progress.
    @return: True if success, False if failed.
    """
    # Establish this object's cloudfront URL
    url = f"{ENV.API_AMAZON}/{s3_path}"

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


"""
TEMPLATE UPDATE UTILS
"""


def check_for_updates(
    templates: Optional[dict[str, list[TemplateDetails]]] = None
) -> dict[str, list[TemplateUpdate]]:
    """
    Check our app and plugin manifests for template updates.
    @param templates: Dict of listed template details, will pull them if not provided.
    @return: Dict containing templates that need an update.
    """
    # Set up our updates return
    updates: dict[str, list[TemplateUpdate]] = {}

    # Get templates if not provided
    if not templates:
        templates = get_templates()

    # Check for an update on each template
    unique_temps = []
    for card_type, temps in templates.items():
        for template in temps:
            if template['id'] not in unique_temps and template['id']:
                unique_temps.append(template)

    # Perform threaded version check requests
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results: Iterator[TemplateUpdate] = executor.map(version_check, unique_temps)

    # Ensure executor is finished before building return
    results: list[TemplateUpdate] = list(results)
    for temp in results:
        if temp:
            updates.setdefault(temp['type'], []).append(temp)
    return updates


def version_check(template: TemplateDetails) -> Optional[TemplateUpdate]:
    """
    Check if a template is up-to-date based on the live file metadata.
    @param template: Dict containing template details.
    @return: TemplateUpdate if update needed, else None.
    """
    # Get our metadata
    data = gdrive_metadata(template['id'])
    if not data:
        # File couldn't be located on Google Drive
        print(f"{template['name']} ({template['type']}) not found on Google Drive!")
        return

    # Compare the versions
    latest = data.get('description', "v1.0.0")
    current = get_current_version(template['id'], template['template_path'])
    if current and current == latest:
        # Version is up-to-date
        return

    # Add 'Front' or 'Back' to name if needed
    updated_name = template['name']
    if 'front' in template['layout']:
        updated_name = f"{updated_name} Front"
    if 'back' in template['layout']:
        updated_name = f"{updated_name} Back"

    # Return our TemplateUpdate dict
    return {
        'id': template['id'],
        'name': updated_name,
        'name_base': template['name'],
        'type': template['type'],
        'filename': data['name'],
        'path': template['template_path'],
        'plugin': os.path.basename(
            os.path.dirname(template['plugin_path'])
        ) if template['plugin_path'] else None,
        'version': latest,
        'size': int(data['size'])
    }


def get_current_version(file_id: str, file_path: str) -> Optional[str]:
    """
    Checks the current on-file version of this template.
    If the file is present, but no version tracked, fill in default.
    @param file_id: Google Drive file ID
    @param file_path: Path to the template PSD
    @return: The current version, or None if not on-file
    """
    # Is it logged in the tracker?
    version = con.versions[file_id] if file_id in con.versions else None

    # PSD file exists
    if os.path.exists(file_path):
        # Version is logged
        if version:
            return version

        # Version is not logged, use default
        con.versions[file_id] = "v1.0.0"
        con.update_version_tracker()
        return "v1.0.0"

    # PSD does not exist, and no version logged
    if not version:
        return

    # PSD does not exist, version mistakenly logged
    del con.versions[file_id]
    con.update_version_tracker()
    return


def update_template(temp: TemplateUpdate, callback: Callable) -> bool:
    """
    Update a given template to the latest version.
    @param temp: Dict containing template information.
    @param callback: Callback method to update progress bar.
    @return: True if succeeded, False if failed.
    """
    try:
        # Adjust to 7z if needed
        file_path = temp['path'].replace('.psd', '.7z') if '.7z' in temp['filename'] else temp['path']

        # Download using Google Drive
        result = download_google(temp['id'], file_path, callback)
        if not result:
            # Google Drive failed, download from Amazon S3
            url = f"{temp['plugin']}/{temp['filename']}" if temp['plugin'] else temp['filename']
            result = download_s3(file_path, url, callback)
        if not result:
            # All Downloads failed
            raise ConnectionError(f"Downloading '{temp['name']} ({temp['type']})' was unsuccessful!")
    except Exception as e:
        print(e)
        return False

    # Update version tracker, return succeeded
    con.versions[temp['id']] = temp['version']
    con.update_version_tracker()
    return result
