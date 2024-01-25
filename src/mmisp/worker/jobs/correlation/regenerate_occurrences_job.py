from mmisp.worker.controller.celery.celery import celery_app
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
    threshold: int = correlation_worker.get_threshold()

    first_changed: bool = __regenerate_over_correlating(threshold)
    second_changed: bool = __regenerate_correlation_values(threshold)
    changed: bool = first_changed or second_changed
    correlation_worker.threshold = 30
    return DatabaseChangedResponse(success=True, database_changed=changed)


def __regenerate_correlation_values(threshold) -> bool:
    changed: bool = False
    correlation_values: list[str] = correlation_worker.misp_sql.get_values_with_correlation()
    for value in correlation_values:
        count = correlation_worker.misp_sql.get_number_of_correlations(value, True)
        if count > threshold:
            correlation_worker.misp_sql.delete_correlations(value)
            correlation_worker.misp_sql.add_over_correlating_value(value, count)
            changed = True
    return changed


def __regenerate_over_correlating(threshold) -> bool:
    changed: bool = False
    over_correlating_values: list[tuple[str, int]] = correlation_worker.misp_sql.get_over_correlating_values()
    for entry in over_correlating_values:
        value: str = entry[0]
        count = correlation_worker.misp_sql.get_number_of_correlations(value, False)
        if count > threshold and count != entry[1]:
            correlation_worker.misp_sql.add_over_correlating_value(value, count)
            changed = True
        elif count <= threshold:
            correlation_worker.misp_sql.delete_over_correlating_value(value)
            correlate_value(correlation_worker.misp_sql, correlation_worker.misp_api, value)
            changed = True
    return changed
