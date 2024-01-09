from src.api.worker_router.worker_api_data import ThresholdResponseData
from src.worker.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from src.worker.correlation_job.plugins.correlation_plugin_factory import CorrelationPluginFactory


class CorrelationWorker:

    __threshold: int = 20
    __plugin_factory = CorrelationPluginFactory()

    @classmethod
    def set_threshold(cls, new_threshold: int) -> ThresholdResponseData:
        pass

    @classmethod
    def get_threshold(cls) -> int:
        return cls.__threshold

    @classmethod
    def get_plugin(cls, plugin_name: str, value: str) -> CorrelationPlugin:
        return cls.__plugin_factory.create(plugin_name, value)

    @classmethod
    def get_plugins(cls) -> list[str]:
        return cls.__plugin_factory.get_plugins()
