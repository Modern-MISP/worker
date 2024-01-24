"""
Encapsulates the response data for the worker router.
"""

from enum import Enum

from pydantic import BaseModel


class WorkerStatusEnum(str, Enum):
    """
    Represents different statuses of a worker
    """

    IDLE = "idle"
    WORKING = "working"
    DEACTIVATED = "deactivated"


class StartStopWorkerResponse(BaseModel):
    """
    Represents the API response of starting and stopping a worker
    """

    success: bool
    message: str
    url: str


class WorkerStatusResponse(BaseModel):
    status: WorkerStatusEnum
    jobs_queued: int
