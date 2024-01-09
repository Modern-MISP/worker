
from typing import List, Self

from src.api.worker_router.worker_router import WorkerEnum
from src.job.job import JobTypeEnum, Job
from src.worker.job import Job, WorkerStatusEnum


class WorkerController:
    _instance: Self
    worker: List[Job]

    @classmethod
    def instance(cls) -> Self:
        pass

    def get_next_job(self, types: List[JobTypeEnum]) -> Job:
        pass

    def get_worker_status(self, name: WorkerEnum) -> WorkerStatusEnum:
        pass

    def enable_worker(self, name: WorkerEnum) -> None:
        pass

    def disable_worker(self, name: WorkerEnum) -> None:
        pass
