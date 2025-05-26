import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from tests.with_remote_misp_only.system_tests.sync.test_sync_helper import check_status


@pytest.mark.asyncio
async def test_pull_full(client, site_admin_user, authorization_headers, remote_misp, pull_job_remote_event):
    user_data: UserData = UserData(user_id=site_admin_user.id)
    data_full: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)
    response: CreateJobResponse = client.post(
        "/job/pull", headers=authorization_headers, json={"user": user_data.dict(), "data": data_full.dict()}
    ).json()
    create_response: CreateJobResponse = CreateJobResponse.model_validate(response)
    job_id = await check_status(client, create_response, authorization_headers)
    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    job_result: PullResult = PullResult.model_validate(response)
    assert job_result.successes == 1
    assert job_result.fails == 0
    assert job_result.pulled_proposals == 0
    assert job_result.pulled_sightings == 0
    assert job_result.pulled_clusters == 0
