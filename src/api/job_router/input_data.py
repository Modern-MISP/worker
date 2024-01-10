"""
Input data classes for the job router.
"""
from enum import Enum
from typing import Annotated

from pydantic import BaseModel


class UserData(BaseModel):
    userId: Annotated[str, "id of the User that started the Job"]


class PushTechniqueEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"


class PullTechniqueEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    PULL_RELEVANT_CLUSTERS = "pull_relevant_clusters"


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


class CorrelateValueData(BaseModel):
    value: str
