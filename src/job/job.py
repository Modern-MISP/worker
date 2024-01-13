from abc import abstractmethod

from celery import Task

from src.misp_database.misp_sql import MispSQL
from src.misp_database.misp_api import MispAPI
from src.misp_database.mmisp_redis import MMispRedis


class Job(Task):
    def __init__(self):
        self._misp_api: MispAPI = MispAPI()
        self._misp_sql: MispSQL = MispSQL()
        self._mmisp_redis: MMispRedis = MMispRedis()
    # status: WorkerStatusEnum
    # isOn: bool
    # currJob: Job
    #
    # def setJob(self, job: Job):
    #     pass
    #
    # def setIsOn(self, val: bool) -> None:
    #     pass
