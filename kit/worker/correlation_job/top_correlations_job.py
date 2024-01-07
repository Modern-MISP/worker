from kit.api.job_router.job_router import TopCorrelationsResponse
from kit.worker.job import Job


class TopCorrelationsJob(Job):

    def run(self) -> TopCorrelationsResponse:
        self._misp_sql.fetch_correlation_values()
        # iteriere über liste
        self._misp_sql.count_value_correlations()

        return TopCorrelationsResponse()
