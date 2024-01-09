from typing import List, TypedDict, Self

from src.job.job import Job


class JobController:
    _instance: Self

    @classmethod
    def instance(cls) -> Self:
        pass

    def add_job(self, job: Job) -> None:
        pass

    def get_job_status(self, job_id: int) -> str:
        pass

    def get_job_result(self, job_id: int) -> str:
        pass

    def cancel_job(self, job_id: int) -> bool:
        pass
