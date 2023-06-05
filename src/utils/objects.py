"""
OBJECT UTILITIES
"""
# Standard Library
from functools import cache
from typing import Union

from _ctypes import COMError

# Third Party
from photoshop.api import Application, Units
from packaging.version import parse


class Singleton(type):
    """
    Maintains a single instance of any child class.
    """
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

    def __new__(cls) -> 'PhotoshopHandler':
        """
        Always return the same Photoshop Application instance on successive calls.
        """
        if cls._instance is None or not cls._instance.is_running():
            cls._instance = super().__new__(cls)
        return cls._instance

    """
    CLASS METHODS
    """

    def refresh_app(self):
        """
        Replace the existing Photoshop Application instance with a new one.
        """
        if not self.is_running():
            super(PhotoshopHandler, self).__init__()
        try:
            self.preferences.rulerUnits = Units.Pixels
            self.preferences.typeUnits = Units.Points
        except Exception:
            raise OSError("Photoshop appears to be busy or is not installed!")

    @classmethod
    def is_running(cls) -> bool:
        """
        Check if the current Photoshop Application instance is still valid.
        """
        try:
            _ = cls._instance.version
            return True
        except (AttributeError, COMError):
            return False

    """
    CACHED CONVERSION METHODS
    """

    @cache
    def charIDToTypeID(self, index: str):
        """
        Caching handler for charIDToTypeID.
        @param index: ID to convert to TypeID.
        """
        return super().charIDToTypeID(index)

    @cache
    def stringIDToTypeID(self, index: str):
        """
        Caching handler for stringIDToTypeID.
        @param index: ID to convert to TypeID.
        """
        return super().stringIDToTypeID(index)

    @cache
    def CharIDToTypeID(self, index: str):
        """
        Caching handler for charIDToTypeID.
        @param index: ID to convert to TypeID.
        """
        return super().charIDToTypeID(index)

    @cache
    def StringIDToTypeID(self, index: str):
        """
        Caching handler for StringIDToTypeID.
        @param index: ID to convert to TypeID.
        """
        return super().stringIDToTypeID(index)

    """
    VERSION CHECKS
    """

    @cache
    def supports_target_text_replace(self) -> bool:
        """
        Checks if Photoshop version supports targeted text replacement.
        @return: True if it does, otherwise False.
        """
        return self.version_meets_requirement('22.0.0')

    @cache
    def supports_webp(self) -> bool:
        """
        Checks if Photoshop version supports targeted text replacement.
        @return: True if it does, otherwise False.
        """
        return self.version_meets_requirement('23.2.0')

    def version_meets_requirement(self, value: str) -> bool:
        """
        Checks if Photoshop version meets or exceeds required value.
        @return: True if it does, otherwise false.
        """
        if parse(self.version) >= parse(value):
            return True
        return False

    """
    DIMENSION CHECKS
    """

    def scale_by_height(self, value: Union[int, float]) -> int:
        """
        Scales a value by comparing 1200 DPI height to current document.
        @param value: Integer or float value to adjust by comparing document height.
        @return: Adjusted value as an integer.
        """
        return int((self.activeDocument.height / self.DIMS_1200[1]) * value)

    def scale_by_width(self, value: Union[int, float]) -> int:
        """
        Scales a value by comparing 1200 DPI width to current document.
        @param value: Integer or float value to adjust by comparing document width.
        @return: Adjusted value as an integer.
        """
        return int((self.activeDocument.width / self.DIMS_1200[0]) * value)
