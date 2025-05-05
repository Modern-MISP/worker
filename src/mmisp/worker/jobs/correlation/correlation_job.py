from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from streaq import WrappedContext

import mmisp.worker.jobs.correlation.plugins  # noqa
from mmisp.db.database import sessionmanager
from mmisp.db.models.attribute import Attribute
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.plugins import factory
from mmisp.plugins.exceptions import PluginExecutionException, PluginNotFound
from mmisp.plugins.types import PluginType
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import CorrelationJobData, CorrelationResponse, InternPluginResult
from mmisp.worker.jobs.correlation.utility import save_correlations
from mmisp.worker.misp_database import misp_sql

from .queue import queue

db_logger = get_jobs_logger(__name__)
PLUGIN_NAME_STRING: str = "The plugin with the name "


@queue.task()
@add_ajob_db_log
async def correlation_job(ctx: WrappedContext[None], user: UserData, data: CorrelationJobData) -> CorrelationResponse:
    """
    Method to execute a correlation plugin job.
    It creates a plugin based on the given data and runs it.
    Finally, it processes the result and returns a response.

    :param user: the user who requested the job
    :type user: UserData
    :param data: specifies the value and the plugin to use
    :type data: CorrelationPluginJobData
    :return: a response with the result of the correlation by the plugin
    :rtype: CorrelationResponse
    """
    assert sessionmanager is not None
    async with sessionmanager.session() as db:
        query = select(Attribute).filter(Attribute.id == data.attribute_id)
        attribute = (await db.execute(query)).scalars().one_or_none()

        if attribute is None:
            return CorrelationResponse(
                success=False,
                found_correlations=False,
                is_excluded_value=False,
                is_over_correlating_value=False,
                plugin_name=data.correlation_plugin_name,
            )
        correlation_threshold: int = 20

        if await misp_sql.is_excluded_correlation(db, attribute.value):
            return CorrelationResponse(
                success=True,
                found_correlations=False,
                is_excluded_value=True,
                is_over_correlating_value=False,
                plugin_name=data.correlation_plugin_name,
            )
        try:
            plugin = factory.get_plugin(PluginType.CORRELATION, data.correlation_plugin_name)
        except PluginNotFound:
            raise PluginNotFound(message=PLUGIN_NAME_STRING + data.correlation_plugin_name + " was not found.")
        try:
            result: CorrelationResponse | InternPluginResult | None = await plugin.run(
                db, attribute, correlation_threshold
            )
        except PluginExecutionException:
            raise PluginExecutionException(
                message=PLUGIN_NAME_STRING
                + data.correlation_plugin_name
                + "and the value"
                + attribute.value
                + " was executed but an error occurred."
            )
        except Exception as exception:
            raise PluginExecutionException(
                message=PLUGIN_NAME_STRING
                + data.correlation_plugin_name
                + " and the value "
                + attribute.value
                + " was executed but the following error occurred: "
                + str(exception)
            )
        if isinstance(result, CorrelationResponse):
            return result

        response: CorrelationResponse = await __process_result(
            db, data.correlation_plugin_name, attribute.value, result
        )
        return response


async def __process_result(
    session: AsyncSession, plugin_name: str, value: str, result: InternPluginResult | None
) -> CorrelationResponse:
    """
    Processes the result of the plugin.
    :param result: the result of the plugin
    :type result: InternPluginResult
    :return: a response with the result of the plugin
    :rtype: CorrelationResponse
    :raises: PluginExecutionException: If the result of the plugin is invalid.
    """
    if result is None:
        raise PluginExecutionException(message="The result of the plugin was None.")

    response: CorrelationResponse = CorrelationResponse(
        success=result.success,
        found_correlations=result.found_correlations,
        is_excluded_value=False,
        is_over_correlating_value=result.is_over_correlating_value,
        plugin_name=plugin_name,
    )
    if result.found_correlations and len(result.correlations) > 1:
        uuid_events: set[UUID] = await save_correlations(session, result.correlations, value)
        response.events = uuid_events
    elif len(result.correlations) <= 1:
        response.found_correlations = False
    return response
