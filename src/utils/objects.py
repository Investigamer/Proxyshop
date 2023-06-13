"""
OBJECT UTILITIES
"""
# Standard Library
from functools import cache
from typing import Union

# Third Party
from photoshop.api import Application, Units
from packaging.version import parse
from src.utils.exceptions import PS_EXCEPTIONS


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

    def __new__(cls) -> 'PhotoshopHandler':
        """Always return the same Photoshop Application instance on successive calls."""
        if cls._instance is None or not cls._instance.is_running():
            try:
                cls._instance = super().__new__(cls)
            except PS_EXCEPTIONS:
                cls._instance = super(Application, cls).__new__(cls)
        return cls._instance

    """
    CLASS METHODS
    """

    def refresh_app(self):
        """Replace the existing Photoshop Application instance with a new one."""
        if not self.is_running():
            super(PhotoshopHandler, self).__init__()
        try:
            self.preferences.rulerUnits = Units.Pixels
            self.preferences.typeUnits = Units.Points
        except Exception:
            raise OSError("Photoshop appears to be busy or is not installed!")

    @classmethod
    def is_running(cls) -> bool:
        """Check if the current Photoshop Application instance is still valid."""
        try:
            _ = cls._instance.version
        except PS_EXCEPTIONS:
            return False
        return True

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
        return self.stringIDToTypeID(index)

    @cache
    def typeIDToCharID(self, index: int) -> str:
        """
        Caching handler for typeIDToCharID.
        @param index: ID to convert to CharID.
        """
        return self.typeIDToCharID(index)

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
        return super().stringIDToTypeID(index)

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
        return self.typeIDToStringID(index)

    @cache
    def t2s(self, index: int) -> str:
        """Shorthand for typeIDToStringID."""
        return self.typeIDToStringID(index)

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
