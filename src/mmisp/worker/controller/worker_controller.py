import logging
import platform
from subprocess import Popen

from celery.app.control import Control

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.misp_database.mmisp_redis import MMispRedis

log = logging.getLogger(__name__)


"""
Encapsulates the logic of the API for the worker router
"""

__worker_processes: dict[WorkerEnum, set[Popen]] = {worker: set() for worker in WorkerEnum}
__NOW_ENABLED: str = "{worker_name}-Worker now enabled"
__ALREADY_ENABLED: str = "{worker_name}-Worker already enabled"
__STOPPED_SUCCESSFULLY: str = "{worker_name}-Worker stopped successfully"
__ALREADY_STOPPED: str = "{worker_name}-Worker was already stopped"


def is_worker_active(name: WorkerEnum) -> bool:
    """
    Checks if the specified worker is active
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: True if the worker active, else False
    :rtype: bool

    """
    # _TaskInfo is not defined in the celery package
    report: dict[str, list[dict]] = celery_app.control.inspect().active()  # type: ignore

    if report:
        return bool(report.get(f"{name.value}@{platform.node()}"))
    return False


async def get_job_count(name: WorkerEnum) -> int:
    """
    Returns the number of jobs in the specified worker queue
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: The amount of jobs in the worker queue
    :rtype: int
    """

    job_count: int = 0

    # _TaskInfo is not defined in the celery package
    reserved_tasks: dict[str, list[dict]] = celery_app.control.inspect().reserved()  # type: ignore
    worker_name: str = f"{name.value}@{platform.node()}"

    if reserved_tasks and worker_name in reserved_tasks:
        job_count += len(reserved_tasks[worker_name])

    job_count += await MMispRedis().get_enqueued_celery_tasks(name)
    return job_count


def inspect_active_queues():  # noqa
    return Control(celery_app).inspect.active_queues()


def pause_all_workers() -> None:
    Control(celery_app).broadcast("pause_consume_from_all_queues")


def reset_worker_queues() -> None:
    Control(celery_app).broadcast("reset_worker_queues")
