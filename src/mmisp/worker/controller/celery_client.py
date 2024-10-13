"""
Module implements the Celery Application.
"""

import os
from typing import Any

from celery import Celery, Task
from celery.signals import before_task_publish, celeryd_after_setup

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.config import ENV_PREFIX
from mmisp.worker.misp_database.mmisp_redis_config import mmisp_redis_config_data


class CeleryConfig:
    """
    Encapsulates configuration for Celery.
    """

    broker_url: str = os.environ.get(
        "CELERY_BROKER_URL",
        (
            f"redis://"
            f"{':' + mmisp_redis_config_data.password + '@' if mmisp_redis_config_data.password else ''}"
            f"{mmisp_redis_config_data.host}:{mmisp_redis_config_data.port}/{mmisp_redis_config_data.db}"
        ),
    )
    result_backend: str = os.environ.get("CELERY_RESULT_BACKEND", broker_url)
    redis_username: str = os.environ.get("CELERY_REDIS_USERNAME", mmisp_redis_config_data.username)
    redis_password: str = os.environ.get("CELERY_REDIS_PASSWORD", mmisp_redis_config_data.password)
    task_routes: dict = {
        "mmisp.worker.jobs.correlation.*": {"queue": WorkerEnum.CORRELATE.value},
        "mmisp.worker.jobs.enrichment.*": {"queue": WorkerEnum.ENRICHMENT.value},
        "mmisp.worker.jobs.email.*": {"queue": WorkerEnum.SEND_EMAIL.value},
        "mmisp.worker.jobs.processfreetext.*": {"queue": WorkerEnum.PROCESS_FREE_TEXT.value},
        "mmisp.worker.jobs.sync.pull.*": {"queue": WorkerEnum.PULL.value},
        "mmisp.worker.jobs.sync.push.*": {"queue": WorkerEnum.PUSH.value},
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


_CELERY_NAMESPACE: str = f"{ENV_PREFIX}"
"""Prefix for Celery Environment Variables"""

JOB_CREATED_STATE: str = "ENQUEUED"
"""Custom Celery task state for enqueued tasks."""

celery_app: Celery = Celery(backend=CeleryConfig.result_backend, broker=CeleryConfig.broker_url)
"""The celery instance"""

celery_app.config_from_object(CeleryConfig, force=False, namespace=_CELERY_NAMESPACE)
"""Configures the celery instance"""


@before_task_publish.connect
def update_sent_state(sender: Task | str | None = None, headers: dict | None = None, **kwargs) -> None:
    """
    Function sets a custom task state for enqueued tasks.
    :param sender: The name of the task to update its state.
    :type sender: celery.Task
    :param headers: The task message headers
    :type headers: dict
    :param kwargs: Not needed
    """
    if headers is None:
        raise ValueError("invalid headers")

    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    backend: Any
    if sender is None:
        backend = celery_app.backend
    else:
        if isinstance(sender, str):
            task = celery_app.tasks.get(sender)
        else:
            task = celery_app.tasks.get(sender.name)
        backend = task.backend if task else celery_app.backend
    backend.store_result(headers["id"], None, JOB_CREATED_STATE)


@celeryd_after_setup.connect
def worker_start(_, instance, **kwargs):  # noqa
    if len(instance.app.amqp.queues) == 1:
        # worker is setup using only the default queues, subscribe to all queues
        for q in WorkerEnum:
            instance.app.amqp.queues.select_add(q.value)
