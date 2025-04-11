import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.api.response_schemas import CreateJobResponse
from mmisp.worker.jobs.sync.push.job_data import PushData, PushTechniqueEnum, PushResult
from ..test_sync_helper import check_status


@pytest.mark.asyncio
async def test_push_full(client, authorization_headers, site_admin_user, remote_misp, set_server_version,
                         sync_test_event, misp_api):
    user_data: UserData = UserData(user_id=site_admin_user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)
    response = client.post("/job/push", headers=authorization_headers,
                           json={'user': user_data.dict(), 'data': push_data.dict()}).json()

    create_response: CreateJobResponse = CreateJobResponse.parse_obj(response)
    job_id = await check_status(client, create_response, authorization_headers)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    job_result: PushResult = PushResult.parse_obj(response)

    assert job_result.success == 1

    pushed_event = await misp_api.get_event(sync_test_event.uuid, remote_misp)
    assert pushed_event.uuid == sync_test_event.uuid

    attributes = await misp_api.get_event_attributes(pushed_event.id, remote_misp)

    assert len(attributes) == sync_test_event.attribute_count


@pytest.mark.asyncio
async def test_push_incremental(client, authorization_headers, site_admin_user, remote_misp, set_server_version,
                                sync_test_event, misp_api):
    user_data: UserData = UserData(user_id=site_admin_user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)
    response = client.post("/job/push", headers=authorization_headers,
                           json={'user': user_data.dict(), 'data': push_data.dict()}).json()

    create_response: CreateJobResponse = CreateJobResponse.parse_obj(response)
    job_id = await check_status(client, create_response, authorization_headers)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    job_result: PushResult = PushResult.parse_obj(response)

    assert job_result.success == 1

    pushed_event = await misp_api.get_event(sync_test_event.uuid, remote_misp)
    assert pushed_event.uuid == sync_test_event.uuid

    attributes = await misp_api.get_event_attributes(pushed_event.id, remote_misp)

    assert len(attributes) == sync_test_event.attribute_count
