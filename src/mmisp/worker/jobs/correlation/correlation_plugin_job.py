from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelationPluginJobData
from mmisp.worker.jobs.correlation.correlation_worker import CorrelationWorker, correlation_worker
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import CorrelationPluginFactory
from mmisp.worker.jobs.correlation.plugins.database_plugin_interface import DatabasePluginInterface


@celery_app.task
def correlation_plugin_job(correlation_plugin_data: CorrelationPluginJobData) -> CorrelateValueResponse:
    database_interface: DatabasePluginInterface = DatabasePluginInterface(correlation_worker.misp_sql)
    factory: CorrelationPluginFactory = CorrelationWorker.get_plugin_factory()
    plugin: CorrelationPlugin = factory.create(correlation_plugin_data.correlation_plugin_name,
                                               correlation_plugin_data.value, database_interface)

    return plugin.run()[0]
