from typing import Optional

from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.object_template.import_object_templates_job import import_object_templates_job
from mmisp.worker.jobs.object_template.job_data import CreateObjectTemplatesImportData


@job_router.post("/importObjectTemplates", dependencies=[Depends(verified)])
async def create_taxonomies_import_job(
    user: UserData, data: Optional[CreateObjectTemplatesImportData] = None
) -> CreateJobResponse:
    data = data or CreateObjectTemplatesImportData()
    return job_controller.create_job(import_object_templates_job, user, data)
