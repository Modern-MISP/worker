from typing import Self

from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.misp_database.misp_api import MispAPI


class PushWorker:
    def __init__(self: Self) -> None:
        self.__misp_api: MispAPI = MispAPI()
        self.__sync_config: SyncConfigData = sync_config_data

    @property
    def misp_api(self: Self) -> MispAPI:
        """
        Returns the MispAPI instance.
        :return: the MispAPI instance
        :rtype: MispAPI
        """
        return self.__misp_api

    @property
    def sync_config(self: Self) -> SyncConfigData:
        """
        Returns the sync configuration.
        :return: the sync configuration
        :rtype: SyncConfigData
        """
        return self.__sync_config


push_worker: PushWorker = PushWorker()
