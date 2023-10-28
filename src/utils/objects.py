"""
OBJECT UTILITIES
"""
# Standard Library
from functools import cache
from contextlib import suppress
from typing import Union, Any, Optional

# Third Party
from photoshop.api import Application, Units, DialogModes, ActionDescriptor
from photoshop.api._core import Photoshop
from packaging.version import parse

# Local Imports
from src.utils.env import ENV
from src.utils.exceptions import PS_EXCEPTIONS, get_photoshop_error_message


"""
* Utility classes
"""


class Singleton(type):
    """Maintains a single instance of any child class."""
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PhotoshopHandler(Application):
    """
    Wrapper for the Photoshop Application object to maintain a single instance globally,
    caching mechanisms, app instance refresh, etc.
    """
    DIMS_1200 = (3264, 4440)
    DIMS_800 = (2176, 2960)
    DIMS_600 = (1632, 2220)
    _instance = None

    def __new__(cls, version: Optional[str] = None) -> 'PhotoshopHandler':
        """Always return the same Photoshop Application instance on successive calls."""
        # Use existing Photoshop instance or create new one
        if cls._instance is None:
            try:
                cls._instance = super().__new__(cls)
            except PS_EXCEPTIONS:
                cls._instance = super(Photoshop, cls).__new__(cls)
        # Establish the version initially passed and return instance
        cls._instance._version = version
        return cls._instance

    """
    CLASS METHODS
    """

    def refresh_app(self):
        """Replace the existing Photoshop Application instance with a new one."""
        if not self.is_running():
            try:
                # Load Photoshop and default preferences
                super(PhotoshopHandler, self).__init__(version=self._version)
                self.preferences.rulerUnits = Units.Pixels
                self.preferences.typeUnits = Units.Points
            except Exception as e:
                # Photoshop is either busy or unresponsive
                return OSError(get_photoshop_error_message(e))
        return

    @classmethod
    def is_running(cls) -> bool:
        """Check if the current Photoshop Application instance is still valid."""
        with suppress(Exception):
            _ = cls._instance.version
            return True
        return False

    """
    CONVERTING CHARACTER ID
    """

    @cache
    def charIDToTypeID(self, index: str) -> int:
        """
        Caching handler for charIDToTypeID.
        @param index: ID to convert to TypeID.
        """
        return super().charIDToTypeID(index)

    @cache
    def CharIDToTypeID(self, index: str) -> int:
        """Utility definition redirecting to charIDToTypeID."""
        return self.charIDToTypeID(index)

    @cache
    def cID(self, index: str) -> int:
        """Shorthand for charIDToTypeID."""
        return self.charIDToTypeID(index)

    @cache
    def typeIDToCharID(self, index: int) -> str:
        """
        Caching handler for typeIDToCharID.
        @param index: ID to convert to CharID.
        """
        return super().typeIDToCharID(index)

    @cache
    def t2c(self, index: int) -> str:
        """Shorthand for typeIDToCharID."""
        return self.typeIDToCharID(index)

    """
    CONVERTING STRING ID
    """

    @cache
    def stringIDToTypeID(self, index: str) -> int:
        """
        Caching handler for stringIDToTypeID.
        @param index: ID to convert to TypeID.
        """
        return super().stringIDToTypeID(index)

    @cache
    def StringIDToTypeID(self, index: str) -> int:
        """Utility definition redirecting to stringIDTotypeID."""
        return self.stringIDToTypeID(index)

    @cache
    def sID(self, index: str) -> int:
        """Shorthand for stringIDToTypeID."""
        return self.stringIDToTypeID(index)

    @cache
    def typeIDToStringID(self, index: int) -> str:
        """
        Caching handler for typeIDToStringID.
        @param index: ID to convert to StringID.
        """
        return super().typeIDToStringID(index)

    @cache
    def t2s(self, index: int) -> str:
        """Shorthand for typeIDToStringID."""
        return self.typeIDToStringID(index)

    """
    EXECUTING ACTION DESCRIPTORS
    """

    def executeAction(
            self, event_id: int,
            descriptor: ActionDescriptor,
            dialogs: DialogModes = DialogModes.DisplayNoDialogs
    ) -> Any:
        """
        Middleware to allow all dialogs when an error occurs upon calling executeAction in development mode.
        @param event_id: Action descriptor event ID.
        @param descriptor: Main action descriptor tree to execute.
        @param dialogs: DialogMode which governs whether to display dialogs.
        """
        if not ENV.PS_ERROR_DIALOG:
            return super().executeAction(event_id, descriptor, dialogs)
        # Allow error dialogs within development environment
        return super().executeAction(event_id, descriptor, DialogModes.DisplayErrorDialogs)

    def ExecuteAction(
            self, event_id: int,
            descriptor: ActionDescriptor,
            dialogs: DialogModes = DialogModes.DisplayNoDialogs
    ) -> Any:
        """Utility definition rerouting to original executeAction function."""
        self.executeAction(event_id, descriptor, dialogs)

    """
    VERSION CHECKS
    """

    @cache
    def supports_target_text_replace(self) -> bool:
        """
        Checks if Photoshop version supports targeted text replacement.
        @return: True if supported.
        """
        return self.version_meets_requirement('22.0.0')

    @cache
    def supports_webp(self) -> bool:
        """
        Checks if Photoshop version supports WEBP files.
        @return: True if supported.
        """
        return self.version_meets_requirement('23.2.0')

    @cache
    def supports_generative_fill(self) -> bool:
        """
        Checks if Photoshop version supports Generative Fill.
        @return: True if supported.
        """
        return self.version_meets_requirement('24.6.0')

    def version_meets_requirement(self, value: str) -> bool:
        """
        Checks if Photoshop version meets or exceeds required value.
        @return: True if supported.
        """
        if parse(self.version) >= parse(value):
            return True
        return False

    """
    DIMENSION CHECKS
    """

    def scale_by_dpi(self, value: Union[int, float]) -> int:
        """
        Scales a value by comparing document DPI to ideal DPI.
        @param value: Integer or float value to adjust by DPI ratio.
        @return: Adjusted value as an integer.
        """
        return int((self.activeDocument.width / 3264) * value)
