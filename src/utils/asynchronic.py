from asyncio import EventLoop, Future, InvalidStateError, get_running_loop, run
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from threading import Thread
from typing import Any

_logger = getLogger(__name__)

_thread_pool = ThreadPoolExecutor(max_workers=4)


def async_to_sync[T](awaitable: Coroutine[Any, Any, T]) -> T:
    return _thread_pool.submit(run, awaitable, loop_factory=EventLoop).result()


def run_in_thread[T](coro: Coroutine[Any, Any, T]) -> Thread:
    def target():
        # Using asyncio.run without a factory starts another Qt loop, since
        # Qt sets the global loop policy to it's own implementation.
        # Starting another Qt loop fails, because the loop also tries to
        # exec another Qt application. As a workaround, we have to specifically
        # create an instance of the default non-Qt event loop.
        run(coro, loop_factory=EventLoop)

    thread = Thread(target=target)
    thread.start()
    return thread


async def run_in_thread_async[T](coro: Coroutine[Any, Any, T]) -> None:
    def target():
        # Using asyncio.run without a factory starts another Qt loop, since
        # Qt sets the global loop policy to it's own implementation.
        # Starting another Qt loop fails, because the loop also tries to
        # exec another Qt application. As a workaround, we have to specifically
        # create an instance of the default non-Qt event loop.
        run(coro, loop_factory=EventLoop)

    get_running_loop().run_in_executor(_thread_pool, target)


def try_threadsafe_set_result[T](task: Future[T], result: T) -> None:
    def set_result_if_not_done():
        if not task.done():
            try:
                task.set_result(result)
            except InvalidStateError as err:
                _logger.warning("Failed to set future result", exc_info=err)

    task.get_loop().call_soon_threadsafe(set_result_if_not_done)
