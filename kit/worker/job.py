from celery import shared_task, Task
from enum import Enum

from kit.misp_database.misp_sql import MispSQL
from kit.misp_database.misp_api import MispAPI
from kit.misp_database.mmisp_redis import MMispRedis


class WorkerStatusEnum(str, Enum):
    idle = "idle"
    working = "working"
    deactivated = "deactivated"


class Job(Task):
    def __init__(self, misp_api: MispAPI, misp_sql: MispSQL, mmisp_redis: MMispRedis):
        self._misp_api: MispAPI = misp_api
        self._misp_sql: MispSQL = misp_sql
        self._mmisp_redis: MMispRedis = mmisp_redis
    # status: WorkerStatusEnum
    # isOn: bool
    # currJob: Job
    #
    # def setJob(self, job: Job):
    #     pass
    #
    # def setIsOn(self, val: bool) -> None:
    #     pass
