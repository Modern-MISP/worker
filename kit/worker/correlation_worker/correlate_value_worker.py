from typing import List
from uuid import UUID
from kit.worker.worker import Worker
from kit.misp_database.misp_api import MispAPI
from kit.misp_database.misp_sql import MispSQL
from kit.misp_database.misp_database_redis import MispDatabaseRedis


class CorrelateValueJob(Worker):

    def run(self, value: str) -> List[UUID]:
        pass
