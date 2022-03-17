"""
LOADS PLUGINS AND TEMPLATES
"""
import os
import json
import configparser
from glob import glob
from pathlib import Path
from importlib import import_module
cwd = os.getcwd()

def get_template(template, layout):
    """
    Get template based on input and layout
    """

    # Get templates json
    templates = get_templates()

    # Select our template
    if layout in templates:
        if template in templates[layout]["other"]:
            selected_template = templates[layout]["other"][template]
        else: selected_template = templates[layout]["default"]
    else: return None
    return getattr(import_module(selected_template[0]), selected_template[1])

def get_templates ():
    """
    Roll templates from our plugins into our main json
    """

    # Plugin folders
    folders = glob(os.path.join(cwd, "plugins\\*\\"))

    # Get our main json
    with open(os.path.join(cwd, "proxyshop\\templates.json"), encoding="utf-8") as json_file:
        main_json = json.load(json_file)

    # Iterate through folders
    for folder in folders:
        if Path(folder).stem == "__pycache__": pass
        else:
            j = []
            make_default = False
            for name in os.listdir(folder):

                # Load json
                if name == "template_map.json":
                    with open(os.path.join(cwd, f"plugins\\{Path(folder).stem}\\{name}"), encoding="utf-8") as this_json:
                        j = json.load(this_json)

                # Load config
                if name == "config.ini":
                    # Import our config file
                    conf = configparser.ConfigParser(allow_no_value=True)
                    conf.read(os.path.join(cwd, f"plugins\\{Path(folder).stem}\\{name}"), encoding="utf-8")
                    try: make_default = conf.getboolean('CONF', 'Make.Default')
                    except: make_default = False

            # Loop through keys in plugin json
            try:
                for key in j.keys():
                    # Key present in original?
                    if key in main_json:
                        # Append additions
                        main_json[key]["other"].update(j[key]["other"])
                        # Change the default?
                        if "default" in j[key] and make_default:
                            main_json[key]["default"] = j[key]["default"]
                    else:
                        # New layout
                        main_json[key] = j[key]
            except: pass

    return main_json

def get_template_class(template):
    """
    Return class for given template
    """
    return getattr(import_module(template[0]), template[1])