"""
* UTILITY DECORATORS
"""
from typing import Callable


"""
* Decorator Funcs
"""


def auto_prop(func: Callable) -> property:
    """Property decorator wrapper that automatically creates a setter."""
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
    """Property decorator wrapper automatically creates a setter and caches the value."""
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


def choose_class_route(condition: bool) -> Callable:
    """
    A decorator that routes a method call to the current class or its parent based on a bool condition.
    @param condition: Route to self if True, otherwise route to self's superclass.
    @return: The wrapped function.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if condition:
                return func(self, *args, **kwargs)
            return getattr(super(self.__class__, self), func.__name__)(*args, **kwargs)
        return wrapper
    return decorator


"""
* Decorator Classes
"""


class enum_class_prop:
    """A decorator for creating a static property for Enum classes."""

    def __init__(self, method: Callable):
        """
        Initializes the property.
        @param method: Class method being decorated.
        """
        self._method = method
        self._name = method.__name__

    def __get__(self, instance, owner):
        """
        Computes and caches the value of a property when accessed.
        @param instance: Instance of the class where descriptor is accessed.
        @param owner: The class that the descriptor exists on.
        @return: The cached value.
        """
        value = self._method(owner)
        setattr(owner, self._name, value)
        return value
