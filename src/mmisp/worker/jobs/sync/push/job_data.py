from enum import Enum

from pydantic import BaseModel


class PushTechniqueEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"


class PushData(BaseModel):
    server_id: int
    technique: PushTechniqueEnum


class PushResult(BaseModel):
    success: bool
