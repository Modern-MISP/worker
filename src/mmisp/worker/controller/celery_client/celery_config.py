import os

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.misp_database.mmisp_redis_config import mmisp_redis_config_data


class CeleryConfig:
    """
    Encapsulates configuration for Celery.
    """

    broker_url: str = os.environ.get(
        "CELERY_BROKER_URL",
        f"redis://{mmisp_redis_config_data.host}:{mmisp_redis_config_data.port}/" f"{mmisp_redis_config_data.db}",
    )
    result_backend: str = os.environ.get("CELERY_RESULT_BACKEND", broker_url)
    redis_username: str = os.environ.get("CELERY_REDIS_USERNAME", mmisp_redis_config_data.username)
    redis_password: str = os.environ.get("CELERY_REDIS_PASSWORD", mmisp_redis_config_data.password)
    task_routes: dict = {
        "mmisp.worker.jobs.correlation.*": WorkerEnum.CORRELATE.value,
        "mmisp.worker.jobs.enrichment.*": WorkerEnum.ENRICHMENT.value,
        "mmisp.worker.jobs.email.*": WorkerEnum.SEND_EMAIL.value,
        "mmisp.worker.jobs.processfreetext.*": WorkerEnum.PROCESS_FREE_TEXT.value,
        "mmisp.worker.jobs.sync.pull.*": WorkerEnum.PULL.value,
        "mmisp.worker.jobs.sync.push.*": WorkerEnum.PUSH.value,
    }
    imports: list[str] = [
        "mmisp.worker.jobs.enrichment.enrich_attribute_job",
        "mmisp.worker.jobs.enrichment.enrich_event_job",
        "mmisp.worker.jobs.correlation.clean_excluded_correlations_job",
        "mmisp.worker.jobs.correlation.correlate_value_job",
        "mmisp.worker.jobs.correlation.correlation_plugin_job",
        "mmisp.worker.jobs.correlation.regenerate_occurrences_job",
        "mmisp.worker.jobs.correlation.top_correlations_job",
        "mmisp.worker.jobs.email.alert_email_job",
        "mmisp.worker.jobs.email.contact_email_job",
        "mmisp.worker.jobs.email.posts_email_job",
        "mmisp.worker.jobs.processfreetext.processfreetext_job",
        "mmisp.worker.jobs.sync.pull.pull_job",
        "mmisp.worker.jobs.sync.push.push_job",
    ]
    task_track_started = True
    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "pickle"
    accept_content = ["pickle"]
