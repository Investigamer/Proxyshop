"""
* Utils: Files
"""
# Standard Library Imports
import os
import json
import shutil
from configparser import ConfigParser
from contextlib import suppress
from pathlib import Path
from typing import Optional, TypedDict, Callable, Union, Iterator
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


"""Data File: TOML (.toml) data type."""
DataFileTOML = DataFileType(
    load=toml_load,
    dump=toml_dump,
    load_kw={},
    dump_kw={'sort_keys': True})

"""Data File: YAML (.yaml) data type."""
DataFileYAML = DataFileType(
    load=yaml_load,
    dump=yaml_dump,
    load_kw={
        'Loader': yamlLoader},
    dump_kw={
        'allow_unicode': True,
        'Dumper': yamlDumper,
        'sort_keys': True,
        'indent': 2,
    })

"""Data File: JSON (.json) data type."""
DataFileJSON = DataFileType(
    load=json.load,
    dump=json.dump,
    load_kw={},
    dump_kw={
        'sort_keys': True,
        'indent': 2,
        'ensure_ascii': False
    })


"""
* Constants
"""

# File util locking mechanism
util_file_lock = Lock()

# Data types alias map
data_types: dict[str, DataFileType] = {
    '.toml': DataFileTOML,
    '.yaml': DataFileYAML,
    '.yml': DataFileYAML,
    '.json': DataFileJSON,
}
supported_data_types = tuple(data_types.keys())

"""
* Data File Utils
"""


def validate_data_type(path: Path) -> None:
    """Checks if a data file matches a supported data file type.

    Args:
        path: Path to the data file.

    Raises:
        ValueError: If data file type not supported.
    """
    # Check if data file is a supported data type
    if path.suffix.lower() not in supported_data_types:
        raise ValueError("Data file provided does not match a supported data file type.\n"
                         f"Types supported: {', '.join(supported_data_types)}\n"
                         f"Type received: {path.suffix}")


def validate_data_file(path: Path) -> None:
    """Checks if a data file exists and is a valid data file type. Raises an exception if validation fails.

    Args:
        path: Path to the data file.

    Raises:
        FileNotFoundError: If data file does not exist.
        ValueError: If data file type not supported.
    """
    # Check if file exists
    if not path.is_file():
        raise FileNotFoundError(f"Data file does not exist:\n{str(path)}")
    validate_data_type(path)


def load_data_file(
    path: Path,
    config: Optional[dict] = None
) -> Union[list, dict, tuple, set]:
    """Load data  object from a data file.

    Args:
        path: Path to the data file to be loaded.
        config: Dict data to modify DataFileType configuration for this data load procedure.

    Returns:
        Data object such as dict, list, tuple, set, etc.

    Raises:
        FileNotFoundError: If data file does not exist.
        ValueError: If data file type not supported.
        OSError: If dumping to data file fails.
    """
    # Check if data file is valid
    validate_data_file(path)

    # Pull the parser and insert user config into kwargs
    parser: DataFileType = data_types.get(path.suffix.lower(), {}).copy()
    if config:
        parser['load_kw'].update(config)

    # Attempt to load data
    with util_file_lock, suppress(Exception), open(path, 'r', encoding='utf-8') as f:
        data = parser['load'](f, **parser['load_kw']) or {}
        return data
    raise OSError(f"Unable to load data from data file:\n{str(path)}")


def dump_data_file(
    obj: Union[list, dict, tuple, set],
    path: Path,
    config: Optional[dict] = None
) -> None:
    """Dump data object to a data file.

    Args:
        obj: Iterable or dict object to save to data file.
        path: Path to the data file to be dumped.
        config: Dict data to modify DataFileType configuration for this data dump procedure.

    Raises:
        FileNotFoundError: If data file does not exist.
        ValueError: If data file type not supported.
        OSError: If dumping to data file fails.
    """
    # Check if data file is valid
    validate_data_type(path)

    # Pull the parser and insert user config into kwargs
    parser: DataFileType = data_types.get(path.suffix.lower(), {}).copy()
    if config:
        parser['dump_kw'].update(config)

    # Attempt to dump data
    with suppress(Exception), util_file_lock, open(path, 'w', encoding='utf-8') as f:
        parser['dump'](obj, f, **parser['dump_kw'])
        return
    raise OSError(f"Unable to dump data from data file:\n{str(path)}")


"""
* Config File Utils
"""


def verify_config_fields(ini_file: Path, data_file: Path) -> None:
    """Validate that all settings fields present in a given json data are present in config file. If any are missing,
    add them and return.

    Args:
        ini_file: Config file to verify contains the proper fields.
        data_file: Data file containing config fields to check for, JSON or TOML.
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
    """Parse config JSON data for use with Kivy settings panel.

    Args:
        raw: Raw loaded JSON data.

    Returns:
        Properly parsed data safe for use with Kivy.
    """
    # Remove unsupported keys
    for row in raw:
        if 'default' in row:
            row.pop('default')
    return raw


def parse_kivy_config_toml(raw: dict) -> list[dict]:
    """Parse config TOML data for use with Kivy settings panel.

    Args:
        raw: Raw loaded TOML data.

    Returns:
        Properly parsed data safe for use with Kivy.
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
    """Return valid JSON data for use with Kivy settings panel.

    Args:
        config: Path to config schema file, JSON or TOML.

    Returns:
        Json string dump of validated data.
    """
    # Need to load data as JSON
    raw = load_data_file(config)

    # Use correct parser
    if config.suffix == '.toml':
        raw = parse_kivy_config_toml(raw)
    return json.dumps(parse_kivy_config_json(raw))


def copy_config_or_verify(path_from: Path, path_to: Path, data_file: Path) -> None:
    """Copy one config to another, or verify it if it exists.

    Args:
        path_from: Path to the file to be copied.
        path_to: Path to the file to create, if it doesn't exist.
        data_file: Data schema file to use for validating an existing INI file.
    """
    if os.path.isfile(path_to):
        return verify_config_fields(path_to, data_file)
    shutil.copy(path_from, path_to)


def remove_config_file(ini_file: str) -> bool:
    """Check if config file exists, then remove it.

    Args:
        ini_file: Path to an ini file.

    Returns:
        True if removed, False if not.
    """
    if os.path.isfile(ini_file):
        with suppress(Exception):
            os.remove(ini_file)
            return True
    return False


def get_config_object(path: Union[str, os.PathLike, list[Union[str, os.PathLike]]]) -> ConfigParser:
    """Returns a ConfigParser object using a valid ini path.

    Args:
        path: Path to ini config file.

    Returns:
        ConfigParser object.

    Raises:
        ValueError: If valid ini file wasn't received.
    """
    config = ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(path, encoding='utf-8')
    return config


"""
* Project File Utils
"""


def get_app_version(path: Path) -> str:
    """Returns the version string stored in the root project file.

    Args:
        path: Path to the root project file.

    Returns:
        Current version string.
    """
    project = load_data_file(path)
    return project.get('tool', {}).get('poetry', {}).get('version', '1.0.0')


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
        if os.path.isfile(check):
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
    Path(os.path.dirname(path)).mkdir(mode=777, parents=True, exist_ok=True)


def get_unique_filename(path: Path) -> Path:
    """
    If a filepath exists, number the file according to the lowest number that doesn't exist.
    @param path: Path to the file.
    """
    i = 1
    stem = path.stem
    while path.is_file():
        path = path.with_stem(f'{stem} ({i})')
        i += 1
    return path


def get_subdirs(path: Path) -> Iterator[Path]:
    """Yields each subdirectory of a given folder.

    Args:
        path: Path to the folder to iterate over.

    Yields:
        A subdirectory of the given folder.
    """
    for dir_path, dir_names, filenames in os.walk(path):
        for dirname in dir_names:
            yield Path(dir_path) / dirname


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
