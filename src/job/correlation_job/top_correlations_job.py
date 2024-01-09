from src.api.job_router.response_data import TopCorrelationsResponse
from src.job.job import Job


class TopCorrelationsJob(Job):

    def run(self) -> TopCorrelationsResponse:
        self._misp_sql.fetch_correlation_values()
        # iteriere über liste
        self._misp_sql.count_value_correlations()

        return TopCorrelationsResponse()
