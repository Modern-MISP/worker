from typing import Any

from streaq import Worker
from streaq.task import RegisteredTask, TaskStatus

from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.exceptions.job_exceptions import JobNotFinishedException


async def get_job_status(queue: Worker, job_id: str) -> TaskStatus:
    """
    Returns the status of the given job.

    Args:
      job_id: The ID of the job.

    Returns:
      The status of the job.
    """
    async with queue:
        return await queue.status_by_id(job_id)


async def get_job_result(queue: Worker, job_id: str) -> Any:
    """
    Returns the result of the specified job

    Args:
      job_id: is the id of the job

    Returns:
      The Task result, i.e. the return of job executed
    """
    async with queue:
        job_status = await queue.status_by_id(job_id)

        if job_status != TaskStatus.DONE:
            raise JobNotFinishedException

        job_result = await queue.result_by_id(job_id)
        return job_result.result


async def cancel_job(queue: Worker, job_id: str) -> bool:
    """
    Revokes a given job.

    Args:
      job_id: The ID of the job

    Returns:
      Whether the revoke action was successful.
    """

    async with queue:
        return await queue.abort_by_id(job_id)


async def create_job(queue: Worker, function: RegisteredTask, *args, **kwargs) -> CreateJobResponse:
    """
    Enqueues a given task.

    Args:
        queue: The Queue to enqueue the task in
        function: The function to enqueue
        args: Arguments passed to the job.
        kwargs: Arguments passed to the job.

    Returns:
        The job_id of the created job and a success status.
    """
    async with queue:
        task = await function.enqueue(*args, **kwargs)
        return CreateJobResponse(job_id=task.id, success=True)
