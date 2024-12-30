from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData
from mmisp.worker.jobs.debug.delayjob.delay_job import delayjob


@job_router.post("/delay")
def create_delay_job() -> CreateJobResponse:
    """
    Creates a process_free_text_job

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the process_free_text_job
    :type data: ProcessFreeTextData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return job_controller.create_job(delayjob)
