from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.processfreetext_job import processfreetext_worker
from mmisp.worker.jobs.processfreetext_job.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


@celery_app.task
def processfreetext_job(user: UserData, data: ProcessFreeTextData) -> ProcessFreeTextResponse:
    pass


def __parse_attribute(attribute: str) -> AttributeType:
    pass


def __refang_input(input):
    pass
