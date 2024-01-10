from enum import Enum


class WorkerEnum(str, Enum):
    PULL = "pull"
    PUSH = "push"
    CORRELATE = "correlation"
    ENRICHMENT = "enrichment"
    SEND_EMAIL = "sendEmail"
    PROCESS_FREE_TEXT = "processFreeText"


