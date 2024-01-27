from uuid import UUID

from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound, PluginExecutionException
from mmisp.worker.jobs.correlation.correlate_value_job import save_correlations
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
    if correlation_worker.misp_sql.is_excluded_correlation(data.value):
        return CorrelateValueResponse(success=True, found_correlations=False, is_excluded_value=True,
                                      is_over_correlating_value=False, plugin_name=data.correlation_plugin_name)
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
    response: CorrelateValueResponse = __process_result(data.correlation_plugin_name, result)
    return response


def __process_result(plugin_name: str, value: str, result: InternPluginResult) -> CorrelateValueResponse:
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
    response: CorrelateValueResponse = (
        CorrelateValueResponse(success=result.success,
                               found_correlations=result.found_correlations,
                               is_excluded_value=False,
                               is_over_correlating_value=result.is_over_correlating_value,
                               plugin_name=plugin_name))
    if result.found_correlations and result.correlations.count() > 1:
        uuid_events: set[UUID] = save_correlations(result.correlations, value)
        response.events = uuid_events
    elif result.correlations.count <= 1:
        response.found_correlations = False
    return response
