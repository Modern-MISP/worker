
from typing import List, Self

from src.api.worker_router.worker_router import WorkerEnum


class WorkerController:
    __instance: Self

    @classmethod
    def get_instance(cls) -> Self:
        pass

    def is_worker_online(self, name: WorkerEnum) -> bool:
        pass

    def is_worker_active(self, name: WorkerEnum) -> bool:
        pass

    def enable_worker(self, name: WorkerEnum) -> None:
        pass

    def disable_worker(self, name: WorkerEnum) -> None:
        pass
