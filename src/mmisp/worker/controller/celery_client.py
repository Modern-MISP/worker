"""
Module implements the Celery Application.
"""

import os
from typing import Any, Set

from celery import Celery, Task
from celery.signals import before_task_publish, celeryd_after_setup

# from celery.worker.control import ControlDispatch
from celery.worker.consumer import Consumer  # type: ignore
from celery.worker.control import control_command  # type: ignore

import mmisp.db.all_models  # noqa
from mmisp.worker.api.requests_schemas import WorkerEnum
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
        "mmisp.worker.jobs.taxonomy.*": {"queue": WorkerEnum.IMPORT_TAXONOMIES.value},
        "mmisp.worker.jobs.object_template.*": {"queue": WorkerEnum.IMPORT_OBJECT_TEMPLATES.value},
        "mmisp.worker.jobs.galaxy.*": {"queue": WorkerEnum.IMPORT_GALAXIES.value},
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
        "mmisp.worker.jobs.taxonomy.import_taxonomies_job",
        "mmisp.worker.jobs.object_template.import_object_templates_job",
        "mmisp.worker.jobs.galaxy.import_galaxies_job",
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
def worker_start(sender, instance, **kwargs):  # noqa
    print(type(instance))
    set_worker_queues_to_default(instance.app)


def get_wanted_queues_by_env() -> Set[str]:
    all_queue_string = "_".join(q.value for q in WorkerEnum)
    env_queues = os.environ.get("QUEUES", all_queue_string)
    if env_queues == "all":
        env_queues = all_queue_string

    return set(env_queues.split("_"))


def set_worker_queues_to_default(app: Celery) -> None:
    selected_queues = get_wanted_queues_by_env()

    for q in WorkerEnum:
        if q.value in selected_queues:
            print("add queue to worker:", q.value)
            app.amqp.queues.select_add(q.value)  # type: ignore


@control_command()
def reset_worker_queues(cp: Any, **kwargs) -> None:
    set_worker_queues_to_default_from_consumer(cp.consumer)


@control_command()
def pause_consume_from_all_queues(cp: Any, **kwargs) -> None:
    for q in WorkerEnum:
        print("remove queue from worker:", q.value)
        cp.consumer.cancel_task_queue(q.value)


def set_worker_queues_to_default_from_consumer(consumer: Consumer) -> None:
    selected_queues = get_wanted_queues_by_env()

    for q in WorkerEnum:
        if q.value in selected_queues:
            print("add queue to worker:", q.value)
            consumer.add_task_queue(q.value)
