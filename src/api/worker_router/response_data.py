from enum import Enum

from pydantic import BaseModel

from src.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo
from src.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo


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
    jobs_queued: int
