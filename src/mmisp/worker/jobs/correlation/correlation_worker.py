from mmisp.worker.jobs.correlation.job_data import ChangeThresholdResponse, ChangeThresholdData
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import CorrelationPluginFactory
from mmisp.worker.jobs.correlation.correlation_config_data import CorrelationConfigData

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL


class CorrelationWorker:

    def __init__(self):
        self.misp_api: MispAPI = MispAPI()
        self.misp_sql: MispSQL = MispSQL()

    MAX_THRESHOLD: int = (2 ** 31) - 1

    __plugin_factory: CorrelationPluginFactory
    __config_data: CorrelationConfigData

    @classmethod
    def load_correlation_plugins(cls):
        pass

    @classmethod
    def set_threshold(cls, data: ChangeThresholdData) -> ChangeThresholdResponse:
        new_threshold: int = data.new_threshold
        if (new_threshold < 1) or (new_threshold > cls.MAX_THRESHOLD):
            return ChangeThresholdResponse(saved=False, valid_threshold=False)
        else:
            cls.__config_data.threshold = new_threshold
            return ChangeThresholdResponse(saved=True, valid_threshold=True, new_threshold=new_threshold)

    @classmethod
    def get_threshold(cls) -> int:
        return cls.__config_data.threshold

    @classmethod
    def get_plugin_factory(cls) -> CorrelationPluginFactory:
        return cls.__plugin_factory

    @classmethod
    def get_plugins(cls) -> list[CorrelationPluginInfo]:
        pass

    @classmethod
    def set_correlation_config_data(cls, config_data: CorrelationConfigData) -> bool:
        CorrelationWorker.__config_data = config_data
        return True


correlation_worker = CorrelationWorker()
