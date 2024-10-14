import logging
import platform
import subprocess
from subprocess import Popen

from celery.app.control import Control

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from mmisp.worker.config import system_config_data
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


def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    """
    Enables the specified worker,if it is not already enabled
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: A response containing information about the success of enabling the worker
    :rtype: StartStopWorkerResponse
    """

    if len(__worker_processes[name]) > 0:
        return StartStopWorkerResponse(
            success=False,
            message=__ALREADY_ENABLED.format(worker_name=name.value.capitalize()),
            url=f"/worker/{name.value}/enable",
        )
    else:
        from mmisp.worker.controller import celery_client

        __worker_processes[name].add(
            subprocess.Popen(
                f"celery -A {celery_client.__name__} worker -Q {name.value} "
                f"--loglevel=info -n {name.value}@%h --concurrency 1",
                shell=True,
            )
        )
        # f"--pidfile={os.path.join(PID_FILE_PATH, f'{name.value}.pid')}"))

        return StartStopWorkerResponse(
            success=True,
            message=__NOW_ENABLED.format(worker_name=name.value.capitalize()),
            url=f"/worker/{name.value}/enable",
        )


def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    """
    Disables the specified worker,if it is not already disabled
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: A response containing information about the success of disabling the worker
    :rtype: StartStopWorkerResponse
    """

    if len(__worker_processes[name]) > 0:
        for process in __worker_processes[name]:
            process.terminate()

            try:
                process.wait(timeout=system_config_data.worker_termination_timeout)
            except subprocess.TimeoutExpired:
                log.exception("Process did not terminate in time. Had to kill...")
                process.kill()

        __worker_processes[name].clear()

        return StartStopWorkerResponse(
            success=True,
            message=__STOPPED_SUCCESSFULLY.format(worker_name=name.value.capitalize()),
            url=f"/worker/{name.value}/disable",
        )
    else:
        return StartStopWorkerResponse(
            success=False,
            message=__ALREADY_STOPPED.format(worker_name=name.value.capitalize()),
            url=f"/worker/{name.value}/disable",
        )


def is_worker_online(name: WorkerEnum) -> bool:
    """
    Checks if the specified worker is online
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: True if the worker online, else False
    :rtype: bool
    """

    return len(__worker_processes[name]) > 0


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
