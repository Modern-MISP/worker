from fastapi import APIRouter
from enum import Enum

from src.api.worker_router.input_data import ChangeThresholdData, WorkerEnum
from src.api.worker_router.response_data import (StartStopWorkerResponse, WorkerStatusResponse,
                                                 GetEnrichmentPluginsResponse, GetCorrelationPluginsResponse)
from src.job.correlation_job.response_data import ThresholdResponseData

worker_router = APIRouter(prefix="/job")


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
def get_correlation_plugins() -> GetCorrelationPluginsResponse:
    return {}


@worker_router.put("/correlation/changeThreshold")
def put_new_threshold(data: ChangeThresholdData) -> ThresholdResponseData:
    return ThresholdResponseData()
