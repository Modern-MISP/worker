from typing import Self

from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.misp_database.misp_api import MispAPI


class PullWorker:
    def __init__(self: Self) -> None:
        self.__misp_api: MispAPI = MispAPI()
        self.__sync_config: SyncConfigData = sync_config_data

    @property
    def misp_api(self: Self) -> MispAPI:
        return self.__misp_api

    @property
    def sync_config(self: Self) -> SyncConfigData:
        return self.__sync_config


pull_worker: PullWorker = PullWorker()
