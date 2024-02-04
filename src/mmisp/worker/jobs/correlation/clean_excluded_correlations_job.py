from mmisp.worker.controller.celery_app.celery_app import celery_app
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse


@celery_app.task
def clean_excluded_correlations_job() -> DatabaseChangedResponse:
    """
    Task to clean the excluded correlations from the correlations of the MISP database.
    For every excluded value the correlations are removed.
    :return: if the job was successful and if the database was changed
    :rtype: DatabaseChangedResponse
    """
    changed: bool = False
    excluded: list[str] = correlation_worker.misp_sql.get_excluded_correlations()
    for value in excluded:
        if correlation_worker.misp_sql.delete_correlations(value):
            changed = True
    return DatabaseChangedResponse(success=True, database_changed=changed)
