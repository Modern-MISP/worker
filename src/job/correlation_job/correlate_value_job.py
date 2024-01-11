from typing import List
from uuid import UUID

from src.job.correlation_job.job_data import CorrelateValueResponse, CorrelateValueData
from src.misp_database.misp_sql import MispSQL
from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.job.job import Job
from src.job.correlation_job.correlation_worker import CorrelationWorker


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
        attributes: List[MispEventAttribute] = misp_sql.get_attribute_with_correlations(value)
        if len(attributes) > CorrelationWorker.get_threshold():
            misp_sql.add_over_correlating_value()
            return CorrelateValueResponse()
        else:
            misp_sql.add_correlation_value(value)
            misp_sql.add_correlations()
            return CorrelateValueResponse()
