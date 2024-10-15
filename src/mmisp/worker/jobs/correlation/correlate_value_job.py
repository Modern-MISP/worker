import asyncio
from uuid import UUID

from mmisp.db.models.attribute import Attribute
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import CorrelateValueData, CorrelateValueResponse
from mmisp.worker.jobs.correlation.utility import save_correlations
from mmisp.worker.misp_database import misp_sql


@celery_app.task
def correlate_value_job(user: UserData, correlate_value_data: CorrelateValueData) -> CorrelateValueResponse:
    """
    Method to execute the job. In CorrelateValueData is the value to correlate.

    :param user: the user who requested the job
    :type user: UserData
    :param correlate_value_data: value to correlate
    :type correlate_value_data: CorrelateValue
    :return: relevant information about the correlation
    :rtype: CorrelateValueResponse
    """
    return asyncio.run(correlate_value(correlate_value_data.value))


async def correlate_value(value: str) -> CorrelateValueResponse:
    """
    Static method to correlate the given value based on the misp_sql database and misp_api interface.
    :param value: to correlate
    :param value: string
    :return: relevant information about the correlation
    :rtype: CorrelateValueResponse
    """
    if await misp_sql.is_excluded_correlation(value):
        return CorrelateValueResponse(
            success=True,
            found_correlations=False,
            is_excluded_value=True,
            is_over_correlating_value=False,
            plugin_name=None,
            events=None,
        )
    attributes: list[Attribute] = await misp_sql.get_attributes_with_same_value(value)
    count: int = len(attributes)
    if count > correlation_worker.threshold:
        await misp_sql.delete_correlations(value)
        await misp_sql.add_over_correlating_value(value, count)
        return CorrelateValueResponse(
            success=True,
            found_correlations=True,
            is_excluded_value=False,
            is_over_correlating_value=True,
            plugin_name=None,
            events=None,
        )
    elif count > 1:
        uuid_events: set[UUID] = await save_correlations(attributes, value)
        return CorrelateValueResponse(
            success=True,
            found_correlations=(len(uuid_events) > 1),
            is_excluded_value=False,
            is_over_correlating_value=False,
            plugin_name=None,
            events=uuid_events,
        )
    else:
        return CorrelateValueResponse(
            success=True,
            found_correlations=False,
            is_excluded_value=False,
            is_over_correlating_value=False,
            plugin_name=None,
            events=None,
        )
