from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from tests.mocks.sync.test_misp_api import TestMispAPI


class TestPushWorker:
    def __init__(self):
        self.__misp_api: TestMispAPI = TestMispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__sync_config: SyncConfigData = sync_config_data

    @property
    def misp_api(self) -> TestMispAPI:
        """
        Returns the MispAPI instance.
        :return: the MispAPI instance
        :rtype: MispAPI
        """
        return self.__misp_api

    @property
    def misp_sql(self) -> MispSQL:
        """
        Returns the MispSQL instance.
        :return: the MispSQL instance
        :rtype: MispSQL
        """
        return self.__misp_sql

    @property
    def sync_config(self) -> SyncConfigData:
        """
        Returns the sync configuration.
        :return: the sync configuration
        :rtype: SyncConfigData
        """
        return self.__sync_config


test_push_worker: TestPushWorker = TestPushWorker()
