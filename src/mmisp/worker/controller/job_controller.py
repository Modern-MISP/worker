from typing import TypeAlias

from celery import states
from celery.result import AsyncResult
from celery.states import state
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse, JobStatusEnum
from mmisp.worker.controller.celery_app.celery_app import celery_app, JOB_CREATED_STATE
from mmisp.worker.exceptions.job_exceptions import NotExistentJobException, JobNotFinishedException
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse, CorrelateValueResponse, \
    TopCorrelationsResponse
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult, EnrichEventResult
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextResponse
from mmisp.worker.jobs.sync.pull.job_data import PullResult
from mmisp.worker.jobs.sync.push.job_data import PushResult

"""
Represents different responses of jobs
"""
ResponseData: TypeAlias = (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                           EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                           | PushResult)


class JobController:
    """
    Encapsulates the logic of the API for the job router
    """

    @staticmethod
    def create_job(job: celery_app.Task, *args, **kwargs) -> CreateJobResponse:
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
            return CreateJobResponse(id=None, success=False)
             # TODO think if thats right

        return CreateJobResponse(job_id=result.id, success=True)

    @classmethod
    def get_job_status(cls, job_id: str) -> JobStatusEnum:
        """
        Returns the status of the given job.

        :param job_id: The ID of the job.
        :type job_id: str
        :return: The status of the job.
        :rtype: JobStatusEnum
        :raises NotExistentJobException: If there is no job with the specified ID.
        """
        celery_state: state = celery_app.AsyncResult(job_id).state

        if celery_state == states.PENDING:
            raise NotExistentJobException(job_id=job_id) # TODO wtf happens here
        return cls.__convert_celery_task_state(celery_state)

    @staticmethod
    def get_job_result(job_id: str) -> ResponseData:
        """
        TODO check if a job throws an exception https://docs.celeryq.dev/en/2.1-archived/reference/celery.result.html
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

        return celery_app.AsyncResult(job_id).result

    @staticmethod
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

    @staticmethod
    def __convert_celery_task_state(job_state: str) -> JobStatusEnum:
        state_map: dict[str, JobStatusEnum] = {
            states.PENDING: None,
            JOB_CREATED_STATE: JobStatusEnum.QUEUED,
            states.RETRY: JobStatusEnum.QUEUED,
            states.STARTED: JobStatusEnum.IN_PROGRESS,
            states.SUCCESS: JobStatusEnum.SUCCESS,
            states.FAILURE: JobStatusEnum.FAILED,
            states.REVOKED: JobStatusEnum.REVOKED,
        }

        return state_map[job_state]
