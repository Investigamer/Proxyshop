"""
EXCEPTION UTILITIES
"""
from typing import Optional

# Standard Library Imports
from _ctypes import COMError

# Third Party Imports
from photoshop.api import PhotoshopPythonAPIError

PS_EXCEPTIONS = (
    PhotoshopPythonAPIError, COMError, AttributeError, IndexError, KeyError, ValueError, TypeError, OSError
)


class ScryfallError(Exception):
    """Exception representing a failure to retrieve Scryfall data."""

    def __init__(
        self,
        url: Optional[str] = None,
        name: Optional[str] = '',
        code: Optional[str] = '',
        number: Optional[str] = '',
        lang: Optional[str] = '',

    ):
        # Establish string patterns
        name = f"{name} " if name else ''
        code = f"[{code}] " if code else ''
        number = f"{{{number}}} " if number else ''
        lang = f"<{lang}>" if lang else ''

        # Pass the correct message
        super().__init__(
            f"Scryfall request failed"
        ) if not any([url, name, code, number, lang]) else (
            f"Couldn't find card: {name}{code}{number}{lang}\n"
            f"Scryfall: {url or 'Request Rejected'}"
        )


"""
UTILITY FUNCTIONS
"""


def get_photoshop_error_message(err: Exception) -> str:
    """
    Gets a user-facing error message based on a given Photoshop access exception.
    @param err: Exception object containing the reason an action failed.
    @return: Proper user response for this exception.
    """
    return (
        "Photoshop is currently busy, close any dialogs and stop any actions.\n"
    ) if 'busy' in str(err).lower() else (
        "Photoshop does not appear to be installed on your system.\n"
        "Please close Proxyshop and install a fresh copy of Photoshop,\n"
        "if Photoshop is installed, view the FAQ for troubleshooting.\n"
    )