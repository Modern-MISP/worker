from kit.worker.worker import Worker


class RegenerateOccurrencesJob(Worker):

    def run(self) -> bool:
        self._misp_sql.fetch_correlation_values()
        self._misp_sql.fetch_over_correlating_values()
        self._misp_sql.add_over_correlating_value()
        # correlate value falls nicht mehr overcorrelating
        self._misp_sql.delete_correlations()
        self._misp_sql.delete_over_correlating_value()

