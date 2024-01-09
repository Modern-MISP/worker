from kit.api.job_router.response_data import CorrelateValueResponse
from kit.api.job_router.input_data import CorrelationPluginData
from kit.worker.correlation_job.correlation_worker import CorrelationWorker
from kit.worker.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from kit.worker.job import Job


class CorrelationPluginJob(Job):

    def run(self, correlation_plugin_data: CorrelationPluginData) -> CorrelateValueResponse:
        plugin: CorrelationPlugin = CorrelationWorker.get_plugin()
        return plugin.run()
