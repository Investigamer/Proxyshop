from collections.abc import Callable
from functools import wraps
from logging import Logger, getLogger

_logger = getLogger(__name__)


def log_on_exception[**P, T, E: Exception](
    msg: str | Callable[[E], str] = "",
    exception_type: type[E] = Exception,
    logger: Logger = _logger,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]):
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            try:
                return func(*args, **kwargs)
            except exception_type as e:
                logger.exception(msg if isinstance(msg, str) else msg(e))  # noqa: TRY401
                raise

        return wrapper

    return decorator
