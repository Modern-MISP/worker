from typing import Optional

from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.taxonomy.import_taxonomies_job import import_taxonomies_job
from mmisp.worker.jobs.taxonomy.job_data import CreateTaxonomiesImportData

from .queue import queue


@job_router.post("/importTaxonomies", dependencies=[Depends(verified)])
async def create_taxonomies_import_job(
    user: UserData, data: Optional[CreateTaxonomiesImportData] = None
) -> CreateJobResponse:
    """Endpoint to create a job for importing taxonomies.

    Args:
        user: User data required for the job.
        data: Optional data containing GitHub repository details for the import. If not provided, defaults are used.

    Returns:
        CreateJobResponse: Response containing the job ID and status.
    """
    data = data or CreateTaxonomiesImportData()

    async with queue:
        return await job_controller.create_job(queue, import_taxonomies_job, user, data)
