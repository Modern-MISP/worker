from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import TopCorrelationsResponse


@celery_app.task
def top_correlations_job(user: UserData) -> TopCorrelationsResponse:
    """
    Method to get a list of all correlations with their occurrence in the database.
    The list is sorted decreasing by the occurrence.
    :param user: the user who requested the job
    :type user: UserData
    :return: TopCorrelationsResponse with the list and if the job was successful
    :rtype: TopCorrelationsResponse
    """
    values: list[str] = correlation_worker.misp_sql.get_values_with_correlation()
    numbers: list[int] = list()
    for value in values:
        count: int = correlation_worker.misp_sql.get_number_of_correlations(value, False)
        if count > 0:
            numbers.append(count)
        else:
            values.remove(value)
    top_correlations: list[tuple[str, int]] = list(zip(values, numbers))  # zip values and numbers together as tuple
    top_correlations.sort(key=lambda a: a[1], reverse=True)  # sort by the second element of the tuple
    return TopCorrelationsResponse(success=True, top_correlations=top_correlations)
