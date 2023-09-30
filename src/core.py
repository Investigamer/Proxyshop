"""
LOADS PLUGINS AND TEMPLATES
"""
# Standard Library Imports
import os
import sys
import json
import os.path as osp
from typing import Callable
from importlib import import_module

# Local Imports
from src.constants import con
from src.settings import cfg
from src.utils.modules import get_loaded_module
from src.types.templates import TemplateDetails, TemplateManifest


"""
TEMPLATE FUNCTIONS
"""


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
        app_json: TemplateManifest = json.load(f)

    # Build a TemplateDetails for each template
    for card_type, templates in app_json.items():
        data[card_type] = [
            {
                "id": template['id'] if 'id' in template else None,
                "name": name,
                "layout": card_type,
                "class_name": template['class'],
                "type": con.card_type_map_raw.get(card_type, 'Normal'),
                "config_path": osp.join(con.path_configs, f"{template['class']}.json"),
                "preview_path": osp.join(con.path_img, f"{template['class']}.jpg"),
                "template_path": osp.join(con.path_templates, template['file']),
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
            plugin_json: TemplateManifest = json.load(f)

        # Add plugin folder to Python environment
        sys.path.append(folder.path)

        # Generate TemplateDetails for plugin templates
        for card_type, templates in plugin_json.items():
            # Get the display name of the type and build our details
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
                    "layout": card_type,
                    "type": con.card_type_map_raw.get(card_type, 'Normal'),
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
    named_type: str, name: str,
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
    templates = templates or get_templates()

    # Get the scryfall appropriate type(s) for this template
    return {
        layout: template for
        layout in con.card_type_map[named_type] for
        template in templates[layout] if template['name'] == name
    }


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
