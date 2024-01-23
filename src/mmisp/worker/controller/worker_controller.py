import os
from typing import Self

from mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from mmisp.worker.controller.celery.celery import celery
from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.exceptions.singleton_exception import SingletonException


class WorkerController:
    __instance: Self

    @classmethod
    def get_instance(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = WorkerController()

        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise SingletonException("Attempted to create a second instance of the 'WorkerController' class.")

    def is_worker_online(self, name: WorkerEnum) -> bool:
        report: dict = celery.control.inspect().active
        if report.get(name.value) is None:
            return False

        return True

    def is_worker_active(self, name: WorkerEnum) -> bool:
        report: dict = celery.control.inspect().active

        if report.get(name.value).isempty():
            return False

        return True

    def get_job_count(self, name: WorkerEnum) -> int:
        return len(celery.control.inspect.reserved()[name.value])

    def enable_worker(self, name: WorkerEnum) -> StartStopWorkerResponse:

        if self.is_worker_online(name):
            return StartStopWorkerResponse(saved=True, success=False, name="Worker already enabled",
                                           message="Worker already enabled",
                                           url="/worker/" + name.value + "/enable")
        else:
            # TODO
            pid_path: str = ""
            os.popen(f'celery -A main.celery worker -Q {name.value} ~--loglevel = info - n {name.value} - '
                     f'-pidfile {pid_path} ')
            return StartStopWorkerResponse(saved=True, success=True, name="Worker now enabled",
                                           message="Worker now enabled",
                                           url="/worker/" + name.value + "/enable")

    def disable_worker(self, name: WorkerEnum) -> StartStopWorkerResponse:

        if self.is_worker_online(name):
            os.popen('pkill -9 -f ' + name.value)

            return StartStopWorkerResponse(saved=True, success=True, name="Worker stopped successfully",
                                           message="Worker stopped successfully",
                                           url="/worker/" + name.value + "/disable")
        else:
            return StartStopWorkerResponse(saved=True, success=False, name="Worker was already stopped",
                                           message="Worker was already stopped",
                                           url="/worker/" + name.value + "/disable")
