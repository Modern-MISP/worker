from enum import Enum

from pydantic import BaseModel


class WorkerEnum(str, Enum):
    PULL = "pull"
    PUSH = "push"
    CORRELATE = "correlation"
    ENRICHMENT = "enrichment"
    SEND_EMAIL = "sendEmail"
    PROCESS_FREE_TEXT = "processFreeText"


class ChangeThresholdData(BaseModel):
    newThreshold: int
