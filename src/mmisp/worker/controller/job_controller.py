from typing import Any

from celery import Task, states
from celery.result import AsyncResult
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse, ExceptionResponse, JobStatusEnum
from mmisp.worker.controller.celery_client import JOB_CREATED_STATE, celery_app
from mmisp.worker.exceptions.job_exceptions import JobNotFinishedException, NotExistentJobException


def get_job_status(job_id: str) -> JobStatusEnum:
    """
    Returns the status of the given job.

    :param job_id: The ID of the job.
    :type job_id: str
    :return: The status of the job.
    :rtype: JobStatusEnum
    :raises NotExistentJobException: If there is no job with the specified ID.
    """
    celery_state: str = celery_app.AsyncResult(job_id).state

    if celery_state == states.PENDING:
        raise NotExistentJobException(job_id=job_id)
    return __convert_celery_task_state(celery_state)


def get_job_result(job_id: str) -> Any:
    """
    Returns the result of the specified job
    :param job_id: is the id of the job
    :type job_id: str
    :return: a special ResponseData depending on the job
    :rtype: ResponseData
    """
    if celery_app.AsyncResult(job_id).state == states.PENDING:
        raise NotExistentJobException

    if not celery_app.AsyncResult(job_id).ready():
        raise JobNotFinishedException

    # celery_app.AsyncResult(job_id).result is annotated as Any | Exception, but it can be only ResponseData or
    # Exception
    result = celery_app.AsyncResult(job_id).result  # type: ignore
    if isinstance(result, Exception):
        return ExceptionResponse(message=str(result))
    return result


def cancel_job(job_id: str) -> bool:
    """
    Revokes a given job.
    :param job_id: The ID of the job
    :type job_id: str
    :return: Whether the revoke action was successful.
    :rtype: bool
    """
    celery_app.control.revoke(job_id)
    return True


def __convert_celery_task_state(job_state: str) -> JobStatusEnum:
    """
    Converts a celery task state to a job status enum.
    :param job_state: The state of the job.
    :type job_state: str
    :return: returns a value of the job status enum
    :rtype: JobStatusEnum
    """
    state_map: dict[str, JobStatusEnum] = {
        states.PENDING: JobStatusEnum.QUEUED,
        JOB_CREATED_STATE: JobStatusEnum.QUEUED,
        states.RETRY: JobStatusEnum.QUEUED,
        states.STARTED: JobStatusEnum.IN_PROGRESS,
        states.SUCCESS: JobStatusEnum.SUCCESS,
        states.FAILURE: JobStatusEnum.FAILED,
        states.REVOKED: JobStatusEnum.REVOKED,
    }

    return state_map[job_state]


def create_job(job: Task, *args, **kwargs) -> CreateJobResponse:
    """
    Enqueues a given celery task.

    :param job: The celery Task to enqueue
    :type job: celery.Task
    :param args: Arguments passed to the job.
    :param kwargs: Arguments passed to the job.
    :return: The job_id of the created job and a success status.
    :rtype: CreateJobResponse
    """
    try:
        result: AsyncResult = job.delay(*args, **kwargs)

    except OperationalError:
        return CreateJobResponse(job_id=None, success=False)

    return CreateJobResponse(job_id=result.id, success=True)
