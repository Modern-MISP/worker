from time import sleep

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app


@celery_app.task
def test_job(user: UserData):
    sleep(15)
