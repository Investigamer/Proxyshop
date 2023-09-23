"""
LOADS PLUGINS AND TEMPLATES
"""
# Standard Library Imports
import os
import sys
import json
import os.path as osp
from pathlib import Path
from concurrent import futures
from typing import Optional, Callable, Union, Iterator
from importlib import import_module
from multiprocessing import cpu_count

# Third Party Imports
import requests

# Local Imports
from src.constants import con
from src.settings import cfg
from src.utils.modules import get_loaded_module
from src.utils.regex import Reg
from src.utils.types_cards import CardDetails
from src.utils.download import download_s3, download_google
from src.utils.env import ENV_VERSION, ENV_API_GOOGLE
from src.utils.types_templates import TemplateDetails, TemplateUpdate

# All Template types
card_types = {
    "Normal": ["normal"],
    "MDFC": ["mdfc_front", "mdfc_back"],
    "Transform": ["transform_front", "transform_back"],
    "Planeswalker": ["planeswalker"],
    "PW MDFC": ["pw_mdfc_front", "pw_mdfc_back"],
    "PW TF": ["pw_tf_front", "pw_tf_back"],
    "Basic": ["basic"],
    "Ixalan": ["ixalan"],
    "Mutate": ["mutate"],
    "Prototype": ["prototype"],
    "Adventure": ["adventure"],
    "Leveler": ["leveler"],
    "Saga": ["saga"],
    "Split": ["split"],
    "Class": ["class"],
    "Battle": ["battle"],
    "Token": ["token"],
    "Miracle": ["miracle"],
    "Snow": ["snow"],
    "Planar": ["planar"]
}


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
    @param template: Dict containing template details.
    @return: Class from this template's module.
    """
    # Built-in template?
    if not template['plugin_path']:
        return getattr(import_module("src.templates"), template['class_name'])

    # Load the plugin module, use hot-loading if enabled
    module = get_loaded_module(
        template['plugin_path'],
        f"templates.{template['plugin_name']}",
        cfg.refresh_plugins
    )
    return getattr(module, template['class_name'])


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
    with open(os.path.join(con.path_data, "app_templates.json"), encoding="utf-8") as f:
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
                "plugin_name": None,
                "plugin_path": None,
            } for name, template in templates.items()
        ]

        # Update our name checker
        names[card_type] = [template['name'] for template in data[card_type]]

    # Iterate through plugin folders
    for folder in [f for f in os.scandir(con.path_plugins) if f.is_dir()]:
        # Mandatory paths
        py_file = osp.join(folder.path, 'templates.py')
        json_file = osp.join(folder.path, 'manifest.json')

        # Ensure mandatory paths exist
        if not osp.exists(json_file) or not osp.exists(py_file):
            continue

        # Load json
        with open(json_file, "r", encoding="utf-8") as f:
            plugin_json = json.load(f)

        # Add plugin folder to Python environment
        sys.path.append(folder.path)

        # Generate TemplateDetails for plugin templates
        for card_type, templates in plugin_json.items():
            # Get the display name of the type and build our details
            named_type = get_named_type(card_type)
            for name, template in templates.items():
                # Is the name unique?
                if name in names[card_type]:
                    name = f"{name} ({folder.name})"
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
                    "plugin_name": str(folder.name),
                    "plugin_path": py_file,
                    "config_path": osp.join(folder.path, f"configs/{template['class']}.json"),
                    "preview_path": osp.join(folder.path, f"img/{template['class']}.jpg"),
                    'template_path': osp.join(folder.path, f"templates/{template['file']}"),

                })

    # Return the templates sorted
    return sort_templates(data)


def sort_templates(data: dict[str, list[TemplateDetails]]) -> dict[str, list[TemplateDetails]]:
    """
    Sort each template type by template name, but forcing "Normal" templates to the beginning of list.
    @param data: Unsorted dict of TemplateDetails, with each key representing a card type.
    @return: Sorted dict of TemplateDetails.
    """
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
    @return: Dict of TemplateDetails with each key being a card type.
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
    Retrieve card name from the input file, and optional tags (artist, set, number).
    @param file_path: Path to the image file.
    @return: Dict of card details.
    """
    # Extract just the card name
    file_name = os.path.basename(str(file_path))
    fn_split = Reg.PATH_SPLIT.split(os.path.splitext(file_name)[0])

    # Match pattern and format data
    artist = Reg.PATH_ARTIST.search(file_name)
    number = Reg.PATH_NUM.search(file_name)
    code = Reg.PATH_SET.search(file_name)

    # Return dictionary
    return {
        'name': fn_split[0].strip(),
        'filename': file_path,
        'artist': artist.group(1) if artist else '',
        'set': code.group(1) if code else '',
        'number': number.group(1) if number and code else '',
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
            'key': ENV_API_GOOGLE
        }
    ).json()
    return result if 'name' in result and 'size' in result else None


def check_app_version() -> bool:
    """
    Check if app is the latest version.
    @return: Return True if up to date, otherwise False.
    """
    try:
        current = f"v{ENV_VERSION}"
        response = requests.get(
            "https://api.github.com/repos/MrTeferi/Proxyshop/releases/latest",
            timeout=(3, 3))
        latest = response.json().get("tag_name", current)
        return bool(current == latest)
    except (requests.HTTPError, json.JSONDecodeError):
        return True
