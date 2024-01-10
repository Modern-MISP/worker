from src.job.correlation_job.response_data import ThresholdResponseData
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
    def get_plugin(cls, plugin_name: str, value: str) -> CorrelationPlugin:
        return cls.__plugin_factory.create(plugin_name, value)

    @classmethod
    def get_plugins(cls) -> list[str]:
        return cls.__plugin_factory.get_plugins()
