"""
EXCEPTION UTILITIES
"""
# Standard Library Imports
from _ctypes import COMError

# Third Party Imports
from photoshop.api import PhotoshopPythonAPIError

PS_EXCEPTIONS = (PhotoshopPythonAPIError, COMError)
