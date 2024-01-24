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
    message: str


class CreateJobResponse(BaseModel):
    """
    Encapsulates the response for a create jobs API call
    """

    success: bool
    jobId: str


class DeleteJobResponse(BaseModel):
    """
    Encapsulates the response for a remove jobs API call
    """

    success: bool
