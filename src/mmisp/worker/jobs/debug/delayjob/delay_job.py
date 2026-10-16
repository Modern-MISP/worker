import asyncio
import logging

from mmisp.lib.logger import add_ajob_db_log
from streaq import WrappedContext

from .queue import queue

logger = logging.getLogger("mmisp")


@queue.task()
@add_ajob_db_log
async def delayjob(ctx: WrappedContext[None], user: dict, data: dict) -> None:
    logger.error("test info logger to db")
    await asyncio.sleep(10)
