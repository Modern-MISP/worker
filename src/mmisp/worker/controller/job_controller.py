from typing import Self
from uuid import UUID

from celery.result import AsyncResult
from celery.states import state
from celery.worker.control import revoke
from kombu.exceptions import OperationalError

from mmisp.worker.api.job_router.response_data import CreateJobResponse
from mmisp.worker.exceptions.singleton_exception import SingletonException
from mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse, CorrelateValueResponse, \
    TopCorrelationsResponse
from mmisp.worker.job.enrichment_job.job_data import EnrichEventResult, EnrichAttributeResult
from mmisp.worker.job.job_type import JobType
from mmisp.worker.job.processfreetext_job.job_data import ProcessFreeTextResponse
from typing import TypeAlias

from mmisp.worker.job.pull_job.job_data import PullResult
from mmisp.worker.job.push_job.job_data import PushResult
from mmisp.worker.controller.celery.celery import celery

ResponseData: TypeAlias = (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                           EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                           | PushResult)


class JobController:
    __instance: Self

    @classmethod
    def get_instance(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = JobController()

        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise SingletonException("Attempted to create a second instance of the 'JobController' class.")

    def create_job(self, job: JobType, *args, **kwargs) -> CreateJobResponse:
        response: CreateJobResponse = CreateJobResponse()

        try:
            result: AsyncResult = job.value.delay(args, kwargs)

        except OperationalError:
            response.id = None
            response.success = False
            return response

        response.id = result.id
        response.success = True

        return response

    def get_job_status(self, job_id: str) -> state:
        return celery.AsyncResult(job_id).state

    def get_job_result(self, job_id: str) -> ResponseData:
        return celery.AsyncResult(job_id).ready

    def cancel_job(self, job_id: str) -> bool:
        revoke(job_id)