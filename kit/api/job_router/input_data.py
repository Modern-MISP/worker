"""
Input data classes for the job router.
"""
from enum import Enum
from typing import Annotated

from pydantic import BaseModel


class UserData(BaseModel):
    userId: Annotated[str, "id of the User that started the Job"]


class PushTechniqueEnum(str, Enum):
    full = "full"
    incremental = "incremental"


class PullTechniqueEnum(str, Enum):
    full = "full"
    incremental = "incremental"
    pull_relevant_clusters = "pull_relevant_clusters"


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
