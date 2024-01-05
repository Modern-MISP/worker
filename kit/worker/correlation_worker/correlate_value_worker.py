from typing import List
from uuid import UUID
from kit.worker.worker import Worker
from kit.misp_database.misp_database_api import MispDatabaseAPI
from kit.misp_database.misp_database_sql import MispDatabaseSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CorrelateValueJob(Worker):

    def run(self, value: str) -> List[UUID]:
        pass
