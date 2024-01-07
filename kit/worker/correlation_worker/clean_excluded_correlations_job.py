from kit.api.job_router.job_router import DatabaseChangedResponse
from kit.worker.worker import Worker


class CleanExcludedCorrelationsJob(Worker):

    def run(self) -> DatabaseChangedResponse:
        # hole liste
        # entferne correlations zu den values
        self._misp_sql.fetch_excluded_correlations()
        self._misp_sql.delete_correlations()

        return DatabaseChangedResponse()
