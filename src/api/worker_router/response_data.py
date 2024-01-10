from enum import Enum

from pydantic import BaseModel

from src.api.worker_router.plugin_data import EnrichmentPlugin, CorrelationPlugin


class WorkerStatusEnum(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    DEACTIVATED = "deactivated"


class StartStopWorkerResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str


class WorkerStatusResponse(BaseModel):
    status: WorkerStatusEnum
    jobsQueued: int


class GetEnrichmentPluginsResponse(BaseModel):
    plugins: list[EnrichmentPlugin]


class GetCorrelationPluginsResponse(BaseModel):
    plugins: list[CorrelationPlugin]