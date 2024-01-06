from typing import List
from uuid import UUID

from kit.api.job_router.job_router import CorrelateValueResponse
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.worker.worker import Worker


class CorrelateValueJob(Worker):

    def run(self, value: str) -> CorrelateValueResponse:
        returnData: CorrelateValueResponse()
        is_excluded: bool = self._misp_sql.is_excluded_correlation(value)
        is_over_correlating: bool = self._misp_sql.is_over_correlating_value(value)
        if is_excluded | is_over_correlating:
            return CorrelateValueResponse(**{"foundCorrelations": False, "events": None})
        attributes: List[MispEventAttribute] = self._misp_sql.fetch_attribute_correlations(value)
        # TODO fragen: if len(attributes) > CorrelationWorker.get_trehsold
        self._misp_sql.add_over_correlating_value()
        self._misp_sql.add_correlation_value()
        self._misp_sql.add_correlations()
