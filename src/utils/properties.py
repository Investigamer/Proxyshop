"""
* Utils: Properties and Meta-classes
"""
# Standard Library Imports
from typing import Callable, Any

"""
* Property Utils
"""


def auto_prop(func: Callable) -> property:
    """Property decorator wrapper which automatically creates a setter."""
    attr_type = func.__annotations__.get('return', str) if (
        hasattr(func, '__annotations__')) else str
    auto_name = f"_{func.__name__}"

    def getter(self) -> attr_type:
        """Getter for retrieving the value of the implied attribute."""
        return getattr(self, auto_name)

    def setter(self, value: attr_type) -> None:
        """Setter for changing the value of the implied attribute."""
        setattr(self, auto_name, value)

    # Return complete property
    return property(getter, setter, doc=func.__doc__)


def auto_prop_cached(func: Callable) -> property:
    """Property decorator wrapper which automatically creates a setter and caches the value."""
    attr_type = func.__annotations__.get('return', str) if (
        hasattr(func, '__annotations__')) else str
    cache_name = f"_{func.__name__}"

    def getter(self) -> attr_type:
        """Wrapper for getting cached value. If value doesn't exist, initialize it."""
        try:
            return getattr(self, cache_name)
        except AttributeError:
            value = func(self)
            setattr(self, cache_name, value)
            return value

    def setter(self, value: attr_type) -> None:
        """Setter for invalidating the property cache and caching a new value."""
        setattr(self, cache_name, value)

    def deleter(self) -> None:
        """Deleter for invalidating the property cache."""
        if hasattr(self, cache_name):
            delattr(self, cache_name)

    # Return complete property
    return property(getter, setter, deleter, getattr(func, '__doc__', ""))


"""
* Class Property Utils
"""


class tracked_prop:
    """A decorator for creating a cached property which tracks changes in the parent object."""

    def __init__(self, getter):
        """Initializes the property.

        Args:
            getter: Decorated method which acts as a getter for the property's default value.
        """
        self.getter = getter
        self._value = None
        self._name = None

    def __get__(self, instance, owner):
        """Either sets and returns the default value or returns the cached value.

        Args:
            instance: Instance of the parent object for the decorated getter.
            owner: Class of the parent object.

        Returns:
            Cached or default value.
        """
        if self._value is None:
            self._value = self.getter(instance)
        return self._value

    def __set__(self, instance, value) -> None:
        """Sets a new cached value for the decorated property and adds it to changes.

        Args:
            instance: Instance of the parent object.
            value: Value to set for the cached property.
        """
        self._value = value
        instance._changes.add(self._name)
        return

    def __call__(self, func):
        """Called when decorator is used aas a function.

        Args:
            func: Function to be decorated.

        Returns:
            An instance of this decorator class.
        """
        self.getter = func
        return self

    def __set_name__(self, owner, name) -> None:
        """Sets the name of the decorated property.

        Args:
            owner: Class of the parent object.
            name: Name of the decorated property.
        """
        self._name = name

    def __delete__(self, owner):
        """Clears the cached value of the decorated property.

        Args:
            owner: Class of the parent object.
        """
        self._value = None


class enum_class_prop:
    """A decorator for creating a static property for Enum classes."""

    def __init__(self, method: Callable):
        """Initializes the property.

        Args:
            method: Class method being decorated.
        """
        self._method = method
        self._name = method.__name__

    def __get__(self, instance: Any, owner: Any) -> Any:
        """Computes and caches the value of a property when accessed.

        Args:
            instance: Instance of the class where descriptor is accessed.
            owner: The class that the descriptor exists on.

        Returns:
            The cached value.
        """
        value = self._method(owner)
        setattr(owner, self._name, value)
        return value


"""
* Meta-class Utils
"""


class Singleton(type):
    """Maintains a single instance of any child class."""
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
