from mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse
from mmisp.worker.job.job import Job


class CleanExcludedCorrelationsJob(Job):

    def run(self) -> DatabaseChangedResponse:
        changed: bool = False
        excluded: list[str] = self._misp_sql.get_excluded_correlations()
        for value in excluded:
            if self._misp_sql.delete_correlations(value):
                changed = True
        return DatabaseChangedResponse(success=True, database_changed=changed)
