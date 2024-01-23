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
    return WorkerController.get_instance().enable_worker(name)


@worker_router.post("/{name}/disable")
def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return WorkerController.get_instance().disable_worker(name)


@worker_router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:
    worker_controller: WorkerController = WorkerController.get_instance()

    jobs_queued: int = worker_controller.get_job_count(name)

    if worker_controller.is_worker_online(name):
        if worker_controller.is_worker_active(name):
            return WorkerStatusResponse(jobs_queued=jobs_queued, status=WorkerStatusEnum.WORKING.value)
        else:
            return WorkerStatusResponse(jobs_queued=jobs_queued, status=WorkerStatusEnum.IDLE.value)
    else:
        return WorkerStatusResponse(jobs_queued=jobs_queued, status=WorkerStatusEnum.DEACTIVATED.value)


@worker_router.get("/enrichment/plugins")
def get_enrichment_plugins() -> list[EnrichmentPluginInfo]:
    return EnrichmentWorker.get_plugins()


@worker_router.get("/correlation/plugins")
def get_correlation_plugins() -> list[CorrelationPluginInfo]:
    return CorrelationWorker.get_plugins()


@worker_router.put("/correlation/changeThreshold")
def put_new_threshold(data: ChangeThresholdData) -> ChangeThresholdResponse:
    return ChangeThresholdResponse()
