import os
from typing import Self

from mmisp.worker.api.worker_router.response_data import StartStopWorkerResponse
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.api.worker_router.input_data import WorkerEnum


class WorkerController:
    __NOW_ENABLED: str = "Worker now enabled"
    __ALREADY_ENABLED: str = "Worker already enabled"
    __STOPPED_SUCCESSFULLY: str = "Worker stopped successfully"
    __ALREADY_STOPPED: str = "Worker was already stopped"

    @staticmethod
    def is_worker_online(name: WorkerEnum) -> bool:
        report: dict = celery_app.control.inspect().active
        if report.get(name.value) is None:
            return False

        return True

    @staticmethod
    def is_worker_active(name: WorkerEnum) -> bool:
        report: dict = celery_app.control.inspect().active

        if report.get(name.value).isempty():
            return False

        return True

    @staticmethod
    def get_job_count(name: WorkerEnum) -> int:
        return len(celery_app.control.inspect.reserved()[name.value])

    @staticmethod
    def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:

        if WorkerController.is_worker_online(name):
            return StartStopWorkerResponse(saved=True, success=False, name=WorkerController.__ALREADY_ENABLED,
                                           message=WorkerController.__ALREADY_ENABLED,
                                           url="/worker/" + name.value + "/enable")
        else:
            # TODO
            pid_path: str = ""
            os.popen(f'celery -A main.celery worker -Q {name.value} ~--loglevel = info - n {name.value} - '
                     f'-pidfile {pid_path} ')
            return StartStopWorkerResponse(saved=True, success=True, name=WorkerController.__NOW_ENABLED,
                                           message=WorkerController.__NOW_ENABLED,
                                           url="/worker/" + name.value + "/enable")

    @staticmethod
    def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:

        if WorkerController.is_worker_online(name):
            os.popen('pkill -9 -f ' + name.value)

            return StartStopWorkerResponse(saved=True, success=True, name=WorkerController.__STOPPED_SUCCESSFULLY,
                                           message=WorkerController.__STOPPED_SUCCESSFULLY,
                                           url="/worker/" + name.value + "/disable")
        else:
            return StartStopWorkerResponse(saved=True, success=False, name=WorkerController.__ALREADY_STOPPED,
                                           message=WorkerController.__ALREADY_STOPPED,
                                           url="/worker/" + name.value + "/disable")
