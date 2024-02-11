from enum import Enum

from pydantic import BaseModel


class PushTechniqueEnum(str, Enum):
    """
    Enum for the different push techniques.
    """
    FULL = "full"
    INCREMENTAL = "incremental"


class PushData(BaseModel):
    """
    Represents the input data of the PushJob.
    """
    server_id: int
    technique: PushTechniqueEnum


class PushResult(BaseModel):
    """
    Represents the result of a PushJob.
    """
    success: bool
