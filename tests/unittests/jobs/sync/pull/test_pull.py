import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from mmisp.worker.jobs.sync.pull.pull_worker import pull_worker
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


@pytest.mark.asyncio
async def test_pull_add_event_full():
    server: Server = await pull_worker.misp_api.get_server(1)
    new_event: AddEditGetEventDetails = get_new_event()
    assert pull_worker.misp_api.save_event(new_event, server)

    user_data: UserData = UserData(user_id=52)
    pull_data: PullData = PullData(server_id=1, technique="full")

    await pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await pull_worker.misp_api.get_event(UUID(new_event.uuid))


@pytest.mark.asyncio
async def test_pull_add_event_incremental():
    server: Server = await pull_worker.misp_api.get_server(1)
    new_event: AddEditGetEventDetails = get_new_event()
    assert pull_worker.misp_api.save_event(new_event, server)

    user_data: UserData = UserData(user_id=52)
    pull_data: PullData = PullData(server_id=1, technique="full")

    await pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await pull_worker.misp_api.get_event(UUID(new_event.uuid))


@pytest.mark.asyncio
async def test_pull_edit_event_full():
    # create new event
    server: Server = await pull_worker.misp_api.get_server(1)
    new_event: AddEditGetEventDetails = get_new_event()
    assert pull_worker.misp_api.save_event(new_event, server)

    user_data: UserData = UserData(user_id=52)
    pull_data: PullData = PullData(server_id=1, technique="full")

    pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await pull_worker.misp_api.get_event(UUID(new_event.uuid))

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert pull_worker.misp_api.update_event(new_event, server)

    pull_job(user_data, pull_data)

    # tests if event was updated on local-server
    remote_event: AddEditGetEventDetails = pull_worker.misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info


@pytest.mark.asyncio
async def test_pull_edit_event_incremental():
    # create new event
    server: Server = await pull_worker.misp_api.get_server(1)
    new_event: AddEditGetEventDetails = get_new_event()
    assert pull_worker.misp_api.save_event(new_event, server)

    user_data: UserData = UserData(user_id=52)
    pull_data: PullData = PullData(server_id=1, technique="full")

    pull_job(user_data, pull_data)

    # if event wasn't pulled to local-server it throws Exception
    await pull_worker.misp_api.get_event(UUID(new_event.uuid))

    sleep(5)
    # edit event
    new_event.info = "edited" + new_event.info
    new_event.timestamp = str(int(time.time()))
    new_event.publish_timestamp = str(int(time.time()))
    assert pull_worker.misp_api.update_event(new_event, server)

    pull_job(user_data, pull_data)

    # tests if event was updated on local-server
    remote_event: AddEditGetEventDetails = await pull_worker.misp_api.get_event(UUID(new_event.uuid))
    assert remote_event.info == new_event.info
