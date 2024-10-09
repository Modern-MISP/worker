from fastapi import Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.api.job_router.job_router import job_router
from mmisp.worker.api.job_router.response_data import CreateJobResponse
from mmisp.worker.controller import job_controller
from mmisp.worker.jobs.sync.pull.job_data import PullData
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from mmisp.worker.jobs.sync.push.job_data import PushData
from mmisp.worker.jobs.sync.push.push_job import push_job


@job_router.post("/pull", dependencies=[Depends(verified)])
def create_pull_job(user: UserData, data: PullData) -> CreateJobResponse:
    """
    Creates a pull_job

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the pull
    :type data: PullData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return job_controller.create_job(pull_job, user, data)


@job_router.post("/push", dependencies=[Depends(verified)])
def create_push_job(user: UserData, data: PushData) -> CreateJobResponse:
    """
    Creates a push_job

    :param user: user who called the method
    :type user: UserData
    :param data: contains the data to run the push
    :type data: PushData
    :return: the response to indicate if the creation was successful
    :rtype: CreateJobResponse
    """
    return job_controller.create_job(push_job, user, data)
