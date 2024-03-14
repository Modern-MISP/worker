from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from tests.mocks.sync.test_misp_api import TestMispAPI


# from mmisp.worker.misp_database.mmisp_redis import MMispRedis


class TestPullWorker:
    def __init__(self):
        # self.__misp_api: MispAPI = MispAPI()
        self.__misp_api: TestMispAPI = TestMispAPI()  # just for testing
        self.__misp_sql: MispSQL = MispSQL()
        # self.__mmisp_redis: MMispRedis = MMispRedis()
        self.__sync_config: SyncConfigData = sync_config_data

    @property
    def misp_api(self) -> MispAPI:
        return self.__misp_api

    @property
    def misp_sql(self) -> MispSQL:
        return self.__misp_sql

    # @property
    # def mmisp_redis(self) -> MMispRedis:
    #     return self.__mmisp_redis

    @property
    def sync_config(self) -> SyncConfigData:
        return self.__sync_config


pull_worker: TestPullWorker = TestPullWorker()
