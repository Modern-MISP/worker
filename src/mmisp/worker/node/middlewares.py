import logging
from typing import Any, Callable, Coroutine, TypeVar

from streaq import WrappedContext

from mmisp.db.database import sessionmanager
from mmisp.lib.logger import print_request_log, reset_db_log, reset_request_log, save_db_log

logger = logging.getLogger("mmisp")

T = TypeVar("T")


def log_middleware(
    ctx: WrappedContext, task: Callable[..., Coroutine[Any, Any, T]]
) -> Callable[..., Coroutine[Any, Any, T]]:
    async def wrapper(*args, **kwargs) -> T:
        reset_request_log()
        reset_db_log()
        try:
            result = await task(*args, **kwargs)
        except:
            logger.error("Exception occurred", exc_info=True)
            print_request_log()
            raise
        else:
            # Emit all logs at the end of the request if no exception
            assert sessionmanager is not None
            async with sessionmanager.session() as db:
                await save_db_log(db)
            print_request_log()
        return result

    return wrapper
