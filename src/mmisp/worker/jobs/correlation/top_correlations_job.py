import asyncio

from mmisp.db.database import sessionmanager
from mmisp.worker.api.requests_schemas import UserData
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
    return asyncio.run(_top_correlations_job(user))


async def _top_correlations_job(user: UserData) -> TopCorrelationsResponse:
    async with sessionmanager.session() as session:
        values: list[str] = await misp_sql.get_values_with_correlation(session)
        top_correlations: list[tuple[str, int]] = list()
        for value in values:
            count: int = await misp_sql.get_number_of_correlations(session, value, False)
            top_correlations.append((value, count))

        top_correlations = list(filter(lambda num: num[1] != 0, top_correlations))  # remove all 0s from the list
        top_correlations.sort(key=lambda a: a[1], reverse=True)  # sort by the second element of the tuple

        return TopCorrelationsResponse(success=True, top_correlations=top_correlations)
