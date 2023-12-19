"""
* Utils: Adobe Photoshop
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
from src._state import AppEnvironment
from src.utils.properties import auto_prop_cached
from src.utils.exceptions import PS_EXCEPTIONS, get_photoshop_error_message

"""
* Util Classes
"""


class ApplicationHandler(Application):
    """Wrapper for the Photoshop Application class."""

    def __init__(self, env: AppEnvironment):
        super().__init__(version=env.PS_VERSION)


class PhotoshopHandler(ApplicationHandler):
    """Wrapper for a single global Photoshop Application object equipped with soft loading,
    caching mechanisms, environment settings, and more."""
    DIMS_1200 = (3264, 4440)
    DIMS_800 = (2176, 2960)
    DIMS_600 = (1632, 2220)
    _instance = None

    def __new__(cls, env: Any) -> 'PhotoshopHandler':
        """Always return the same Photoshop Application instance on successive calls.

        Args:
            env (AppEnvironment): Global app environment containing relevant env variables.

        Returns:
            The existing or newly created PhotoshopHandler instance.
        """
        # Use existing Photoshop instance or create new one
        if cls._instance is None:
            try:
                cls._instance = super().__new__(cls)
            except PS_EXCEPTIONS:
                cls._instance = super(Photoshop, cls).__new__(cls)

        # Establish the app environment object
        cls._instance._env = env
        return cls._instance

    """
    * Managing the application object
    """

    def refresh_app(self):
        """Replace the existing Photoshop Application instance with a new one."""
        if not self.is_running():
            try:
                # Load Photoshop and default preferences
                super(PhotoshopHandler, self).__init__(env=self._env)
                self.preferences.rulerUnits = Units.Pixels
                self.preferences.typeUnits = Units.Points
            except Exception as e:
                # Photoshop is either busy or unresponsive
                return OSError(get_photoshop_error_message(e))
        return

    """
    * Handler Properties
    """

    @auto_prop_cached
    def _env(self) -> Any:
        """AppEnvironment: Global app environment object."""
        return

    @auto_prop_cached
    def ALLOW_ERROR_DIALOGS(self) -> bool:
        """bool: Whether to allow error dialogs, defined in app environment object."""
        if self._env:
            return self._env.PS_ERROR_DIALOG
        return False

    @auto_prop_cached
    def PS_VERSION(self) -> Optional[str]:
        """Optional[str]: Photoshop version to look for in registry."""
        return self._env.PS_VERSION

    """
    * Class Methods
    """

    @classmethod
    def is_running(cls) -> bool:
        """Check if the current Photoshop Application instance is still valid."""
        with suppress(Exception):
            _ = cls._instance.version
            return True
        return False

    """
    * Action Descriptor ID Conversions
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
    * Executing Action Descriptors
    """

    def executeAction(
        self, event_id: int,
        descriptor: ActionDescriptor,
        dialogs: DialogModes = DialogModes.DisplayNoDialogs
    ) -> Any:
        """Middleware to allow all dialogs when an error occurs upon calling executeAction in development mode.

        Args:
            event_id: Action descriptor event ID.
            descriptor: Main action descriptor tree to execute.
            dialogs: DialogMode which governs whether to display dialogs.

        Returns:
            Result of the action descriptor execution.
        """
        if self.ALLOW_ERROR_DIALOGS:
            # Allow error dialogs if enabled in the app environment
            return super().executeAction(event_id, descriptor, DialogModes.DisplayErrorDialogs)
        return super().executeAction(event_id, descriptor, dialogs)

    def ExecuteAction(
            self, event_id: int,
            descriptor: ActionDescriptor,
            dialogs: DialogModes = DialogModes.DisplayNoDialogs
    ) -> Any:
        """Utility definition rerouting to original `executeAction`."""
        self.executeAction(event_id, descriptor, dialogs)

    """
    * Version Checks
    """

    @cache
    def supports_target_text_replace(self) -> bool:
        """bool: Checks if Photoshop version supports targeted text replacement."""
        return self.version_meets_requirement('22.0.0')

    @cache
    def supports_webp(self) -> bool:
        """bool: Checks if Photoshop version supports WEBP files."""
        return self.version_meets_requirement('23.2.0')

    @cache
    def supports_generative_fill(self) -> bool:
        """Checks if Photoshop version supports Generative Fill."""
        return self.version_meets_requirement('24.6.0')

    def version_meets_requirement(self, value: str) -> bool:
        """Checks if Photoshop version meets or exceeds required value.

        Args:
            value: Minimum version string required.
        """
        if parse(self.version) >= parse(value):
            return True
        return False

    """
    * Dimensions
    """

    def scale_by_dpi(self, value: Union[int, float]) -> int:
        """
        Scales a value by comparing document DPI to ideal DPI.
        @param value: Integer or float value to adjust by DPI ratio.
        @return: Adjusted value as an integer.
        """
        return int((self.activeDocument.width / 3264) * value)
