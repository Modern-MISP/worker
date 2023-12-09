from typing import List, Annotated
from fastapi import FastAPI, HTTPException
from enum import Enum
from pydantic import BaseModel


class WorkerEnum(str, Enum):
    pull = "pull"
    push = "push"
    correlate = "correlation"
    enrichment = "enrichment"
    sendEmail = "sendEmail"
    processFreeText = "processFreeText"


class WorkerStatusEnum(str, Enum):
    idle = "idle"
    working = "working"
    deactivated = "deactivated"

class JobStatusEnum(str, Enum):
    success = "success"
    failed = "failed"
    inProgress = "inProgress"
    queued = "queued"

class PullTechniqueEnum(str, Enum):
    full = "full"
    incremental = "incremental"
    pull_relevant_clusters = "pull_relevant_clusters"

class PushTechniqueEnum(str, Enum):
    full = "full"
    incremental = "incremental"

class PluginType(str, Enum):
    correlation = "correlation"
    enrichment = "enrichment"


class EnrichmentPluginType(str, Enum):
    expansion = "expansion"
    hover = "hover"


class CorrelationPluginType(str, Enum):
    default = "default"


### datentypenklassem

class UserData(BaseModel):
    userId: Annotated[str, "id of the User that started the Job"]


class EventAttribute(BaseModel):
    eventId: int
    objectId: int
    objectRelation: str
    category: str
    type: str
    value: str
    toIds: bool
    timestamp: int
    distribution: int
    sharingGroupId: int
    comment: str
    deleted: bool
    disableCorrelation: bool
    firstSeen: int
    lastSeen: int


class EventTag(BaseModel):
    name: str
    colour: str
    exportable: bool
    orgId: int
    userId: str
    hideTag: bool
    numericalValue: int
    isGalaxy: bool
    isCustomGalaxy: bool
    inherited: int


class Plugin(BaseModel):
    name: str
    pluginType: PluginType
    description: str
    author: str
    version: float


class PluginIO(BaseModel):
    input: List[str]  # Attributstypen die vom Plugin akzeptiert werden.
    output: List[str]  # Attributstypen die vom Plugin erstellt/zurückgegeben werden können.


class EnrichmentPlugin(BaseModel):
    plugin: Plugin
    enrichment: dict = {
        "type": EnrichmentPluginType,
        "mispAttributes": PluginIO
    }

class CorrelationPlugin(BaseModel):
    plugin: Plugin
    correlation: dict = {
        "type": CorrelationPluginType,
        "mispAttributes": PluginIO
    }


class GetEnrichmentPluginsResponse(BaseModel):
    plugins: List[EnrichmentPlugin]


class GetCorrelationPluginsResponse(BaseModel):
    plugins: List[CorrelationPlugin]

class ProcessFreeTextData(BaseModel):
    data: str


class EnrichEventData(BaseModel):
    eventId: int
    enrichmentPlugins: List[str]


class EnrichAttributeData(BaseModel):
    attributeId: int
    enrichmentPlugins: List[str]


class CorrelationPluginData(BaseModel):
    value: str
    correlationPlugins: List[str]


class JobReturnData(BaseModel):
    status: str
    jobID: int
    jobType: str


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


class ChangeThresholdData(BaseModel):
    newThreshold: int

class PullDate(BaseModel):
    server_id: int
    technique: PullTechniqueEnum

class PushDate(BaseModel):
    server_id: int
    technique: PushTechniqueEnum


### define response types

class StartStopWorkerResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str


class WorkerStatusResponse(BaseModel):
    status: WorkerStatusEnum
    jobsQueued: int


class JobStatusResponse(BaseModel):
    status: JobStatusEnum
    message: str


class CreateJobResponse(BaseModel):
    success: bool
    jobId: int

class DeleteJobResponse(BaseModel):
    success: bool



class ProcessFreeTextResponse(BaseModel):
    attributes: List[EventAttribute]


class EnrichmentAttributeResponse(BaseModel):
    eventAttribute: EventAttribute
    tags: List[int]
    newTags: List[EventTag]


class EnrichAttributeResponse(BaseModel):
    attributes: List[EnrichmentAttributeResponse]
    eventTags: List[int]
    newEventTags: List[EventTag]


class CorrelateValueResponse(BaseModel):
    foundCorrelations: bool
    events: List[EventAttribute] | None


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


app = FastAPI()


@app.post("/worker/{name}/enable")
def enable_a_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@app.post("/worker/{name}/disable")
def disable_a_worker(name: WorkerEnum) -> StartStopWorkerResponse:
    return StartStopWorkerResponse()


@app.get("/worker/{name}/status")
def get_worker_status(name: WorkerEnum) -> WorkerStatusResponse:
    return {"status": "success"}


@app.get("/worker/enrichment/plugins")
def get_enrichmentPlugins() -> GetEnrichmentPluginsResponse:
    return {}


@app.get("/worker/correlation/plugins")
def get_correlationPlugins() -> GetCorrelationPluginsResponse:
    return {}


@app.put("/worker/correlation/changeThreshold")
def put_newThreshold(data: ChangeThresholdData) -> StartStopWorkerResponse:
    return_value = JobReturnData()
    return {"result": return_value}


@app.get("/job/{job_id}/status", responses={404: {"model": NotExistentJobException}})
def get_job_status(job_id: int) -> JobStatusResponse:
    if job_id == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {}

@app.post("/job/correlationPlugin")
def create_correlationPlugin_job(user: UserData, data: CorrelationPluginData) -> CreateJobResponse:
    return {}

@app.post("/job/pull")
def create_pull_job(user: UserData, data: PullDate) -> CreateJobResponse:
    return {}


@app.post("/job/push")
def create_push_job(user: UserData, data: PushDate) -> CreateJobResponse:
    return {}


@app.post("/job/enrichEvent")
def create_enrichEvent_job(user: UserData, data: EnrichEventData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/enrichAttribute")
def create_enrichAttribute_job(user: UserData, data: EnrichAttributeData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/postsEmail")
def create_postsEmail_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/alertEmail")
def create_alertEmail_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/contactEmail")
def create_alertEmail_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/processFreeText")
def create_processFreeText_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/correlateValue")
def create_correlateValue_job(user: UserData, data: CorrelateValueData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/topCorrelations")
def create_topCorrelations_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/cleanExcluded")
def create_cleanExcluded_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.post("/job/generateOccurences")
def create_generateOccurences_job(user: UserData) -> CreateJobResponse:
    return_value = JobReturnData()
    return {}


@app.get("/job/{jobId}/result", responses={404: {"model": NotExistentJobException}, 202: {"model": JobNotFinishedException}, 204:{}})
def get_job_result(jobId: int) -> ProcessFreeTextResponse | EnrichAttributeResponse | CorrelateValueResponse | DatabaseChangedResponse:
    if jobId != 0:
        raise HTTPException(status_code=404, description="Job does not exist")
    if jobId != 1:
        raise HTTPException(status_code=204, description =  "The job has no result")
        raise HTTPException(status_code=202, description=   "The job is not yet finished, please try again later")
    return{}

@app.delete("/job/{jobId}/cancel", responses={404: {"model": NotExistentJobException}})
def remove_job(jobId: int) -> DeleteJobResponse:
    return{}
