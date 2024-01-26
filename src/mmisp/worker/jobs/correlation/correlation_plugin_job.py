from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound, PluginExecutionException
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelationPluginJobData, InternPluginResult
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.plugins.database_plugin_interface import DatabasePluginInterface


@celery_app.task
def correlation_plugin_job(data: CorrelationPluginJobData) -> CorrelateValueResponse:
    database_interface: DatabasePluginInterface = DatabasePluginInterface(correlation_worker.misp_sql,
                                                                          correlation_worker.misp_api,
                                                                          correlation_worker.threshold)
    try:
        plugin: CorrelationPlugin = correlation_plugin_factory.create(data.correlation_plugin_name, data.value,
                                                                      database_interface)
    except PluginNotFound:
        raise PluginNotFound("The plugin with the name " + data.correlation_plugin_name + " was not found.")
        # TODO nochmal checken ob das geht
    try:
        result: InternPluginResult = plugin.run()
    except PluginExecutionException:
        raise PluginExecutionException("The plugin with the name " + data.correlation_plugin_name + "and the value"
                                       + data.value + " was executed but an error occurred.")
        # TODO nochmal checken ob das geht
    response: CorrelateValueResponse = __process_result(result)
    return plugin.run()[0]


def __process_result(self, result: InternPluginResult) -> CorrelateValueResponse:
    """
    Processes the result of the plugin.
    :param result: the result of the plugin
    :type result: InternPluginResult
    :return: a response with the result of the plugin
    :rtype: CorrelateValueResponse
    :raises: PluginExecutionException: If the result of the plugin is invalid.
    """
    if result is None:
        raise PluginExecutionException("The result of the plugin was None.")


