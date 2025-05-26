from datetime import datetime
from uuid import UUID

import pytest

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxies import ExportGalaxyGalaxyElement
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse, PutGalaxyClusterRequest
from mmisp.api_schemas.organisations import GetOrganisationElement
from mmisp.db.models.event import Event
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.sync.pull.pull_job import pull_job, queue


@pytest.mark.asyncio
async def test_pull_add_event_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_event):
    event_uuid: str = pull_job_remote_event.uuid

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)
    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
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

    async with queue:
        await pull_job.run(user_data, pull_data)
    await db.commit()

    # Assert event saved locally
    assert event_uuid == (await misp_api.get_event(UUID(event_uuid))).uuid

    remote_event_from_api: AddEditGetEventDetails = await misp_api.get_event(UUID(event_uuid), remote_misp)

    updated_info: str = "edited_" + pull_job_remote_event.info

    remote_event_from_api.info = updated_info
    remote_event_from_api.timestamp = datetime.now()
    assert await misp_api.update_event(remote_event_from_api, remote_misp)

    remote_event_from_api = await misp_api.get_event(UUID(event_uuid), remote_misp)
    assert remote_event_from_api.info == updated_info
    assert int(remote_event_from_api.timestamp or 0) > pull_job_remote_event.timestamp

    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.successes == 1

    pulled_event = await misp_api.get_event(UUID(event_uuid))
    assert pulled_event.info == updated_info


@pytest.mark.asyncio
async def test_pull_local_modified_event(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_event):
    event: Event = pull_job_remote_event
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.successes == 1

    # Edit local event
    event_from_api: AddEditGetEventDetails = await misp_api.get_event(event.uuid)
    event_from_api.info = "edited_" + event_from_api.info
    event_from_api.locked = False
    assert await misp_api.update_event(event_from_api)

    # Edit remote event
    event_from_api: AddEditGetEventDetails = await misp_api.get_event(event.uuid, remote_misp)
    event_from_api.info = "edited_2_" + event_from_api.info
    event_from_api.timestamp = datetime.now()
    assert await misp_api.update_event(event_from_api, remote_misp)

    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    # Assert that the local event was not updated due to the local edit
    assert pull_result.fails == 0
    assert pull_result.successes == 0


@pytest.mark.asyncio
async def test_pull_add_cluster_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_galaxy_cluster):
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

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
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
async def test_pull_edit_cluster_full(init_api_config, db, misp_api, user, remote_misp, pull_job_remote_galaxy_cluster):
    cluster: GalaxyCluster = pull_job_remote_galaxy_cluster["galaxy_cluster"]

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.pulled_clusters == 2

    # Edit remote cluster
    new_value: str = str(cluster.value) + "_edited"
    new_ge: ExportGalaxyGalaxyElement = ExportGalaxyGalaxyElement(key="new_key", value="new_value")

    cluster_from_api: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid, remote_misp)
    cluster_from_api.value = new_value
    cluster_from_api.GalaxyElement.append(new_ge)

    assert await misp_api.update_cluster(PutGalaxyClusterRequest(**cluster_from_api.model_dump()), remote_misp)

    # Test
    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.pulled_clusters == 1

    pulled_cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid)
    assert pulled_cluster.value == new_value

    assert new_ge.key in [ge.key for ge in pulled_cluster.GalaxyElement]


@pytest.mark.asyncio
async def test_pull_add_cluster_orgc_full(
    init_api_config, db, misp_api, user, remote_misp, remote_organisation, pull_job_remote_cluster_with_new_orgc
):
    cluster: GalaxyCluster = pull_job_remote_cluster_with_new_orgc

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)

    async with queue:
        pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    assert pull_result.successes == 0
    assert pull_result.fails == 0
    assert pull_result.pulled_proposals == 0
    assert pull_result.pulled_sightings == 0
    assert pull_result.pulled_clusters == 1

    # Assert that the orgc of the cluster has been pulled
    pulled_org: GetOrganisationElement = await misp_api.get_organisation(remote_organisation.uuid)
    assert pulled_org.name.startswith(remote_organisation.name)

    pulled_cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid)
    assert pulled_cluster.orgc_id == pulled_org.id


@pytest.mark.asyncio
async def test_pull_local_modified_cluster_full(
    init_api_config, db, misp_api, user, remote_misp, pull_job_remote_galaxy_cluster
):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.FULL)
    cluster: GalaxyCluster = pull_job_remote_galaxy_cluster["galaxy_cluster"]

    pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    assert pull_result.fails == 0
    assert pull_result.pulled_clusters == 2

    # Edit local cluster
    new_value: str = str(cluster.value) + "_edited"

    cluster_from_api: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid)
    cluster_from_api.value = new_value
    cluster_from_api.locked = False
    assert await misp_api.update_cluster(PutGalaxyClusterRequest(**cluster_from_api.model_dump()))

    # Edit remote cluster
    cluster_from_api: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.uuid, remote_misp)
    assert await misp_api.update_cluster(PutGalaxyClusterRequest(**cluster_from_api.model_dump()), remote_misp)

    pull_result: PullResult = await pull_job.run(user_data, pull_data)
    await db.commit()

    # Assert that the local cluster was not updated due to the local edit
    assert pull_result.fails == 0
    assert pull_result.pulled_clusters == 0


@pytest.mark.asyncio
async def test_pull_relevant_clusters(
    db, init_api_config, misp_api, user, test_galaxy, remote_db, remote_misp, remote_test_galaxy
):
    local_cluster: GalaxyCluster = test_galaxy["galaxy_cluster"]
    local_cluster.locked = True
    local_galaxy: Galaxy = test_galaxy["galaxy"]
    local_galaxy.uuid = remote_test_galaxy["galaxy"].uuid
    await db.commit()

    cluster: GalaxyCluster = remote_test_galaxy["galaxy_cluster"]
    galaxy_elements: list[GalaxyElement] = [
        remote_test_galaxy["galaxy_element"],
        remote_test_galaxy["galaxy_element2"],
    ]

    # Save galaxy elements to compare later. Pull job deletes and recreates them.
    minimal_galaxy_elements: list[tuple] = [(ce.key, ce.value) for ce in galaxy_elements]

    # Edit remote cluster
    cluster_value: str = str(cluster.value) + "_edited"
    cluster.version += 1
    cluster.value = cluster_value
    await remote_db.commit()

    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=remote_misp.id, technique=PullTechniqueEnum.PULL_RELEVANT_CLUSTERS)

    pull_result: PullResult = await pull_job.run(user_data, pull_data)
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

    assert len(pulled_cluster.GalaxyElement) == len(minimal_galaxy_elements)

    for i in range(len(minimal_galaxy_elements)):
        for ce in minimal_galaxy_elements:
            if pulled_cluster.GalaxyElement[i].key == ce[0] and pulled_cluster.GalaxyElement[i].value == ce[1]:
                return
        assert False, (
            f"GalaxyElement not pulled correctly. "
            f"{pulled_cluster.GalaxyElement[i].key}:{pulled_cluster.GalaxyElement[i].value} "
            f"not in {minimal_galaxy_elements}"
        )


@pytest.mark.asyncio
async def test_pull_forbidden(user, server):
    user_data: UserData = UserData(user_id=user.id)
    pull_data: PullData = PullData(server_id=server.id, technique=PullTechniqueEnum.FULL)

    assert not server.pull

    with pytest.raises(ForbiddenByServerSettings):
        await pull_job.run(user_data, pull_data)


# TODO: Implement
# @pytest.mark.asyncio
# async def test_pull_add_event_incremental(init_api_config, misp_api, user, remote_misp, remote_event):
#     assert False, "Incremental pull technique does not yet work correctly"


# TODO: Implement
# @pytest.mark.asyncio
# async def test_pull_edit_event_incremental(init_api_config, misp_api, remote_event, user, remote_db, remote_misp):
#     assert False, "Incremental pull technique does not yet work correctly"
