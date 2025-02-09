import time

import pytest

from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse, SearchGalaxyClusterGalaxyClustersDetails
from mmisp.api_schemas.server import Server
from mmisp.lib.serialisation_helper import timestamp_or_empty_string
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
        remote_test_default_galaxy["galaxy_cluster"].id, server)
    assert str(cluster.uuid) == remote_test_default_galaxy["galaxy_cluster"].uuid


@pytest.mark.asyncio
async def test_get_minimal_events_from_server(db, init_api_config, misp_api, remote_misp, remote_event, remote_event2):
    server: Server = await get_server(db, remote_misp.id)
    assert server
    events = await misp_api.get_minimal_events(True, server)
    assert remote_event.uuid in [event.uuid for event in events]
    assert remote_event2.uuid in [event.uuid for event in events]


@pytest.mark.asyncio
async def test_save_event_to_server(db, init_api_config, misp_api, remote_misp, event, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server
    event = await misp_api.save_event(event, remote_server)

    await remote_db.commit()

    assert event.uuid == misp_api.get_event(event_id=event.uuid, server=remote_server).uuid


@pytest.mark.asyncio
async def test_update_event_on_server(db, init_api_config, misp_api, remote_misp, event, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    # needed to update event
    remote_db.add(event)
    await remote_db.commit()

    event.info = "edited" + event.info
    timestamp: str = str(int(time.time()))
    event.timestamp = timestamp

    publish_timestamp: str = str(int(time.time()))
    event.publish_timestamp = publish_timestamp

    event = await misp_api.update_event(event, remote_server)

    await remote_db.commit()

    assert event.uuid == misp_api.get_event(event_id=event.uuid, server=remote_server).uuid
    assert event.info == "edited" + event.info
    assert event.timestamp == timestamp
    assert event.publish_timestamp == publish_timestamp


@pytest.mark.asyncio
async def test_save_proposal_to_server(db, init_api_config, misp_api, remote_misp,
                                       shadow_attribute_with_organisation_event, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    # shadow_attribute needs event and organisation at remote server
    remote_db.add(shadow_attribute_with_organisation_event["organisation"])
    remote_db.add(shadow_attribute_with_organisation_event["event"])
    await remote_db.commit()

    assert await misp_api.save_proposal(shadow_attribute_with_organisation_event, remote_server)

    await remote_db.commit()

    assert shadow_attribute_with_organisation_event.uuid == misp_api.get_proposal(
        proposal_id=shadow_attribute_with_organisation_event.uuid, server=remote_server).uuid


@pytest.mark.asyncio
async def test_save_sighting_to_server(db, init_api_config, misp_api, remote_misp, sighting, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    # sighting needs event and organisation at remote server
    remote_db.add(sighting["organisation"])
    remote_db.add(sighting["event"])
    await remote_db.commit()

    assert await misp_api.save_sighting(sighting["sighting"], remote_server)

    await remote_db.commit()

    assert sighting.uuid == misp_api.get_sighting(sighting_id=sighting[sighting].uuid, server=remote_server).uuid


@pytest.mark.asyncio
async def test_save_cluster_to_server(db, init_api_config, misp_api, remote_misp, remote_test_default_galaxy, remote_db):
    remote_server: Server = await get_server(db, remote_misp.id)
    assert remote_server

    # galaxy_cluster needs galaxy at remote server
    remote_db.add(remote_test_default_galaxy["galaxy"])
    await remote_db.commit()

    assert await misp_api.save_cluster(remote_test_default_galaxy["galaxy_cluster"], remote_server)

    await remote_db.commit()

    #todo uuuid at api point to add
    assert remote_test_default_galaxy["galaxy_cluster"].uuid == misp_api.get_galaxy_cluster(
        galaxy_cluster_id=remote_test_default_galaxy["galaxy_cluster"].uuid, server=remote_server).uuid
