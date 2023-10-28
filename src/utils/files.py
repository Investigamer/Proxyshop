"""
FILE UTILITIES
"""
# Standard Library Imports
import os
import json
import shutil
from configparser import ConfigParser
from os import path as osp
from os import remove
from pathlib import Path
from typing import Optional, TypedDict, Callable, Union, Literal


# Third Party Imports
from yaml import (
    load as yaml_load,
    dump as yaml_dump,
    Loader as yamlLoader,
    Dumper as yamlDumper)
from tomlkit import dump as toml_dump, load as toml_load

# Local Imports
from src.constants import con


class DataFileType (TypedDict):
    """Data file type (json, toml, yaml, etc)."""
    load: Callable
    dump: Callable
    load_kw: dict[str, Union[Callable, bool, str]]
    dump_kw: dict[str, Union[Callable, bool, str]]


# Data types for loading test case files
data_types: dict[str, DataFileType] = {
    'toml': {
        'load': toml_load, 'load_kw': {},
        'dump': toml_dump, 'dump_kw': {'sort_keys': True}
    },
    'yaml': {
        'load': yaml_load, 'load_kw': {'Loader': yamlLoader},
        'dump': yaml_dump, 'dump_kw': {
            'Dumper': yamlDumper,
            'sort_keys': True,
            'indent': 2,
            'allow_unicode': True}
    },
    'json': {
        'load': json.load, 'load_kw': {},
        'dump': json.dump, 'dump_kw': {
            'sort_keys': True,
            'indent': 2,
            'ensure_ascii': False
        }
    }
}


"""
FILE INFO UTILITIES
"""


def get_file_size_mb(file_path: str, decimal: int = 1) -> float:
    """
    Get a file's size in megabytes rounded.
    @param file_path: Path to the file.
    @param decimal: Number of decimal places to allow when rounding.
    @return: Float representing the filesize in megabytes rounded.
    """
    return round(os.path.getsize(file_path) / (1024 * 1024), decimal)


"""
DATA FILE UTILS
"""


def load_data_file(
    data_type: Literal['json', 'toml', 'yaml'] = 'toml',
    file_name: str = 'frame_data',
    file_path: Union[str, Path] = 'tests',
    config: Optional[dict] = None
) -> Union[list, dict, tuple, set]:
    """
    Load object from a data file.
    @param data_type: Data file type, supports json, toml, and yaml.
    @param file_name: Name of the file (not including extension).
    @param file_path: Path to the file, starting at data directory.
    @param config: Dict data to modify DataFileType configuration for this data load procedure.
    @return: Iterable/table object loaded from data file.
    """
    parser: DataFileType = data_types.get(data_type, {})
    parser.update(config if config else {})
    with open(osp.join(con.path_data, file_path, f'{file_name}.{data_type}'), 'r', encoding='utf-8') as f:
        return parser['load'](f, **parser['load_kw'])


def dump_data_file(
    obj: Union[list, dict, tuple, set],
    data_type: Literal['json', 'toml', 'yaml'] = 'toml',
    file_name: str = 'frame_data',
    file_path: Union[str, Path] = 'tests',
    config: Optional[dict] = None
) -> None:
    """
    Dump object to a data file.
    @param obj: Iterable/table object to save to data file.
    @param data_type: Data file type, supports json, toml, and yaml.
    @param file_name: Name of the file (not including extension).
    @param file_path: Path to the file, starting at data directory.
    @param config: Dict data to modify DataFileType configuration for this data dump procedure.
    """
    parser: DataFileType = data_types.get(data_type, {})
    parser.update(config if config else {})
    with open(osp.join(con.path_data, file_path, f'{file_name}.{data_type}'), 'w', encoding='utf-8') as f:
        parser['dump'](obj, f, **parser['dump_kw'])


"""
CONFIG FILES
"""


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


"""
PATHS AND FILENAMES
"""


def ensure_path_exists(path: str):
    """
    Ensure that directories in path exists.
    @param path:
    @return:
    """
    Path(osp.dirname(path)).mkdir(mode=711, parents=True, exist_ok=True)


def get_unique_filename(path: str, name: str, ext: str, suffix: str):
    """
    If a filepath exists, number the file according to the lowest number that doesn't exist.
    @param path: Path to the file.
    @param name: Name of the file.
    @param ext: Extension of the file.
    @param suffix: Suffix to add before the number.
    @return: Unique filename.
    """
    num = 0
    new_name = f"{name} ({suffix})" if suffix else name
    suffix = f' ({suffix}'+' {})' if suffix else ' ({})'
    while osp.isfile(osp.join(path, f"{new_name}{ext}")):
        num += 1
        new_name = name + suffix.format(num)
    return new_name
