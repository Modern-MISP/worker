from mmisp.worker.job.correlation_job.correlate_value_job import CorrelateValueJob
from mmisp.worker.job.correlation_job.correlation_worker import CorrelationWorker
from mmisp.worker.job.correlation_job.job_data import DatabaseChangedResponse
from mmisp.worker.job.job import Job


class RegenerateOccurrencesJob(Job):

    def run(self) -> DatabaseChangedResponse:
        threshold: int = CorrelationWorker.get_threshold()

        first_changed: bool = self.__regenerate_over_correlating(threshold)
        second_changed: bool = self.__regenerate_correlation_values(threshold)
        changed: bool = first_changed or second_changed
        return DatabaseChangedResponse(success=True, database_changed=changed)

    def __regenerate_correlation_values(self, threshold) -> bool:
        changed: bool = False
        correlation_values: list[str] = self._misp_sql.get_values_with_correlation()
        for value in correlation_values:
            count = self._misp_sql.get_number_of_correlations(value, True)
            if count > threshold:
                self._misp_sql.delete_correlations(value)
                self._misp_sql.add_over_correlating_value(value, count)
                changed = True
        return changed

    def __regenerate_over_correlating(self, threshold) -> bool:
        changed: bool = False
        over_correlating_values: list[tuple[str, int]] = self._misp_sql.get_over_correlating_values()
        for entry in over_correlating_values:
            value: str = entry[0]
            count = self._misp_sql.get_number_of_correlations(value, False)
            if count > threshold and count != entry[1]:
                self._misp_sql.add_over_correlating_value(value, count)
                changed = True
            elif count <= threshold:
                self._misp_sql.delete_over_correlating_value(value)
                CorrelateValueJob.correlate_value(self._misp_sql, self._misp_api, value)
                changed = True
        return changed
