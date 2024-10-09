import asyncio
from uuid import UUID

from mmisp.plugins.exceptions import PluginExecutionException
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelationPluginJobData, InternPluginResult
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.utility import save_correlations
from mmisp.worker.misp_database import misp_sql

PLUGIN_NAME_STRING: str = "The plugin with the name "


@celery_app.task
def correlation_plugin_job(user: UserData, data: CorrelationPluginJobData) -> CorrelateValueResponse:
    """
    Method to execute a correlation plugin job.
    It creates a plugin based on the given data and runs it.
    Finally, it processes the result and returns a response.

    :param user: the user who requested the job
    :type user: UserData
    :param data: specifies the value and the plugin to use
    :type data: CorrelationPluginJobData
    :return: a response with the result of the correlation by the plugin
    :rtype: CorrelateValueResponse
    """
    if asyncio.run(misp_sql.is_excluded_correlation(data.value)):
        return CorrelateValueResponse(
            success=True,
            found_correlations=False,
            is_excluded_value=True,
            is_over_correlating_value=False,
            plugin_name=data.correlation_plugin_name,
        )
    try:
        plugin: CorrelationPlugin = correlation_plugin_factory.create(
            data.correlation_plugin_name,
            data.value,
            correlation_worker.misp_api,
            correlation_worker.threshold,
        )
    except PluginNotFound:
        raise PluginNotFound(message=PLUGIN_NAME_STRING + data.correlation_plugin_name + " was not found.")
    try:
        result: InternPluginResult | None = asyncio.run(plugin.run())
    except PluginExecutionException:
        raise PluginExecutionException(
            message=PLUGIN_NAME_STRING
            + data.correlation_plugin_name
            + "and the value"
            + data.value
            + " was executed but an error occurred."
        )
    except Exception as exception:
        raise PluginExecutionException(
            message=PLUGIN_NAME_STRING
            + data.correlation_plugin_name
            + "and the value"
            + data.value
            + " was executed but the following error occurred: "
            + str(exception)
        )
    response: CorrelateValueResponse = asyncio.run(__process_result(data.correlation_plugin_name, data.value, result))
    return response


async def __process_result(plugin_name: str, value: str, result: InternPluginResult | None) -> CorrelateValueResponse:
    """
    Processes the result of the plugin.
    :param result: the result of the plugin
    :type result: InternPluginResult
    :return: a response with the result of the plugin
    :rtype: CorrelateValueResponse
    :raises: PluginExecutionException: If the result of the plugin is invalid.
    """
    if result is None:
        raise PluginExecutionException(message="The result of the plugin was None.")
    response: CorrelateValueResponse = CorrelateValueResponse(
        success=result.success,
        found_correlations=result.found_correlations,
        is_excluded_value=False,
        is_over_correlating_value=result.is_over_correlating_value,
        plugin_name=plugin_name,
    )
    if result.found_correlations and len(result.correlations) > 1:
        uuid_events: set[UUID] = await save_correlations(result.correlations, value)
        response.events = uuid_events
    elif len(result.correlations) <= 1:
        response.found_correlations = False
    return response
