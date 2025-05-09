"""
Encapsulates API calls for jobs
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from streaq import Worker

from mmisp.worker.controller import job_controller
from mmisp.worker.exceptions.job_exceptions import (
    JobHasNoResultException,
    JobNotFinishedException,
    NotExistentJobException,
)

job_router: APIRouter = APIRouter(prefix="/job")


async def translate_job_result(queue: Worker, task_id: str) -> Any:
    try:
        return await job_controller.get_job_result(queue, task_id)
    except JobNotFinishedException as exception:
        raise HTTPException(status_code=409, detail=str(exception))
    except NotExistentJobException as exception:
        raise HTTPException(status_code=404, detail=str(exception))
    except JobHasNoResultException as exception:
        raise HTTPException(status_code=204, detail=str(exception))
