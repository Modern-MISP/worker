from celery.result import AsyncResult
from celery.states import state
from celery.worker.control import revoke
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse
from mmisp.worker.jobs.correlation_job.job_data import DatabaseChangedResponse, CorrelateValueResponse, \
    TopCorrelationsResponse
from mmisp.worker.jobs.enrichment_job.job_data import EnrichEventResult, EnrichAttributeResult
from mmisp.worker.jobs.job_type import JobType
from mmisp.worker.jobs.processfreetext_job.job_data import ProcessFreeTextResponse
from typing import TypeAlias

from mmisp.worker.jobs.pull_job.job_data import PullResult
from mmisp.worker.jobs.push_job.job_data import PushResult
from mmisp.worker.controller.celery.celery import celery_app

ResponseData: TypeAlias = (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                           EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                           | PushResult)


class JobController:

    @staticmethod
    def create_job(job: JobType, *args, **kwargs) -> CreateJobResponse:

        try:
            result: AsyncResult = job.value.delay(args, kwargs)

        except OperationalError:
            return CreateJobResponse(id=None, success=False)

        return CreateJobResponse(id=result.id, success=True)

    @staticmethod
    def get_job_status(job_id: str) -> state:
        return celery_app.AsyncResult(job_id).state

    @staticmethod
    def get_job_result(job_id: str) -> ResponseData:
        return celery_app.AsyncResult(job_id).ready

    @staticmethod
    def cancel_job(job_id: str) -> bool:
        revoke(job_id)
