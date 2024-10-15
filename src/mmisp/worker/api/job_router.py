"""
Encapsulates API calls for jobs
"""

import typing

from fastapi import APIRouter, Depends, HTTPException

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.response_schemas import (
    DeleteJobResponse,
    ExceptionResponse,
    JobStatusEnum,
    JobStatusResponse,
)
from mmisp.worker.controller import job_controller
from mmisp.worker.exceptions.job_exceptions import (
    JobHasNoResultException,
    JobNotFinishedException,
    NotExistentJobException,
)

job_router: APIRouter = APIRouter(prefix="/job")

"""
Every method in this file is a route for the job_router
every endpoint is prefixed with /job and requires the user to be verified
"""


@job_router.get("/{job_id}/status", responses={404: {"model": ExceptionResponse}}, dependencies=[Depends(verified)])
def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Returns the status of the job with the given id

    :param job_id: the id of the job to get the status from
    :type job_id: str
    :return: the status of the job
    :rtype: JobStatusResponse
    """

    try:
        status: JobStatusEnum = job_controller.get_job_status(job_id)
    except NotExistentJobException as exception:
        raise HTTPException(status_code=404, detail=str(exception))

    match status:
        case JobStatusEnum.QUEUED:
            return JobStatusResponse(status=status, message="Job is currently enqueued")
        case JobStatusEnum.FAILED:
            return JobStatusResponse(status=status, message="Job failed during execution")
        case JobStatusEnum.REVOKED:
            return JobStatusResponse(status=status, message="The job was canceled before it could be processed")
        case JobStatusEnum.SUCCESS:
            return JobStatusResponse(status=status, message="Job is finished")
        case JobStatusEnum.IN_PROGRESS:
            return JobStatusResponse(status=status, message="Job is currently being executed")
        case _:
            raise RuntimeError(
                "The Job with id {id} was in an unexpected state: {state}".format(id=job_id, state=status)
            )


@job_router.get(
    "/{job_id}/result",
    responses={404: {"model": ExceptionResponse}, 202: {"model": ExceptionResponse}, 409: {"model": ExceptionResponse}},
    dependencies=[Depends(verified)],
)
def get_job_result(job_id: str) -> typing.Any:
    """
    Returns the result of the job with the given id
    when the Job is not finished, a 409 status code is returned
    when the Job has no result, a 204 status code is returned
    when the Job does not exist, a 404 status code is returned

    :param job_id: the id of the job to get the result from
    :type job_id: str
    :return: returns the result of the job
    :rtype: job_controller.ResponseData
    """
    try:
        return job_controller.get_job_result(job_id)
    except JobNotFinishedException as exception:
        raise HTTPException(status_code=409, detail=str(exception))
    except NotExistentJobException as exception:
        raise HTTPException(status_code=404, detail=str(exception))
    except JobHasNoResultException as exception:
        raise HTTPException(status_code=204, detail=str(exception))


@job_router.delete("/{job_id}/cancel", responses={404: {"model": ExceptionResponse}}, dependencies=[Depends(verified)])
def remove_job(job_id: str) -> DeleteJobResponse:
    """
    Removes the given job

    :param job_id: is the id of the job to remove
    :type job_id: str
    :return: the response to indicate if the job was successfully deleted
    :rtype: DeleteJobResponse
    """
    result = job_controller.cancel_job(job_id)
    return DeleteJobResponse(success=result)
