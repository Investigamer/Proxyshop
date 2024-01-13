"""
* Utils: Modules
"""
# Standard Library Imports
import sys
from importlib import import_module
from importlib.util import find_spec, module_from_spec
from types import ModuleType

"""
* Module Funcs
"""


def get_loaded_module(module_path: str, hotswap: bool = False) -> ModuleType:
    """Lookup a dynamic module by its module path, forcing a reload if hotswap enabled.

    Args:
        module_path: Path to the module in module notation, e.g. "plugins.WarpDandy"
        hotswap: If True, always load module fresh.

    Returns:
        ModuleType: Loaded module.

    Raises:
        ImportError: If module couldn't be loaded successfully.
    """

    # Check if the module has already been loaded
    if module_path in sys.modules:
        if not hotswap:
            return sys.modules[module_path]
        del sys.modules[module_path]

    # Try loading module
    try:
        # Find the module's spec
        spec = find_spec(module_path)
        if spec is None:
            raise ImportError(f"Couldn't generate spec from module path: '{module_path}'")

        # Create a new module based on spec
        module = module_from_spec(spec)
        sys.modules[module_path] = module

        # Execute the module and return it
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        # Failed to load module
        raise ImportError(f"Error loading module path: '{module_path}'") from e


def get_local_module(module_path: str, hotswap: bool = False) -> ModuleType:
    """Lookup a local module by its module path, forcing a reload if hotswap enabled.

    Args:
        module_path: Path to the module in module notation, e.g. "src.templates"
        hotswap: If True, always load module fresh.

    Returns:
        ModuleType: Loaded module.

    Raises:
        ImportError: If module couldn't be loaded successfully.
    """

    # Check if the module has already been loaded
    if module_path in sys.modules:
        if not hotswap:
            return sys.modules[module_path]
        del sys.modules[module_path]

    # Load the module fresh and cache it
    try:
        module = import_module(module_path)
        sys.modules[module_path] = module
        return module
    except Exception as e:
        # Failed to load module
        raise ImportError(f"Error loading module path: '{module_path}'") from e
