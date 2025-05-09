from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse

# from mmisp.worker.api.worker_router import worker_router
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute_job
from mmisp.worker.jobs.enrichment.enrich_event_job import enrich_event_job
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData, EnrichEventData

# from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from .queue import queue


@job_router.post("/enrichEvent", dependencies=[Depends(verified)])
async def create_enrich_event_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    """
    Creates an enrich_event_job

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the enrich_event_job
    :type data: EnrichEventData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    async with queue:
        return await job_controller.create_job(queue, enrich_event_job, user, data)


@job_router.post("/enrichAttribute", dependencies=[Depends(verified)])
async def create_enrich_attribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    """
    Creates an enrich_attribute_job

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the enrich_attribute_job
    :type data: EnrichAttributeData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return await job_controller.create_job(queue, enrich_attribute_job, user, data)


# @worker_router.get("/enrichment/plugins", dependencies=[Depends(verified)])
# def get_enrichment_plugins() -> list[EnrichmentPluginInfo]:
#    """
#    Returns for each loaded enrichment plugin an information
#    :return:  A list of all loaded enrichment plugins information
#    :rtype: list[EnrichmentPluginInfo]
#    """
#    return enrichment_plugin_factory.get_plugins()
