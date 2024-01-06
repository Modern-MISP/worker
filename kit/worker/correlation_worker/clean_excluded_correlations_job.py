from kit.worker.worker import Worker


class CleanExcludedCorrelationsJob(Worker):

    def run(self) -> bool:
        # hole alte liste
        # vergleiche
        # entferne correlations zu den values
        self._misp_sql.delete_correlations()
        return True
