from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.sync.pull.pull_job import pull_job


@pytest.mark.asyncio
async def test_pull_add_event_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_event):
    event_uuid: str = pull_job_remote_event.uuid

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.successes == 1

    pulled_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event_uuid))
    assert event_uuid == pulled_event.uuid
    assert pulled_event.locked


# TODO: Implement
# @pytest.mark.asyncio
# async def test_pull_add_event_incremental(init_api_config, misp_api, user, remote_misp, remote_event):
#     assert False, "Incremental pull technique does not yet work correctly"
#
#     user_data: UserData = UserData(user_id=user.id)
#     pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.INCREMENTAL)
#
#     pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
#     assert pull_result.fails == 0
#     assert pull_result.successes == 1
#
#     assert remote_event.uuid == (await misp_api.get_event(UUID(remote_event.uuid))).uuid


@pytest.mark.asyncio
async def test_pull_edit_event_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_event):
    event_uuid: str = pull_job_remote_event.uuid

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    pull_job.delay(user_data, pull_data).get()
    await db.commit()

    # Assert event saved locally
    assert event_uuid == (await misp_api.get_event(UUID(event_uuid))).uuid

    remote_event_from_api: AddEditGetEventDetails = await misp_api.get_event(UUID(event_uuid), remote_misp)

    updated_info: str = "edited_" + pull_job_remote_event.info

    remote_event_from_api.info = updated_info
    remote_event_from_api.timestamp = None
    assert await misp_api.update_event(remote_event_from_api, remote_misp)

    remote_event_from_api = await misp_api.get_event(UUID(event_uuid), remote_misp)
    assert remote_event_from_api.info == updated_info

    pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.successes == 1

    pulled_event = await misp_api.get_event(UUID(event_uuid))
    assert pulled_event.info == updated_info


# TODO: Implement
# @pytest.mark.asyncio
# async def test_pull_edit_event_incremental(init_api_config, misp_api, remote_event, user, remote_db, remote_misp):
#     assert False, "Incremental pull technique does not yet work correctly"
#     user_data: UserData = UserData(user_id=user.id)
#     pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.INCREMENTAL)
#
#     pull_job.delay(user_data, pull_data).get()
#
#     assert remote_event.uuid == (await misp_api.get_event(UUID(remote_event.uuid))).uuid
#
#     sleep(5)
#
#     # edit event
#     remote_event.info = "edited" + remote_event.info
#
#     remote_event.timestamp = str(int(time.time()))
#     remote_event.publish_timestamp = str(int(time.time()))
#
#     await remote_db.commit()
#
#     pull_job.delay(user_data, pull_data).get()
#
#     # tests if event was updated on local-server
#     new_event: AddEditGetEventDetails = misp_api.get_event(UUID(remote_event.uuid))
#     assert new_event.info == remote_event.old_info
#     assert new_event.timestamp == remote_event.timestamp
#     assert new_event.publish_timestamp == remote_event.publish_timestamp


# TODO:#1. User who starts the test is user.role.perm_site_admin

"""
Testcase which we need to implement
1. User who starts the test is user.role.perm_site_admin
2. User who starts the test is not user.role.perm_site_admin
"""
