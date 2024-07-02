import logging
import platform
import subprocess
from subprocess import Popen
from typing import Type

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from mmisp.worker.config.system_config_data import system_config_data
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.misp_database.mmisp_redis import MMispRedis

log = logging.getLogger(__name__)


class WorkerController:
    """
    Encapsulates the logic of the API for the worker router
    """

    __worker_processes: dict[WorkerEnum, set[Popen]] = {worker: set() for worker in WorkerEnum}
    __NOW_ENABLED: str = "{worker_name}-Worker now enabled"
    __ALREADY_ENABLED: str = "{worker_name}-Worker already enabled"
    __STOPPED_SUCCESSFULLY: str = "{worker_name}-Worker stopped successfully"
    __ALREADY_STOPPED: str = "{worker_name}-Worker was already stopped"

    @classmethod
    def enable_worker(cls: Type["WorkerController"], name: WorkerEnum) -> StartStopWorkerResponse:
        """
        Enables the specified worker,if it is not already enabled
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: A response containing information about the success of enabling the worker
        :rtype: StartStopWorkerResponse
        """

        if len(cls.__worker_processes[name]) > 0:
            return StartStopWorkerResponse(
                success=False,
                message=cls.__ALREADY_ENABLED.format(worker_name=name.value.capitalize()),
                url=f"/worker/{name.value}/enable",
            )
        else:
            from mmisp.worker.controller.celery_client import celery_client

            cls.__worker_processes[name].add(
                subprocess.Popen(
                    f"celery -A {celery_client.__name__} worker -Q {name.value} "
                    f"--loglevel=info -n {name.value}@%h --concurrency 1",
                    shell=True,
                )
            )
            # f"--pidfile={os.path.join(PID_FILE_PATH, f'{name.value}.pid')}"))

            return StartStopWorkerResponse(
                success=True,
                message=cls.__NOW_ENABLED.format(worker_name=name.value.capitalize()),
                url=f"/worker/{name.value}/enable",
            )

    @classmethod
    def disable_worker(cls: Type["WorkerController"], name: WorkerEnum) -> StartStopWorkerResponse:
        """
        Disables the specified worker,if it is not already disabled
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: A response containing information about the success of disabling the worker
        :rtype: StartStopWorkerResponse
        """

        if len(cls.__worker_processes[name]) > 0:
            for process in cls.__worker_processes[name]:
                process.terminate()

                try:
                    process.wait(timeout=system_config_data.worker_termination_timeout)
                except subprocess.TimeoutExpired:
                    log.exception("Process did not terminate in time. Had to kill...")
                    process.kill()

            cls.__worker_processes[name].clear()

            return StartStopWorkerResponse(
                success=True,
                message=WorkerController.__STOPPED_SUCCESSFULLY.format(worker_name=name.value.capitalize()),
                url=f"/worker/{name.value}/disable",
            )
        else:
            return StartStopWorkerResponse(
                success=False,
                message=WorkerController.__ALREADY_STOPPED.format(worker_name=name.value.capitalize()),
                url=f"/worker/{name.value}/disable",
            )

    @classmethod
    def is_worker_online(cls: Type["WorkerController"], name: WorkerEnum) -> bool:
        """
        Checks if the specified worker is online
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: True if the worker online, else False
        :rtype: bool
        """

        return len(cls.__worker_processes[name]) > 0

    @staticmethod
    def is_worker_active(name: WorkerEnum) -> bool:
        """
        Checks if the specified worker is active
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: True if the worker active, else False
        :rtype: bool

        """
        report: dict = celery_app.control.inspect().active()

        if report:
            return bool(report.get(f"{name.value}@{platform.node()}"))
        return False

    @classmethod
    def get_job_count(cls: Type["WorkerController"], name: WorkerEnum) -> int:
        """
        Returns the number of jobs in the specified worker queue
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: The amount of jobs in the worker queue
        :rtype: int
        """

        job_count: int = 0

        reserved_tasks: dict = celery_app.control.inspect().reserved()
        worker_name: str = f"{name.value}@{platform.node()}"

        if reserved_tasks and worker_name in reserved_tasks:
            job_count += len(reserved_tasks[worker_name])

        job_count += MMispRedis().get_enqueued_celery_tasks(name)
        return job_count
