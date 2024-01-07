from typing import List, Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException
from enum import Enum
from pydantic import BaseModel

from kit.job.job import JobStatusEnum
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.worker.enrichment_worker.enrich_attribute_job import EnrichAttributeResult, EnrichAttributeData
from kit.worker.enrichment_worker.enrich_event_job import EnrichEventData, EnrichEventResult


### datentypenklassen

class PushTechniqueEnum(str, Enum):
    full = "full"
    incremental = "incremental"


class PullTechniqueEnum(str, Enum):
    full = "full"
    incremental = "incremental"
    pull_relevant_clusters = "pull_relevant_clusters"


class UserData(BaseModel):
    userId: Annotated[str, "id of the User that started the Job"]


class ProcessFreeTextData(BaseModel):
    data: str

class CorrelationPluginData(BaseModel):
    value: str
    correlationPluginName: str


class PullDate(BaseModel):
    server_id: int
    technique: PullTechniqueEnum


class PushDate(BaseModel):
    server_id: int
    technique: PushTechniqueEnum


class PostsEmailData(BaseModel):
    eventId: int
    postId: int
    title: str
    message: str


class AlertEmailData(BaseModel):
    eventId: int
    oldPublish: str


class ContactEmailData(BaseModel):
    eventId: int
    message: str
    creatorOnly: bool


class CorrelateValueData(BaseModel):
    value: str


### define response types

class JobReturnData(BaseModel):
    status: str
    jobID: int
    jobType: str


class JobStatusResponse(BaseModel):
    status: JobStatusEnum
    message: str


class CreateJobResponse(BaseModel):
    success: bool
    jobId: int


class DeleteJobResponse(BaseModel):
    success: bool


class ProcessFreeTextResponse(BaseModel):
    attributes: List[MispEventAttribute]


class CorrelateValueResponse(BaseModel):
    foundCorrelations: bool
    isExcludedValue: bool
    isOverCorrelatingValue: bool
    pluginName: str | None
    events: list[UUID] | None


class TopCorrelationsResponse(BaseModel):
    topCorrelations: list[(str, int)]


class DatabaseChangedResponse(BaseModel):
    success: bool
    databaseChanged: bool


"""Exceptions"""


class NotExistentJobException(BaseModel):
    message: str = "Job does not exist"


class JobNotFinishedException(BaseModel):
    message: str = "Job is not finished yet, please try again later"


class JobHasNoResultException(BaseModel):
    message: str = "Jobtype has no result that can be returned"


router = APIRouter(prefix="/job")


@router.get("/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: int) -> JobStatusResponse:
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {}


@router.post("/correlationPlugin")
def create_correlationPlugin_job(user: UserData, data: CorrelationPluginData) -> CreateJobResponse:
    return {}


@router.post("/pull")
def create_pull_job(user: UserData, data: PullDate) -> CreateJobResponse:
    return {}


@router.post("/push")
def create_push_job(user: UserData, data: PushDate) -> CreateJobResponse:
    return {}


@router.post("/enrichEvent")
def create_enrichEvent_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/enrichAttribute")
def create_enrichAttribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/postsEmail")
def create_postsEmail_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/alertEmail")
def create_alertEmail_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/contactEmail")
def create_alertEmail_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/processFreeText")
def create_processFreeText_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/correlateValue")
def create_correlateValue_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/topCorrelations")
def create_topCorrelations_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/cleanExcluded")
def create_cleanExcluded_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.post("/regenerateOccurrences")
def create_regenerateOccurrences_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@router.get("/{jobId}/result",
            responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204: {}})
def get_job_result(job_id: int) -> (ProcessFreeTextResponse | EnrichEventResult | EnrichAttributeResult
                                    | CorrelateValueResponse | DatabaseChangedResponse | TopCorrelationsResponse):
    if job_id != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if job_id != 1:
        raise HTTPException(status_code=204, description="The job has no result")
        raise HTTPException(status_code=202, description="The job is not yet finished, please try again later")
    return {}


@router.delete("/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(jobId: int) -> DeleteJobResponse:
    return {}
