from fastapi import APIRouter
from enum import Enum

from kit.api.worker_router.plugin_data import GetEnrichmentPluginsResponse, GetCorrelationPluginsResponse
from kit.api.worker_router.worker_api_data import ChangeThresholdData, ThresholdResponseData, StartStopWorkerResponse, \
    WorkerStatusResponse


class WorkerEnum(str, Enum):
    pull = "pull"
    push = "push"
    correlate = "correlation"
    enrichment = "enrichment"
    sendEmail = "sendEmail"
    processFreeText = "processFreeText"


worker_router = APIRouter(prefix="/worker")


@worker_router.post("/{name}/enable")
def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@worker_router.post("/{name}/disable")
def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@worker_router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:
    return {"status": "success"}


@worker_router.get("/enrichment/plugins")
def get_enrichment_plugins() -> GetEnrichmentPluginsResponse:
    return {}


@worker_router.get("/correlation/plugins")
def get_correlationPlugins() -> GetCorrelationPluginsResponse:
    return {}


@worker_router.put("/correlation/changeThreshold")
def put_newThreshold(data: ChangeThresholdData) -> ThresholdResponseData:
    return ThresholdResponseData()
