import os

from mmisp.worker.api.worker_router.input_data import WorkerEnum


class CeleryConfig:
    """
    Encapsulates configuration for Celery.
    """

    broker_url: str = 'redis://localhost:6379/0'
    broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend: str = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    task_routes: dict = {'mmisp.worker.jobs.correlation.*': WorkerEnum.CORRELATE.value,
                         'mmisp.worker.jobs.enrichment.*': WorkerEnum.ENRICHMENT.value,
                         'mmisp.worker.jobs.email.*': WorkerEnum.SEND_EMAIL.value,
                         'mmisp.worker.jobs.processfreetext.*': WorkerEnum.PROCESS_FREE_TEXT.value,
                         'mmisp.worker.jobs.pull.*': WorkerEnum.PULL.value,
                         'mmisp.worker.jobs.push.*': WorkerEnum.PUSH.value}
    include: list[str] = ['mmisp.worker.jobs']
    task_track_started = True
