import asyncio

from mmisp.worker.api.job_router.input_data import UserData
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
    changed: bool = False
    excluded: list[str] = asyncio.run(misp_sql.get_excluded_correlations())
    for value in excluded:
        if asyncio.run(misp_sql.delete_correlations(value)):
            changed = True
    return DatabaseChangedResponse(success=True, database_changed=changed)
