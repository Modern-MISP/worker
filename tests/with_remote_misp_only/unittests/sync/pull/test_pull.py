from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.sync.pull.pull_job import pull_job


@pytest.mark.asyncio
async def test_pull_add_event_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_event):
    event_uuid: str = pull_job_remote_event.uuid

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.successes == 1

    pulled_event: AddEditGetEventDetails = await misp_api.get_event(UUID(event_uuid))
    assert event_uuid == pulled_event.uuid
    assert pulled_event.locked


@pytest.mark.asyncio
async def test_pull_edit_event_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_event):
    event_uuid: str = pull_job_remote_event.uuid

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    pull_job.delay(user_data, pull_data).get()
    await db.commit()

    # Assert event saved locally
    assert event_uuid == (await misp_api.get_event(UUID(event_uuid))).uuid

    remote_event_from_api: AddEditGetEventDetails = await misp_api.get_event(UUID(event_uuid), remote_misp)

    updated_info: str = "edited_" + pull_job_remote_event.info

    remote_event_from_api.info = updated_info
    remote_event_from_api.timestamp = None
    assert await misp_api.update_event(remote_event_from_api, remote_misp)

    remote_event_from_api = await misp_api.get_event(UUID(event_uuid), remote_misp)
    assert remote_event_from_api.info == updated_info
    assert int(remote_event_from_api.timestamp or 0) > pull_job_remote_event.timestamp

    pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.successes == 1

    pulled_event = await misp_api.get_event(UUID(event_uuid))
    assert pulled_event.info == updated_info


@pytest.mark.asyncio
async def test_pull_add_cluster_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_galaxy_cluster):
    galaxy: Galaxy = pull_job_remote_galaxy_cluster["galaxy"]
    cluster: GalaxyCluster = pull_job_remote_galaxy_cluster["galaxy_cluster"]
    cluster_elements: list[GalaxyElement] = [
        pull_job_remote_galaxy_cluster["galaxy_element"],
        pull_job_remote_galaxy_cluster["galaxy_element2"],
    ]

    cluster_2: GalaxyCluster = pull_job_remote_galaxy_cluster["galaxy_cluster2"]
    cluster_2_elements: list[GalaxyElement] = [
        pull_job_remote_galaxy_cluster["galaxy_element21"],
        pull_job_remote_galaxy_cluster["galaxy_element22"],
    ]

    # Add galaxy with same uuid to local server. Galaxy pull not yet implemented.
    local_galaxy: Galaxy = Galaxy(uuid=galaxy.uuid,
                                  name=galaxy.name,
                                  type=galaxy.type,
                                  description=galaxy.description,
                                  version=galaxy.version,
                                  org_id=remote_misp.org_id,
                                  orgc_id=remote_misp.org_id,
                                  distribution=galaxy.distribution,
                                  created=galaxy.created,
                                  modified=galaxy.modified)

    db.add(local_galaxy)
    await db.commit()
    await db.refresh(local_galaxy)

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
    await db.commit()

    assert pull_result.successes == 0
    assert pull_result.fails == 0
    assert pull_result.pulled_proposals == 0
    assert pull_result.pulled_sightings == 0
    assert pull_result.pulled_clusters == 2

    for cluster in (cluster, cluster_2):
        pulled_cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid)
        assert pulled_cluster.locked
        assert pulled_cluster.uuid == cluster.uuid
        assert pulled_cluster.description == cluster.description
        assert pulled_cluster.value == cluster.value

        # TODO: Galaxy pull does not work yet
        # assert pulled_cluster.Galaxy.uuid == galaxy.uuid

        if cluster == cluster_2:
            cluster_elements = cluster_2_elements

        assert len(pulled_cluster.GalaxyElement) == len(cluster_elements)

        for i in range(len(cluster_elements)):
            assert pulled_cluster.GalaxyElement[i].key == cluster_elements[i].key
            assert pulled_cluster.GalaxyElement[i].value == cluster_elements[i].value


@pytest.mark.asyncio
async def test_pull_relevant_clusters(db, init_api_config, misp_api, user, pull_job_galaxy_cluster,
                                      remote_db, remote_misp, remote_test_default_galaxy):
    local_cluster: GalaxyCluster = pull_job_galaxy_cluster["galaxy_cluster"]
    local_cluster.locked = True
    local_galaxy: Galaxy = pull_job_galaxy_cluster["galaxy"]
    local_galaxy.uuid = remote_test_default_galaxy["galaxy"].uuid
    await db.commit()

    cluster: GalaxyCluster = remote_test_default_galaxy["galaxy_cluster"]
    cluster_elements: list[GalaxyElement] = [
        remote_test_default_galaxy["galaxy_element"],
        remote_test_default_galaxy["galaxy_element2"],
    ]

    # Edit remote cluster
    cluster_value: str = str(cluster.value) + "_edited"
    cluster.version += 1
    cluster.value = cluster_value
    await remote_db.commit()

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.PULL_RELEVANT_CLUSTERS)

    pull_result: PullResult = pull_job.delay(user_data, pull_data).get()
    await db.commit()

    assert pull_result.successes == 0
    assert pull_result.fails == 0
    assert pull_result.pulled_proposals == 0
    assert pull_result.pulled_sightings == 0
    assert pull_result.pulled_clusters == 1

    pulled_cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid)
    assert pulled_cluster.locked
    assert pulled_cluster.uuid == cluster.uuid
    assert pulled_cluster.description == cluster.description
    assert pulled_cluster.value == cluster.value

    # TODO: Galaxy pull does not work yet
    # assert pulled_cluster.Galaxy.uuid == galaxy.uuid

    assert len(pulled_cluster.GalaxyElement) == len(cluster_elements)

    for i in range(len(cluster_elements)):
        assert pulled_cluster.GalaxyElement[i].key == cluster_elements[i].key
        assert pulled_cluster.GalaxyElement[i].value == cluster_elements[i].value


@pytest.mark.asyncio
async def test_pull_forbidden(user, server):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=server.id, technique=PullTechniqueEnum.FULL)

    assert server.pull == False

    with pytest.raises(ForbiddenByServerSettings):
        await pull_job.delay(user_data, pull_data).get()


# TODO: Implement
# @pytest.mark.asyncio
# async def test_pull_add_event_incremental(init_api_config, misp_api, user, remote_misp, remote_event):
#     assert False, "Incremental pull technique does not yet work correctly"


# TODO: Implement
# @pytest.mark.asyncio
# async def test_pull_edit_event_incremental(init_api_config, misp_api, remote_event, user, remote_db, remote_misp):
#     assert False, "Incremental pull technique does not yet work correctly"


# TODO:#1. User who starts the test is user.role.perm_site_admin

"""
Testcase which we need to implement
1. User who starts the test is user.role.perm_site_admin
2. User who starts the test is not user.role.perm_site_admin
"""
