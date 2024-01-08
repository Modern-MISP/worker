from typing import List
from uuid import UUID

from kit.api.job_router.job_router import CorrelateValueResponse
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.worker.job import Job
from kit.worker.correlation_job.correlation_worker import CorrelationWorker
from kit.api.job_router.job_router import CorrelateValueData


class CorrelateValueJob(Job):

    def run(self, correlate_value_data: CorrelateValueData) -> CorrelateValueResponse:
        return self.correlate_value(correlate_value_data.value)

    def correlate_value(self, value: str) -> CorrelateValueResponse:
        returnData: CorrelateValueResponse()
        is_excluded: bool = self._misp_sql.is_excluded_correlation(value)
        is_over_correlating: bool = self._misp_sql.is_over_correlating_value(value)
        if is_excluded | is_over_correlating:
            return CorrelateValueResponse(**{"foundCorrelations": False, "events": None})
        attributes: List[MispEventAttribute] = self._misp_sql.fetch_attribute_correlations(value)
        if len(attributes) > CorrelationWorker.get_threshold():
            self._misp_sql.add_over_correlating_value()
        else:
            self._misp_sql.add_correlation_value()
            self._misp_sql.add_correlations()
