import os
from typing import Self

from src.mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from src.mmisp.worker.controller.celery.celery import celery
from src.mmisp.worker.api.worker_router.input_data import WorkerEnum
from src.mmisp.worker.exceptions.singleton_exception import SingletonException


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

        response: StartStopWorkerResponse = StartStopWorkerResponse()

        if self.is_worker_online(name):
            response.success = False
            response.message = "Worker already enabled"
            response.name = "Worker already enabled"

        else:
            # TODO
            pid_path: str = ""
            os.popen(f'celery -A main.celery worker -Q {name.value} ~--loglevel = info - n {name.value} - '
                     f'-pidfile {pid_path} ')
            response.success = True
            response.message = "Worker now enabled"
            response.name = "Worker now enabled"

        return response

    def disable_worker(self, name: WorkerEnum) -> StartStopWorkerResponse:
        response: StartStopWorkerResponse = StartStopWorkerResponse()

        if self.is_worker_online(name):
            os.popen('pkill -9 -f ' + name.value)
            response.success = True
            response.name = "Worker stop signal sent"
            response.message = "Worker stop signal sent"

        else:
            response.success = False
            response.name = "Worker already stopped"
            response.message = "Worker already stopped"

        return response
