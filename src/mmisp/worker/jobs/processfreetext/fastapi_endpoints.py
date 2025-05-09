from fastapi import Depends
from streaq.task import TaskStatus

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router, translate_job_result
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.jobs.processfreetext.processfreetext_job import processfreetext_job

from .queue import queue


@job_router.post("/processFreeText", dependencies=[Depends(verified)], tags=["processfreetext"])
async def create_process_free_text_job(user: UserData, data: ProcessFreeTextData) -> CreateJobResponse:
    return await job_controller.create_job(queue, processfreetext_job, user, data)


@job_router.get("/processFreeText/{task_id}", dependencies=[Depends(verified)], tags=["processfreetext"])
async def get_free_text_job_result(task_id: str) -> ProcessFreeTextResponse:
    return await translate_job_result(queue, task_id)


@job_router.get("/processFreeText/{task_id}/status", dependencies=[Depends(verified)], tags=["processfreetext"])
async def get_free_text_job_status(task_id: str) -> TaskStatus:
    return await job_controller.get_job_status(queue, task_id)


@job_router.delete("/processFreeText/{task_id}", dependencies=[Depends(verified)], tags=["processfreetext"])
async def abort_free_text_job(task_id: str) -> bool:
    return await job_controller.cancel_job(queue, task_id)
