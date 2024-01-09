from enum import Enum

from pydantic import BaseModel


class WorkerEnum(str, Enum):
    pull = "pull"
    push = "push"
    correlate = "correlation"
    enrichment = "enrichment"
    sendEmail = "sendEmail"
    processFreeText = "processFreeText"


class ChangeThresholdData(BaseModel):
    newThreshold: int
