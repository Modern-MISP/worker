import os

from fastapi import APIRouter

from src.mmisp.worker.api.worker_router.input_data import WorkerEnum
from src.mmisp.worker.api.worker_router.response_data import (StartStopWorkerResponse, WorkerStatusResponse,
                                                              WorkerStatusEnum)
from src.mmisp.worker.controller.worker_controller import WorkerController
from src.mmisp.worker.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from src.mmisp.worker.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from src.mmisp.worker.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo


worker_router = APIRouter(prefix="/worker")


@worker_router.post("/{name}/enable")
def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    pid_path: str = ""
    os.popen(f'celery -A main.celery worker -Q {name} ~--loglevel = info - n {name} - -pidfile {pid_path} ')
    return StartStopWorkerResponse()


@worker_router.post("/{name}/disable")
def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    os.popen('pkill -9 -f ' + name)
    return StartStopWorkerResponse()


@worker_router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:

    worker_controller: WorkerController = WorkerController.get_instance()

    response: WorkerStatusResponse = WorkerStatusResponse()

    if worker_controller.is_worker_online(name):
        if worker_controller.is_worker_active(name):
            response.status = WorkerStatusEnum.WORKING
        else:
            response.status = WorkerStatusEnum.IDLE
    else:
        response.status = WorkerStatusEnum.DEACTIVATED

    response.jobs_queued = worker_controller.get_job_count(name)
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
