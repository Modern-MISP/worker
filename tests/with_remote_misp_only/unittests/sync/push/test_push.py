import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData, PushTechniqueEnum, PushResult
from mmisp.worker.jobs.sync.push.push_job import push_job, _push_job
from tests.with_remote_misp_only.unittests.sync.test_sync_helper import get_new_event


@pytest.mark.asyncio
async def test_push_add_event_full(misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = await _push_job(user_data, push_data)
    assert push_result.success == True

    server: Server = await misp_api.get_server(remote_misp.id)

    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid


@pytest.mark.asyncio
async def test_push_add_event_incremental(misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    push_result: PushResult = await _push_job(user_data, push_data)
    assert push_result.success == True

    server: Server = await misp_api.get_server(remote_misp.id)

    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid


@pytest.mark.asyncio
async def test_push_edit_event_full(db, misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = await _push_job(user_data, push_data)
    assert push_result.success == True

    server: Server = await misp_api.get_server(remote_misp.id)

    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid

    sleep(5)
    # edit event
    event.info = "edited" + event.info
    event.timestamp = str(int(time.time()))
    event.publish_timestamp = str(int(time.time()))
    db.commit()

    push_job(user_data, push_data)

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event.uuid))
    assert remote_event.info == event.info


@pytest.mark.asyncio
async def test_push_edit_event_incremental(misp_api):
    assert False
    # create new event
    new_event: AddEditGetEventDetails = get_new_event()
    assert await misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="incremental")

    push_job(user_data, push_data)

    server: Server = await misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await misp_api.get_event(UUID(new_event.uuid), server)

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert misp_api.update_event(new_event, server)

    push_job(user_data, push_data)

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info
