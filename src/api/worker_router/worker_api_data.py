from pydantic import BaseModel

from src.worker.job import WorkerStatusEnum


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
