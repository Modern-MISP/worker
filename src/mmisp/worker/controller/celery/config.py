import os
from dotenv import load_dotenv

load_dotenv()


class CeleryConfig:
    broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://172.17.0.2:12482/0")
    result_backend: str = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:9443/0")
    task_routes: dict = {}
    include: list[str] = ['worker.jobs']
    task_track_started = True


celery_config = CeleryConfig()
