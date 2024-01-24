from typing import Self

from celery.result import AsyncResult
from celery.states import state
from celery.worker.control import revoke
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.correlation_job.job_data import DatabaseChangedResponse, CorrelateValueResponse, \
    TopCorrelationsResponse
from mmisp.worker.jobs.enrichment.job_data import EnrichEventResult, EnrichAttributeResult
from mmisp.worker.jobs.job_type import JobType
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextResponse
from typing import TypeAlias

from mmisp.worker.jobs.pull.job_data import PullResult
from mmisp.worker.jobs.push.job_data import PushResult

ResponseData: TypeAlias = (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                           EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                           | PushResult)


class JobController:

    @classmethod
    def create_job(job: JobType, *args, **kwargs) -> CreateJobResponse:

        try:
            result: AsyncResult = job.value.delay(args, kwargs)

        except OperationalError:
            return CreateJobResponse(id=None, success=False)

        return CreateJobResponse(id=result.id, success=True)

    @classmethod
    def get_job_status(job_id: str) -> state:
        return celery_app.AsyncResult(job_id).state

    @classmethod
    def get_job_result(job_id: str) -> ResponseData:
        return celery_app.AsyncResult(job_id).ready

    @classmethod
    def cancel_job(job_id: str) -> bool:
        revoke(job_id)
