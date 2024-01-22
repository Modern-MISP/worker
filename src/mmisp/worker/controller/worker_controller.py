from typing import Self

from celery import Celery

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
        if report.get(name) is None:
            return False

        return True

    def is_worker_active(self, name: WorkerEnum) -> bool:
        report: dict = celery.control.inspect().active

        if report.get(name).isempty():
            return False

        return True

    def get_job_count(self, name: WorkerEnum) -> int:
        return len(celery.control.inspect.reserved()[name])

    def enable_worker(self, name: WorkerEnum) -> None:
        pass

    def disable_worker(self, name: WorkerEnum) -> None:
        pass
