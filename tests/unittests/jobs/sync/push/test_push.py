import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.jobs.sync.push.push_worker import push_worker
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


@pytest.mark.asyncio
async def test_push_add_event_full():
    new_event: AddEditGetEventDetails = get_new_event()
    assert push_worker.misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="full")

    await push_job(user_data, push_data)

    server: Server = await push_worker.misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await push_worker.misp_api.get_event(UUID(new_event.uuid), server)


@pytest.mark.asyncio
async def test_push_add_event_incremental():
    new_event: AddEditGetEventDetails = get_new_event()
    assert push_worker.misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="incremental")

    await push_job(user_data, push_data)

    server: Server = await push_worker.misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await push_worker.misp_api.get_event(UUID(new_event.uuid), server)


@pytest.mark.asyncio
async def test_push_edit_event_full():
    # create new event
    new_event: AddEditGetEventDetails = get_new_event()
    assert push_worker.misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="full")

    await push_job(user_data, push_data)

    server: Server = await push_worker.misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await push_worker.misp_api.get_event(UUID(new_event.uuid), server)

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert push_worker.misp_api.update_event(new_event, server)

    await push_job(user_data, push_data)

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = push_worker.misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info


@pytest.mark.asyncio
async def test_push_edit_event_incremental():
    # create new event
    new_event: AddEditGetEventDetails = get_new_event()
    assert push_worker.misp_api.save_event(new_event)

    user_data: UserData = UserData(user_id=52)
    push_data: PushData = PushData(server_id=1, technique="incremental")

    await push_job(user_data, push_data)

    server: Server = await push_worker.misp_api.get_server(1)

    # if event wasn't pushed to remote-server it throws Exception
    await push_worker.misp_api.get_event(UUID(new_event.uuid), server)

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert push_worker.misp_api.update_event(new_event, server)

    await push_job(user_data, push_data)

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = push_worker.misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info
