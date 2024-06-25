from celery import Celery, Task
from celery.signals import after_task_publish

from mmisp.worker.config.config_data import ENV_PREFIX
from mmisp.worker.controller.celery_client.celery_config import CeleryConfig

"""
Module implements the Celery Application.
"""

_CELERY_NAMESPACE: str = f"{ENV_PREFIX}"
"""Prefix for Celery Environment Variables"""

JOB_CREATED_STATE: str = "ENQUEUED"
"""Custom Celery task state for enqueued tasks."""

celery_app = Celery(backend=CeleryConfig.result_backend, broker=CeleryConfig.broker_url)
"""The celery instance"""

celery_app.config_from_object(CeleryConfig, force=False, namespace=_CELERY_NAMESPACE)
"""Configures the celery instance"""


@after_task_publish.connect
def update_sent_state(sender: Task = None, headers: dict = None, **kwargs) -> None:
    """
    Function sets a custom task state for enqueued tasks.
    :param sender: The name of the task to update its state.
    :type sender: celery.Task
    :param headers: The task message headers
    :type headers: dict
    :param kwargs: Not needed
    """

    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = celery_app.tasks.get(sender)
    backend = task.backend if task else celery_app.backend
    backend.store_result(headers["id"], None, JOB_CREATED_STATE)
