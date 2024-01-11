from fastapi import APIRouter, HTTPException

from src.api.job_router.input_data import UserData, ProcessFreeTextData, PullDate, PushDate
from src.api.job_router.job_exceptions import NotExistentJobException, JobNotFinishedException
from src.api.job_router.response_data import JobStatusResponse, CreateJobResponse, DeleteJobResponse
from src.job.correlation_job.job_data import CorrelateValueResponse, TopCorrelationsResponse, \
    DatabaseChangedResponse, CorrelationPluginJobData, CorrelateValueData
from src.job.email_job.alert_email_job import AlertEmailData
from src.job.email_job.contact_email_job import ContactEmailData
from src.job.email_job.posts_email_job import PostsEmailData
from src.job.enrichment_job.job_data import EnrichAttributeData, EnrichAttributeResult, EnrichEventData, \
    EnrichEventResult

from celery.states import state

from src.job.processfreetext_job.job_data import ProcessFreeTextResponse
from src.job.pull_job.job_data import PullResult
from src.job.push_job.job_data import PushResult

job_router = APIRouter(prefix="/job")


@job_router.get("/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: int) -> JobStatusResponse:
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {}


@job_router.post("/correlationPlugin")
def create_correlationPlugin_job(user: UserData, data: CorrelationPluginJobData) -> CreateJobResponse:
    return {}


@job_router.post("/pull")
def create_pull_job(user: UserData, data: PullDate) -> CreateJobResponse:
    return {}


@job_router.post("/push")
def create_push_job(user: UserData, data: PushDate) -> CreateJobResponse:
    return {}


@job_router.post("/enrichEvent")
def create_enrichEvent_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    return {}


@job_router.post("/enrichAttribute")
def create_enrichAttribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    return {}


@job_router.post("/postsEmail")
def create_postsEmail_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    return {}


@job_router.post("/alertEmail")
def create_alertEmail_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    return {}


@job_router.post("/contactEmail")
def create_alertEmail_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    return {}


@job_router.post("/processFreeText")
def create_processFreeText_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return {}


@job_router.post("/correlateValue")
def create_correlateValue_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    return {}


@job_router.post("/topCorrelations")
def create_topCorrelations_job(user: UserData) -> CreateJobResponse:
    return {}


@job_router.post("/cleanExcluded")
def create_cleanExcluded_job(user: UserData) -> CreateJobResponse:
    return {}


@job_router.post("/regenerateOccurrences")
def create_regenerateOccurrences_job(user: UserData) -> CreateJobResponse:
    return {}


@job_router.get("/{jobId}/result",
                responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204: {}})
def get_job_result(job_id: int) -> (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                                    EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                                    | PushResult):
    if job_id != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if job_id != 1:
        raise HTTPException(status_code=204, description="The job has no result")
        raise HTTPException(status_code=202, description="The job is not yet finished, please try again later")
    return {}


@job_router.delete("/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(jobId: int) -> DeleteJobResponse:
    return {}
