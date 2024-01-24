"""
Encapsulates the response data for the jobs router.
"""
from enum import Enum
from pydantic import BaseModel

"""
Encapsulates the status of a Job
"""


class JobStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "inProgress"
    QUEUED = "queued"


"""
Encapsulates the response for a jobs status API call
"""


class JobStatusResponse(BaseModel):
    status: JobStatusEnum
    message: str


"""
Encapsulates the response for a create jobs API call
"""


class CreateJobResponse(BaseModel):
    success: bool
    jobId: str


"""
Encapsulates the response for a remove jobs API call
"""


class DeleteJobResponse(BaseModel):
    success: bool
