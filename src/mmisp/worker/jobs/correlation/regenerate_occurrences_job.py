from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse


@celery_app.task
def regenerate_occurrences_job() -> DatabaseChangedResponse:
    """
    Method to regenerate the occurrences of the correlations in the database.
    Over correlating values and values with correlations are checked.
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
        count = correlation_worker.misp_sql.get_number_of_correlations(value, True)
        if count > correlation_worker.threshold:
            correlation_worker.misp_sql.delete_correlations(value)
            correlation_worker.misp_sql.add_over_correlating_value(value, count)
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
        count = correlation_worker.misp_sql.get_number_of_correlations(value, False)
        if count > correlation_worker.threshold and count != entry[1]:
            correlation_worker.misp_sql.add_over_correlating_value(value, count)
            changed = True
        elif count <= correlation_worker.threshold:
            correlation_worker.misp_sql.delete_over_correlating_value(value)
            correlate_value(value)
            changed = True
    return changed
