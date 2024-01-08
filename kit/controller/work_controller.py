
from typing import List, Self

from kit.api.worker_router.worker_router import WorkerEnum
from kit.job.job import JobTypeEnum, Job
from kit.worker.job import Job, WorkerStatusEnum

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
