from typing import Optional

from fastapi import Depends
from streaq import TaskStatus

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.object_template.import_object_templates_job import import_object_templates_job
from mmisp.worker.jobs.object_template.job_data import CreateObjectTemplatesImportData, ImportObjectTemplatesResult

from .queue import queue


@job_router.post("/importObjectTemplates", dependencies=[Depends(verified)], tags=["objecttemplate"])
async def create_taxonomies_import_job(
    user: UserData, data: Optional[CreateObjectTemplatesImportData] = None
) -> CreateJobResponse:
    data = data or CreateObjectTemplatesImportData()
    return await job_controller.create_job(queue, import_object_templates_job, user, data)


@job_router.get("/importObjectTemplates/{task_id}", dependencies=[Depends(verified)], tags=["objecttemplate"])
async def get_free_text_job_result(task_id: str) -> ImportObjectTemplatesResult:
    return await job_controller.get_job_result(queue, task_id)


@job_router.get("/importObjectTemplates/{task_id}/status", dependencies=[Depends(verified)], tags=["objecttemplate"])
async def get_free_text_job_status(task_id: str) -> TaskStatus:
    return await job_controller.get_job_status(queue, task_id)


@job_router.delete("/importObjectTemplates/{task_id}", dependencies=[Depends(verified)], tags=["objecttemplate"])
async def abort_free_text_job(task_id: str) -> bool:
    return await job_controller.cancel_job(queue, task_id)
