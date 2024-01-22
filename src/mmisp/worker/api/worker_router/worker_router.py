import os

import dictionary
from celery import app, Celery
from fastapi import APIRouter

from src.mmisp.worker.api.worker_router.input_data import WorkerEnum
from src.mmisp.worker.api.worker_router.response_data import (StartStopWorkerResponse, WorkerStatusResponse)
from src.mmisp.worker.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from src.mmisp.worker.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from src.mmisp.worker.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo

from src.mmisp.worker.api.worker_router.response_data import WorkerStatusEnum

worker_router = APIRouter(prefix="/worker")


@worker_router.post("/{name}/enable")
def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@worker_router.post("/{name}/disable")
def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    os.popen('pkill -9 -f ' + name)
    return StartStopWorkerResponse()


@worker_router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:
    """TODO den celery_app bums in Konstruktor?"""

    celery_app = Celery('worker', broker='redis:')
    report: dictionary = celery_app.control.inspect().active

    response: StartStopWorkerResponse = StartStopWorkerResponse()
    response.jobs_queued = celery_app.control.inspect.reserved()[name]

    if report.get(name) is None:
        response.status = WorkerStatusEnum.DEACTIVATED
    elif report.get(name).isempty():
        response.status = WorkerStatusEnum.IDLE
    else:
        response.status = WorkerStatusEnum.WORKING

    return response


@worker_router.get("/enrichment/plugins")
def get_enrichment_plugins() -> list[EnrichmentPluginInfo]:
    return {}


@worker_router.get("/correlation/plugins")
def get_correlation_plugins() -> list[CorrelationPluginInfo]:
    return {}


@worker_router.put("/correlation/changeThreshold")
def put_new_threshold(data: ChangeThresholdData) -> ChangeThresholdResponse:
    return ChangeThresholdResponse()
