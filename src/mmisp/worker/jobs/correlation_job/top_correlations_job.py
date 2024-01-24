from mmisp.worker.job.correlation_job.job_data import TopCorrelationsResponse
from mmisp.worker.job.job import Job


class TopCorrelationsJob(Job):

    def run(self) -> TopCorrelationsResponse:
        values: list[str] = self._misp_sql.get_values_with_correlation()
        numbers: list[int] = list()
        for value in values:
            numbers.append(self._misp_sql.get_number_of_correlations(value, True))
        top_correlations: list[tuple[str, int]] = list(zip(values, numbers))
        top_correlations.sort(key=lambda a: a[1], reverse=True)
        return TopCorrelationsResponse(success=True, top_correlations=top_correlations)
