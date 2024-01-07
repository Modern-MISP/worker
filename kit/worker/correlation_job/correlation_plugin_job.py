from kit.api.job_router.job_router import CorrelationPluginData, CorrelateValueResponse
from kit.worker.correlation_job.correlation_worker import CorrelationWorker
from kit.worker.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from kit.worker.job import Job


class CorrelationPluginJob(Job):

    def run(self, correlation_plugin_data: CorrelationPluginData) -> CorrelateValueResponse:
        plugin: CorrelationPlugin = CorrelationWorker.get_plugin()
        return plugin.process()
