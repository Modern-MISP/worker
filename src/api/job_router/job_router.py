from fastapi import APIRouter, HTTPException

from src.api.job_router.input_data import UserData
from src.exceptions.job_exceptions import NotExistentJobException, JobNotFinishedException
from src.api.job_router.response_data import JobStatusResponse, CreateJobResponse, DeleteJobResponse
from src.job.correlation_job.job_data import  CorrelationPluginJobData, CorrelateValueData
from src.job.email_job.alert_email_job import AlertEmailData
from src.job.email_job.contact_email_job import ContactEmailData
from src.job.email_job.posts_email_job import PostsEmailData
from src.job.enrichment_job.job_data import EnrichAttributeData, EnrichEventData

from src.job.processfreetext_job.processfreetext_job import ProcessFreeTextData
from src.job.pull_job.job_data import PullDate
from src.job.push_job.job_data import PushDate
from src.controller.job_control import ResponseData

job_router = APIRouter(prefix="/job")


@job_router.get("/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: int) -> JobStatusResponse:
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {}


@job_router.post("/correlationPlugin")
def create_correlation_plugin_job(user: UserData, data: CorrelationPluginJobData) -> CreateJobResponse:
    return {}


@job_router.post("/pull")
def create_pull_job(user: UserData, data: PullDate) -> CreateJobResponse:
    return {}


@job_router.post("/push")
def create_push_job(user: UserData, data: PushDate) -> CreateJobResponse:
    return {}


@job_router.post("/enrichEvent")
def create_enrich_event_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    return {}


@job_router.post("/enrichAttribute")
def create_enrich_attribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    return {}


@job_router.post("/postsEmail")
def create_posts_email_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    return {}


@job_router.post("/alertEmail")
def create_alert_email_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    return {}


@job_router.post("/contactEmail")
def create_contact_email_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    return {}


@job_router.post("/processFreeText")
def create_process_free_text_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return {}


@job_router.post("/correlateValue")
def create_correlate_value_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    return {}


@job_router.post("/topCorrelations")
def create_top_correlations_job(user: UserData) -> CreateJobResponse:
    return {}


@job_router.post("/cleanExcluded")
def create_clean_excluded_job(user: UserData) -> CreateJobResponse:
    return {}


@job_router.post("/regenerateOccurrences")
def create_regenerate_occurrences_job(user: UserData) -> CreateJobResponse:
    return {}


@job_router.get("/{jobId}/result",
                responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204: {}})
def get_job_result(job_id: int) -> ResponseData:
    if job_id != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if job_id != 1:
        raise HTTPException(status_code=204, description="The job has no result")
        raise HTTPException(status_code=202, description="The job is not yet finished, please try again later")
    return None


@job_router.delete("/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(job_id: int) -> DeleteJobResponse:
    cancel_job(job_id)
    return {}
