from typing import Self

from celery.states import state
from src.job.job import Job


class JobController:
    __instance: Self

    @classmethod
    def instance(cls) -> Self:
        pass

    def get_job_status(self, job_id: int) -> state:
        pass

    def get_job_result(self, job_id: int) -> str: #TODO return typ ändern
        pass

    def cancel_job(self, job_id: int) -> bool:
        pass
