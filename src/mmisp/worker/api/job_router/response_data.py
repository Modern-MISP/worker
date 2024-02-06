"""
Encapsulates the response data for the jobs router.
"""
from enum import Enum
from pydantic import BaseModel


class JobStatusEnum(str, Enum):
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
    job_id: str
    """The id of the created job"""


class DeleteJobResponse(BaseModel):
    """
    Encapsulates the response for a remove jobs API call
    """

    success: bool
    """The API call was successful or not"""
