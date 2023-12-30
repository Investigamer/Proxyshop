"""
* Utils: Adobe Photoshop
"""
# Standard Library
from functools import cache, cached_property
from contextlib import suppress
from typing import Union, Any, Optional, TypedDict

# Third Party
from photoshop.api import Application, Units, DialogModes, ActionDescriptor, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._core import Photoshop
from packaging.version import parse

# Local Imports
from src._state import AppEnvironment
from src.utils.properties import auto_prop_cached
from src.utils.exceptions import PS_EXCEPTIONS, get_photoshop_error_message


"""
* Types
"""


# Layer bounds: left, top, right, bottom
LayerBounds = list[int, int, int, int]


class LayerDimensions(TypedDict):
    """Calculated layer dimension info for a layer."""
    width: int
    height: int
    center_x: int
    center_y: int
    left: int
    right: int
    top: int
    bottom: int


"""
* Util Classes
"""


class ApplicationHandler(Application):
    """Wrapper for the Photoshop Application class."""

    def __init__(self, env: Optional[AppEnvironment] = None):
        version = env.PS_VERSION if env else None
        super().__init__(version=version)
        self._env = env

    """
    * Handler Properties
    """

    @auto_prop_cached
    def _env(self) -> Optional[AppEnvironment]:
        """AppEnvironment: Global app environment object."""
        return

    def is_error_dialog_enabled(self) -> bool:
        """bool: Whether to allow error dialogs, defined in app environment object."""
        if self._env:
            return self._env.PS_ERROR_DIALOG
        return False


class PhotoshopHandler(ApplicationHandler):
    """Wrapper for a single global Photoshop Application object equipped with soft loading,
    caching mechanisms, environment settings, and more."""
    DIMS_1200 = (3264, 4440)
    DIMS_800 = (2176, 2960)
    DIMS_600 = (1632, 2220)
    _instance = None

    def __new__(cls, env: Optional[Any] = None) -> 'PhotoshopHandler':
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
        """Caching handler for charIDToTypeID.

        Args:
            index: Char ID to convert to Type ID.

        Returns:
            Type ID converted from Char ID.
        """
        return super().charIDToTypeID(index)

    @cache
    def CharIDToTypeID(self, index: str) -> int:
        """Uppercase redirect for charIDToTypeID."""
        return self.charIDToTypeID(index)

    @cache
    def cID(self, index: str) -> int:
        """Shorthand redirect for charIDToTypeID."""
        return self.charIDToTypeID(index)

    @cache
    def typeIDToCharID(self, index: int) -> str:
        """Caching handler for typeIDToCharID.

        Args:
            index: Type ID to convert to Char ID.

        Returns:
            Character representation of Type ID.
        """
        return super().typeIDToCharID(index)

    @cache
    def t2c(self, index: int) -> str:
        """Shorthand redirect for typeIDToCharID."""
        return self.typeIDToCharID(index)

    """
    * String ID Conversions
    """

    @cache
    def stringIDToTypeID(self, index: str) -> int:
        """Caching handler for stringIDToTypeID.

        Args:
            index: String ID to convert to Type ID.

        Returns:
            Type ID converted from string ID.
        """
        return super().stringIDToTypeID(index)

    @cache
    def StringIDToTypeID(self, index: str) -> int:
        """Uppercase redirect for stringIDTotypeID."""
        return self.stringIDToTypeID(index)

    @cache
    def sID(self, index: str) -> int:
        """Shorthand redirect for stringIDToTypeID."""
        return self.stringIDToTypeID(index)

    @cache
    def typeIDToStringID(self, index: int) -> str:
        """Caching handler for typeIDToStringID.

        Args:
            index: Type ID to convert to String ID.

        Returns:
            str: String representation of Type ID.
        """
        return super().typeIDToStringID(index)

    @cache
    def t2s(self, index: int) -> str:
        """Shorthand redirect for typeIDToStringID."""
        return self.typeIDToStringID(index)

    """
    * String / Char ID Conversions
    """

    @cache
    def charIDToStringID(self, index: int) -> str:
        """Converts a Char ID to a String ID.

        Args:
            index: Char ID to convert to String ID.

        Returns:
            str: String representation of Char ID.
        """
        return self.typeIDToStringID(
            self.charIDToTypeID(index))

    @cache
    def stringIDToCharID(self, index: int) -> str:
        """Converts a String ID to a Char ID.

        Args:
            index: String ID to convert to Char ID.

        Returns:
            str: Character representation of String ID.
        """
        return self.typeIDToCharID(
            self.stringIDToTypeID(index))

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
        if self.is_error_dialog_enabled():
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

    @cache
    def scale_by_dpi(self, value: Union[int, float]) -> int:
        """Scales a value by comparing document DPI to ideal DPI.

        Args:
            value: Integer or float value to adjust by DPI ratio.

        Returns:
            Adjusted value as an integer.
        """
        return int((self.activeDocument.width / 3264) * value)


class ReferenceLayer(ArtLayer):
    """A static ArtLayer whose properties such as width or height are not going to change. Most often
    used as a reference to position or size other layers."""

    def __init__(self, parent: Any = None, app: PhotoshopHandler = None):
        self._global_app = app if app else PhotoshopHandler()
        super().__init__(parent=parent)

    """
    * API Methods
    """

    def duplicate(self, relativeObject=None, insertionLocation=None):
        """Duplicates the layer and returns it as a `ReferenceLayer` object."""
        return ReferenceLayer(self.app.duplicate(relativeObject, insertionLocation))

    """
    * Cached Conversions
    """

    @cache
    def sID(self, index: str) -> int:
        """Caching handler for stringIDToTypeID on the global application object.

        Args:
            index: String ID to convert to Type ID.

        Returns:
            Type ID converted from string ID.
        """
        return self._global_app.stringIDToTypeID(index)

    """
    * Layer Properties
    """

    @cached_property
    def id(self) -> int:
        """int: This layer's ID (cached)."""
        return self.app.id

    @cached_property
    def action_getter(self) -> ActionReference:
        """Gets action descriptor info object for this layer.

        Returns:
            Action descriptor info object about the layer.
        """
        ref = ActionReference()
        ref.putIdentifier(self.sID('layer'), self.id)
        return self._global_app.executeActionGet(ref)

    """
    * Layer Bounds
    """

    @cached_property
    def bounds(self) -> LayerBounds:
        """LayerBounds: Bounds of the layer (left, top, right, bottom)."""
        return self.app.bounds

    @cached_property
    def bounds_no_effects(self) -> LayerBounds:
        """LayerBounds: Bounds of the layer (left, top, right, bottom) without layer effects applied."""
        with suppress(Exception):
            d = self.action_getter
            try:
                # Try getting bounds no effects
                bounds = d.getObjectValue(self.sID('boundsNoEffects'))
            except PS_EXCEPTIONS:
                # Try getting bounds
                bounds = d.getObjectValue(self.sID('bounds'))
            return [
                bounds.getInteger(self.sID('left')),
                bounds.getInteger(self.sID('top')),
                bounds.getInteger(self.sID('right')),
                bounds.getInteger(self.sID('bottom'))]
        # Fallback to layer object bounds property
        return self.bounds

    """
    * Layer Dimensions
    """

    @cached_property
    def dims(self) -> type[LayerDimensions]:
        """LayerDimensions: Returns dimensions of the layer (cached), including:
            - bounds (left, right, top, bottom)
            - height
            - width
            - center_x
            - center_y
        """
        return self.get_dimensions_from_bounds(self.bounds)

    @cached_property
    def dims_no_effects(self) -> type[LayerDimensions]:
        """LayerDimensions: Returns dimensions of the layer (cached) without layer effects applied, including:
            - bounds (left, right, top, bottom)
            - height
            - width
            - center_x
            - center_y
        """
        return self.get_dimensions_from_bounds(self.bounds_no_effects)

    """
    * Utility Methods
    """

    @staticmethod
    def get_dimensions_from_bounds(bounds) -> type[LayerDimensions]:
        """Compute width and height based on a set of bounds given.

        Args:
            bounds: List of bounds given.

        Returns:
            Dict containing height, width, and positioning locations.
        """
        width = int(bounds[2] - bounds[0])
        height = int(bounds[3] - bounds[1])
        return LayerDimensions(
            width=width,
            height=height,
            center_x=round((width / 2) + bounds[0]),
            center_y=round((height / 2) + bounds[1]),
            left=int(bounds[0]), right=int(bounds[2]),
            top=int(bounds[1]), bottom=int(bounds[3]))
