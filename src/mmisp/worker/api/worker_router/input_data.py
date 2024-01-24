from enum import Enum


class WorkerEnum(str, Enum):
    """
    Represents the implemented workers
    """

    PULL = "pull"
    PUSH = "push"
    CORRELATE = "correlation"
    ENRICHMENT = "enrichment"
    SEND_EMAIL = "sendEmail"
    PROCESS_FREE_TEXT = "processFreeText"
