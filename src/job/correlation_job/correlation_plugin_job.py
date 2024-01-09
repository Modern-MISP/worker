from src.api.job_router.response_data import CorrelateValueResponse
from src.api.job_router.input_data import CorrelationPluginData
from src.job.correlation_job.correlation_worker import CorrelationWorker
from src.job.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from src.job.job import Job


class CorrelationPluginJob(Job):

    def run(self, correlation_plugin_data: CorrelationPluginData) -> CorrelateValueResponse:
        plugin: CorrelationPlugin = CorrelationWorker.get_plugin()
        return plugin.run()