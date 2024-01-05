from kit.misp_database.misp_api import MispAPI
from kit.misp_database.misp_sql import MispSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CorrelationWorker:
    __threshold: int

    def change_threshold(self, new_threshold: int) -> bool:
        pass
