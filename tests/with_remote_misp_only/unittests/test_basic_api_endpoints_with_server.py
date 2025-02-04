import pytest

from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse, SearchGalaxyClusterGalaxyClustersDetails
from mmisp.api_schemas.server import Server
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

    print("bonobo_test_get_custom_clusters_from_server", str(clusters))

    assert isinstance(clusters[0], SearchGalaxyClusterGalaxyClustersDetails)
    assert any(remote_test_default_galaxy["galaxy_cluster"].id == cluster.id for cluster in clusters)


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
