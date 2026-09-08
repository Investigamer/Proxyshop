from collections.abc import Callable
from functools import cached_property
from threading import Thread

from src.utils.event import SubscribableEvent


class ThreadInitializedInstance[T]:
    def __init__(self, factory: Callable[[], T]) -> None:
        self._on_ready: SubscribableEvent[T] = SubscribableEvent()
        self._factory = factory
        self.ready: bool = False
        self._initialization: Thread | None = None

    @cached_property
    def instance(self) -> T:
        # Instance access is synchronous
        if thread := self.initialize():
            thread.join()
        return self.instance

    def initialize(self) -> Thread | None:
        """
        Start initialization of instance.

        Initialize should be called well ahead of the moment
        when the instance is actually needed, because instance
        access is synchronous.

        Subscribe to `on_ready` to access the instance in a callback once it's ready.
        """
        if self.ready:
            return None

        if not self._initialization:

            def init_in_thread() -> None:
                self.instance = self._factory()
                self.ready = True
                self._initialization = None
                self._on_ready.trigger(self.instance)

            self._initialization = Thread(target=init_in_thread)
            self._initialization.start()

        return self._initialization

    def add_listener(self, listener: Callable[[T], None]) -> None:
        self._on_ready.listen_once(listener)

    def remove_listener(self, listener: Callable[[T], None]) -> None:
        self._on_ready.remove_listener(listener)
