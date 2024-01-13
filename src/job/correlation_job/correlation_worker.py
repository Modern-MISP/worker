from src.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from src.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from src.job.correlation_job.plugins.correlation_plugin_factory import CorrelationPluginFactory
from src.job.correlation_job.correlation_config_data import CorrelationConfigData


class CorrelationWorker:

    __plugin_factory = CorrelationPluginFactory()
    __config_data = CorrelationConfigData()
    __threshold = int

    @classmethod
    def load_correlation_plugins(cls):
        pass

    @classmethod
    def set_threshold(cls, data: ChangeThresholdData) -> ChangeThresholdResponse:
        return ChangeThresholdResponse()

    @classmethod
    def get_threshold(cls) -> int:
        pass

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
