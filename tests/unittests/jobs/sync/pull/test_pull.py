import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullTechniqueEnum, PullResult
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


@pytest.mark.asyncio
async def test_pull_add_event_full(init_api_config, misp_api, remote_site_admin_user, remote_misp, remote_event):
    server_id: int = remote_misp.id
    server: Server = await misp_api.get_server(server_id)

    user_data: UserData = UserData(user_id=remote_site_admin_user.id)
    pull_data: PullData = PullData(server_id=server_id, technique=PullTechniqueEnum.FULL)

    pull_result: PullResult = pull_job(user_data, pull_data)
    assert pull_result.fails == 0
    assert pull_result.successes == 1

    # if event wasn't pulled to local-server it throws Exception
    await misp_api.get_event(UUID(remote_event.uuid))
    # TODO: Compare events?


@pytest.mark.asyncio
async def test_pull_add_event_incremental(init_api_config, misp_api, user, remote_misp, remote_event):
    assert False
    # TODO: Implement this test correctly

    server_id: int = remote_misp.id
    server: Server = await misp_api.get_server(server_id)

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=server_id, technique=PullTechniqueEnum.INCREMENTAL)

    pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await misp_api.get_event(UUID(remote_event.uuid))


@pytest.mark.asyncio
async def test_pull_edit_event_full(init_api_config, misp_api):
    assert False
    # create new event
    server: Server = await misp_api.get_server(1)
    new_event: AddEditGetEventDetails = get_new_event()
    assert misp_api.save_event(new_event, server)

    user_data: UserData = UserData(user_id=52)
    pull_data: PullData = PullData(server_id=1, technique="full")

    pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await misp_api.get_event(UUID(new_event.uuid))

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert misp_api.update_event(new_event, server)

    pull_job(user_data, pull_data)

    # tests if event was updated on local-server
    remote_event: AddEditGetEventDetails = misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info


@pytest.mark.asyncio
async def test_pull_edit_event_incremental(init_api_config, misp_api):
    assert False
    # create new event
    server: Server = await misp_api.get_server(1)
    new_event: AddEditGetEventDetails = get_new_event()
    assert misp_api.save_event(new_event, server)

    user_data: UserData = UserData(user_id=52)
    pull_data: PullData = PullData(server_id=1, technique="full")

    pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await misp_api.get_event(UUID(new_event.uuid))

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert misp_api.update_event(new_event, server)

    pull_job(user_data, pull_data)

    # tests if event was updated on local-server
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info


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
