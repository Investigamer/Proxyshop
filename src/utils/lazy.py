from collections.abc import Callable
from functools import cached_property


class LazyLoader[T]:
    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory

    @cached_property
    def _cached_value(self) -> T:
        return self._factory()

    def __call__(self) -> T:
        return self._cached_value
