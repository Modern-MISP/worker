from src.job.correlation_job.job_data import TopCorrelationsResponse
from src.job.job import Job


class TopCorrelationsJob(Job):

    def run(self) -> TopCorrelationsResponse:
        self._misp_sql.get_values_with_correlation()
        # iteriere über liste
        self._misp_sql.get_number_of_correlations()

        return TopCorrelationsResponse()
