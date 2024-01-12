from fastapi import APIRouter

from src.api.worker_router.input_data import WorkerEnum
from src.api.worker_router.response_data import (StartStopWorkerResponse, WorkerStatusResponse)
from src.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from src.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from src.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo

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
def get_enrichment_plugins() -> list[EnrichmentPluginInfo]:
    return {}


@worker_router.get("/correlation/plugins")
def get_correlation_plugins() -> list[CorrelationPluginInfo]:
    return {}


@worker_router.put("/correlation/changeThreshold")
def put_new_threshold(data: ChangeThresholdData) -> ChangeThresholdResponse:
    return ChangeThresholdResponse()
