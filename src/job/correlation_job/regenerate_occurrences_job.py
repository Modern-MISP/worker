from src.job.correlation_job.job_data import DatabaseChangedResponse
from src.job.job import Job


class RegenerateOccurrencesJob(Job):

    def run(self) -> DatabaseChangedResponse:
        self._misp_sql.get_correlation_values()
        self._misp_sql.get_over_correlating_values()
        self._misp_sql.add_over_correlating_value()
        # correlate value falls nicht mehr overcorrelating
        self._misp_sql.delete_correlations()
        self._misp_sql.get_count_value_correlations()
        self._misp_sql.delete_over_correlating_value()

        return DatabaseChangedResponse()

