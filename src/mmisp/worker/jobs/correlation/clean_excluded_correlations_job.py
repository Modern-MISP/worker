import asyncio

from mmisp.db.database import sessionmanager
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.misp_database import misp_sql


@celery_app.task
def clean_excluded_correlations_job(user: UserData) -> DatabaseChangedResponse:
    """
    Task to clean the excluded correlations from the correlations of the MISP database.
    For every excluded value the correlations are removed.
    :param user: the user who requested the job
    :type user: UserData
    :return: if the job was successful and if the database was changed
    :rtype: DatabaseChangedResponse
    """

    return asyncio.run(_clean_excluded_correlations_job(user))


async def _clean_excluded_correlations_job(user: UserData) -> DatabaseChangedResponse:
    async with sessionmanager.session() as session:
        changed: bool = False
        excluded: list[str] = await misp_sql.get_excluded_correlations(session)
        for value in excluded:
            if await misp_sql.delete_correlations(session, value):
                changed = True
        return DatabaseChangedResponse(success=True, database_changed=changed)
