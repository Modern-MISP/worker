import time
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.misp_database.misp_sql import get_server


@pytest.mark.asyncio
async def test_push_add_event_full(
        init_api_config, db, misp_api, user, remote_misp, sync_test_event, set_server_version, remote_db
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    pushed_event = await misp_api.get_event(UUID(sync_test_event.uuid), remote_misp)
    assert sync_test_event.uuid == pushed_event.uuid


@pytest.mark.asyncio
async def test_push_add_event_incremental(
        init_api_config, db, misp_api, user, remote_misp, sync_test_event, set_server_version, remote_db
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    pushed_event = await misp_api.get_event(UUID(sync_test_event.uuid), remote_misp)
    assert sync_test_event.uuid == pushed_event.uuid


@pytest.mark.asyncio
async def test_push_edit_event_full(
        init_api_config, db, misp_api, user, remote_misp, sync_test_event, remote_db, set_server_version
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    server: Server = await get_server(db, remote_misp.id)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    event_to_update = await misp_api.get_event(UUID(sync_test_event.uuid))
    assert event_to_update

    # edit event
    event_to_update.info = "edited" + sync_test_event.info
    event_to_update.timestamp = str(int(time.time()))

    await misp_api.update_event(event_to_update)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event_to_update.uuid), server)
    assert remote_event.info == event_to_update.info


@pytest.mark.asyncio
async def test_push_edit_event_incremental(
        init_api_config, db, misp_api, user, remote_misp, remote_db, sync_test_event, set_server_version
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    server: Server = await get_server(db, remote_misp.id)

    print("bonobo_pre_id: ", server.last_pushed_id)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    server: Server = await get_server(db, remote_misp.id)
    print("bonobo_post_id: ", server.last_pushed_id)

    event_to_update = await misp_api.get_event(UUID(sync_test_event.uuid))
    assert event_to_update

    # edit event
    event_to_update.info = "edited" + sync_test_event.info
    event_to_update.timestamp = str(int(time.time()))

    await misp_api.update_event(event_to_update)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    server: Server = await get_server(db, remote_misp.id)
    print("bonobo_post2_id: ", server.last_pushed_id)



    # tests if event was updated on remote-server
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event_to_update.uuid), server)
    assert remote_event.info == event_to_update.info


@pytest.mark.asyncio
async def test_push_galaxy_cluster_full(
        init_api_config, db, misp_api, user, remote_misp, remote_db, sync_test_event, set_server_version, push_galaxy
):
    """
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    push_result: PushResult = push_job.delay(user_data, push_data).get()
    assert push_result.success

    galaxy_cluster_1 = await misp_api.get_galaxy_cluster(test_galaxy["galaxy_cluster"].uuid, remote_misp)
    galaxy_cluster_2 = await misp_api.get_galaxy_cluster(test_galaxy["galaxy_cluster2"].uuid, remote_misp)

    assert galaxy_cluster_1
    assert galaxy_cluster_2

    # TODO
    # gl elements testen
    # sachen löschen in neuen fixture
    """
