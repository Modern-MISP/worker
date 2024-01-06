from kit.worker.worker import Worker


class TopCorrelationsJob(Worker):

    def run(self) -> bool:
        self._misp_sql.fetch_correlation_values()
        # iteriere über liste
        self._misp_sql.count_value_correlations()
        self._misp_redis.set_tc_entry()
        return True
