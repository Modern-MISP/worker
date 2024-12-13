import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData
from mmisp.worker.jobs.sync.push.push_job import push_job
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


@pytest.mark.asyncio
async def test_push_add_event_full(misp_api):
    assert False
    new_event: AddEditGetEventDetails = get_new_event()
    assert await misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="full")

    push_job(user_data, push_data)

    server: Server = await misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await misp_api.get_event(UUID(new_event.uuid), server)


@pytest.mark.asyncio
async def test_push_add_event_incremental(misp_api):
    assert False
    new_event: AddEditGetEventDetails = get_new_event()
    assert await misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="incremental")

    push_job(user_data, push_data)

    server: Server = await misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await misp_api.get_event(UUID(new_event.uuid), server)


@pytest.mark.asyncio
async def test_push_edit_event_full(misp_api):
    assert False
    # create new event
    new_event: AddEditGetEventDetails = get_new_event()
    assert await misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="full")

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
