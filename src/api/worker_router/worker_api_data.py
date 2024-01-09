from enum import Enum

from pydantic import BaseModel


class WorkerStatusEnum(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    DEACTIVATED = "deactivated"


class ChangeThresholdData(BaseModel):
    newThreshold: int


class ThresholdResponseData(BaseModel):
    saved: bool
    validThreshold: bool
    newThreshold: int | None


class StartStopWorkerResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str


class WorkerStatusResponse(BaseModel):
    status: WorkerStatusEnum
    jobsQueued: int
