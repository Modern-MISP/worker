from src.api.job_router.response_data import DatabaseChangedResponse
from src.job.job import Job


class RegenerateOccurrencesJob(Job):

    def run(self) -> DatabaseChangedResponse:
        self._misp_sql.fetch_correlation_values()
        self._misp_sql.fetch_over_correlating_values()
        self._misp_sql.add_over_correlating_value()
        # correlate value falls nicht mehr overcorrelating
        self._misp_sql.delete_correlations()
        self._misp_sql.delete_over_correlating_value()

        return DatabaseChangedResponse()
