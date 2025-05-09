from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.email.alert_email_job import AlertEmailData, alert_email_job
from mmisp.worker.jobs.email.contact_email_job import ContactEmailData, contact_email_job
from mmisp.worker.jobs.email.posts_email_job import PostsEmailData, posts_email_job

from .queue import queue


@job_router.post("/postsEmail", dependencies=[Depends(verified)])
async def create_posts_email_job(user: UserData, data: PostsEmailData) -> CreateJobResponse:
    """
    Creates a posts_email_job

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the posts_email_job
    :type data: PostsEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    async with queue:
        return await job_controller.create_job(queue, posts_email_job, user, data)


@job_router.post("/alertEmail", dependencies=[Depends(verified)])
async def create_alert_email_job(user: UserData, data: AlertEmailData) -> CreateJobResponse:
    """
    Creates an alert_email_job

    :param user: user who called the method (not used)
    :type user: UserData
    :param data: contains the data to run the alert_email_job
    :type data: AlertEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    async with queue:
        return await job_controller.create_job(queue, alert_email_job, user, data)


@job_router.post("/contactEmail", dependencies=[Depends(verified)])
async def create_contact_email_job(user: UserData, data: ContactEmailData) -> CreateJobResponse:
    """
    Creates a contact_email_job

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the contact_email_job
    :type data: ContactEmailData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    async with queue:
        return await job_controller.create_job(queue, contact_email_job, user, data)
