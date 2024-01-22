from typing import Self

import dictionary

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
        pass

    def is_worker_active(self, name: WorkerEnum) -> bool:
        pass

    def enable_worker(self, name: WorkerEnum) -> None:
        pass

    def disable_worker(self, name: WorkerEnum) -> None:
        """TODO den celery_app bums in Konstruktor?"""

        celery_app = Celery('worker', broker='redis:')
        report: dictionary = celery_app.control.inspect().active

        response: WorkerStatusResponse = WorkerStatusResponse()
        response.jobs_queued = len(celery_app.control.inspect.reserved()[name])

        if report.get(name) is None:
            response.status = WorkerStatusEnum.DEACTIVATED
        elif report.get(name).isempty():
            response.status = WorkerStatusEnum.IDLE
        else:
            response.status = WorkerStatusEnum.WORKING

        return response
