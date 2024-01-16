from mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse
from mmisp.worker.job.job import Job


class CleanExcludedCorrelationsJob(Job):

    def run(self) -> DatabaseChangedResponse:
        # hole liste
        # entferne correlations zu den values
        self._misp_sql.get_excluded_correlations()
        self._misp_sql.delete_correlations()

        return DatabaseChangedResponse()
