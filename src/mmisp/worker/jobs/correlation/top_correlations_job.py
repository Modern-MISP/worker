import asyncio

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.correlation.job_data import TopCorrelationsResponse
from mmisp.worker.misp_database import misp_sql


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
    values: list[str] = asyncio.run(misp_sql.get_values_with_correlation())
    top_correlations: list[tuple[str, int]] = list()
    for value in values:
        count: int = asyncio.run(misp_sql.get_number_of_correlations(value, False))
        top_correlations.append((value, count))

    top_correlations = list(filter(lambda num: num[1] != 0, top_correlations))  # remove all 0s from the list
    top_correlations.sort(key=lambda a: a[1], reverse=True)  # sort by the second element of the tuple

    return TopCorrelationsResponse(success=True, top_correlations=top_correlations)
