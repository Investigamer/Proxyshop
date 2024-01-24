"""
* Utils: Modules
"""
# Standard Library Imports
import importlib
import os
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import sys
from types import ModuleType
from typing import Union, Optional

"""
* Sys Utils
"""


def _add_python_path(path: Union[str, os.PathLike]) -> None:
    """Add a path to 'sys.path' to allow relative import discovery.

    Args:
        path: Path containing a module which needs relative import behavior.
    """
    p = str(path)
    if p not in sys.path:
        sys.path.append(p)


def _remove_python_path(path: Union[str, os.PathLike]) -> None:
    """Remove a path to 'sys.path' to keep the namespace clean.

    Args:
        path: Path containing a module which needs relative import behavior.
    """
    p = str(path)
    if p in sys.path:
        sys.path.remove(p)


"""
* Packages
"""


def import_package(name: str, path: Path, hotswap: bool = False) -> Optional[ModuleType]:
    """Loads a module package using importlib or from 'sys.modules', allowing for forced reloads.

    Args:
        name: Name of the module.
        path: Path to the module.
        hotswap: Whether to force the module to be reloaded fresh.

    Returns:
        The loaded module.
    """
    # Return previously loaded module
    if name in sys.modules:
        if not hotswap:
            return sys.modules[name]
        del sys.modules[name]

    # Add parent folder to path
    _add_python_path(str(path))

    # Collect nested modules before importing and executing
    import_nested_modules(
        name=name,
        path=path,
        recursive=True,
        hotswap=hotswap,
        ignored=['__init__.py'])

    # Return None if init module not found
    init_module = path / '__init__.py'
    if not init_module.is_file():
        _remove_python_path(str(path))
        return

    # Import and execute the init module
    module = import_module_from_path(name=name, path=init_module, hotswap=hotswap)

    # Reset system paths and return
    _remove_python_path(str(path))
    return module


"""
* Dynamic Modules
"""


def import_nested_modules(
    name: str,
    path: Path,
    recursive: bool = True,
    hotswap: bool = False,
    ignored: Optional[list[str]] = None
) -> None:
    """Imports modules nested inside a directory."""
    ignored = ignored or []
    for item in os.listdir(path):
        if item in ['__pycache__', *ignored]:
            continue
        p = path / item
        n = '.'.join([name, p.stem])
        if p.is_dir() and recursive:
            # Import directory
            _add_python_path(str(p))
            import_nested_modules(
                name=n, path=p, hotswap=hotswap, ignored=ignored)
            _remove_python_path(str(p))
            continue
        elif p.is_file():
            # Import module
            import_module_from_path(name=n, path=p, hotswap=hotswap)


def import_module_from_path(name: str, path: Path, hotswap: bool = False) -> ModuleType:
    """Import a module from a given path.

    Args:
        name: Name of the module.
        path: Path to the module.
        hotswap: Whether to

    Returns:
        Loaded and executed module.
    """
    # Return previously loaded module
    if name in sys.modules:
        if not hotswap:
            return sys.modules[name]
        del sys.modules[name]

    # Import and execute the module
    spec = spec_from_file_location(name=name, location=path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module


"""
* Local Modules
"""


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
    module = importlib.import_module(module_path)
    sys.modules[module_path] = module
    return module
