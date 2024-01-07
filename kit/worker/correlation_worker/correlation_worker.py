from kit.api.worker_router.worker_router import ThresholdResponseData
from kit.worker.correlation_worker.plugins.correlation_plugin import CorrelationPlugin
from kit.worker.correlation_worker.plugins.correlation_plugin_factory import CorrelationPluginFactory


class CorrelationWorker:

    __threshold: int = 20
    __plugin_factory = CorrelationPluginFactory()

    @staticmethod
    def set_threshold(new_threshold: int) -> ThresholdResponseData:
        pass

    @staticmethod
    def get_threshold() -> int:
        return CorrelationWorker.__threshold

    @staticmethod
    def get_plugin(plugin_name: str, value: str) -> CorrelationPlugin:
        return CorrelationWorker.__plugin_factory.create(plugin_name, value)
