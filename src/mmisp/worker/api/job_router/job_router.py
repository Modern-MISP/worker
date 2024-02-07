"""
Encapsulates API calls for jobs
"""

from fastapi import APIRouter, HTTPException, Depends

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.api.job_router.response_data import JobStatusResponse, CreateJobResponse, DeleteJobResponse, \
    JobStatusEnum, ExceptionResponse
from mmisp.worker.controller.job_controller import ResponseData, JobController
from mmisp.worker.exceptions.job_exceptions import NotExistentJobException, JobNotFinishedException, \
    JobHasNoResultException
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
from mmisp.worker.jobs.sync.pull.job_data import PullData
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from mmisp.worker.jobs.sync.push.job_data import PushData
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.api.api_verification import verified

job_router: APIRouter = APIRouter(prefix="/job")


@job_router.get("/{job_id}/status", responses={404: {"model": ExceptionResponse}}, dependencies=[Depends(verified)])
def get_job_status(job_id: str) -> JobStatusResponse:
    """
    TODO
    :param job_id:
    :type job_id:
    :return:
    :rtype:
    """

    try:
        status: JobStatusEnum = JobController.get_job_status(job_id)
    except NotExistentJobException as exception:
        raise HTTPException(status_code=404, detail=str(exception))

    match status:
        case JobStatusEnum.QUEUED:
            return JobStatusResponse(status=status, message="Job is currently enqueued")
        case JobStatusEnum.FAILED:
            return JobStatusResponse(status=status, message="Job failed during execution")
        case JobStatusEnum.REVOKED:
            return JobStatusResponse(status=status, message="The job was canceled before it could be processed")
        case JobStatusEnum.SUCCESS:
            return JobStatusResponse(status=status, message="Job is finished")
        case JobStatusEnum.IN_PROGRESS:
            pass
        case _:
            raise RuntimeError(
                "The Job with id {id} was in an unexpected state: {state}".format(id=job_id, state=status))


@job_router.get("/{job_id}/result", responses={404: {"model": ExceptionResponse},
                                              202: {"model": ExceptionResponse}, 409: {"model": ExceptionResponse}},
                dependencies=[Depends(verified)])
def get_job_result(job_id: str) -> ResponseData:
    """
    TODO write doc stuff
    :param job_id:
    :type job_id:
    :return:
    :rtype:
    """
    try:
        return JobController.get_job_result(job_id)
    except JobNotFinishedException as exception:
        raise HTTPException(status_code=409, detail=str(exception))
    except NotExistentJobException as exception:
        raise HTTPException(status_code=404, detail=str(exception))
    except JobHasNoResultException as exception:
        raise HTTPException(status_code=204, detail=str(exception))


@job_router.delete("/{job_id}/cancel", responses={404: {"model": ExceptionResponse}}, dependencies=[Depends(verified)])
def remove_job(job_id: str) -> DeleteJobResponse:
    """
    Removes the given job
    :param job_id: is the id of the job to remove
    :type job_id: str
    :return: the response to indicate if the job was successfully deleted
    :rtype: DeleteJobResponse
    """
    result = JobController.cancel_job(job_id)
    return DeleteJobResponse(success=result)


@job_router.post("/correlationPlugin", dependencies=[Depends(verified)])
def create_correlation_plugin_job(user: UserData, data: CorrelationPluginJobData) -> CreateJobResponse:
    """
    Creates a correlation_plugin_job
    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the correlation_plugin_job
    :type data: CorrelationPluginJobData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(correlation_plugin_job, data)


@job_router.post("/pull", dependencies=[Depends(verified)])
def create_pull_job(user: UserData, data: PullData) -> CreateJobResponse:
    """
    Creates a pull_job
    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the pull
    :type data: PullData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(pull_job, user, data)


@job_router.post("/push", dependencies=[Depends(verified)])
def create_push_job(user: UserData, data: PushData) -> CreateJobResponse:
    """
    Creates a push_job
    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the push
    :type data: PushData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(push_job, user, data)


@job_router.post("/enrichEvent", dependencies=[Depends(verified)])
def create_enrich_event_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    """
    Creates an enrich_event_job
    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the enrich_event_job
    :type data: EnrichEventData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(enrich_event_job, data)


@job_router.post("/enrichAttribute", dependencies=[Depends(verified)])
def create_enrich_attribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    """
    Creates an enrich_attribute_job
    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the enrich_attribute_job
    :type data: EnrichAttributeData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(enrich_attribute_job, data)


@job_router.post("/postsEmail", dependencies=[Depends(verified)])
def create_posts_email_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    """
    Creates a posts_email_job
    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the posts_email_job
    :type data: PostsEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(posts_email_job, data)


@job_router.post("/alertEmail", dependencies=[Depends(verified)])
def create_alert_email_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    """
    Creates an alert_email_job
    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the alert_email_job
    :type data: AlertEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(alert_email_job, data)


@job_router.post("/contactEmail", dependencies=[Depends(verified)])
def create_contact_email_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    """
    Creates a contact_email_job
    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the contact_email_job
    :type data: ContactEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(contact_email_job, user, data)


@job_router.post("/processFreeText", dependencies=[Depends(verified)])
def create_process_free_text_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    """
    Creates a process_free_text_job
    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the process_free_text_job
    :type data: ProcessFreeTextData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(processfreetext_job, user, data)


@job_router.post("/correlateValue", dependencies=[Depends(verified)])
def create_correlate_value_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    """
    Creates a correlate_value_job
    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the correlate_value_job
    :type data: CorrelateValueData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(correlate_value_job(), data)


@job_router.post("/topCorrelations", dependencies=[Depends(verified)])
def create_top_correlations_job(user: UserData) -> CreateJobResponse:
    """
    Creates a top_correlations_job
    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(top_correlations_job)


@job_router.post("/cleanExcluded", dependencies=[Depends(verified)])
def create_clean_excluded_job(user: UserData) -> CreateJobResponse:
    """
    Creates a clean_excluded_job
    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(clean_excluded_correlations_job)


@job_router.post("/regenerateOccurrences", dependencies=[Depends(verified)])
def create_regenerate_occurrences_job(user: UserData) -> CreateJobResponse:
    """
    Creates a regenerate-occurrences_job
    :param user: user who called the method (not used)
    :type user: UserData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return JobController.create_job(regenerate_occurrences_job)
