import sys
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import Attribute
from mmisp.lib.logger import get_jobs_logger
from mmisp.plugins import factory
from mmisp.plugins.types import CorrelationPluginType, PluginType
from mmisp.worker.jobs.correlation.job_data import CorrelationResponse
from mmisp.worker.jobs.correlation.utility import save_correlations
from mmisp.worker.misp_database import misp_sql

db_logger = get_jobs_logger(__name__)

NAME: str = "ExactValueCorrelationPlugin"
PLUGIN_TYPE: PluginType = PluginType.CORRELATION
DESCRIPTION: str = "This plugin searches for attributes with the same value."
AUTHOR: str = "Konstantin Zangerle"
VERSION: str = "0.1"
CORRELATION_TYPE: CorrelationPluginType = CorrelationPluginType.ALL_CORRELATIONS


async def run(db: AsyncSession, attribute: Attribute, correlation_threshold: int) -> CorrelationResponse:
    """
    Static method to correlate the given value based on the misp_sql database and misp_api interface.
    :param value: to correlate
    :param value: string
    :return: relevant information about the correlation
    :rtype: CorrelationResponse
    """
    value = attribute.value
    if await misp_sql.is_excluded_correlation(db, value):
        return CorrelationResponse(
            success=True,
            found_correlations=False,
            is_excluded_value=True,
            is_over_correlating_value=False,
            plugin_name=None,
            events=None,
        )
    attributes: list[Attribute] = await misp_sql.get_attributes_with_same_value(db, value)
    count: int = len(attributes)
    if count > correlation_threshold:
        await misp_sql.delete_correlations(db, value)
        await misp_sql.add_over_correlating_value(db, value, count)
        return CorrelationResponse(
            success=True,
            found_correlations=True,
            is_excluded_value=False,
            is_over_correlating_value=True,
            plugin_name=None,
            events=None,
        )
    elif count > 1:
        uuid_events: set[UUID] = await save_correlations(db, attributes, value)
        return CorrelationResponse(
            success=True,
            found_correlations=(len(uuid_events) > 1),
            is_excluded_value=False,
            is_over_correlating_value=False,
            plugin_name=None,
            events=uuid_events,
        )

    return CorrelationResponse(
        success=True,
        found_correlations=False,
        is_excluded_value=False,
        is_over_correlating_value=False,
        plugin_name=NAME,
        events=None,
    )


factory.register(sys.modules[__name__])
