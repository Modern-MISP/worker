from datetime import datetime
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.api_schemas.galaxy_clusters import PutGalaxyClusterRequest
from mmisp.api_schemas.server import Server
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.jobs.sync.push.push_job import push_job, queue
from mmisp.worker.misp_database.misp_sql import get_server


@pytest.mark.asyncio
async def test_push_add_event_full(
    init_api_config, db, misp_api, user, remote_misp, sync_test_event, set_server_version, remote_db
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)
    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    pushed_event = await misp_api.get_event(UUID(sync_test_event.uuid), remote_misp)
    assert sync_test_event.uuid == pushed_event.uuid


@pytest.mark.asyncio
async def test_push_add_event_incremental(
    init_api_config, db, misp_api, user, remote_misp, sync_test_event, set_server_version, remote_db
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.INCREMENTAL)

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
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
    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    event_to_update = await misp_api.get_event(UUID(sync_test_event.uuid))
    assert event_to_update

    # edit event
    event_to_update.info = "edited" + sync_test_event.info
    event_to_update.timestamp = datetime.now()

    assert await misp_api.update_event(event_to_update)

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
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

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    event_to_update = await misp_api.get_event(UUID(sync_test_event.uuid))
    assert event_to_update

    # edit event
    event_to_update.info = "edited" + sync_test_event.info
    event_to_update.timestamp = datetime.now()
    # checks if event was updated locally
    await misp_api.update_event(event_to_update)
    local_updated_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event_to_update.uuid))
    assert local_updated_event.info == event_to_update.info

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    # tests if event was not updated on server, because of incremental push
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event_to_update.uuid), server)
    assert remote_event.info == sync_test_event.info


@pytest.mark.asyncio
async def test_push_older_event(
    init_api_config, db, misp_api, user, remote_misp, sync_test_event, remote_db, set_server_version
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    server: Server = await get_server(db, remote_misp.id)

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    remote_event_to_update = await misp_api.get_event(UUID(sync_test_event.uuid), server)
    assert remote_event_to_update

    # edit event
    remote_event_to_update.info = "edited" + sync_test_event.info
    remote_event_to_update.timestamp = datetime.now()
    # checks if event was updated remote
    await misp_api.update_event(remote_event_to_update, server)
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(remote_event_to_update.uuid), server)
    assert remote_event.info == remote_event_to_update.info

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    # tests if event was not updated form push on remote-server because of older timestamp
    remote_event: AddEditGetEventDetails = await misp_api.get_event(UUID(remote_event_to_update.uuid), server)
    assert remote_event.info == remote_event_to_update.info


@pytest.mark.asyncio
async def test_push_galaxy_cluster_full(
    init_api_config, db, misp_api, user, remote_misp, remote_db, set_server_version, push_galaxy
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    assert await misp_api.get_galaxy_cluster(push_galaxy["galaxy_cluster"].uuid, remote_misp)
    assert await misp_api.get_galaxy_cluster(push_galaxy["galaxy_cluster2"].uuid, remote_misp)


@pytest.mark.asyncio
async def test_push_galaxy_cluster_full_old_galaxy_version(
    init_api_config, db, misp_api, user, remote_misp, remote_db, set_server_version, push_galaxy
):
    user_data: UserData = UserData(user_id=user.id)
    push_data: PushData = PushData(server_id=remote_misp.id, technique=PushTechniqueEnum.FULL)

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    cluster_from_api: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(
        push_galaxy["galaxy_cluster"].uuid, remote_misp
    )
    assert cluster_from_api
    assert await misp_api.get_galaxy_cluster(push_galaxy["galaxy_cluster2"].uuid, remote_misp)

    # edit galaxy cluster
    cluster_edit_body: PutGalaxyClusterRequest = PutGalaxyClusterRequest(**cluster_from_api.model_dump())
    cluster_edit_body.value = cluster_from_api.value + "_edited"
    cluster_edit_body.version = cluster_from_api.version + 1
    await misp_api.update_cluster(cluster_edit_body, remote_misp)

    async with queue:
        push_result: PushResult = await push_job.run(user_data, push_data)
    assert push_result.success

    remote_cluster = await misp_api.get_galaxy_cluster(push_galaxy["galaxy_cluster"].uuid, remote_misp)
    assert remote_cluster.value == cluster_edit_body.value


@pytest.mark.asyncio
async def test_push_forbidden(user, server):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PushData = PushData(server_id=server.id, technique=PushTechniqueEnum.FULL)

    assert not server.push

    with pytest.raises(ForbiddenByServerSettings):
        async with queue:
            await push_job.run(user_data, pull_data)


@pytest.mark.asyncio
async def test_push_not_existing_server(user):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PushData = PushData(server_id=69696969, technique=PushTechniqueEnum.FULL)

    with pytest.raises(JobException):
        async with queue:
            await push_job.run(user_data, pull_data)
