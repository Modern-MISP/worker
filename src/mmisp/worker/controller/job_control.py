from typing import Self

from celery.states import state
from celery.worker.control import revoke

from src.mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse, CorrelateValueResponse, TopCorrelationsResponse
from src.mmisp.worker.job.enrichment_job.job_data import EnrichEventResult, EnrichAttributeResult
from src.mmisp.worker.job.processfreetext_job.job_data import ProcessFreeTextResponse
from typing import TypeAlias

from mmisp.worker.job.pull_job.job_data import PullResult
from mmisp.worker.job.push_job.job_data import PushResult

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
