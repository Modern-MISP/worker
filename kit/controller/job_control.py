from typing import List, TypedDict, Self

from kit.job.job import Job, JobTypeEnum
from kit.job_database import job_database


class JobController:
    _instance: Self
    jobs: TypedDict[JobTypeEnum, List[int]]
    database: job_database

    @classmethod
    def instance(cls) -> Self:
        pass

    def add_job(self, job: Job) -> None:
        pass

    def pop_job(self, types: List[JobTypeEnum]) -> Job:
        pass

    def get_job_status(self, job_id: int) -> str:
        pass

    def get_job_result(self, job_id: int) -> str:
        pass

    def cancel_job(self, job_id: int) -> bool:
        pass
