from streaq import WrappedContext

from mmisp.db.database import sessionmanager
from mmisp.lib.logger import get_jobs_logger
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.misp_database import misp_sql

from .queue import queue

db_logger = get_jobs_logger(__name__)


@queue.task()
async def clean_excluded_correlations_job(ctx: WrappedContext[None], user: UserData) -> DatabaseChangedResponse:
    """
    Task to clean the excluded correlations from the correlations of the MISP database.
    For every excluded value the correlations are removed.
    :param user: the user who requested the job
    :type user: UserData
    :return: if the job was successful and if the database was changed
    :rtype: DatabaseChangedResponse
    """
    assert sessionmanager is not None
    async with sessionmanager.session() as session:
        changed = False
        excluded = await misp_sql.get_excluded_correlations(session)
        for value in excluded:
            if await misp_sql.delete_correlations(session, value):
                changed = True
        return DatabaseChangedResponse(success=True, database_changed=changed)
