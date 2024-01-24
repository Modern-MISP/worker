from celery import Celery

from .config import celery_config

CELERY_NAMESPACE: str = "MMISP"

celery_app = Celery()
celery_app.config_from_object(celery_config, force=False, namespace=CELERY_NAMESPACE)