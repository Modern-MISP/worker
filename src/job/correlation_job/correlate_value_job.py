from typing import List
from uuid import UUID

from src.job.correlation_job.response_data import CorrelateValueResponse
from src.misp_database.misp_sql import MispSQL
from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.job.job import Job
from src.job.correlation_job.correlation_worker import CorrelationWorker
from src.api.job_router.input_data import CorrelateValueData


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
