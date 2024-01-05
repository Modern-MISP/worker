from kit.worker.worker import Worker
from kit.misp_database.misp_api import MispAPI
from kit.misp_database.misp_sql import MispSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class RegenerateOccurrencesWorker(Worker):

    def run(self) -> bool:
        pass
