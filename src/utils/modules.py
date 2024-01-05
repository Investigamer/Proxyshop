"""
* Utils: Modules
"""
# Standard Library Imports
import sys
import importlib
from types import ModuleType
from contextlib import suppress


"""
* Module Funcs
"""


def get_loaded_module(module_path: str, hotswap: bool = False) -> ModuleType:
    """Lookup a loaded module by its filepath and reload it. If not found, load the module fresh.

    Args:
        module_path: Path to the module in module notation, e.g. "src.templates"
        hotswap: If True, always load modules fresh.

    Returns:
        ModuleType: Loaded module.

    Raises:
        ImportError: If module couldn't be loaded successfully.
    """

    # Check if the module has already been loaded
    if not hotswap and module_path in sys.modules:
        return sys.modules[module_path]
    elif hotswap and module_path in sys.modules:
        del sys.modules[module_path]

    # Load the module fresh and cache it
    with suppress(Exception):
        module = importlib.import_module(module_path)
        sys.modules[module_path] = module
        return module

    # Import error occurred
    raise ImportError(f"Error loading module: '{module_path}'")
