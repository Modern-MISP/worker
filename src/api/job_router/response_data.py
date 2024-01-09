"""
Response Data for the Job Router.
"""
from typing import List
from uuid import UUID

from pydantic import BaseModel

from celery.states import state
from src.misp_dataclasses.misp_attribute import MispEventAttribute


class JobReturnData(BaseModel):
    status: str
    jobID: int
    jobType: str


class JobStatusResponse(BaseModel):
    status: state
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
    topCorrelations: list[tuple[str, int]]


class DatabaseChangedResponse(BaseModel):
    success: bool
    databaseChanged: bool
