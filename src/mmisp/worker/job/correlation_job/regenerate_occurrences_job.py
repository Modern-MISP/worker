from mmisp.worker.job.correlation_job.correlate_value_job import CorrelateValueJob
from mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse
from mmisp.worker.job.job import Job


class RegenerateOccurrencesJob(Job):

    def run(self) -> DatabaseChangedResponse:
        self._misp_sql.get_values_with_correlation()
        self._misp_sql.get_over_correlating_values()
        self._misp_sql.add_over_correlating_value()
        CorrelateValueJob.correlate_value()
        # correlate value falls nicht mehr overcorrelating
        self._misp_sql.delete_correlations()
        self._misp_sql.get_number_of_correlations()
        self._misp_sql.delete_over_correlating_value()

        return DatabaseChangedResponse()

