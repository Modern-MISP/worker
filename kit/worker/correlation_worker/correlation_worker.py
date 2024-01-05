from kit.worker.worker import Worker
from kit.misp_database.misp_database_api import MispDatabaseAPI
from kit.misp_database.misp_database_sql import MispDatabaseSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CorrelationWorker(Worker):
    __threshold: int

    def change_threshold(self, new_threshold: int) -> bool:
        pass
