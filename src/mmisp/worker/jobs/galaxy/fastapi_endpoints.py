from typing import Optional

from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.galaxy.import_galaxies_job import import_galaxies_job
from mmisp.worker.jobs.galaxy.job_data import CreateGalaxiesImportData

from .queue import queue


@job_router.post("/importGalaxies", dependencies=[Depends(verified)])
async def create_galaxies_import_job(
    user: UserData, data: Optional[CreateGalaxiesImportData] = None
) -> CreateJobResponse:
    """Endpoint to create a job for importing galaxies.

    Args:
        user: User data required for the job.
        data: Optional data containing GitHub repository details for the import. If not provided, defaults are used.

    Returns:
        CreateJobResponse: Response containing the job ID and status.
    """
    data = data or CreateGalaxiesImportData()
    async with queue:
        return await job_controller.create_job(queue, import_galaxies_job, user, data)
