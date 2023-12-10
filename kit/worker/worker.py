from abc import ABC
from enum import Enum

from kit.job.job import Job


class WorkerStatusEnum(str, Enum):
    idle = "idle"
    working = "working"
    deactivated = "deactivated"


class Worker(ABC):
    status: WorkerStatusEnum
    isOn: bool
    currJob: Job

    def setJob(self, job: Job):
        pass

    def setIsOn(self, val: bool) -> None:
        pass