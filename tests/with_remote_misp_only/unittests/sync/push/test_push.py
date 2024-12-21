import time
from time import sleep
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData, PushTechniqueEnum, PushResult
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.misp_database.misp_sql import get_server


@pytest.mark.asyncio
async def test_push_add_event_full(init_api_config, db, misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = await push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)
    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid


@pytest.mark.asyncio
async def test_push_add_event_incremental(init_api_config, db, misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    push_result: PushResult = await push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)
    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid


@pytest.mark.asyncio
async def test_push_edit_event_full(init_api_config, db, misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = await push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)

    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid

    sleep(5)
    # edit event
    event.info = "edited" + event.info
    event.timestamp = str(int(time.time()))
    event.publish_timestamp = str(int(time.time()))
    db.commit()

    push_result: PushResult = await push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event.uuid))
    assert remote_event.info == event.info


@pytest.mark.asyncio
async def test_push_edit_event_incremental(init_api_config, db, misp_api, user, event, remote_misp):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    push_result: PushResult = await push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)
    assert event.uuid == (await misp_api.get_event(UUID(event.uuid), server)).uuid

    sleep(5)
    # edit event
    event.info = "edited" + event.info
    event.timestamp = str(int(time.time()))
    event.publish_timestamp = str(int(time.time()))
    await db.commit()

    push_result: PushResult = await push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = misp_api.get_event(UUID(event.uuid))
    assert remote_event.info == event.info
