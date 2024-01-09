from kit.api.job_router.response_data import DatabaseChangedResponse
from kit.worker.job import Job


class CleanExcludedCorrelationsJob(Job):

    def run(self) -> DatabaseChangedResponse:
        # hole liste
        # entferne correlations zu den values
        self._misp_sql.fetch_excluded_correlations()
        self._misp_sql.delete_correlations()

        return DatabaseChangedResponse()
