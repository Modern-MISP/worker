from fastapi import Depends
from streaq.task import TaskStatus

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router, translate_job_result
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.sync.pull.job_data import PullData
from mmisp.worker.jobs.sync.pull.pull_job import PullResult, pull_job
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult
from mmisp.worker.jobs.sync.push.push_job import push_job

from .queue import queue


@job_router.post("/pull", dependencies=[Depends(verified)], tags=["sync"])
async def create_pull_job(user: UserData, data: PullData) -> CreateJobResponse:
    return await job_controller.create_job(queue, pull_job, user, data)


@job_router.post("/push", dependencies=[Depends(verified)], tags=["sync"])
async def create_push_job(user: UserData, data: PushData) -> CreateJobResponse:
    return await job_controller.create_job(queue, push_job, user, data)


@job_router.get("/pull/{task_id}", dependencies=[Depends(verified)], tags=["sync"])
async def get_pull_result(task_id: str) -> PullResult:
    return await translate_job_result(queue, task_id)


@job_router.get("/push/{task_id}", dependencies=[Depends(verified)], tags=["sync"])
async def get_push_result(task_id: str) -> PushResult:
    return await translate_job_result(queue, task_id)


@job_router.get("/pull/{task_id}/status", dependencies=[Depends(verified)], tags=["sync"])
async def get_pull_job_status(task_id: str) -> TaskStatus:
    return await job_controller.get_job_status(queue, task_id)


@job_router.get("/push/{task_id}/status", dependencies=[Depends(verified)], tags=["sync"])
async def get_push_job_status(task_id: str) -> TaskStatus:
    return await job_controller.get_job_status(queue, task_id)


@job_router.delete("/pull/{task_id}", dependencies=[Depends(verified)], tags=["sync"])
async def abort_pull_job(task_id: str) -> bool:
    return await job_controller.cancel_job(queue, task_id)


@job_router.delete("/push/{task_id}", dependencies=[Depends(verified)], tags=["sync"])
async def abort_push_job(task_id: str) -> bool:
    return await job_controller.cancel_job(queue, task_id)
