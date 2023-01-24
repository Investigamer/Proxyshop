"""
LOADS PLUGINS AND TEMPLATES
"""
import os
import re
import sys
import json
import requests
import os.path as osp
from glob import glob
from pathlib import Path
from typing import Optional, Callable, TypedDict, Union
from typing_extensions import NotRequired
from importlib import util, import_module
from proxyshop import update
from proxyshop.constants import con
cwd = os.getcwd()

# All Template types
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
    "Prototype": ["prototype"],
    "Adventure": ["adventure"],
    "Leveler": ["leveler"],
    "Saga": ["saga"],
    "Miracle": ["miracle"],
    "Snow": ["snow"],
    "Planar": ["planar"]
}

reg_artist = re.compile(r'\(+(.*?)\)')
reg_set = re.compile(r'\[(.*)]')
reg_creator = re.compile(r'{(.*)}')


"""
TYPES
"""


class TemplateDetails(TypedDict):
    class_name: str
    plugin_path: Optional[str]
    config_path: str
    name: str
    type: str
    loaded_class: NotRequired[Callable]


class CardDetails(TypedDict):
    name: str
    set: Optional[str]
    artist: Optional[str]
    creator: Optional[str]
    filename: Union[str, Path]


"""
TEMPLATE FUNCTIONS
"""


def get_named_type(layout_class: str) -> Optional[str]:
    """
    Finds the named type for a given layout class.
    @param layout_class: Scryfall authentic layout type, ex: mdfc_font
    @return: Displayed name of that type, ex: MDFC
    """
    for name, types in card_types.items():
        if layout_class in types:
            return name
    return


def get_template_class(template: TemplateDetails) -> Callable:
    """
    Get template based on input and layout
    """
    # Built-in template?
    if not template['plugin_path']:
        return getattr(import_module("proxyshop.templates"), template['class_name'])

    # Plugin template
    spec = util.spec_from_file_location("templates", template['plugin_path'])
    temp_mod = util.module_from_spec(spec)
    spec.loader.exec_module(temp_mod)
    return getattr(temp_mod, template['class_name'])


def get_templates() -> dict[str, list[TemplateDetails]]:
    """
    Generate a dictionary of templates using app included json and any plugins.
    @return: Dictionary of lists containing template details.
    """
    # Plugin folders
    folders = glob(os.path.join(cwd, "proxyshop\\plugins\\*\\"))

    # Process the default templates.json
    with open(os.path.join(cwd, "proxyshop\\templates.json"), encoding="utf-8") as f:
        app_json = json.load(f)
        main_json = {}
        for card_type, templates in app_json.items():
            main_json[card_type] = []
            named_type = get_named_type(card_type)
            for name, class_name in templates.items():
                main_json[card_type].append({
                    "plugin_path": None,
                    "config_path": osp.join(cwd, f"proxyshop/configs/{class_name}.json"),
                    "class_name": class_name,
                    "name": name,
                    "type": named_type
                })

    # Iterate through plugin folders
    for folder in folders:
        # Guard clauses
        if Path(folder).stem == "__pycache__": continue
        json_file = osp.join(folder, 'template_map.json')
        py_file = osp.join(folder, 'templates.py')
        if not osp.exists(json_file) and not osp.exists(py_file):
            continue

        # Load json
        with open(json_file, "r", encoding="utf-8") as f:
            plugin_json = json.load(f)

        # Add plugin folder to Python environment
        sys.path.append(folder)

        # Add plugin templates to dictionary
        for card_type, templates in plugin_json.items():
            named_type = get_named_type(card_type)
            for name, class_name in templates.items():
                main_json[card_type].append({
                    "plugin_path": py_file,
                    "config_path": py_file.replace('templates.py', f'configs/{class_name}.json'),
                    "class_name": class_name,
                    "name": name,
                    "type": named_type
                })
    return main_json


def get_template_details(
    named_type: str,
    name: str,
    templates: dict[str, list[TemplateDetails]] = None
) -> dict[str, TemplateDetails]:
    """
    Retrieve the full template details given a named type and a name.
    @param named_type: Displayed type name, ex: MDFC
    @param name: Displayed name of the template
    @param templates: Dictionary of templates
    @return:
    """
    # Get templates if not provided
    if not templates:
        templates = get_templates()

    # Get the scryfall appropriate type(s) for this template
    result = {}
    for layout in card_types[named_type]:
        for template in templates[layout]:
            if template['name'] == name:
                result[layout] = template
    return result


def get_my_templates(provided: dict[str, str]) -> dict[str, TemplateDetails]:
    """
    Retrieve templates based on user selection
    @param provided: Provided templates to look up details for.
    @return: A dict of templates matching each layout type.
    """
    result = {}
    selected = {}
    templates = get_templates()

    # Loop through our selected templates and get their details
    for named_type, name in provided.items():
        selected.update(get_template_details(named_type, name, templates))

    # Loop through all template types, use the ones selected or Normal for default
    for card_type, temps in templates.items():
        if card_type in selected:
            result[card_type] = selected[card_type]
        else:
            for template in temps:
                if template['name'] == "Normal":
                    result[card_type] = template
    return result


"""
CARD FUNCTIONS
"""


def retrieve_card_info(filename: Union[str, Path]) -> CardDetails:
    """
    Retrieve card name and (if specified) artist from the input file.
    """
    # Extract just the card name
    fname = os.path.basename(str(filename))
    sep = [' {', ' [', ' (']
    fn_split = re.split('|'.join(map(re.escape, sep)), os.path.splitext(fname)[0])
    name = fn_split[0]

    # Match pattern
    artist = reg_artist.findall(fname)
    set_code = reg_set.findall(fname)
    creator = reg_creator.findall(fname)

    # Check for these values
    creator = creator[0] if creator else ''
    artist = artist[0] if artist else ''
    set_code = set_code[0] if set_code else ''

    # Correct strange set codes like promo variants (PMID)
    if (
        set_code and
        set_code.upper() not in con.set_symbols and
        set_code.upper()[1:] in con.set_symbols
    ):
        set_code = set_code[1:]

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


def check_for_updates() -> dict:
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
        s3_enabled = data['__CONFIG__']['S3']
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
                temp['s3'] = s3_enabled

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
            s3_enabled = False
            if "__CONFIG__" in data:
                if "S3" in data['__CONFIG__']:
                    s3_enabled = data['__CONFIG__']['S3']
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
                    temp['s3'] = s3_enabled

                    # Does this template need an update?
                    file = version_check(temp, plug['name'])
                    if file:
                        if cat not in updates:
                            updates[cat] = [file]
                        else:
                            updates[cat].append(file)

    # Return dict of templates needing updates
    return updates


def version_check(temp: dict, plugin: Optional[str] = None) -> Optional[dict]:
    """
    Check if a given file is up-to-date based on the live file metadata.
    @param temp: Template json data from the manifest
    @param plugin: Plugin name, optional
    @return: Dict of file details if it needs and update, otherwise None
    """
    # Get our current version

    # Get our basic metadata dict
    data = gdrive_metadata(temp['id'])
    if not data or 'name' not in data:
        # Gdrive couldn't locate the file
        print(temp['name'], "couldn't be located!")
        return
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
    if file['version_old'] != file['version_new']:
        return file
    return


def get_current_version(file_id: str, path: str) -> Optional[str]:
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


def update_template(temp: dict, callback: Callable) -> bool:
    """
    Update a given template to the latest version.
    @param temp: Dict containing template information.
    @param callback: Callback method to update progress bar.
    """
    # Download using authorization
    try:
        result = update.download_google(temp['id'], temp['path'], callback)
        if not result:
            if temp['s3']:
                # Try grabbing from Amazon S3 instead
                result = update.download_s3(temp, callback)
    except Exception as e:
        print(e)
        return False

    # Change the version to match the new version
    if result:
        con.versions[temp['id']] = temp['version_new']
        con.update_version_tracker()
    return result


def gdrive_metadata(file_id: str) -> dict:
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


def import_json_config(path: str) -> dict:
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
