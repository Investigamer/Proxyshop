"""
LOADS PLUGINS AND TEMPLATES
"""
import os
import re
import sys
import json
import requests
from glob import glob
from pathlib import Path
from typing import Optional, Callable
from importlib import util, import_module
from proxyshop import gdown
from proxyshop.constants import con
cwd = os.getcwd()

# Card types with more than 1 template
card_types = {
    "Normal": ["normal"],
    "MDFC": ["mdfc_front", "mdfc_back"],
    "Transform": ["transform_front", "transform_back"],
    "Planeswalker": ["planeswalker"],
    "PW MDFC": ["pw_mdfc_front", "pw_mdfc_back"],
    "PW TF": ["pw_tf_front", "pw_tf_back"],
    "Basic Land": ["basic"],
    "Ixalan": ["ixalan"],
    "Mutate": ["mutate"],
    "Adventure": ["adventure"],
    "Leveler": ["leveler"],
    "Saga": ["saga"],
    "Miracle": ["miracle"],
    "Snow": ["snow"],
    "Planar": ["planar"]
}

# REGEX Patterns
re_art = re.compile(r'\(+(.*?)\)')
re_set = re.compile(r'\[(.*)\]')
re_cre = re.compile(r'{(.*)}')

"""
TEMPLATE FUNCTIONS
"""


def get_template(template: list, layout: Optional[str] = None):
    """
    Get template based on input and layout
    """
    # Was layout provided?
    if layout:
        # Get templates json
        templates = get_templates()

        # Select our template
        if layout in templates:
            if template in templates[layout]:
                selected_template = templates[layout][template]
            else: selected_template = templates[layout]["Normal"]
        else: return None
    else: selected_template = template

    # Built-in template?
    if selected_template[0] is None:
        return getattr(import_module("proxyshop.templates"), selected_template[1])

    # Plugin template
    spec = util.spec_from_file_location("templates", os.path.join(cwd, selected_template[0]))
    temp_mod = util.module_from_spec(spec)
    spec.loader.exec_module(temp_mod)
    return getattr(temp_mod, selected_template[1])


def get_templates():
    """
    Roll templates from our plugins into our main json
    """

    # Plugin folders
    folders = glob(os.path.join(cwd, "proxyshop\\plugins\\*\\"))

    # Get our main json
    with open(os.path.join(cwd, "proxyshop\\templates.json"), encoding="utf-8") as json_file:
        this_json = json.load(json_file)
        main_json = {}
        for key, val in this_json.items():
            main_json[key] = {}
            for k, v in val.items():
                main_json[key][k] = [None, v]

    # Iterate through folders
    for folder in folders:
        if Path(folder).stem == "__pycache__": continue
        else:
            j = []
            for name in os.listdir(folder):

                # Load json
                if name == "template_map.json":
                    with open(
                        os.path.join(cwd, f"proxyshop\\plugins\\{Path(folder).stem}\\{name}"),
                        encoding="utf-8"
                    ) as this_json:
                        j = json.load(this_json)

                # Add to sys.path
                sys.path.append(os.path.join(cwd, f"proxyshop/plugins/{Path(folder).stem}"))

            # Loop through keys in plugin json
            try:
                for key, val in j.items():
                    # Add to existing templates
                    for k, v in val.items():
                        main_json[key][k] = [f"proxyshop\\plugins\\{Path(folder).stem}\\templates.py", v]
            except Exception as e: print(e)

    return main_json


def get_my_templates(selected: dict):
    """
    Retrieve templates based on user selection
    @param selected: Selected templates to return data for.
    @return: A dict of templates matching each layout type.
    """
    temps = {}
    templates = get_templates()
    # Create new dict of selected templates
    for key in card_types:
        for k in selected:
            if k == key:
                for lay in card_types[key]:
                    temps[lay] = templates[lay][selected[k]]

    # Add default template for any unselected
    for layout in templates:
        if layout not in temps:
            temps[layout] = templates[layout]["Normal"]
    return temps


"""
CARD FUNCTIONS
"""


def retrieve_card_info(filename):
    """
    Retrieve card name and (if specified) artist from the input file.
    """
    # Extract just the card name
    fname = os.path.basename(str(filename))
    sep = [' {', ' [', ' (']
    fn_split = re.split('|'.join(map(re.escape, sep)), os.path.splitext(fname)[0])
    name = fn_split[0]

    # Match pattern
    artist = re_art.findall(fname)
    set_code = re_set.findall(fname)
    creator = re_cre.findall(fname)

    # Check for these values
    if creator: creator = creator[0]
    else: creator = None
    if artist: artist = artist[0]
    else: artist = None
    if set_code:
        set_code = set_code[0]
        if set_code.upper() not in con.set_symbols:
            if set_code.upper()[1:] in con.set_symbols:
                set_code = set_code[1:]
    else: set_code = None

    return {
        'name': name,
        'artist': artist,
        'set': set_code,
        'creator': creator,
        'filename': filename
    }


"""
UPDATE FUNCTIONS
"""


def check_for_updates():
    """
    Check our app manifest for base template updates.
    Also check any plugins for an update manifest.
    @return: Dict containing base temps and plugins temps needing updates.
    """
    # Base vars
    updates = {}

    # Base app manifest
    with open("proxyshop/manifest.json", encoding="utf-8") as f:
        # Get config info
        data = json.load(f)
        s3_bucket = data['__CONFIG__']['S3']
        data.pop("__CONFIG__")

        # Build update dict
        for cat, temps in data.items():
            for name, temp in temps.items():

                # Is the ID valid?
                if temp['id'] in ("", None, 0): continue

                # Add important data to our temp dict
                temp['type'] = cat
                temp['name'] = name
                temp['plugin'] = None
                temp['manifest'] = os.path.join(cwd, 'proxyshop/manifest.json')
                temp['s3'] = s3_bucket

                # Does this template need an update?
                file = version_check(temp)
                if file:
                    if cat not in updates: updates[cat] = [file]
                    else: updates[cat].append(file)

    # Get plugin manifests
    plugins = []
    folders = glob(os.path.join(cwd, "proxyshop\\plugins\\*\\"))
    for folder in folders:
        if Path(folder).stem == "__pycache__": continue
        elif 'manifest.json' in os.listdir(folder):
            plugins.append({
                'name': Path(folder).stem,
                'path': os.path.join(folder, "manifest.json")
            })

    # Check the manifest of each plugin
    for plug in plugins:
        with open(plug['path'], encoding="utf-8") as f:
            # Check for S3 compatibility
            data = json.load(f)
            if "__CONFIG__" in data:
                if "S3" in data['__CONFIG__']:
                    s3_bucket = data['__CONFIG__']['S3']
                else: s3_bucket = None
                data.pop("__CONFIG__")

            # Append to the updates dict
            for cat, temps in data.items():
                for name, temp in temps.items():

                    # Is the ID valid?
                    if temp['id'] in ("", None, 0): continue

                    # Add important data to our temp dict
                    temp['type'] = cat
                    temp['name'] = name
                    temp['plugin'] = plug['name']
                    temp['manifest'] = plug['path']
                    temp['s3'] = s3_bucket

                    # Does this template need an update?
                    file = version_check(temp, plug['name'])
                    if file:
                        if cat not in updates: updates[cat] = [file]
                        else: updates[cat].append(file)

    # Return dict of templates needing updates
    return updates


def version_check(temp: dict, plugin: Optional[str] = None):
    """
    Check if a given file is up-to-date based on the live file metadata.
    @param temp: Template json data from the manifest
    @param plugin: Plugin name, optional
    @return: True if it needs an update, False if it doesn't
    """
    # Get our current version

    # Get our basic metadata dict
    data = gdrive_metadata(temp['id'])
    plugin_path = f"{plugin}/" if plugin else ""
    full_path = os.path.join(cwd, f"templates/{plugin_path}{temp['file']}")
    if 'description' not in data: data['description'] = "v1.0.0"
    elif data['description'] == "": data['description'] = "v1.0.0"
    current = get_current_version(temp['id'], full_path)

    # Build our return
    file = {
        'id': temp['id'],
        'name': temp['name'],
        'type': temp['type'],
        'filename': data['name'],
        'path': full_path,
        'manifest': temp['manifest'],
        'plugin': temp['plugin'],
        'version_old': current,
        'version_new': data['description'],
        'size': data['size'],
        's3': temp['s3']
    }

    # Yes update if file has never been downloaded
    if not file['version_old']: return file

    # No update if version is still FIRST version
    if file['version_new'] in ("v1", "v1.0", "v1.0.0", "1", "1.0", "1.0.0", ""): return None

    # Update if version doesn't match
    if file['version_old'] != file['version_new']: return file
    else: return None


def get_current_version(file_id: str, path: str):
    """
    Checks the current on-file version of this template.
    If the file is present, but no version tracked, fill in default.
    @param file_id: Google Drive file ID
    @param path: Path to the template PSD
    @return: The current version, or None if not on-file
    """
    # Is it logged in the tracker?
    if file_id in con.versions:
        version = con.versions[file_id]
    else: version = None

    # Is the file available?
    if os.path.exists(path):
        if version: return version
        else:
            version = "v1.0.0"
            con.versions[file_id] = version
    else:
        if version:
            version = None
            del con.versions[file_id]
        else: return None

    # Update the tracker
    con.update_version_tracker()
    return version


def update_template(temp: dict, callback: Callable, s3_callback: Callable):
    """
    Update a given template to the latest version.
    @param temp: Dict containing template information.
    @param callback: Callback method to update progress bar.
    @param s3_callback: Callback method to update progress bar for S3 downloading.
    """
    # Download using authorization
    result = gdown.download(temp['id'], temp['path'], callback)
    if not result:
        if temp['s3']:
            # Try grabbing from Amazon S3 instead
            result = gdown.download_s3(temp, s3_callback)

    # Change the version to match the new version
    if result:
        con.versions[temp['id']] = temp['version_new']
        con.update_version_tracker()
    return result


def gdrive_metadata(file_id: str):
    """
    Get the metadata of a given template file.
    @param file_id: ID of the Google Drive file
    @return: Dict of metadata
    """
    source = "https://www.googleapis.com/drive/" \
             f"v3/files/{file_id}?alt=json&fields=description,name,size&key={con.google_api}"
    return requests.get(source, headers=con.http_header).json()


"""
SYSTEM FUNCTIONS
"""


def import_json_config(path: str):
    with open(os.path.join(f"{cwd}/proxyshop/plugins", path)) as f:
        return json.load(f)


"""
HEADLESS CONSOLE
"""


class Console:
    """
    Replaces the GUI console when running headless.
    """

    @staticmethod
    def message(msg):
        print(msg)

    @staticmethod
    def wait(msg):
        print(msg)
        input("Would you like to continue?")

console = Console()