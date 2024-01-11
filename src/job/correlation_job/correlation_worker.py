from src.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from src.job.correlation_job.plugins.correlation_plugin import CorrelationPluginInfo
from src.job.correlation_job.plugins.correlation_plugin_factory import CorrelationPluginFactory


class CorrelationWorker:

    __threshold: int = 20
    __plugin_factory = CorrelationPluginFactory()

    @classmethod
    def load_correlation_plugins(cls):
        pass

    @classmethod
    def set_threshold(cls, data: ChangeThresholdData) -> ChangeThresholdResponse:
        return ChangeThresholdResponse()

    @classmethod
    def get_threshold(cls) -> int:
        return cls.__threshold

    @classmethod
    def get_plugin_factory(cls) -> CorrelationPluginFactory:
        return cls.__plugin_factory

    @classmethod
    def get_plugins(cls) -> list[CorrelationPluginInfo]:
        pass
