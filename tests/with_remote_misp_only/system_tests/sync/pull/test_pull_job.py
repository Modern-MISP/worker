from asyncio import sleep

import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import JobStatusEnum, CreateJobResponse, JobStatusResponse
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullTechniqueEnum, PullResult


@pytest.mark.asyncio
async def test_pull_full(client, site_admin_user, authorization_headers, remote_misp, pull_job_remote_event):
    user_data: UserData = UserData(user_id=site_admin_user.id)
    data_full: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)
    response: CreateJobResponse = client.post("/job/pull", headers=authorization_headers,
                                              json={'user': user_data.dict(), 'data': data_full.dict()}).json()
    print(f"response: {response}")
    create_response: CreateJobResponse = CreateJobResponse.parse_obj(response)
    job_id = await check_status(client, create_response, authorization_headers)
    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    job_result: PullResult = PullResult.parse_obj(response)
    assert job_result.successes == 1
    assert job_result.fails == 0
    assert job_result.pulled_proposals == 0
    assert job_result.pulled_sightings == 0
    assert job_result.pulled_clusters == 0


async def check_status(client, response: CreateJobResponse, authorization_headers) -> str:
    job_id: str = response.job_id
    assert response.success
    ready: bool = False
    count: float = 0
    times: int = 0
    timer: float = 0.5
    while not ready:
        request = client.get(f"/job/{job_id}/status", headers=authorization_headers)
        response: JobStatusResponse = JobStatusResponse.parse_obj(request.json())

        assert request.status_code == 200

        if response.status == JobStatusEnum.SUCCESS:
            assert response.message == "Job is finished"
            return job_id
        assert response.status != JobStatusEnum.FAILED, response.message

        times += 1
        count += timer
        if times % 10 == 0 and times != 0:
            timer *= 2
        await sleep(timer)
    return job_id
