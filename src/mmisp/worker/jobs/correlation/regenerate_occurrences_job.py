from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.utility import get_amount_of_possible_correlations
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispSQLEventAttribute


@celery_app.task
def regenerate_occurrences_job(user: UserData) -> DatabaseChangedResponse:
    """
    Method to regenerate the occurrences of the correlations in the database.
    Over correlating values and values with correlations are checked.
    :param user: the user who requested the job
    :type user: UserData
    :return: if the job was successful and if the database was changed
    :rtype: DatabaseChangedResponse
    """
    first_changed: bool = __regenerate_over_correlating()
    second_changed: bool = __regenerate_correlation_values()
    changed: bool = first_changed or second_changed
    return DatabaseChangedResponse(success=True, database_changed=changed)


def __regenerate_correlation_values() -> bool:
    """
    Method to regenerate the amount of correlations for the values with correlations.
    :return: if the database was changed
    :rtype: bool
    """
    changed: bool = False
    correlation_values: list[str] = correlation_worker.misp_sql.get_values_with_correlation()
    for value in correlation_values:
        count: int = correlation_worker.misp_sql.get_number_of_correlations(value, False)
        current_attributes: list[MispSQLEventAttribute] = (
            correlation_worker.misp_sql.get_attributes_with_same_value(value))
        current_count: int = get_amount_of_possible_correlations(current_attributes)
        if current_count > correlation_worker.threshold:
            correlation_worker.misp_sql.delete_correlations(value)
            correlation_worker.misp_sql.add_over_correlating_value(value, current_count)
            changed = True
        elif current_count != count:
            correlation_worker.misp_sql.delete_correlations(value)
            correlate_value(value)
            changed = True
        elif current_count == count == 0:
            correlation_worker.misp_sql.delete_correlations(value)
            changed = True
    return changed


def __regenerate_over_correlating() -> bool:
    """
    Method to regenerate the amount of correlations for the over correlating values.
    :return: if the database was changed
    :rtype: bool
    """
    changed: bool = False
    over_correlating_values: list[tuple[str, int]] = correlation_worker.misp_sql.get_over_correlating_values()
    for entry in over_correlating_values:
        value: str = entry[0]
        count: int = entry[1]

        current_attributes: list[MispSQLEventAttribute] = (
            correlation_worker.misp_sql.get_attributes_with_same_value(value))
        current_count: int = get_amount_of_possible_correlations(current_attributes)

        if current_count != count and current_count > correlation_worker.threshold:
            correlation_worker.misp_sql.add_over_correlating_value(value, current_count)
            changed = True
        elif current_count == count:
            continue
        elif current_count <= correlation_worker.threshold:
            correlation_worker.misp_sql.delete_over_correlating_value(value)
            correlate_value(value)
            changed = True
    return changed
