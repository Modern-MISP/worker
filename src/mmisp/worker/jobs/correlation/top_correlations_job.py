from mmisp.worker.controller.celery_app.celery_app import celery_app
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import TopCorrelationsResponse


@celery_app.task
def top_correlations_job() -> TopCorrelationsResponse:
    """
    Method to get a list of all correlations with their occurrence in the database.
    The list is sorted decreasing by the occurrence.
    :return: TopCorrelationsResponse with the list and if the job was successful
    :rtype: TopCorrelationsResponse
    """
    values: list[str] = correlation_worker.misp_sql.get_values_with_correlation()
    numbers: list[int] = list()
    for value in values:
        numbers.append(correlation_worker.misp_sql.get_number_of_correlations(value, True))
    top_correlations: list[tuple[str, int]] = list(zip(values, numbers))
    top_correlations.sort(key=lambda a: a[1], reverse=True)
    return TopCorrelationsResponse(success=True, top_correlations=top_correlations)
