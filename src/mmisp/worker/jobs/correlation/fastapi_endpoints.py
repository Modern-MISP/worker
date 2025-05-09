from typing import Annotated

from fastapi import Body, Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.api.worker_router import worker_router
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import clean_excluded_correlations_job

# from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value_job
from mmisp.worker.jobs.correlation.correlation_job import correlation_job
from mmisp.worker.jobs.correlation.job_data import (
    ChangeThresholdData,
    ChangeThresholdResponse,
    CorrelationJobData,
)

# from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import regenerate_occurrences_job
from mmisp.worker.jobs.correlation.top_correlations_job import top_correlations_job

from .queue import queue


@job_router.post("/correlationPlugin", dependencies=[Depends(verified)])
async def create_correlation_job(user: UserData, data: CorrelationJobData) -> CreateJobResponse:
    """
    Creates a correlation_job

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the correlation_job
    :type data: CorrelationJobData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return await job_controller.create_job(queue, correlation_job, user, data)


@job_router.post("/topCorrelations", dependencies=[Depends(verified)])
async def create_top_correlations_job(user: Annotated[UserData, Body(embed=True)]) -> CreateJobResponse:
    """
    Creates a top_correlations_job

    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return await job_controller.create_job(queue, top_correlations_job, user)


@job_router.post("/cleanExcluded", dependencies=[Depends(verified)])
async def create_clean_excluded_job(user: Annotated[UserData, Body(embed=True)]) -> CreateJobResponse:
    """
    Creates a clean_excluded_job

    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return await job_controller.create_job(queue, clean_excluded_correlations_job, user)


@job_router.post("/regenerateOccurrences", dependencies=[Depends(verified)])
async def create_regenerate_occurrences_job(user: Annotated[UserData, Body(embed=True)]) -> CreateJobResponse:
    """
    Creates a regenerate-occurrences_job

    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return await job_controller.create_job(queue, regenerate_occurrences_job, user)


# @worker_router.get("/correlation/plugins", dependencies=[Depends(verified)])
# def get_correlation_plugins() -> list[CorrelationPluginInfo]:
#    """
#    Returns for each loaded correlation plugin an information
#    :return:  A list of all loaded correlation plugins information
#    :rtype: list[CorrelationPluginInfo]
#    """
#    return correlation_plugin_factory.get_plugins()


@worker_router.put("/correlation/changeThreshold", dependencies=[Depends(verified)])
def put_new_threshold(user: UserData, data: ChangeThresholdData) -> ChangeThresholdResponse:
    """
    Sets the threshold for the correlation jobs to a new value. Returns if the new threshold
    was saved successfully, if it was valid and the new threshold.
    :param user: the user who wants to change the threshold
    :type user: UserData
    :param data: contains the new threshold
    :type data: ChangeThresholdData
    :return: if the new threshold was saved, if it was valid and the new threshold
    :rtype: ChangeThresholdResponse
    """
    raise NotImplementedError("change threshold is currently not implemented")


@worker_router.get("/correlation/threshold", dependencies=[Depends(verified)])
def get_threshold() -> int:
    """
    Returns the current threshold for the correlation jobs
    :return: the current threshold
    :rtype: int
    """
    raise NotImplementedError("get threshold is currently not implemented")
