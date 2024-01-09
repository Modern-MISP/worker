from typing import List
from uuid import UUID

from kit.api.job_router.response_data import CorrelateValueResponse
from kit.misp_database.misp_sql import MispSQL
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.worker.job import Job
from kit.worker.correlation_job.correlation_worker import CorrelationWorker
from kit.api.job_router.input_data import CorrelateValueData


class CorrelateValueJob(Job):

    def run(self, correlate_value_data: CorrelateValueData) -> CorrelateValueResponse:
        return self.correlate_value(correlate_value_data.value)

    @staticmethod
    def correlate_value(misp_sql: MispSQL, value: str) -> CorrelateValueResponse:
        returnData: CorrelateValueResponse()
        is_excluded: bool = misp_sql.is_excluded_correlation(value)
        is_over_correlating: bool = misp_sql.is_over_correlating_value(value)
        if is_excluded | is_over_correlating:
            return CorrelateValueResponse(**{"foundCorrelations": False, "events": None})
        attributes: List[MispEventAttribute] = misp_sql.fetch_attribute_correlations(value)
        if len(attributes) > CorrelationWorker.get_threshold():
            misp_sql.add_over_correlating_value()
        else:
            misp_sql.add_correlation_value()
            misp_sql.add_correlations()
