"""
Encapsulates the response data for the worker router.
"""

from enum import Enum

from pydantic import BaseModel

"""
Represents different statuses of a worker 
"""


class WorkerStatusEnum(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    DEACTIVATED = "deactivated"


"""
Represents the API response of starting and stopping a worker
:att
"""


class StartStopWorkerResponse(BaseModel):
    success: bool
    message: str
    url: str


class WorkerStatusResponse(BaseModel):
    status: WorkerStatusEnum
    jobs_queued: int
