import time

import pytest
from sqlalchemy import select

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse, SearchGalaxyClusterGalaxyClustersDetails
from mmisp.api_schemas.server import Server
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.tests.generators.event_generator import generate_valid_random_create_event_data
from mmisp.worker.misp_database.misp_sql import get_server


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
async def test_get_custom_clusters_from_server(db, init_api_config, misp_api, remote_misp, remote_test_default_galaxy):
    server: Server = await get_server(db, remote_misp.id)
    conditions: dict[str, bool] = {"published": True, "minimal": True, "custom": True}
    clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions, server)
    assert clusters and len(clusters) > 0

    assert isinstance(clusters[0], SearchGalaxyClusterGalaxyClustersDetails)
    cluster_id_exists: bool = False
    for cluster in clusters:
        if cluster.uuid == remote_test_default_galaxy["galaxy_cluster"].uuid:
            cluster_id_exists = True
            break

    assert cluster_id_exists


@pytest.mark.asyncio
async def test_get_galaxy_cluster_from_server(db, init_api_config, misp_api, remote_misp, remote_test_default_galaxy):
    server: Server = await get_server(db, remote_misp.id)
    cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(
        remote_test_default_galaxy["galaxy_cluster"].id, server
    )
    assert str(cluster.uuid) == remote_test_default_galaxy["galaxy_cluster"].uuid


@pytest.mark.asyncio
async def test_get_minimal_events_from_server(db, init_api_config, misp_api, remote_misp, remote_event, remote_event2):
    server: Server = await get_server(db, remote_misp.id)
    assert server
    events = await misp_api.get_minimal_events(True, server)
    assert remote_event.uuid in [event.uuid for event in events]
    assert remote_event2.uuid in [event.uuid for event in events]


@pytest.mark.asyncio
async def test_save_event_to_server(db, init_api_config, misp_api, remote_misp, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    event: AddEditGetEventDetails = generate_valid_random_create_event_data()
    assert await misp_api.save_event(event, remote_server)

    await remote_db.commit()

    assert (
            event.uuid == (await misp_api.get_event(event_id=event.uuid,
                                                    server=remote_server)).uuid
    )


@pytest.mark.asyncio
async def test_update_event_on_server(db, init_api_config, misp_api, remote_misp, remote_event, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    event_to_update = await misp_api.get_event(event_id=remote_event.uuid, server=remote_server)

    info = "edited" + remote_event.info
    event_to_update.info = info
    timestamp: str = str(int(time.time()))
    event_to_update.timestamp = timestamp

    publish_timestamp: str = str(int(time.time()))
    event_to_update.publish_timestamp = publish_timestamp

    assert await misp_api.update_event(event_to_update, remote_server)

    await remote_db.commit()

    updated_event = await misp_api.get_event(event_id=event_to_update.uuid, server=remote_server)
    assert updated_event.uuid == event_to_update.uuid
    assert updated_event.info == info
    assert updated_event.timestamp == timestamp
    assert updated_event.publish_timestamp == publish_timestamp


@pytest.mark.asyncio
async def test_save_proposal_to_server(
        db, init_api_config, misp_api, remote_misp, shadow_attribute_with_organisation_event, remote_db
):
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

    assert misp_api.get_event(ev.uuid, remote_server)

    statement = select(Organisation).where(Organisation.id == org.id)
    result: Organisation | None = (await remote_db.execute(statement)).scalars().first()

    assert result

    proposal_event = await misp_api.get_event(ev.uuid, remote_server)

    assert await misp_api.save_proposal(proposal_event, remote_server)

    await remote_db.commit()

    proposals = await misp_api.get_proposals(server=remote_server)
    assert (
            shadow_attribute_with_organisation_event["shadow_attribute"].uuid in [proposal.uuid for proposal in proposals]
    )

    # needed to have clean db
    remote_db.delete(org)
    remote_db.delete(ev)
    await remote_db.commit()


@pytest.mark.asyncio
async def test_save_sighting_to_server(db, init_api_config, misp_api, remote_misp, sighting, remote_db):
    assert False, "not implemented yet"


@pytest.mark.asyncio
async def test_save_cluster_to_server(db, init_api_config, misp_api, remote_misp, test_default_galaxy, remote_db):

    """
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server


    # galaxy_cluster needs galaxy at remote server
    gl = Galaxy(**test_default_galaxy["galaxy"].asdict())
    remote_db.add(gl)
    await remote_db.commit()


    print("bonobo_test_save_cluster_to_server_1")
    assert await misp_api.save_cluster(GetGalaxyClusterResponse.parse_obj(
        test_default_galaxy["galaxy_cluster"].asdict()), remote_server)

    print("bonobo_test_save_cluster_to_server_2")

    await remote_db.commit()

    print("bonobo_test_save_cluster_to_server_3")

    # todo uuuid at api point to add
    assert (
            test_default_galaxy["galaxy_cluster"].uuid
            == await misp_api.get_galaxy_cluster(
        galaxy_cluster_id=test_default_galaxy["galaxy_cluster"].uuid, server=remote_server
    ).uuid
    )

    print("bonobo_test_save_cluster_to_server_4")


    # needed to have clean db
    remote_db.delete(gl)
    await remote_db.commit()

    """
