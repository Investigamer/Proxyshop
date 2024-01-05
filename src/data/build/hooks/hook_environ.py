"""
* Pyinstaller Hook
* Establishes frozen Environment Variables
"""
# Standard Library Imports
import os
import tomli

"""
* Hooks
"""


def load_version() -> None:
    """Store version as a static environment variable for built exe."""
    if os.environ.get('VERSION'):
        return
    with open('pyproject.toml', 'rb', encoding='utf-8') as f:
        pyproject = tomli.load(f)
        version = pyproject['tool']['poetry']['version']
        os.environ['VERSION'] = version


# Load the hook
load_version()
