import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullTechniqueEnum, PullResult
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from tests.with_remote_misp_only.conftest import remote_event


@pytest.mark.asyncio
async def test_pull_add_event_full(init_api_config, misp_api, user, remote_misp, remote_event):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    pull_result: PullResult = await pull_job.delay(user_data, pull_data).get()
    assert pull_result.fails == 0
    assert pull_result.successes == 1

    assert remote_event.uuid == (await misp_api.get_event(UUID(remote_event.uuid))).uuid


@pytest.mark.asyncio
async def test_pull_add_event_incremental(init_api_config, misp_api, user, remote_misp, remote_event):
    # TODO: Implement this test correctly

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.INCREMENTAL)

    pull_result: PullResult = await pull_job.delay(user_data, pull_data).get()
    assert pull_result.fails == 0
    assert pull_result.successes == 1

    assert remote_event.uuid == (await misp_api.get_event(UUID(remote_event.uuid))).uuid


@pytest.mark.asyncio
async def test_pull_edit_event_full(init_api_config, misp_api, remote_event, user, remote_misp,
                                    remote_db):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    await pull_job.delay(user_data, pull_data).get()

    assert remote_event.uuid == (await misp_api.get_event(UUID(remote_event.uuid))).uuid

    sleep(5)

    # edit event
    remote_event.info = "edited" + remote_event.info

    remote_event.timestamp = str(int(time.time()))
    remote_event.publish_timestamp = str(int(time.time()))

    await remote_db.commit()

    await pull_job.delay(user_data, pull_data).get()

    # tests if event was updated on local-server
    new_event: AddEditGetEventDetails = misp_api.get_event(UUID(remote_event.uuid))
    assert new_event.info == remote_event.old_info
    assert new_event.timestamp == remote_event.timestamp
    assert new_event.publish_timestamp == remote_event.publish_timestamp


@pytest.mark.asyncio
async def test_pull_edit_event_incremental(init_api_config, misp_api, remote_event, user, remote_db,
                                           remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.INCREMENTAL)

    await pull_job.delay(user_data, pull_data).get()

    assert remote_event.uuid == (await misp_api.get_event(UUID(remote_event.uuid))).uuid

    sleep(5)

    # edit event
    remote_event.info = "edited" + remote_event.info

    remote_event.timestamp = str(int(time.time()))
    remote_event.publish_timestamp = str(int(time.time()))

    await remote_db.commit()

    await pull_job.delay(user_data, pull_data).get()

    # tests if event was updated on local-server
    new_event: AddEditGetEventDetails = misp_api.get_event(UUID(remote_event.uuid))
    assert new_event.info == remote_event.old_info
    assert new_event.timestamp == remote_event.timestamp
    assert new_event.publish_timestamp == remote_event.publish_timestamp


'''
Fixtures we need to implement:
1. user -done
2. galaxyCluster -done
3. event -done
4. proposal -done
5. sightings -done
'''

'''
Testcase which we need to implement
1. User who starts the test is user.role.perm_site_admin
2. User who starts the test is not user.role.perm_site_admin
'''
