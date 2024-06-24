from typing import Self

from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.misp_database.misp_sql import MispSQL
from tests.mocks.sync.test_misp_api import TestMispAPI


class TestPullWorker:
    def __init__(self: Self) -> None:
        self.__misp_api: TestMispAPI = TestMispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__sync_config: SyncConfigData = sync_config_data

    @property
    def misp_api(self: Self) -> TestMispAPI:
        return self.__misp_api

    @property
    def misp_sql(self: Self) -> MispSQL:
        return self.__misp_sql

    @property
    def sync_config(self: Self) -> SyncConfigData:
        return self.__sync_config


test_pull_worker: TestPullWorker = TestPullWorker()
