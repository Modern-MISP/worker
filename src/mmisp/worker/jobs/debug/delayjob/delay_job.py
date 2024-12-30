import asyncio

from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.worker.controller.celery_client import celery_app

logger = get_jobs_logger(__name__)


@celery_app.task
def delayjob() -> None:
    asyncio.run(_delayjob())


@add_ajob_db_log
async def _delayjob() -> None:
    logger.error("test info logger to db")
    await asyncio.sleep(10)
