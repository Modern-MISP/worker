from fastapi import APIRouter, HTTPException
from celery.states import state

from src.mmisp.worker.api.job_router.input_data import UserData
from src.mmisp.worker.api.job_router.response_data import JobStatusResponse, CreateJobResponse, DeleteJobResponse
from src.mmisp.worker.controller.job_controller import ResponseData, JobController
from src.mmisp.worker.exceptions.job_exceptions import NotExistentJobException, JobNotFinishedException
from src.mmisp.worker.job.correlation_job.job_data import CorrelationPluginJobData, CorrelateValueData
from src.mmisp.worker.job.email_job.alert_email_job import AlertEmailData
from src.mmisp.worker.job.email_job.contact_email_job import ContactEmailData
from src.mmisp.worker.job.email_job.posts_email_job import PostsEmailData
from src.mmisp.worker.job.enrichment_job.job_data import EnrichAttributeData, EnrichEventData
from src.mmisp.worker.job.job import JobType
from src.mmisp.worker.job.processfreetext_job.job_data import ProcessFreeTextData
from src.mmisp.worker.job.pull_job.job_data import PullDate
from src.mmisp.worker.job.push_job.job_data import PushDate

job_router = APIRouter(prefix="/job")


@job_router.get("/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: str) -> JobStatusResponse:
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    status: state = JobController.get_instance().get_job_status(job_id)

    # TODO: Initialize response
    response = JobStatusResponse()

    return response



@job_router.post("/correlationPlugin")
def create_correlation_plugin_job(user: UserData, data: CorrelationPluginJobData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.CORRELATION_PLUGIN_JOB, data)

@job_router.post("/pull")
def create_pull_job(user: UserData, data: PullDate) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.PULL_JOB, user, data)


@job_router.post("/push")
def create_push_job(user: UserData, data: PushDate) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.PUSH_JOB, user, data)


@job_router.post("/enrichEvent")
def create_enrich_event_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.ENRICH_EVENT_JOB, data)


@job_router.post("/enrichAttribute")
def create_enrich_attribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.ENRICH_ATTRIBUTE_JOB, data)


@job_router.post("/postsEmail")
def create_posts_email_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.POSTS_EMAIL_JOB, data)


@job_router.post("/alertEmail")
def create_alert_email_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.ALERT_EMAIL_JOB, data)


@job_router.post("/contactEmail")
def create_contact_email_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.CONTACT_EMAIL_JOB, user, data)


@job_router.post("/processFreeText")
def create_processfreetext_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.PROCESS_FREE_TEXT_JOB, user, data)


@job_router.post("/correlateValue")
def create_correlate_value_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.CORRELATE_VALUE_JOB, data)


@job_router.post("/topCorrelations")
def create_top_correlations_job(user: UserData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.TOP_CORRELATIONS_JOB)


@job_router.post("/cleanExcluded")
def create_clean_excluded_job(user: UserData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.CLEAN_EXCLUDED_CORRELATIONS_JOB)


@job_router.post("/regenerateOccurrences")
def create_regenerate_occurrences_job(user: UserData) -> CreateJobResponse:
    return JobController.get_instance().create_job(JobType.REGENERATE_OCCURRENCES_JOB)


@job_router.get("/{jobId}/result",
                responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204: {}})
def get_job_result(job_id: str) -> ResponseData:
    if job_id != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if job_id != 1:
        raise HTTPException(status_code=204, description="The job has no result")
        raise HTTPException(status_code=202, description="The job is not yet finished, please try again later")
    return JobController.get_instance().get_job_result(job_id)


@job_router.delete("/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(job_id: str) -> DeleteJobResponse:
    JobController.get_instance().cancel_job(job_id)
    return {}
