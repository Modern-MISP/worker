
from typing import List, Self

from src.api.worker_router.worker_router import WorkerEnum
from src.job.job import Job, WorkerStatusEnum


class WorkerController:
    _instance: Self
    worker: List[Job]

    @classmethod
    def instance(cls) -> Self:
        pass

    def is_worker_online(self, name: WorkerEnum) -> bool:
        pass

    def is_worker_active(self, name: WorkerEnum) -> bool:
        pass

    def enable_worker(self, name: WorkerEnum) -> None:
        pass

    def disable_worker(self, name: WorkerEnum) -> None:
        pass
