from typing import TypeAlias

from celery.result import AsyncResult
from celery.states import state
from celery.worker.control import revoke
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse
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

    @staticmethod
    def get_job_status(job_id: str) -> state:
        return celery_app.AsyncResult(job_id).state

    @staticmethod
    def get_job_result(job_id: str) -> ResponseData:
        return celery_app.AsyncResult(job_id).ready

    @staticmethod
    def cancel_job(job_id: str) -> bool:
        revoke(job_id)
