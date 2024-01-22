from src.mmisp.worker.job.correlation_job.job_data import CorrelateValueResponse, CorrelationPluginJobData
from mmisp.worker.job.correlation_job.correlation_worker import CorrelationWorker
from mmisp.worker.job.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.job.correlation_job.plugins.correlation_plugin_factory import CorrelationPluginFactory
from mmisp.worker.job.correlation_job.plugins.database_plugin_interface import DatabasePluginInterface
from mmisp.worker.job.job import Job


class CorrelationPluginJob(Job):

    def run(self, correlation_plugin_data: CorrelationPluginJobData) -> CorrelateValueResponse:
        database_interface: DatabasePluginInterface = DatabasePluginInterface(self._misp_sql)
        factory: CorrelationPluginFactory = CorrelationWorker.get_plugin_factory()
        plugin: CorrelationPlugin = factory.create(correlation_plugin_data.correlation_plugin_name,
                                                   correlation_plugin_data.value, database_interface )

        return plugin.run()[0]
