"""
* File Utilities
"""
# Standard Library Imports
import os
import json
import shutil
from configparser import ConfigParser
from contextlib import suppress
from os import path as osp
from os import remove
from pathlib import Path
from typing import Optional, TypedDict, Callable, Union
from threading import Lock

# Third Party Imports
from yaml import (
    load as yaml_load,
    dump as yaml_dump,
    Loader as yamlLoader,
    Dumper as yamlDumper)
from tomlkit import dump as toml_dump, load as toml_load

# Local Imports
from src.utils.strings import msg_bold

"""
* Types
"""


class DataFileType (TypedDict):
    """Data file type (json, toml, yaml, etc)."""
    load: Callable
    dump: Callable
    load_kw: dict[str, Union[Callable, bool, str]]
    dump_kw: dict[str, Union[Callable, bool, str]]


"""
* Constants
"""

# File util locking mechanism
util_file_lock = Lock()

# Data types for loading test case files
data_types: dict[str, DataFileType] = {
    'toml': {
        'load': toml_load, 'load_kw': {},
        'dump': toml_dump, 'dump_kw': {'sort_keys': True}
    },
    'yml': {
        'load': yaml_load, 'load_kw': {'Loader': yamlLoader},
        'dump': yaml_dump, 'dump_kw': {
            'Dumper': yamlDumper,
            'sort_keys': True,
            'indent': 2,
            'allow_unicode': True}
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
* File Info Utils
"""


def get_file_size_mb(file_path: Union[str, os.PathLike], decimal: int = 1) -> float:
    """
    Get a file's size in megabytes rounded.
    @param file_path: Path to the file.
    @param decimal: Number of decimal places to allow when rounding.
    @return: Float representing the filesize in megabytes rounded.
    """
    return round(os.path.getsize(file_path) / (1024 * 1024), decimal)


"""
* Data File Utils
"""


def load_data_file(
    data_file: Union[str, os.PathLike],
    config: Optional[dict] = None
) -> Union[list, dict, tuple, set]:
    """
    Load object from a data file.
    @param data_file: Path to the data file to be loaded.
    @param config: Dict data to modify DataFileType configuration for this data load procedure.
    @return: Iterable or dict object loaded from data file.
    @raise ValueError: If data file type not supported.
    @raise OSError: If loading data file fails.
    """
    data_type = Path(data_file).suffix[1:]
    parser: DataFileType = data_types.get(data_type, {}).copy()
    if not parser:
        raise ValueError("Data file provided does not match a supported data file type.\n"
                         f"Types supported: {', '.join(data_types.keys())}\n"
                         f"Type received: {data_type}")
    if config:
        parser.update(config)
    with util_file_lock:
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                return parser['load'](f, **parser['load_kw']) or {}
            except Exception as e:
                raise OSError(f"Unable to load data from data file:\n{data_file}") from e


def dump_data_file(
    obj: Union[list, dict, tuple, set],
    data_file: Union[str, os.PathLike],
    config: Optional[dict] = None
) -> None:
    """
    Dump object to a data file.
    @param obj: Iterable or dict object to save to data file.
    @param data_file: Path to the data file to be dumps.
    @param config: Dict data to modify DataFileType configuration for this data dump procedure.
    @raise ValueError: If data file type not supported.
    @raise OSError: If dumping to data file fails.
    """
    data_type = Path(data_file).suffix[1:]
    parser: DataFileType = data_types.get(data_type, {})
    if not parser:
        raise ValueError("Data file provided does not match a supported data file type.\n"
                         f"Types supported: {', '.join(data_types.keys())}\n"
                         f"Type received: {data_type}")
    if config:
        parser.update(config)
    with util_file_lock:
        with open(data_file, 'w', encoding='utf-8') as f:
            try:
                parser['dump'](obj, f, **parser['dump_kw'])
            except Exception as e:
                raise OSError(f"Unable to dump data to data file:\n{data_file}") from e


"""
* Config File Utils
"""


def verify_config_fields(ini_file: Path, data_file: Path) -> None:
    """
    Validate that all settings fields present in a given json data are present in config file.
    If any are missing, add them and return
    @param ini_file: Config file to verify contains the proper fields.
    @param data_file: Data file containing config fields to check for, JSON or TOML.
    """
    # Track data and changes
    data, changed = {}, False

    # Data file doesn't exist or is unsupported data type
    if not data_file.is_file() or data_file.suffix not in ['.toml', '.json']:
        return

    # Load data from JSON or TOML file
    raw = load_data_file(data_file)
    raw = parse_kivy_config_toml(raw) if data_file.suffix == '.toml' else raw

    # Ensure INI file exists and load ConfigParser
    ensure_path_exists(ini_file)
    config = get_config_object(ini_file)

    # Build a dictionary of the necessary values
    for row in raw:
        # Add row if it's not a title
        if row.get('type', 'title') == 'title':
            continue
        data.setdefault(
            row.get('section', 'BROKEN'), []
        ).append({
            'key': row.get('key', ''),
            'value': row.get('default', 0)
        })

    # Add the data to ini where missing
    for section, settings in data.items():
        # Check if the section exists
        if not config.has_section(section):
            config.add_section(section)
            changed = True
        # Check if each setting exists
        for setting in settings:
            if not config.has_option(section, setting['key']):
                config.set(section, setting['key'], str(setting['value']))
                changed = True

    # If ini has changed, write changes
    if changed:
        with open(ini_file, "w", encoding="utf-8") as f:
            config.write(f)


def parse_kivy_config_json(raw: list[dict]) -> list[dict]:
    """
    Parse config JSON data for use with Kivy settings panel.
    @param raw: Raw loaded JSON data.
    @return: Properly parsed data safe for use with Kivy.
    """
    # Remove unsupported keys
    for row in raw:
        if 'default' in row:
            row.pop('default')
    return raw


def parse_kivy_config_toml(raw: dict) -> list[dict]:
    """
    Parse config TOML data for use with Kivy settings panel.
    @param raw: Raw loaded TOML data.
    @return: Properly parsed data safe for use with Kivy.
    """

    # Process __CONFIG__ header if present
    cfg_header = raw.pop('__CONFIG__', {})
    prefix = cfg_header.get('prefix', '')

    # Process data
    data: list[dict] = []
    for section, settings in raw.items():

        # Add section title if it exists
        if title := settings.pop('title', None):
            data.append({
                'type': 'title',
                'title': title
            })

        # Add each setting within this section
        for key, field in settings.items():

            # Establish data type and default value
            data_type = field.get('type', 'bool')
            display_default = default = field.get('default', 0)
            if data_type == 'bool':
                display_default = 'True' if default else 'False'
            elif data_type in ['string', 'options', 'path']:
                display_default = f"'{default}'"
            setting = {
                'type': data_type,
                'title': msg_bold(field.get('title', 'Broken Setting')),
                'desc': f"{field.get('desc', '')}\n"
                        f"{msg_bold(f'(Default: {display_default})')}",
                'section': f'{prefix}.{section}' if prefix else section,
                'key': key, 'default': default}
            if options := field.get('options'):
                setting['options'] = options
            data.append(setting)

    # Return parsed data
    return data


def get_kivy_config_from_schema(config: Path) -> str:
    """
    Return valid JSON data for use with Kivy settings panel.
    @param config: Path to config schema file, JSON or TOML.
    @return: Json string dump of validated data.
    """
    # Need to load data as JSON
    raw = load_data_file(data_file=config)

    # Use correct parser
    if config.suffix == '.toml':
        raw = parse_kivy_config_toml(raw)
    return json.dumps(parse_kivy_config_json(raw))


def copy_config_or_verify(path_from: Path, path_to: Path, data_file: Path) -> None:
    """
    Copy one config to another, or verify it if it exists.
    @param path_from: Path to the file to be copied.
    @param path_to: Path to the file to create, if it doesn't exist.
    @param data_file: Data schema file to use for validating an existing INI file.
    """
    if osp.isfile(path_to):
        return verify_config_fields(path_to, data_file)
    shutil.copy(path_from, path_to)


def remove_config_file(ini_file: str) -> bool:
    """
    Check if config file exists, then remove it.
    @return: True if removed, False if not.
    """
    if osp.isfile(ini_file):
        with suppress(Exception):
            remove(ini_file)
            return True
    return False


def get_config_object(path: Union[str, os.PathLike, list[Union[str, os.PathLike]]]) -> ConfigParser:
    """
    Returns a ConfigParser object using a valid ini path.
    @param path: Path to ini config file.
    @return: ConfigParser object.
    @raise: ValueError if valid ini file wasn't received.
    """
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(path, encoding='utf-8')
    return config


"""
* Paths and filenames
"""


def check_valid_file(path: Union[str, os.PathLike], ext: Optional[str] = None) -> bool:
    """
    Checks if a file path provided exists, optionally validate an extension type.
    @param path: Path to the file to verify.
    @param ext: Extension to check, if provided.
    @return: True if file is valid, otherwise False.
    """
    with suppress(Exception):
        check = str(path).lower()
        if osp.isfile(check):
            if ext:
                ext = (ext if ext.startswith('.') else f'.{ext}').lower()
                if not check.endswith(ext):
                    return False
            return True
    return False


def ensure_path_exists(path: Union[str, os.PathLike]) -> None:
    """
    Ensure that directories in path exists.
    @param path: Folder path to check and create if necessary.
    """
    Path(osp.dirname(path)).mkdir(mode=711, parents=True, exist_ok=True)


def get_unique_filename(path: Union[str, os.PathLike], name: str, ext: str, suffix: str) -> str:
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
    while Path(path, f"{new_name}{ext}").is_file():
        num += 1
        new_name = f"{name}{suffix.format(num)}"
    return new_name
