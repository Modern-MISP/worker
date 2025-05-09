from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from streaq import WrappedContext

from mmisp.db.database import sessionmanager
from mmisp.db.models.attribute import Attribute
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlation_job import correlation_job
from mmisp.worker.jobs.correlation.job_data import CorrelationJobData, DatabaseChangedResponse
from mmisp.worker.jobs.correlation.utility import get_amount_of_possible_correlations
from mmisp.worker.misp_database.misp_sql import (
    add_over_correlating_value,
    delete_correlations,
    delete_over_correlating_value,
    get_attributes_with_same_value,
    get_number_of_correlations,
    get_over_correlating_values,
    get_values_with_correlation,
)

from .queue import queue

db_logger = get_jobs_logger(__name__)


@queue.task()
@add_ajob_db_log
async def regenerate_occurrences_job(ctx: WrappedContext[None], user: UserData) -> DatabaseChangedResponse:
    """
    Method to regenerate the occurrences of the correlations in the database.
    Over correlating values and values with correlations are checked.
    :param user: the user who requested the job
    :type user: UserData
    :return: if the job was successful and if the database was changed
    :rtype: DatabaseChangedResponse
    """
    assert sessionmanager is not None
    # TODO: get correlation_threshold from redis, or db, anything that can be changed
    correlation_threshold = 30
    async with sessionmanager.session() as session:
        first_changed: bool = await __regenerate_over_correlating(session, correlation_threshold)
        second_changed: bool = await __regenerate_correlation_values(session, correlation_threshold)
        changed: bool = first_changed or second_changed
        return DatabaseChangedResponse(success=True, database_changed=changed)


async def __regenerate_correlation_values(session: AsyncSession, correlation_threshold: int) -> bool:
    """
    Method to regenerate the amount of correlations for the values with correlations.
    :return: if the database was changed
    :rtype: bool
    """
    changed: bool = False
    correlation_values: list[str] = await get_values_with_correlation(session)
    for value in correlation_values:
        query = select(Attribute.id).filter(Attribute.value == value).limit(1)  # type: ignore
        attribute_id = (await session.execute(query)).scalars().first()
        if attribute_id is None:
            continue

        count_correlations: int = await get_number_of_correlations(session, value, False)
        current_attributes: list[Attribute] = await get_attributes_with_same_value(session, value)
        count_possible_correlations: int = get_amount_of_possible_correlations(current_attributes)
        count_attributes: int = len(current_attributes)
        if count_attributes > correlation_threshold:
            await delete_correlations(session, value)
            await add_over_correlating_value(session, value, count_attributes)
            changed = True
        elif count_possible_correlations != count_correlations:
            await delete_correlations(session, value)
            job_data = CorrelationJobData(attribute_id=attribute_id)
            user_data = UserData(user_id=0)
            await correlation_job.run(user_data, job_data)
            changed = True
        elif count_possible_correlations == count_correlations == 0:
            await delete_correlations(session, value)
            changed = True
    return changed


async def __regenerate_over_correlating(session: AsyncSession, correlation_threshold: int) -> bool:
    """
    Method to regenerate the amount of correlations for the over correlating values.
    :return: if the database was changed
    :rtype: bool
    """
    changed: bool = False
    over_correlating_values: list[tuple[str, int]] = await get_over_correlating_values(session)
    for entry in over_correlating_values:
        value: str = entry[0]
        count: int = entry[1]

        query = select(Attribute.id).filter(Attribute.value == value).limit(1)  # type: ignore
        attribute_id = (await session.execute(query)).scalars().first()
        if attribute_id is None:
            continue

        current_attributes: list[Attribute] = await get_attributes_with_same_value(session, value)
        count_attributes: int = len(current_attributes)

        if count_attributes != count and count_attributes > correlation_threshold:
            await add_over_correlating_value(session, value, count_attributes)
            changed = True
        elif count_attributes <= correlation_threshold:
            await delete_over_correlating_value(session, value)
            job_data = CorrelationJobData(attribute_id=attribute_id)
            user_data = UserData(user_id=0)
            await correlation_job.run(user_data, job_data)
            changed = True
    return changed
