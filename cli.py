"""
* Headless CLI Application
"""
# Standard Library Imports
import os
os.environ['HEADLESS'] = '1'

# Local Imports
from src.commands import ProxyshopCLI


if __name__ == '__main__':
    # Launch the CLI Application
    ProxyshopCLI()
