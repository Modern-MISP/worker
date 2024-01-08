
from typing import List, Self
from kit.job.job import JobTypeEnum, Job
from kit.worker.worker import Worker, WorkerStatusEnum

class WorkerController:
    _instance: Self
    worker: List[Worker]

    @classmethod
    def instance(cls) -> Self:
        pass

    def get_next_job(self, types: List[JobTypeEnum]) -> Job:
        pass

    def get_worker_status(self, id: int) -> WorkerStatusEnum:
        pass

    def enable_worker(self, id: int) -> None:
        pass

    def disable_worker(self, id: int) -> None:
        pass
