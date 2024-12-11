"""
This module provides the API endpoints for creating various types of jobs to import feeds.
The endpoints are secured with verification to ensure
that only authenticated users can initiate the job.

This module relies on FastAPI's request handling and dependency injection to
perform user verification and job creation.
"""

from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.importFeed.import_feed_job import import_feed_job
from mmisp.worker.jobs.importFeed.job_data import ImportFeedData


@job_router.post("/importFeed", dependencies=[Depends(verified)])
def create_import_feed_job(user: UserData, data: ImportFeedData) -> CreateJobResponse:
    """
    Creates an import_feed_job and triggers its execution.

    This function is responsible for creating and initiating an import_feed_job based on
    the provided user and data. The job will be processed asynchronously, and the result
    will be communicated through the returned response.

    Args:
        user: The user who requested the job creation. This data is used to
            track the request and ensure the correct user context.
        data: Contains the necessary information, such as the feed id,
            required to execute the import_feed_job.

    Returns:
        A response object indicating the success or failure of the
        job creation process. It contains status information relevant
        to the job creation.
    """
    return job_controller.create_job(import_feed_job, user, data)
