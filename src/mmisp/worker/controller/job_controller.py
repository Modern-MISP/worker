from typing import TypeAlias

from celery import states
from celery.result import AsyncResult
from celery.states import state
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse, JobStatusEnum
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse, CorrelateValueResponse, \
    TopCorrelationsResponse
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult, EnrichEventResult
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextResponse
from mmisp.worker.jobs.pull.job_data import PullResult
from mmisp.worker.jobs.push.job_data import PushResult

ResponseData: TypeAlias = (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                           EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                           | PushResult)


class JobController:

    @staticmethod
    def create_job(job: celery_app.Task, *args, **kwargs) -> CreateJobResponse:
        try:
            result: AsyncResult = job.delay(args, kwargs)

        except OperationalError:
            return CreateJobResponse(id=None, success=False)

        return CreateJobResponse(id=result.id, success=True)

    @classmethod
    def get_job_status(cls, job_id: str) -> JobStatusEnum:
        celery_state: state = celery_app.AsyncResult(job_id).state
        return cls.convert_celery_task_state(job_id)

    @staticmethod
    def get_job_result(job_id: str) -> ResponseData:
        return celery_app.AsyncResult(job_id).ready

    @staticmethod
    def cancel_job(job_id: str) -> bool:
        # TODO: Return value
        # TODO: Check if it does work correctly.
        celery_app.control.revoke(job_id)
        return True

    @staticmethod
    def convert_celery_task_state(job_state: str) -> JobStatusEnum:
        state_map: dict[str, JobStatusEnum] = {
            states.PENDING: JobStatusEnum.QUEUED,
            states.RETRY: JobStatusEnum.QUEUED,
            states.STARTED: JobStatusEnum.IN_PROGRESS,
            states.SUCCESS: JobStatusEnum.SUCCESS,
            states.FAILURE: JobStatusEnum.FAILED,
            states.REVOKED: JobStatusEnum.REVOKED,
        }

        return state_map[job_state]
