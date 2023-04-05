"""
File Utilities
"""
import json
import shutil
from configparser import ConfigParser
from os import path as osp
from os import remove
from pathlib import Path


def verify_config_fields(ini_file: str, json_file: str):
    """
    Validate that all settings fields present in a given json data are present in config file.
    If any are missing, add them and return
    @param ini_file: Config file to verify contains the proper fields.
    @param json_file: Json file containing config fields to check for.
    """
    # Track data
    data = {}
    changed = False

    # Load the json
    if not osp.exists(json_file):
        return
    with open(json_file, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Load the config
    conf_file = ConfigParser(allow_no_value=True)
    conf_file.optionxform = str
    if not osp.exists(ini_file):
        # Create a blank file if it doesn't exist
        with open(ini_file, "w", encoding="utf-8") as f:
            conf_file.write(f)
    with open(ini_file, "r", encoding="utf-8") as f:
        conf_file.read_file(f)

    # Build a dictionary of the necessary values
    for row in raw:
        # Add row if it's not a title
        if row['type'] == 'title':
            continue
        data.setdefault(row['section'], []).append({
            'key': row.get('key', ''),
            'value': row.get('default', 0)
        })

    # Add the data to ini where missing
    for section, settings in data.items():
        # Check if the section exists
        if not conf_file.has_section(section):
            conf_file.add_section(section)
            changed = True
        # Check if each setting exists
        for setting in settings:
            if not conf_file.has_option(section, setting['key']):
                conf_file.set(section, setting['key'], str(setting['value']))
                changed = True

    # If ini has changed, write changes
    if changed:
        with open(ini_file, "w", encoding="utf-8") as f:
            conf_file.write(f)


def get_valid_config_json(json_file: str):
    """
    Return valid JSON data for use with settings panel.
    @param json_file: Path to json file.
    @return: Json string dump of validated data.
    """
    # Load the json
    with open(json_file, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Remove unsupported keys
    for row in raw:
        if 'default' in row:
            row.pop('default')

    # Return json data
    return json.dumps(raw)


def copy_config_or_verify(path_from: str, path_to: str, validate_json: str) -> None:
    """
    Copy one config to another, or verify it if it exists.
    @param path_from: Path to the file to be copied.
    @param path_to: Path to the file to create, if it doesn't exist.
    @param validate_json: JSON settins to validate if the file exists.
    """
    if osp.isfile(path_to):
        verify_config_fields(path_to, validate_json)
    else:
        shutil.copy(path_from, path_to)


def remove_config_file(ini_file: str) -> bool:
    """
    Check if config file exists, then remove it.
    @return: True if removed, False if not.
    """
    if osp.isfile(ini_file):
        try:
            remove(ini_file)
            return True
        except OSError:
            return False
    return False


def ensure_path_exists(path: str):
    """
    Ensure that directories in path exists.
    @param path:
    @return:
    """
    Path(osp.dirname(path)).mkdir(mode=511, parents=True, exist_ok=True)
