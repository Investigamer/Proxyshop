"""
LOADS PLUGINS AND TEMPLATES
"""
import os
import re
import sys
import json
from multiprocessing import cpu_count

import requests
import os.path as osp
from glob import glob
from pathlib import Path
from concurrent import futures
from typing import Optional, Callable, Union, Iterator
from importlib import util, import_module

from src import update
from src.constants import con
from src.utils.types_cards import CardDetails
from src.utils.types_templates import TemplateDetails, TemplateUpdate

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
    "Class": ["class"],
    "Miracle": ["miracle"],
    "Snow": ["snow"],
    "Planar": ["planar"]
}

reg_artist = re.compile(r'\(+(.*?)\)')
reg_set = re.compile(r'\[(.*)]')
reg_number = re.compile(r'{(.*)}')


"""
TEMPLATE FUNCTIONS
"""


def get_named_type(layout_class: str) -> str:
    """
    Finds the named type for a given layout class.
    @param layout_class: Scryfall authentic layout type, ex: mdfc_font
    @return: Displayed name of that type, ex: MDFC
    """
    for name, types in card_types.items():
        if layout_class in types:
            return name
    return 'Normal'


def get_template_class(template: TemplateDetails) -> Callable:
    """
    Get template based on input and layout
    """
    # Built-in template?
    if not template['plugin_path']:
        return getattr(import_module("src.templates"), template['class_name'])

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
    # Track names for uniqueness
    names = {}

    # Plugin folders and main data to return
    data: dict[str, list[TemplateDetails]] = {}

    # Load the built-in templates
    with open(os.path.join(con.path_data, "app_manifest.json"), encoding="utf-8") as f:
        app_json = json.load(f)

    # Build a TemplateDetails for each template
    for card_type, templates in app_json.items():
        # Get the display name of the type and build our details
        named_type = get_named_type(card_type)
        data[card_type] = [
            {
                "id": template['id'] if 'id' in template else None,
                "name": name,
                "type": named_type,
                "layout": card_type,
                "class_name": template['class'],
                "config_path": osp.join(con.path_src, f"configs/{template['class']}.json"),
                "preview_path": osp.join(con.path_img, f"{template['class']}.jpg"),
                "template_path": osp.join(con.cwd, f"templates/{template['file']}"),
                "plugin_path": None,
            } for name, template in templates.items()
        ]

        # Update our name checker
        names[card_type] = [template['name'] for template in data[card_type]]

    # Iterate through plugin folders
    for folder in glob(os.path.join(con.path_plugins, "*\\")):
        # Mandatory paths
        py_file = osp.join(folder, 'templates.py')
        json_file = osp.join(folder, 'manifest.json')

        # Ensure mandatory paths exist
        if not osp.exists(json_file) or not osp.exists(py_file):
            continue

        # Load json
        with open(json_file, "r", encoding="utf-8") as f:
            plugin_json = json.load(f)

        # Add plugin folder to Python environment
        sys.path.append(folder)

        # Generate TemplateDetails for plugin templates
        for card_type, templates in plugin_json.items():
            # Get the display name of the type and build our details
            named_type = get_named_type(card_type)
            for name, template in templates.items():
                # Is the name unique?
                if name in names[card_type]:
                    name = f"{name} ({os.path.basename(os.path.normpath(folder))})"
                # If name still not unique, skip
                if name in names[card_type]:
                    continue
                names[card_type].append(name)
                data[card_type].append({
                    "id": template['id'] if 'id' in template else None,
                    "name": name,
                    "type": named_type,
                    "layout": card_type,
                    "class_name": template['class'],
                    "plugin_path": py_file,
                    "config_path": osp.join(folder, f"configs/{template['class']}.json"),
                    "preview_path": osp.join(folder, f"img/{template['class']}.jpg"),
                    'template_path': osp.join(folder, f"templates/{template['file']}"),

                })

    # Sort alphabetically, with "Normal" at the top of each list
    for key in data:
        templates = data[key]
        templates_sorted = sorted(templates, key=lambda x: x['name'])
        normal_template = next((x for x in templates_sorted if x['name'] == 'Normal'), None)
        if normal_template:
            templates_sorted.remove(normal_template)
            templates_sorted.insert(0, normal_template)
        data[key] = templates_sorted

    return data


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
    Retrieve templates based on user selection.
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
            result[card_type] = selected.get(card_type)
        else:
            for template in temps:
                if template['name'] == "Normal":
                    result[card_type] = template
    return result


"""
CARD FUNCTIONS
"""


def retrieve_card_info(file_path: Union[str, Path]) -> CardDetails:
    """
    Retrieve card name and (if specified) artist from the input file.
    """
    # Extract just the card name
    sep = [' [', ' (', ' {', '$']
    file_name = os.path.basename(str(file_path))
    fn_split = re.split('|'.join(map(re.escape, sep)), os.path.splitext(file_name)[0])

    # Match pattern and format data
    artist = reg_artist.findall(file_name)
    number = reg_number.findall(file_name)
    set_code = reg_set.findall(file_name)

    # Return dictionary
    return {
        'name': fn_split[0],
        'filename': file_path,
        'artist': artist[0] if artist else '',
        'set': set_code[0] if set_code else '',
        'number': number[0] if number and set_code else '',
        'creator': fn_split[-1] if '$' in file_name else None,
    }


"""
UPDATE FUNCTIONS
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
    with futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        results: Iterator[TemplateUpdate] = executor.map(version_check, unique_temps)

    # Ensure executor is finished before building return
    results = list(results)
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
        # Download using Google Drive
        result = update.download_google(temp['id'], temp['path'], callback)
        if not result and not temp['plugin']:
            # Google Drive failed, download from Amazon S3
            url = f"{temp['plugin']}/{temp['filename']}" if temp['plugin'] else temp['filename']
            result = update.download_s3(temp['path'], url, callback)
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
            'key': con.google_api
        }
    ).json()
    return result if 'name' in result and 'size' in result else None


"""
HEADLESS CONSOLE
"""


class Console:
    """
    Replaces the GUI console when running headless.
    """

    @staticmethod
    def update(msg):
        print(msg)

    @staticmethod
    def wait(msg):
        print(msg)
        input("Would you like to continue?")
