"""
Response Data for the Job Router.
"""
from enum import Enum
from typing import List

from pydantic import BaseModel

from src.misp_dataclasses.misp_attribute import MispEventAttribute


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


class ProcessFreeTextResponse(BaseModel):
    attributes: List[MispEventAttribute]
