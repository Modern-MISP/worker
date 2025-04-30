import time

import pytest
from sqlalchemy import delete

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import (
    GalaxyClusterSearchBody,
    GetGalaxyClusterResponse,
    PutGalaxyClusterRequest,
    SearchGalaxyClusterGalaxyClustersDetails,
)
from mmisp.api_schemas.organisations import GetOrganisationElement
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.servers import EditServer
from mmisp.db.models.event import Event
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.tests.generators.event_generator import generate_valid_random_create_event_data
from mmisp.worker.misp_database.misp_sql import get_server
from mmisp.worker.misp_dataclasses.misp_user import MispUser


@pytest.mark.asyncio
async def test_get_event_from_server(db, init_api_config, misp_api, remote_misp, remote_event):
    server: Server = await get_server(db, remote_misp.id)

    event = await misp_api.get_event(remote_event.id, server)
    assert event.uuid == remote_event.uuid


@pytest.mark.asyncio
async def test_get_server(db, init_api_config, misp_api, server):
    get_server_result: Server = await get_server(db, server.id)
    assert server.name == get_server_result.name
    assert server.url == get_server_result.url


@pytest.mark.asyncio
async def test_get_organisation_from_server(db, init_api_config, misp_api, remote_misp, remote_organisation):
    server: Server = await get_server(db, remote_misp.id)
    organisation: GetOrganisationElement = await misp_api.get_organisation(remote_organisation.id, server)
    assert organisation.uuid == remote_organisation.uuid
    assert organisation.name == remote_organisation.name


@pytest.mark.asyncio
async def test_get_custom_clusters_from_server_minimal(db, init_api_config, misp_api, remote_misp, remote_test_galaxy):
    server: Server = await get_server(db, remote_misp.id)
    conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, minimal=True, custom=True)
    clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions, server)
    assert clusters and len(clusters) == 2

    assert isinstance(clusters[0], SearchGalaxyClusterGalaxyClustersDetails)

    assert remote_test_galaxy["galaxy_cluster"].uuid in [cluster.uuid for cluster in clusters]
    assert remote_test_galaxy["galaxy_cluster2"].uuid in [cluster.uuid for cluster in clusters]

    # minimal=True -> id and other fields are None
    assert clusters[0].id is None


@pytest.mark.asyncio
async def test_get_custom_clusters_from_server(db, init_api_config, misp_api, remote_misp, remote_test_galaxy):
    server: Server = await get_server(db, remote_misp.id)
    conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, custom=True)
    clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions, server)
    assert clusters and len(clusters) == 2

    assert isinstance(clusters[0], SearchGalaxyClusterGalaxyClustersDetails)

    assert remote_test_galaxy["galaxy_cluster"].uuid in [cluster.uuid for cluster in clusters]
    assert remote_test_galaxy["galaxy_cluster2"].uuid in [cluster.uuid for cluster in clusters]

    # minimal=True -> id and other fields are None
    assert clusters[0].id


@pytest.mark.asyncio
async def test_get_galaxy_cluster_from_server(db, init_api_config, misp_api, remote_misp, remote_test_galaxy):
    server: Server = await get_server(db, remote_misp.id)
    cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(
        remote_test_galaxy["galaxy_cluster"].id, server
    )
    assert str(cluster.uuid) == remote_test_galaxy["galaxy_cluster"].uuid


@pytest.mark.asyncio
async def test_get_minimal_events_from_server(db, init_api_config, misp_api, remote_misp, remote_event, remote_event2):
    server: Server = await get_server(db, remote_misp.id)
    assert server
    events = await misp_api.get_minimal_events(True, server)
    assert remote_event.uuid in [event.uuid for event in events]
    assert remote_event2.uuid in [event.uuid for event in events]


@pytest.mark.asyncio
async def test_save_event_to_server(db, init_api_config, misp_api, remote_misp, remote_db, remote_instance_owner_org):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    event: AddEditGetEventDetails = generate_valid_random_create_event_data(
        remote_instance_owner_org.id, remote_instance_owner_org.id
    )
    assert await misp_api.save_event(event, remote_server)

    await remote_db.commit()

    assert event.uuid == (await misp_api.get_event(event_id=event.uuid, server=remote_server)).uuid

    statement = delete(Event).where(Event.uuid == event.uuid)
    await remote_db.execute(statement)


@pytest.mark.asyncio
async def test_update_event_on_server(
    db, init_api_config, misp_api, remote_misp, remote_db, remote_instance_owner_org, remote_event
):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    event_to_update = await misp_api.get_event(event_id=remote_event.uuid, server=remote_server)

    info = "abc"
    event_to_update.info = info
    event_to_update.timestamp = str(int(time.time()))
    event_to_update.publish_timestamp = str(int(time.time()))

    assert await misp_api.update_event(event_to_update, remote_server)
    # need to commit for updating recorde for fixture remote_event
    await remote_db.commit()

    updated_event = await misp_api.get_event(event_id=event_to_update.uuid, server=remote_server)
    assert updated_event.uuid == event_to_update.uuid
    assert updated_event.info == info


# TODO implement API endpoint in new API
@pytest.mark.asyncio
async def test_save_proposal_to_server(
    db, init_api_config, misp_api, remote_misp, shadow_attribute_with_organisation_event, remote_db
):
    """
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    # shadow_attribute needs event and organisation at remote server
    org = Organisation(**shadow_attribute_with_organisation_event["organisation"].asdict())
    ev = Event(**shadow_attribute_with_organisation_event["event"].asdict())
    del org.id
    del ev.id
    remote_db.add(org)
    remote_db.add(ev)
    await remote_db.commit()

    assert await misp_api.get_event(ev.uuid, remote_server)

    statement = select(Organisation).where(Organisation.id == org.id)
    result: Organisation | None = (await remote_db.execute(statement)).scalars().first()

    assert result

    proposal_event = await misp_api.get_event(ev.uuid, remote_server)

    assert await misp_api.save_proposal(proposal_event, remote_server)

    await remote_db.commit()

    proposals = await misp_api.get_proposals(server=remote_server)
    assert (
            shadow_attribute_with_organisation_event["shadow_attribute"].uuid in [proposal.uuid for proposal in
                                                                                  proposals])

    # needed to have clean db
    remote_db.delete(org)
    remote_db.delete(ev)
    await remote_db.commit()
    """
    assert True, (
        "The save_proposals endpoint is only available in older MISP versions and has not yet been "
        "implemented in the new API."
    )


@pytest.mark.asyncio
async def test_save_sighting_to_server(db, init_api_config, misp_api, remote_misp, sighting, remote_db):
    assert True, "not implemented yet"


@pytest.mark.asyncio
async def test_save_cluster_to_server(
    db, init_api_config, misp_api, remote_misp, test_galaxy, remote_db, remote_organisation
):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    # galaxy_cluster needs galaxy at remote server
    gl = Galaxy(**test_galaxy["galaxy"].asdict())
    remote_db.add(gl)
    await remote_db.commit()

    glc_dict = test_galaxy["galaxy_cluster"].asdict()
    glc_dict["GalaxyElement"] = [
        test_galaxy["galaxy_element"].asdict(),
        test_galaxy["galaxy_element2"].asdict(),
    ]
    glc = GetGalaxyClusterResponse.parse_obj(glc_dict)
    assert await misp_api.save_cluster(glc, remote_server)

    assert (
        test_galaxy["galaxy_cluster"].uuid
        == (await misp_api.get_galaxy_cluster(cluster_id=test_galaxy["galaxy_cluster"].uuid, server=remote_server)).uuid
    )

    # needed to have clean db
    statement = delete(GalaxyCluster).where(GalaxyCluster.uuid == glc.uuid)
    await remote_db.execute(statement)

    await remote_db.delete(gl)
    await remote_db.commit()


@pytest.mark.asyncio
async def test_update_cluster_on_server(remote_db, init_api_config, misp_api, remote_test_galaxy, remote_misp):
    cluster = remote_test_galaxy["galaxy_cluster"]
    cluster_from_api: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.id, remote_misp)

    cluster_edit_body: PutGalaxyClusterRequest = PutGalaxyClusterRequest(**cluster_from_api.dict())
    cluster_edit_body.value = cluster_from_api.value + "_edited"

    assert await misp_api.update_cluster(cluster_edit_body, remote_misp)
    await remote_db.commit()

    updated_cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster.id, remote_misp)
    assert updated_cluster.value == cluster_edit_body.value


@pytest.mark.asyncio
async def test_get_user_from_server(init_api_config, misp_api, remote_misp, remote_site_admin_user):
    user: MispUser = await misp_api.get_user(remote_site_admin_user.id, remote_misp)
    assert user.email == remote_site_admin_user.email

    own_user: MispUser = await misp_api.get_user(None, remote_misp)
    assert own_user.id == remote_site_admin_user.id


@pytest.mark.asyncio
async def test_edit_server(db, init_api_config, misp_api, remote_misp):
    remote_server: Server = await get_server(db, remote_misp.id)

    remote_server_dict: dict = remote_server.__dict__
    remote_server_dict["push"] = not remote_server.push
    remote_server_dict["cache_timestamp"] = False

    await misp_api.edit_server(EditServer.parse_obj(remote_server_dict), remote_server.id)

    await db.commit()

    updatet_server: Server = await get_server(db, remote_server.id)

    assert updatet_server.push == remote_server_dict["push"]
