from kit.job.job import Job
from kit.worker.worker import Worker
from kit.misp_database.misp_database_api import MispDatabaseAPI
from kit.misp_database.misp_database_sql import MispDatabaseSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CorrelationWorker(Worker):
    __threshold: int

    def run(self):
        pass

    def __change_threshold(self, new_threshold: int) -> bool:
        pass

    def __correlate_value(self, value: str) -> bool:
        pass

    def __top_correlations(self) -> bool:
        return MispDatabaseRedis.set_tc_entry()

    def __regenerate_occurrences(self) -> bool:
        pass

    def __clean_excluded_correlations(self) -> bool:
        pass
