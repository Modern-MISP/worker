"""
Response Data for the Job Router.
"""
from enum import Enum
from pydantic import BaseModel


class JobStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "inProgress"
    QUEUED = "queued"


class JobStatusResponse(BaseModel):
    status: JobStatusEnum
    message: str


class CreateJobResponse(BaseModel):
    success: bool
    jobId: int


class DeleteJobResponse(BaseModel):
    success: bool



