from src.job.correlation_job.job_data import ThresholdResponseData
from src.job.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from src.job.correlation_job.plugins.correlation_plugin_factory import CorrelationPluginFactory


class CorrelationWorker:

    __threshold: int = 20
    __plugin_factory = CorrelationPluginFactory()

    @classmethod
    def set_threshold(cls, new_threshold: int) -> ThresholdResponseData:
        return ThresholdResponseData()

    @classmethod
    def get_threshold(cls) -> int:
        return cls.__threshold

    @classmethod
    def get_plugin_factory(cls) -> CorrelationPluginFactory:
        return cls.__plugin_factory

    @classmethod
    def get_plugins(cls) -> list[str]:
        return cls.__plugin_factory.get_plugins()
