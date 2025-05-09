"""
Encapsulates the response data for the jobs router.
"""

from enum import StrEnum

from pydantic import BaseModel


class JobStatusEnum(StrEnum):
    """
    Encapsulates the status of a Job
    """

    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "inProgress"
    QUEUED = "queued"
    REVOKED = "revoked"


class JobStatusResponse(BaseModel):
    """
    Encapsulates the response for a jobs status API call
    """

    status: JobStatusEnum
    """The status of the job"""
    message: str
    """A costume message which describes the success of getting the job status"""


class ExceptionResponse(BaseModel):
    """
    Encapsulates the response for a jobs where an exception was raised
    """

    message: str
    """A costume message which describes the error that occurred"""


class CreateJobResponse(BaseModel):
    """
    Encapsulates the response for a create jobs API call
    """

    success: bool
    """The API call was successful or not"""
    job_id: str | None = None
    """The id of the created job"""


class DeleteJobResponse(BaseModel):
    """
    Encapsulates the response for a remove jobs API call
    """

    success: bool
    """The API call was successful or not"""


"""
Encapsulates the response data for the worker router.
"""


class WorkerStatusEnum(StrEnum):
    """
    Represents different statuses of a worker
    """

    IDLE = "idle"
    WORKING = "working"
    DEACTIVATED = "deactivated"


class StartStopWorkerResponse(BaseModel):
    """
    Represents the API response of starting and stopping a worker
    """

    success: bool
    """The API call was successful or not"""
    message: str
    """A costume message which describes the success of starting or stopping the worker"""
    url: str
    """The API url"""


class WorkerStatusResponse(BaseModel):
    """
    Represents the API response of getting the status of a worker
    """

    status: WorkerStatusEnum
    """The status of the worker"""
    jobs_queued: int
    """The number of queued jobs of the worker"""
