"""
MODULE UTILITIES
"""
import sys
from importlib.util import spec_from_file_location, module_from_spec
from types import ModuleType


def get_loaded_module(module_path: str, module_name: str, recache: bool = False) -> ModuleType:
    """
    Lookup a loaded module by its filepath and reload it. If not found, load the module fresh.
    @param module_path: File path to the module.
    @param module_name: Name to give the module if loading it fresh.
    @param recache: If True, reload the module before returning it.
    @return: True if loaded, otherwise False.
    """
    # Check if this module has been imported before
    if module_name in sys.modules:
        if recache:
            del sys.modules[module_name]
            return get_new_module(module_path, module_name)
        return sys.modules[module_name]

    # Model not loaded, load it now
    return get_new_module(module_path, module_name)


def get_new_module(module_path: str, module_name: str) -> ModuleType:
    """
    Loads a module from a given path with assigned name.
    @param module_path: Path to module file.
    @param module_name: Name of the loaded module.
    @return: Loaded module.
    """
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module
