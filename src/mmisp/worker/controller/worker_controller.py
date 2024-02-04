import os
import platform

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from mmisp.worker.controller.celery_app.celery_app import celery_app

PID_FILE_PATH: str = os.path.expanduser("~/.mmisp/worker/celery/")
os.makedirs(PID_FILE_PATH, exist_ok=True)


class WorkerController:
    """
    Encapsulates the logic of the API for the worker router
    """

    __NOW_ENABLED: str = "{worker_name}-Worker now enabled"
    __ALREADY_ENABLED: str = "{worker_name}-Worker already enabled"
    __STOPPED_SUCCESSFULLY: str = "{worker_name}-Worker stopped successfully"
    __ALREADY_STOPPED: str = "{worker_name}-Worker was already stopped"

    @staticmethod
    def is_worker_online(name: WorkerEnum) -> bool:
        """
        Checks if the specified worker is online
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: True if the worker online, else False
        :rtype: bool
        """
        report: dict = celery_app.control.inspect().active()
        if report:
            # return report.get(f"{name.value}@{platform.node()}")
            return f"{name.value}@{platform.node()}" in report
        return False

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
            return not report.get(f"{name.value}@{platform.node()}").isempty()
        return False

    @staticmethod
    def get_job_count(name: WorkerEnum) -> int:
        """
        Returns the number of jobs in the specified worker queue
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: The amount of jobs in the worker queue
        :rtype: int
        """
        return len(celery_app.control.inspect.reserved()[name.value])

    @classmethod
    def enable_worker(cls, name: WorkerEnum) -> StartStopWorkerResponse:
        """
        Enables the specified worker,if it is not already enabled
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: A response containing information about the success of enabling the worker
        :rtype: StartStopWorkerResponse
        """
        if cls.is_worker_online(name):
            return StartStopWorkerResponse(success=False,
                                           message=cls.__ALREADY_ENABLED.format(worker_name=name.value.capitalize()),
                                           url="/worker/" + name.value + "/enable")
        else:
            from mmisp.worker.controller.celery_app import celery_app
            os.popen(f"celery -A {celery_app.__name__} worker -Q {name.value} "
                     f"--loglevel=info -n {name.value}@%h --concurrency 1 "
                     f"--pidfile={os.path.join(PID_FILE_PATH, f'{name.value}.pid')}")

            return StartStopWorkerResponse(success=True,
                                           message=cls.__NOW_ENABLED.format(worker_name=name.value.capitalize()),
                                           url="/worker/" + name.value + "/enable")

    @staticmethod
    def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
        """
        Disables the specified worker,if it is not already disabled
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: A response containing information about the success of disabling the worker
        :rtype: StartStopWorkerResponse
        """

        pid_file_path = os.path.join(PID_FILE_PATH, f"{name.value}.pid")
        if os.path.exists(pid_file_path):
        #if WorkerController.is_worker_online(name):
            #os.popen(f"pkill -9 -f {os.path.join(cls.PID_FILE_PATH, f'{name.value}.pid')}")
            os.popen(f"cat {pid_file_path} | xargs kill -9")

            return StartStopWorkerResponse(success=True,
                                           message=WorkerController.__STOPPED_SUCCESSFULLY.
                                           format(worker_name=name.value.capitalize()),
                                           url="/worker/" + name.value + "/disable")
        else:
            return StartStopWorkerResponse(success=False,
                                           message=WorkerController.__ALREADY_STOPPED.format(
                                               worker_name=name.value.capitalize()),
                                           url="/worker/" + name.value + "/disable")
