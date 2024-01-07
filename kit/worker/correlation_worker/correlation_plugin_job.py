from kit.api.job_router.job_router import CorrelationPluginData, CorrelateValueResponse
from kit.worker.correlation_worker.correlation_worker import CorrelationWorker
from kit.worker.correlation_worker.plugins.correlation_plugin import CorrelationPlugin
from kit.worker.worker import Worker


class CorrelationPluginJob(Worker):

    def run(self, correlation_plugin_data: CorrelationPluginData) -> CorrelateValueResponse:
        plugin: CorrelationPlugin = CorrelationWorker.get_plugin()
        return plugin.process()
