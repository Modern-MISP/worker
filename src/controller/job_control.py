from typing import Self

from celery.states import state
from celery.worker.control import revoke

from src.job.job import Job


class JobController:
    __instance: Self

    @classmethod
    def get_instance(cls) -> Self:
        pass

    def get_job_status(self, job_id: int) -> state:
        pass

    def get_job_result(self, job_id: int) -> str: #TODO return typ ändern
        pass

    def cancel_job(self, job_id: int) -> bool:
        revoke(job_id, terminate=True)
        pass
