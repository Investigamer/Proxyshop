"""
* Utils: Adobe Photoshop
"""

from _ctypes import ArgumentError, COMError
from collections.abc import Callable
from contextlib import suppress
from ctypes import c_uint32
from functools import cached_property, wraps
from typing import Self, TypedDict

from packaging.version import parse
from photoshop.api import (
    ActionDescriptor,
    ActionReference,
    Application,
    PhotoshopPythonAPIError,
)
from photoshop.api._artlayer import ArtLayer
from photoshop.api._core import Photoshop
from photoshop.api._document import Document
from photoshop.api._layer import Layer
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import DialogModes, ElementPlacement, TypeUnits, Units
from win32api import FormatMessage

from src._state import AppEnvironment
from src.utils.windows import (
    WindowState,
    get_window_handle_by_process_file_path_suffix,
    set_window_state,
)

"""
* Types & Definitions
"""

# Common Layer Objects
LayerContainer = LayerSet, Document
LayerObject = LayerSet, ArtLayer

# Common Layer Types
LayerContainerTypes = LayerSet | Document
LayerObjectTypes = ArtLayer | LayerSet

# Common Photoshop Exceptions
PS_EXCEPTIONS = (
    PhotoshopPythonAPIError,
    ArgumentError,
    COMError,
    AttributeError,
    IndexError,
    KeyError,
    ValueError,
    TypeError,
    OSError,
)

_CHAR_ID_TO_TYPE_ID_CACHE: dict[tuple[object, ...], int] = {}
_TYPE_ID_TO_CHAR_ID_CACHE: dict[tuple[object, ...], str] = {}
_STRING_ID_TO_TYPE_ID_CACHE: dict[tuple[object, ...], int] = {}
_TYPE_ID_TO_STRING_ID_CACHE: dict[tuple[object, ...], str] = {}
_CHAR_ID_TO_STRING_ID_CACHE: dict[tuple[object, ...], str] = {}
_STRING_ID_TO_CHAR_ID_CACHE: dict[tuple[object, ...], str] = {}
_SCALE_BY_DPI_CACHE: dict[tuple[object, ...], int] = {}


def _cache_result[**P, T](
    result_cache: dict[tuple[object, ...], T],
    key_func: Callable[..., tuple[object, ...]] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Cache a method result without retaining the method's instance."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = (
                key_func(*args, **kwargs)
                if key_func
                else (args[1:], *sorted(kwargs.items()))
            )
            if key not in result_cache:
                result_cache[key] = func(*args, **kwargs)
            return result_cache[key]

        return wrapper

    return decorator


def _scale_by_dpi_cache_key(handler: Application, value: float) -> tuple[object, ...]:
    return (handler.activeDocument.width, value)


PS_ERROR_CODES: dict[int, str] = {
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
    -2147213404: "Tried to delete a layer that doesn't exist.",
}


# Layer bounds: left, top, right, bottom
LayerBounds = tuple[float, float, float, float]


class LayerDimensions(TypedDict):
    """Calculated layer dimension info for a layer."""

    width: float
    height: float
    center_x: float
    center_y: float
    left: float
    right: float
    top: float
    bottom: float


"""
* Util Classes
"""


class ApplicationHandler(Application):
    """Wrapper for the Photoshop Application class."""

    def __init__(self, env: AppEnvironment | None = None):
        version = env.PS_VERSION if env else None
        super().__init__(version=version)
        self._env = env

        # Set error dialog state
        with suppress(Exception):
            self.displayDialogs = (
                DialogModes.DisplayErrorDialogs
                if (env and env.PS_ERROR_DIALOG)
                else DialogModes.DisplayNoDialogs
            )

    """
    * Handler Properties
    """

    @cached_property
    def _env(self) -> AppEnvironment | None:
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

    _instance = None
    _window_handle: int | None = None

    @property
    def window_handle(self) -> int | None:
        if self._window_handle is None:
            self._window_handle = get_window_handle_by_process_file_path_suffix(
                "Photoshop.exe"
            )
        return self._window_handle

    def __new__(cls, env: AppEnvironment | None = None) -> Self:
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

    def refresh_app(self) -> OSError | None:
        """Replace the existing Photoshop Application instance with a new one."""
        if not self.is_running():
            try:
                # Load Photoshop and default preferences
                super().__init__(env=self._env)
                self.preferences.rulerUnits = Units.Pixels
                self.preferences.typeUnits = TypeUnits.TypePoints
            except Exception as e:  # noqa: BLE001
                # Photoshop is either busy or unresponsive
                return OSError(get_photoshop_error_message(e))

            # Clear window handle as it might have changed
            self._window_handle = None
        return

    def set_window_state(self, state: WindowState) -> None:
        if (handle := self.window_handle) is not None:
            set_window_state(handle, state)

    """
    * Class Methods
    """

    @classmethod
    def is_running(cls) -> bool:
        """Check if the current Photoshop Application instance is still valid."""
        with suppress(Exception):
            if cls._instance and cls._instance.version:
                return True
        return False

    """
    * Action Descriptor ID Conversions
    """

    @_cache_result(_CHAR_ID_TO_TYPE_ID_CACHE)
    def charIDToTypeID(self, index: str) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Caching handler for charIDToTypeID.

        Args:
            index: Char ID to convert to Type ID.

        Returns:
            Type ID converted from Char ID.
        """
        return super().charIDToTypeID(index)

    def cID(self, index: str) -> int:
        """Shorthand redirect for charIDToTypeID."""
        return self.charIDToTypeID(index)

    @_cache_result(_TYPE_ID_TO_CHAR_ID_CACHE)
    def typeIDToCharID(self, index: int) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Caching handler for typeIDToCharID.

        Args:
            index: Type ID to convert to Char ID.

        Returns:
            Character representation of Type ID.
        """
        return super().typeIDToCharID(index)

    """
    * String ID Conversions
    """

    @_cache_result(_STRING_ID_TO_TYPE_ID_CACHE)
    def stringIDToTypeID(self, index: str) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Caching handler for stringIDToTypeID.

        Args:
            index: String ID to convert to Type ID.

        Returns:
            Type ID converted from string ID.
        """
        return super().stringIDToTypeID(index)

    def sID(self, index: str) -> int:
        """Shorthand redirect for stringIDToTypeID."""
        return self.stringIDToTypeID(index)

    @_cache_result(_TYPE_ID_TO_STRING_ID_CACHE)
    def typeIDToStringID(self, index: int) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Caching handler for typeIDToStringID.

        Args:
            index: Type ID to convert to String ID.

        Returns:
            str: String representation of Type ID.
        """
        return super().typeIDToStringID(index)

    """
    * String / Char ID Conversions
    """

    @_cache_result(_CHAR_ID_TO_STRING_ID_CACHE)
    def charIDToStringID(self, index: str) -> str:
        """Converts a Char ID to a String ID.

        Args:
            index: Char ID to convert to String ID.

        Returns:
            str: String representation of Char ID.
        """
        return self.typeIDToStringID(self.charIDToTypeID(index))

    @_cache_result(_STRING_ID_TO_CHAR_ID_CACHE)
    def stringIDToCharID(self, index: str) -> str:
        """Converts a String ID to a Char ID.

        Args:
            index: String ID to convert to Char ID.

        Returns:
            str: Character representation of String ID.
        """
        return self.typeIDToCharID(self.stringIDToTypeID(index))

    """
    * Executing Action Descriptors
    """

    def executeAction(
        self,
        event_id: int,
        descriptor: ActionDescriptor | None = None,
        display_dialogs: DialogModes = DialogModes.DisplayNoDialogs,
    ) -> ActionDescriptor:
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
            return super().executeAction(
                event_id, descriptor, DialogModes.DisplayErrorDialogs
            )
        return super().executeAction(event_id, descriptor, display_dialogs)

    """
    * Version Checks
    """

    @cached_property
    def supports_target_text_replace(self) -> bool:
        """bool: Checks if Photoshop version supports targeted text replacement."""
        return self.version_meets_requirement("22.0.0")

    @cached_property
    def supports_webp(self) -> bool:
        """bool: Checks if Photoshop version supports WEBP files."""
        return self.version_meets_requirement("23.2.0")

    @cached_property
    def supports_generative_fill(self) -> bool:
        """Checks if Photoshop version supports Generative Fill."""
        return self.version_meets_requirement("24.6.0")

    @cached_property
    def supports_uxp_scripts(self) -> bool:
        return self.version_meets_requirement("23.5.0")

    def version_meets_requirement(self, value: str) -> bool:
        """Checks if Photoshop version meets or exceeds required value.

        Args:
            value: Minimum version string required.
        """
        return parse(self.version) >= parse(value)

    """
    * Dimensions
    """

    @_cache_result(_SCALE_BY_DPI_CACHE, _scale_by_dpi_cache_key)
    def scale_by_dpi(self, value: float) -> int:
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

    def __init__(
        self, parent: Photoshop | None = None, app: PhotoshopHandler | None = None
    ):
        self._global_app = app if app else PhotoshopHandler()
        super().__init__(parent=parent)

    """
    * API Methods
    """

    def duplicate(
        self,
        relativeObject: Layer | None = None,
        insertionLocation: ElementPlacement | None = None,
    ) -> ArtLayer:
        """Duplicates the layer and returns it as a `ReferenceLayer` object."""
        return ReferenceLayer(super().duplicate(relativeObject, insertionLocation))

    """
    * Layer Properties
    """

    @cached_property
    def id(self) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        """int: This layer's ID (cached)."""
        return super().id

    @cached_property
    def action_getter(self) -> ActionDescriptor:
        """Gets action descriptor info object for this layer.

        Returns:
            Action descriptor info object about the layer.
        """
        ref = ActionReference()
        ref.putIdentifier(self._global_app.sID("layer"), self.id)
        return self._global_app.executeActionGet(ref)

    """
    * Layer Bounds
    """

    @cached_property
    def bounds(self) -> LayerBounds:  # pyright: ignore[reportIncompatibleMethodOverride]
        """LayerBounds: Bounds of the layer (left, top, right, bottom) (cached)."""
        return super().bounds

    @cached_property
    def bounds_no_effects(self) -> LayerBounds:
        """LayerBounds: Bounds of the layer (left, top, right, bottom) without layer effects applied."""
        with suppress(Exception):
            d = self.action_getter
            try:
                # Try getting bounds no effects
                bounds = d.getObjectValue(self._global_app.sID("boundsNoEffects"))
            except PS_EXCEPTIONS:
                # Try getting bounds
                bounds = d.getObjectValue(self._global_app.sID("bounds"))
            return (
                bounds.getInteger(self._global_app.sID("left")),
                bounds.getInteger(self._global_app.sID("top")),
                bounds.getInteger(self._global_app.sID("right")),
                bounds.getInteger(self._global_app.sID("bottom")),
            )
        # Fallback to layer object bounds property
        return self.bounds

    """
    * Layer Dimensions
    """

    @cached_property
    def dims(self) -> LayerDimensions:
        """LayerDimensions: Returns dimensions of the layer (cached), including:
        - bounds (left, right, top, bottom)
        - height
        - width
        - center_x
        - center_y
        """
        return self.get_dimensions_from_bounds(self.bounds)

    @cached_property
    def dims_no_effects(self) -> LayerDimensions:
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
    def get_dimensions_from_bounds(
        bounds: tuple[float, float, float, float],
    ) -> LayerDimensions:
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
            left=int(bounds[0]),
            right=int(bounds[2]),
            top=int(bounds[1]),
            bottom=int(bounds[3]),
        )


"""
* Utility Decorators
"""


def try_photoshop[**P, T](func: Callable[P, T]) -> Callable[P, T | None]:
    """Decorator to handle trying to run a Photoshop action but allowing exceptions to fail silently.

    Args:
        func: Function being wrapped.

    Returns:
        The wrapped function.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs):
        try:
            return func(*args, **kwargs)
        except PS_EXCEPTIONS:
            return

    return wrapper


"""
* Utility Funcs
"""


def get_photoshop_error_message(err: Exception) -> str:
    """Gets a user-facing error message based on a given Photoshop access exception.

    Args:
        err: Exception object containing the reason an action failed.

    Returns:
        Proper user response for this exception.
    """
    return (
        ("Photoshop is currently busy, close any dialogs and stop any actions.\n")
        if "busy" in str(err).lower()
        else (
            "Photoshop does not appear to be installed on your system.\n"
            "Please close Proxyshop and install a fresh copy of Photoshop,\n"
            "if Photoshop is installed, view the FAQ for troubleshooting.\n"
        )
    )


def get_com_error(signed_int: int) -> str:
    """Check for an error message for both the signed and unsigned version of a COMError code (HRESULT).

    Args:
        signed_int: Signed integer representing a COMError exception.

    Returns:
        The string error message associated with this COMError code.
    """
    try:
        err = FormatMessage(signed_int)
    except Exception as e:  # noqa: BLE001
        try:
            unsigned_int = c_uint32(signed_int).value
            err = FormatMessage(unsigned_int) or e.args[2]
        except Exception as e:  # noqa: BLE001
            err = e.args[2]
    return err
