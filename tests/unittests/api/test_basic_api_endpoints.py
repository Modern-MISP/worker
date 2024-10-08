from uuid import UUID

import pytest

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.misp_database import misp_sql
from mmisp.worker.misp_database.misp_api import MispAPI


@pytest.mark.asyncio
async def test_get_server():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    assert server.name == "MISP 01"


@pytest.mark.asyncio
async def test_get_custom_clusters_from_server():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    conditions: dict[str, bool] = {"published": True, "minimal": True, "custom": True}
    clusters = await misp_api.get_custom_clusters(conditions, server)

    assert isinstance(clusters[0], GetGalaxyClusterResponse)


@pytest.mark.asyncio
async def test_get_galaxy_cluster_from_server():
    mmisp_api: MispAPI = MispAPI()
    server: Server = await mmisp_api.get_server(1)
    cluster = await mmisp_api.get_galaxy_cluster(50, server)
    assert cluster.uuid == "a47b3aa0-604c-4c27-938b-c9aed2724309"


@pytest.mark.asyncio
async def test_get_minimal_events_from_server():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    events = await misp_api.get_minimal_events(True, server)
    assert len(events) > 1300


@pytest.mark.asyncio
async def test_get_event():
    misp_api: MispAPI = MispAPI()

    event: AddEditGetEventDetails = await misp_api.get_event(100)
    assert isinstance(type(event), AddEditGetEventDetails)


@pytest.mark.asyncio
async def test_get_event_for_server():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)

    event = await misp_api.get_event(2, server)
    assert event.uuid == UUID("54ae77a8-f9e7-4bc3-abbc-672c11f2e00f")


@pytest.mark.asyncio
async def test_get_sightings_from_event():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)

    sightings = await misp_api.get_sightings_from_event(20, server)
    assert sightings[0].id == 10


@pytest.mark.asyncio
async def test_get_proposals():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    proposals = await misp_api.get_proposals(server)
    assert proposals[0].id == 2


@pytest.mark.asyncio
async def test_get_sharing_groups():
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)

    sharing_groups = await misp_api.get_sharing_groups(server)
    assert sharing_groups[0].SharingGroup.name == "biggest test"


@pytest.mark.asyncio
async def test_get_event_attributes():
    misp_api: MispAPI = MispAPI()
    attributes = await misp_api.get_event_attributes(2)
    assert isinstance(attributes[0], AttributeWithTagRelationship)


@pytest.mark.asyncio
async def test_get_user():
    misp_api: MispAPI = MispAPI()
    user = await misp_api.get_user(1)
    assert user.email == "admin@admin.test"


@pytest.mark.asyncio
async def test_get_object():
    misp_api: MispAPI = MispAPI()
    misp_object: ObjectWithAttributesResponse = await misp_api.get_object(2)
    assert misp_object.uuid == UUID("875aa3e7-569c-49b0-9e5b-bf2418a1bce8")


@pytest.mark.asyncio
async def test_get_sharing_group():
    misp_api: MispAPI = MispAPI()
    sharing_group = await misp_api.get_sharing_group(1)
    assert sharing_group.SharingGroup.name == "TestSharingGroup"


@pytest.mark.asyncio
async def test_create_attribute():
    misp_api: MispAPI = MispAPI()
    event_attribute: AddAttributeBody = AddAttributeBody(
        event_id=2,
        object_id=3,
        object_relation="act-as",
        category="Other",
        type="text",
        to_ids=False,
        uuid="7e3fc923-c5c1-11ee-b7e9-00158350240e",
        timestamp=1700088063,
        distribution=0,
        sharing_group_id=0,
        comment="No comment",
        deleted=False,
        disable_correlation=False,
        first_seen="2023-11-23T00:00:00.000000+00:00",
        last_seen="2023-11-23T00:00:00.000000+00:00",
        value="testing",
    )
    assert (await misp_api.create_attribute(event_attribute)) > 0


@pytest.mark.asyncio
async def test_create_tag():
    misp_api: MispAPI = MispAPI()
    tag: TagCreateBody = TagCreateBody(
        name="Test tag",
        colour="#ffffff",
        exportable=True,
        org_id=12345,
        user_id=1,
        hide_tag=False,
        numerical_value=12345,
        local_only=True,
    )
    assert (await misp_api.create_tag(tag)) >= 0


@pytest.mark.asyncio
async def test_attach_attribute_tag():
    misp_api: MispAPI = MispAPI()
    await misp_api.attach_attribute_tag(attribute_id=14, tag_id=1464, local=True)


@pytest.mark.asyncio
async def test_attach_event_tag():
    misp_api: MispAPI = MispAPI()
    await misp_api.attach_event_tag(event_id=20, tag_id=1464, local=True)


@pytest.mark.asyncio
async def test_modify_event_tag_relationship(db):
    misp_api: MispAPI = MispAPI()
    event_tag_id: int = await misp_sql.get_event_tag_id(20, 1464)
    await misp_api.modify_event_tag_relationship(event_tag_id=event_tag_id, relationship_type="")


@pytest.mark.asyncio
async def test_modify_attribute_tag_relationship():
    misp_api: MispAPI = MispAPI()
    attribute_tag_id: int = await misp_sql.get_attribute_tag_id(14, 1464)
    await misp_api.modify_attribute_tag_relationship(attribute_tag_id=attribute_tag_id, relationship_type="")
