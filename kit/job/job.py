from enum import Enum


class JobStatusEnum(str, Enum):
    success = "success"
    failed = "failed"
    inProgress = "inProgress"
    queued = "queued"


class JobTypeEnum(str, Enum):
    pass