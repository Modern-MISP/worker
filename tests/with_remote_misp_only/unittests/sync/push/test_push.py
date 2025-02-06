import time
from functools import cache
from time import sleep
from uuid import UUID

import pytest
from sqlalchemy import select
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server, ServerVersion
from mmisp.db.models.event import Event
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData, PushTechniqueEnum, PushResult
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.misp_database.misp_sql import get_server


@pytest.mark.asyncio
async def test_push_add_event_full(init_api_config, db, misp_api, user, remote_misp, sync_test_event):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)
    assert sync_test_event.uuid == (await misp_api.get_event(UUID(sync_test_event.uuid), server)).uuid


@pytest.mark.asyncio
async def test_push_add_event_incremental(init_api_config, db, misp_api, user, remote_misp, sync_test_event):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)
    assert sync_test_event.uuid == (await misp_api.get_event(UUID(sync_test_event.uuid), server)).uuid


@pytest.mark.asyncio
async def test_push_edit_event_full(init_api_config, db, misp_api, user, remote_misp, sync_test_event):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)

    assert sync_test_event.uuid == (await misp_api.get_event(UUID(sync_test_event.uuid), server)).uuid

    sleep(5)
    # edit event
    sync_test_event.info = "edited" + sync_test_event.info
    sync_test_event.timestamp = str(int(time.time()))
    sync_test_event.publish_timestamp = str(int(time.time()))
    db.commit()

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event.uuid))
    assert remote_event.info == event.info


@pytest.mark.asyncio
async def test_push_edit_event_incremental(init_api_config, db, misp_api, user, remote_misp, remote_db, sync_test_event):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    try:
        statement = select(Event.uuid)
        result = (await remote_db.execute(statement)).scalars()
        print("bananenbieger_test_push_edit_event_incremental_remote_events", list(result))
    except Exception:
        print("bananenbieger_test_push_edit_event_incremental_remote_events", "no remote events")

    try:
        statement = select(Event.uuid, Event.id)
        result = (await db.execute(statement)).scalars()
        print("bananenbieger_test_push_edit_event_incremental_local_events", list(result))
    except Exception:
        print("bananenbieger_test_push_edit_event_incremental_local_events", "no remote events")


    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    server: Server = await get_server(db, remote_misp.id)
    print("bananenbieger_test_push_edit_event_incremental_server_attributes", vars(server))

    server_version: ServerVersion = await misp_api.get_server_version(server)

    print("bonobo_push_job_server_version", vars(server_version))


    print("bananenbieger_test_push_edit_event_incremental_fixture_uuid", sync_test_event.uuid)

    statement = select(Event.uuid)
    result = (await remote_db.execute(statement)).scalars()
    print("bananenbieger_test_push_edit_event_incremental_remote_events", list(result))

    assert sync_test_event.uuid == (await misp_api.get_event(UUID(sync_test_event.uuid), server)).uuid

    sleep(5)
    # edit event
    sync_test_event.info = "edited" + sync_test_event.info
    sync_test_event.timestamp = str(int(time.time()))
    sync_test_event.publish_timestamp = str(int(time.time()))
    await db.commit()

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success == True

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = misp_api.get_event(UUID(sync_test_event.uuid))
    assert remote_event.info == sync_test_event.info
