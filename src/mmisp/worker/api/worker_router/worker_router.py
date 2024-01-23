from fastapi import APIRouter

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.api.worker_router.response_data import (StartStopWorkerResponse, WorkerStatusResponse,
                                                              WorkerStatusEnum)
from mmisp.worker.controller.worker_controller import WorkerController
from mmisp.worker.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from mmisp.worker.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo

from src.mmisp.worker.job.correlation_job.correlation_worker import CorrelationWorker
from src.mmisp.worker.job.enrichment_job.enrichment_worker import EnrichmentWorker

worker_router = APIRouter(prefix="/worker")


@worker_router.post("/{name}/enable")
def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:

    response: StartStopWorkerResponse = WorkerController.get_instance().enable_worker(name)
    response.url = "/worker/" + name.value + "/enable"
    response.saved = True

    return response


@worker_router.post("/{name}/disable")
def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:

    response: StartStopWorkerResponse = WorkerController.get_instance().disable_worker(name)
    response.url = "/worker/" + name.value + "/disable"
    response.saved = True

    return response


@worker_router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:

    worker_controller: WorkerController = WorkerController.get_instance()
    response: WorkerStatusResponse = WorkerStatusResponse()

    if worker_controller.is_worker_online(name):
        if worker_controller.is_worker_active(name):
            response.status = WorkerStatusEnum.WORKING.value
        else:
            response.status = WorkerStatusEnum.IDLE.value
    else:
        response.status = WorkerStatusEnum.DEACTIVATED.value

    response.jobs_queued = worker_controller.get_job_count(name)

    return response


@worker_router.get("/enrichment/plugins")
def get_enrichment_plugins() -> list[EnrichmentPluginInfo]:
    return EnrichmentWorker.get_plugins()


@worker_router.get("/correlation/plugins")
def get_correlation_plugins() -> list[CorrelationPluginInfo]:
    return CorrelationWorker.get_plugins()


@worker_router.put("/correlation/changeThreshold")
def put_new_threshold(data: ChangeThresholdData) -> ChangeThresholdResponse:
    return ChangeThresholdResponse()
