from typing import Self

from celery.states import state
from celery.worker.control import revoke

from src.job.correlation_job.job_data import DatabaseChangedResponse, CorrelateValueResponse, TopCorrelationsResponse
from src.job.enrichment_job.job_data import EnrichEventResult, EnrichAttributeResult
from src.job.processfreetext_job.job_data import ProcessFreeTextResponse
from typing import TypeAlias

from src.job.pull_job.job_data import PullResult
from src.job.push_job.job_data import PushResult

ResponseData: TypeAlias = (DatabaseChangedResponse | CorrelateValueResponse | TopCorrelationsResponse |
                           EnrichAttributeResult | EnrichEventResult | ProcessFreeTextResponse | PullResult
                           | PushResult)


class JobController:
    __instance: Self

    @classmethod
    def get_instance(cls) -> Self:
        pass

    def get_job_status(self, job_id: int) -> state:
        pass

    def get_job_result(self, job_id: int) -> ResponseData:
        pass

    def cancel_job(self, job_id: int) -> bool:
        revoke(job_id, terminate=True)
        pass
