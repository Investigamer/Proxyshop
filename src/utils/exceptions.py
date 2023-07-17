"""
EXCEPTION UTILITIES
"""
# Standard Library Imports
from _ctypes import COMError
from ctypes import c_uint32
from typing import Optional

# Third Party Imports
from photoshop.api import PhotoshopPythonAPIError
from win32api import FormatMessage

PS_EXCEPTIONS = (
    PhotoshopPythonAPIError, COMError, AttributeError, IndexError, KeyError, ValueError, TypeError, OSError
)

PS_ERROR_CODES: dict[int: str] = {
    # --> COMError Messages that contain a message string
    # Response: "The message filter indicated that the application is busy."
    -2147417846: "Photoshop is currently busy, close any dialog boxes and stop any pending actions.",
    # Response: "The remote procedure call failed."
    -2147023170: "Unable to make connection with Photoshop, please check the FAQ for solutions.",
    # Response: "Invalid index."
    -2147352565: "Failed to load a PSD template or other file, ensure template file isn't corrupted "
                 "and that you have allocated enough scratch disk space and RAM to Photoshop.",
    # Response: "Exception occurred."
    -2147352567: "Photoshop does not appear to be installed. If Photoshop is installed, check the FAQ for solutions.",

    # --> COMError Messages that don't contain a message string, but have been investigated
    # Reference: https://docs.google.com/document/d/1j5xkWCWeHEFUZUaVtF59ccvAm9zTFsZ1qJcmFsXvkCM
    -2147220261: "Invalid data type passed to action descriptor function.",
    # Reference: https://docs.google.com/document/d/1LWXWyMa1kXAcGp4mDBZlpvqIgaR5jlk-H6j7uaKvOvI
    -2147213497: "Tried to transform, select, or translate an empty layer.",
    # Reference: https://docs.google.com/document/d/1mMeqi2lSaq2oUm1khl9rC0k9QLSI556a6m-MmLk19nw
    -2147212704: "Action descriptor or layer object key/property is missing.",
    # Reference: https://docs.google.com/document/d/1Oz69nNO0jR9qBbhjv3SVlMmk8iRnZY1LG7VaX7pqB-U
    -2147220262: "Photoshop tried to load a PSD template or file that doesn't exist.",

    # --> COMError Messages that don't contain a message string, but have been identified with testing
    # Test case: Pass a value to layer.textItem.color that isn't a SolidColor object
    -2147220279: "Wrong type of value passed to a Photoshop object property.",
    # Test case: Try to access the textItem property of a layer that isn't a TextLayer
    # Also: Observed when accessing the textItem property of a layer that contains an uninstalled font
    -2147213327: "Tried to interact with a text layer that is rasterized or has an uninstalled font.",
    # Test case: Delete a layer object, then try to delete it again.
    -2147213404: "Tried to delete a layer that doesn't exist."
}


"""
EXCEPTION CLASSES
"""


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


def get_com_error(signed_int: int) -> str:
    """
    Check for an error message for both the signed and unsigned version of a COMError code (HRESULT).
    @param signed_int: Signed integer representing a COMError exception.
    @return: The string error message associated with this COMError code.
    """
    try:
        err = FormatMessage(signed_int)
    except BaseException as e:
        try:
            unsigned_int = c_uint32(signed_int).value
            err = FormatMessage(unsigned_int)
        except BaseException as e:
            err = e.args[2]
    return err
