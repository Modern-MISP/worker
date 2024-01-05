from kit.misp_database.misp_database_api import MispDatabaseAPI
from kit.misp_database.misp_database_sql import MispDatabaseSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CorrelationWorker:
    __threshold: int

    def change_threshold(self, new_threshold: int) -> bool:
        pass
