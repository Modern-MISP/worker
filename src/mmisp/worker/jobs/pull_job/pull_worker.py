from mmisp.worker.jobs.pull_job.pull_config_data import PullConfigData
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_database.mmisp_redis import MMispRedis


class PullWorker:
    def __init__(self):
        self.misp_api: MispAPI = MispAPI()
        self.misp_sql: MispSQL = MispSQL()
        self.misp_redis: MMispRedis = MMispRedis()
        self.config = PullConfigData()


pull_worker: PullWorker = PullWorker()
