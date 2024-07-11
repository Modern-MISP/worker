from mmisp.db.models.attribute import Attribute
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client.celery_client import celery_app
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
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


@celery_app.task
async def regenerate_occurrences_job(user: UserData) -> DatabaseChangedResponse:
    """
    Method to regenerate the occurrences of the correlations in the database.
    Over correlating values and values with correlations are checked.
    :param user: the user who requested the job
    :type user: UserData
    :return: if the job was successful and if the database was changed
    :rtype: DatabaseChangedResponse
    """
    first_changed: bool = await __regenerate_over_correlating()
    second_changed: bool = await __regenerate_correlation_values()
    changed: bool = first_changed or second_changed
    return DatabaseChangedResponse(success=True, database_changed=changed)


async def __regenerate_correlation_values() -> bool:
    """
    Method to regenerate the amount of correlations for the values with correlations.
    :return: if the database was changed
    :rtype: bool
    """
    changed: bool = False
    correlation_values: list[str] = await get_values_with_correlation()
    for value in correlation_values:
        count_correlations: int = await get_number_of_correlations(value, False)
        current_attributes: list[Attribute] = await get_attributes_with_same_value(value)
        count_possible_correlations: int = get_amount_of_possible_correlations(current_attributes)
        count_attributes: int = len(current_attributes)
        if count_attributes > correlation_worker.threshold:
            await delete_correlations(value)
            await add_over_correlating_value(value, count_attributes)
            changed = True
        elif count_possible_correlations != count_correlations:
            await delete_correlations(value)
            await correlate_value(value)
            changed = True
        elif count_possible_correlations == count_correlations == 0:
            await delete_correlations(value)
            changed = True
    return changed


async def __regenerate_over_correlating() -> bool:
    """
    Method to regenerate the amount of correlations for the over correlating values.
    :return: if the database was changed
    :rtype: bool
    """
    changed: bool = False
    over_correlating_values: list[tuple[str, int]] = await get_over_correlating_values()
    for entry in over_correlating_values:
        value: str = entry[0]
        count: int = entry[1]

        current_attributes: list[Attribute] = await get_attributes_with_same_value(value)
        count_attributes: int = len(current_attributes)

        if count_attributes != count and count_attributes > correlation_worker.threshold:
            await add_over_correlating_value(value, count_attributes)
            changed = True
        elif count_attributes <= correlation_worker.threshold:
            await delete_over_correlating_value(value)
            await correlate_value(value)
            changed = True
    return changed
