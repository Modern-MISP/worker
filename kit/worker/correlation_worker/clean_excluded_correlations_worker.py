from kit.worker.worker import Worker
from kit.misp_database.misp_database_api import MispDatabaseAPI
from kit.misp_database.misp_database_sql import MispDatabaseSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CleanExcludedCorrelationsWorker(Worker):

    def run(self) -> bool:
        pass
