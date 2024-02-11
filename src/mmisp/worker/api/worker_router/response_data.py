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
    """The API call was successful or not"""
    message: str
    """A costume message which describes the success of starting or stopping the worker"""
    url: str
    """The API url"""


class WorkerStatusResponse(BaseModel):
    """
    Represents the API response of getting the status of a worker
    """

    status: WorkerStatusEnum
    """The status of the worker"""
    jobs_queued: int
    """The number of queued jobs of the worker"""
