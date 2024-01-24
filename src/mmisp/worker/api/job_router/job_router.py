"""
Encapsulates API calls for jobs
"""

from celery.states import state
from fastapi import APIRouter, HTTPException

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.api.job_router.response_data import JobStatusResponse, CreateJobResponse, DeleteJobResponse
from mmisp.worker.controller.job_controller import ResponseData, JobController
from mmisp.worker.exceptions.job_exceptions import NotExistentJobException, JobNotFinishedException
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import clean_excluded_correlations_job
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value_job
from mmisp.worker.jobs.correlation.correlation_plugin_job import correlation_plugin_job
from mmisp.worker.jobs.correlation.job_data import CorrelationPluginJobData, CorrelateValueData
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import regenerate_occurrences_job
from mmisp.worker.jobs.correlation.top_correlations_job import top_correlations_job
from mmisp.worker.jobs.email.alert_email_job import AlertEmailData, alert_email_job
from mmisp.worker.jobs.email.contact_email_job import ContactEmailData, contact_email_job
from mmisp.worker.jobs.email.posts_email_job import PostsEmailData, posts_email_job
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute_job
from mmisp.worker.jobs.enrichment.enrich_event_job import enrich_event_job
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData, EnrichEventData
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData
from mmisp.worker.jobs.processfreetext.processfreetext_job import processfreetext_job
from mmisp.worker.jobs.pull.job_data import PullData
from mmisp.worker.jobs.pull.pull_job import pull_job
from mmisp.worker.jobs.push.job_data import PushData
from mmisp.worker.jobs.push.push_job import push_job

job_router: APIRouter = APIRouter(prefix="/jobs")


@job_router.get("/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: str) -> JobStatusResponse:
    """
    TODO
    :param job_id:
    :type job_id:
    :return:
    :rtype:
    """
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    status: state = JobController.get_job_status(job_id)

    # TODO: Initialize response
    response = JobStatusResponse()

    return response


@job_router.post("/correlationPlugin")
def create_correlation_plugin_job(user: UserData, data: CorrelationPluginJobData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the correlation_plugin_job
    :type data: CorrelationPluginJobData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(correlation_plugin_job, data)


@job_router.post("/pull")
def create_pull_job(user: UserData, data: PullData) -> CreateJobResponse:
    """

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the pull
    :type data: PullData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(pull_job, user, data)


@job_router.post("/push")
def create_push_job(user: UserData, data: PushData) -> CreateJobResponse:
    """

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the push
    :type data: PushData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(push_job, user, data)


@job_router.post("/enrichEvent")
def create_enrich_event_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the enrich_event_job
    :type data: EnrichEventData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(enrich_event_job, data)


@job_router.post("/enrichAttribute")
def create_enrich_attribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the enrich_attribute_job
    :type data: EnrichAttributeData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(enrich_attribute_job, data)


@job_router.post("/postsEmail")
def create_posts_email_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the posts_email_job
    :type data: PostsEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(posts_email_job, data)


@job_router.post("/alertEmail")
def create_alert_email_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the alert_email_job
    :type data: AlertEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(alert_email_job, data)


@job_router.post("/contactEmail")
def create_contact_email_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    """

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the contact_email_job
    :type data: ContactEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(contact_email_job, user, data)


@job_router.post("/processFreeText")
def create_processfreetext_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    """

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the processfreetext
    :type data: ProcessFreeTextData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(processfreetext_job, user, data)


@job_router.post("/correlateValue")
def create_correlate_value_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the correlate_value_job
    :type data: CorrelateValueData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(correlate_value_job(), data)


@job_router.post("/topCorrelations")
def create_top_correlations_job(user: UserData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(top_correlations_job)


@job_router.post("/cleanExcluded")
def create_clean_excluded_job(user: UserData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(clean_excluded_correlations_job)


@job_router.post("/regenerateOccurrences")
def create_regenerate_occurrences_job(user: UserData) -> CreateJobResponse:
    """

    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(regenerate_occurrences_job)


@job_router.get("/{jobId}/result",
                responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204: {}})
def get_job_result(job_id: str) -> ResponseData:
    """

    :param job_id:
    :type job_id:
    :return:
    :rtype:
    """
    # TODO tf is != 0 und 1 bei string??????
    if job_id != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if job_id != 1:
        raise HTTPException(status_code=204, description="The jobs has no result")
        # raise HTTPException(status_code=202, description="The jobs is not yet finished, please try again later")
    return JobController.get_job_result(job_id)


@job_router.delete("/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(job_id: str) -> DeleteJobResponse:
    """

    :param job_id:
    :type job_id:
    :return:
    :rtype:
    """
    JobController.cancel_job(job_id)
    return {} # TODO
