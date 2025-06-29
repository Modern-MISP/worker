from typing import Optional

from fastapi import Depends
from streaq.task import TaskStatus

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router, translate_job_result
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.galaxy.import_galaxies_job import import_galaxies_job
from mmisp.worker.jobs.galaxy.job_data import CreateGalaxiesImportData, ImportGalaxiesResult

from .queue import queue


@job_router.post("/importGalaxies", dependencies=[Depends(verified)], tags=["importGalaxies"])
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


@job_router.get("/importGalaxies/{task_id}", dependencies=[Depends(verified)], tags=["importGalaxies"])
async def get_galaxy_job_result(task_id: str) -> ImportGalaxiesResult:
    return await translate_job_result(queue, task_id)


@job_router.get("/importGalaxies/{task_id}/status", dependencies=[Depends(verified)], tags=["importGalaxies"])
async def get_galaxy_job_status(task_id: str) -> TaskStatus:
    return await job_controller.get_job_status(queue, task_id)


@job_router.delete("/importGalaxies/{task_id}", dependencies=[Depends(verified)], tags=["importGalaxies"])
async def abort_galaxy_job(task_id: str) -> bool:
    return await job_controller.cancel_job(queue, task_id)
