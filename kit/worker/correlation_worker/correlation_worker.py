from kit.api.worker_router.worker_router import ThresholdResponseData
from kit.worker.correlation_worker.plugins.correlation_plugin_factory import CorrelationPluginFactory


class CorrelationWorker:

    def __init__(self):
        self.__threshold: int = 20
        self.__plugin_factory = CorrelationPluginFactory()

    def change_threshold(self, new_threshold: int) -> ThresholdResponseData:
        pass
