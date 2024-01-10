"""
Response Data for the Job Router.
"""
from enum import Enum
from typing import List
from uuid import UUID

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


class CorrelateValueResponse(BaseModel):
    success: bool
    foundCorrelations: bool
    isExcludedValue: bool
    isOverCorrelatingValue: bool
    pluginName: str | None
    events: list[UUID] | None


class TopCorrelationsResponse(BaseModel):
    success: bool
    topCorrelations: list[tuple[str, int]]


class DatabaseChangedResponse(BaseModel):
    success: bool
    databaseChanged: bool
