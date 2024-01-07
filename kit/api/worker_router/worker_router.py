from typing import List
from fastapi import APIRouter
from enum import Enum
from pydantic import BaseModel

from kit.api.job_router.job_router import JobReturnData
from kit.worker.correlation_job.plugins.correlation_plugin import CorrelationPluginType
from kit.worker.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType
from kit.plugins.plugin import PluginIO, PluginMeta
from kit.worker.job import WorkerStatusEnum


class WorkerEnum(str, Enum):
    pull = "pull"
    push = "push"
    correlate = "correlation"
    enrichment = "enrichment"
    sendEmail = "sendEmail"
    processFreeText = "processFreeText"


### datentypenklassem


class EnrichmentPlugin(BaseModel):
    plugin: PluginMeta
    enrichment: dict = {
        "type": EnrichmentPluginType,
        "mispAttributes": PluginIO
    }


class CorrelationPlugin(BaseModel):
    plugin: PluginMeta
    correlationType: CorrelationPluginType

class GetEnrichmentPluginsResponse(BaseModel):
    plugins: List[EnrichmentPlugin]


class GetCorrelationPluginsResponse(BaseModel):
    plugins: List[CorrelationPlugin]


class ChangeThresholdData(BaseModel):
    newThreshold: int


class ThresholdResponseData(BaseModel):
    saved: bool
    validThreshold: bool
    newThreshold: int | None


### define response types

class StartStopWorkerResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str


class WorkerStatusResponse(BaseModel):
    status: WorkerStatusEnum
    jobsQueued: int


router = APIRouter(prefix="/worker")


@router.post("/{name}/enable")
def enable_a_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@router.post("/{name}/disable")
def disable_a_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:
    return {"status": "success"}


@router.get("/enrichment/plugins")
def get_enrichment_plugins() -> GetEnrichmentPluginsResponse:
    return {}


@router.get("/correlation/plugins")
def get_correlationPlugins() -> GetCorrelationPluginsResponse:
    return {}


@router.put("/correlation/changeThreshold")
def put_newThreshold(data: ChangeThresholdData) -> ThresholdResponseData:
    return ThresholdResponseData()
