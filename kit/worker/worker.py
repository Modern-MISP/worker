from celery import shared_task, Task
from enum import Enum

from kit.job.job import Job
from kit.misp_database.misp_redis import MispRedis
from kit.misp_database.misp_sql import MispSQL
from kit.misp_database.misp_api import MispAPI


class WorkerStatusEnum(str, Enum):
    idle = "idle"
    working = "working"
    deactivated = "deactivated"


class Worker(Task):
    def __init__(self, misp_api: MispAPI, misp_sql: MispSQL, misp_redis: MispRedis):
        self._misp_api: MispAPI = misp_api
        self._misp_sql: MispSQL = misp_sql
        self._misp_redis: MispRedis = misp_redis
    # status: WorkerStatusEnum
    # isOn: bool
    # currJob: Job
    #
    # def setJob(self, job: Job):
    #     pass
    #
    # def setIsOn(self, val: bool) -> None:
    #     pass