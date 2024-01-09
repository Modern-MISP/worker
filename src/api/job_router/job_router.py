from fastapi import APIRouter, HTTPException

from src.api.job_router.input_data import UserData, ProcessFreeTextData, CorrelationPluginData, PullDate, PushDate, \
    PostsEmailData, AlertEmailData, ContactEmailData, CorrelateValueData
from src.api.job_router.job_exceptions import NotExistentJobException, JobNotFinishedException
from src.api.job_router.response_data import JobReturnData, JobStatusResponse, CreateJobResponse, DeleteJobResponse, \
    ProcessFreeTextResponse, CorrelateValueResponse, TopCorrelationsResponse, DatabaseChangedResponse
from src.worker.enrichment_job.enrich_attribute_job import EnrichAttributeResult, EnrichAttributeData
from src.worker.enrichment_job.enrich_event_job import EnrichEventData, EnrichEventResult


job_router = APIRouter(prefix="/job")


@job_router.get("/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: int) -> JobStatusResponse:
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {}


@job_router.post("/correlationPlugin")
def create_correlationPlugin_job(user: UserData, data: CorrelationPluginData) -> CreateJobResponse:
    return {}


@job_router.post("/pull")
def create_pull_job(user: UserData, data: PullDate) -> CreateJobResponse:
    return {}


@job_router.post("/push")
def create_push_job(user: UserData, data: PushDate) -> CreateJobResponse:
    return {}


@job_router.post("/enrichEvent")
def create_enrichEvent_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/enrichAttribute")
def create_enrichAttribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/postsEmail")
def create_postsEmail_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/alertEmail")
def create_alertEmail_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/contactEmail")
def create_alertEmail_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/processFreeText")
def create_processFreeText_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/correlateValue")
def create_correlateValue_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/topCorrelations")
def create_topCorrelations_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/cleanExcluded")
def create_cleanExcluded_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.post("/regenerateOccurrences")
def create_regenerateOccurrences_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@job_router.get("/{jobId}/result",
                responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204: {}})
def get_job_result(job_id: int) -> (ProcessFreeTextResponse | EnrichEventResult | EnrichAttributeResult
                                    | CorrelateValueResponse | DatabaseChangedResponse | TopCorrelationsResponse):
    if job_id != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if job_id != 1:
        raise HTTPException(status_code=204, description="The job has no result")
        raise HTTPException(status_code=202, description="The job is not yet finished, please try again later")
    return {}


@job_router.delete("/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(jobId: int) -> DeleteJobResponse:
    return {}