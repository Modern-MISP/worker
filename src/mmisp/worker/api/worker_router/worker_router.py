"""
Encapsulates API calls for worker
"""
from fastapi import APIRouter

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.api.worker_router.response_data import (StartStopWorkerResponse, WorkerStatusResponse,
                                                          WorkerStatusEnum)
from mmisp.worker.controller.worker_controller import WorkerController
from mmisp.worker.jobs.correlation.job_data import ChangeThresholdResponse, ChangeThresholdData
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginInfo

from mmisp.worker.jobs.enrichment.enrichment_worker import EnrichmentWorker
from mmisp.worker.jobs.correlation.correlation_worker import CorrelationWorker

worker_router: APIRouter = APIRouter(prefix="/worker")


@worker_router.post("/{name}/enable")
def enable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    """
    Enables the specified worker,if it is not already enabled
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: A response containing information about the success of enabling the worker
    :rtype: StartStopWorkerResponse
    """
    return WorkerController.enable_worker(name)


@worker_router.post("/{name}/disable")
def disable_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    """
    Disables the specified worker,if it is not already disabled
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: A response containing information about the success of disabling the worker
    :rtype: StartStopWorkerResponse
    """
    return WorkerController.disable_worker(name)


@worker_router.get("/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:
    """
    Returns the status of the specified worker
    :param name: Contains the name of the worker
    :type name: WorkerEnum
    :return: The status of the worker and the amount of queued jobs
    :rtype: WorkerStatusResponse
    """
    jobs_queued: int = WorkerController.get_job_count(name)

    if WorkerController.is_worker_online(name):
        if WorkerController.is_worker_active(name):
            return WorkerStatusResponse(jobs_queued=jobs_queued, status=WorkerStatusEnum.WORKING.value)
        else:
            return WorkerStatusResponse(jobs_queued=jobs_queued, status=WorkerStatusEnum.IDLE.value)
    else:
        return WorkerStatusResponse(jobs_queued=jobs_queued, status=WorkerStatusEnum.DEACTIVATED.value)


@worker_router.get("/enrichment/plugins")
def get_enrichment_plugins() -> list[EnrichmentPluginInfo]:
    """
    Returns for each loaded enrichment plugin an information
    :return:  A list of all loaded enrichment plugins information
    :rtype: list[EnrichmentPluginInfo]
    """
    return EnrichmentWorker.get_plugins()


@worker_router.get("/correlation/plugins")
def get_correlation_plugins() -> list[CorrelationPluginInfo]:
    """
    Returns for each loaded correlation plugin an information
    :return:  A list of all loaded correlation plugins information
    :rtype: list[CorrelationPluginInfo]
    """
    return CorrelationWorker.get_plugins()


@worker_router.put("/correlation/changeThreshold")
def put_new_threshold(data: ChangeThresholdData) -> ChangeThresholdResponse:
    """
    TODO Tobias Pydoc
    :param data:
    :type data:
    :return:
    :rtype:
    """
    return ChangeThresholdResponse()
