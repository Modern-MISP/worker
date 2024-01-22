from typing import Self

from celery.states import state
from celery.worker.control import revoke

from src.mmisp.worker.exceptions.singleton_exception import SingletonException
from src.mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse, CorrelateValueResponse, \
    TopCorrelationsResponse
from src.mmisp.worker.job.enrichment_job.job_data import EnrichEventResult, EnrichAttributeResult
from src.mmisp.worker.job.processfreetext_job.job_data import ProcessFreeTextResponse
from typing import TypeAlias

from src.mmisp.worker.job.pull_job.job_data import PullResult
from src.mmisp.worker.job.push_job.job_data import PushResult
from src.mmisp.worker.controller.celery.celery import celery

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

    def get_job_status(self, job_id: str) -> state:
        pass

    def get_job_result(self, job_id: str) -> ResponseData:
        pass

    def cancel_job(self, job_id: str) -> bool:
        revoke(job_id, terminate=True)
        pass
