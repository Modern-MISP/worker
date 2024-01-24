import os

from mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.api.worker_router.input_data import WorkerEnum

"""
Encapsulates the logic of the API for the worker router 
"""


class WorkerController:
    __NOW_ENABLED: str = "Worker now enabled"
    __ALREADY_ENABLED: str = "Worker already enabled"
    __STOPPED_SUCCESSFULLY: str = "Worker stopped successfully"
    __ALREADY_STOPPED: str = "Worker was already stopped"

    @staticmethod
    def is_worker_online(name: WorkerEnum) -> bool:
        """
        Checks if the specified worker is online
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: True if the worker online, else False
        :rtype: bool
        """
        report: dict = celery_app.control.inspect().active
        if report.get(name.value) is None:
            return False

        return True

    @staticmethod
    def is_worker_active(name: WorkerEnum) -> bool:
        """
        Checks if the specified worker is active
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: True if the worker active, else False
        :rtype: bool

        """
        report: dict = celery_app.control.inspect().active

        if report.get(name.value).isempty():
            return False

        return True

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

    @staticmethod
    def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
        """
        Enables the specified worker,if it is not already enabled
        :param name: Contains the name of the worker
        :type name: WorkerEnum
        :return: A response containing information about the success of enabling the worker
        :rtype: StartStopWorkerResponse
        """
        if WorkerController.is_worker_online(name):
            return StartStopWorkerResponse(saved=True, success=False, name=WorkerController.__ALREADY_ENABLED,
                                           message=WorkerController.__ALREADY_ENABLED,
                                           url="/worker/" + name.value + "/enable")
        else:
            os.popen(f'celery -A main.celery worker -Q {name.value} --loglevel = info - n {name.value} --concurrency 1')
            return StartStopWorkerResponse(saved=True, success=True, name=WorkerController.__NOW_ENABLED,
                                           message=WorkerController.__NOW_ENABLED,
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
        if WorkerController.is_worker_online(name):
            os.popen('pkill -9 -f ' + name.value)

            return StartStopWorkerResponse(saved=True, success=True, name=WorkerController.__STOPPED_SUCCESSFULLY,
                                           message=WorkerController.__STOPPED_SUCCESSFULLY,
                                           url="/worker/" + name.value + "/disable")
        else:
            return StartStopWorkerResponse(saved=True, success=False, name=WorkerController.__ALREADY_STOPPED,
                                           message=WorkerController.__ALREADY_STOPPED,
                                           url="/worker/" + name.value + "/disable")
