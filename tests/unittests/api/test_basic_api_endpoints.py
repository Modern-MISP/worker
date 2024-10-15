from uuid import UUID

import pytest
from sqlalchemy import and_, select

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.event import EventTag
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.misp_database import misp_sql
from mmisp.worker.misp_database.misp_api import MispAPI


@pytest.mark.asyncio
async def test_get_server(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    assert server.name == "MISP 01"


@pytest.mark.asyncio
async def test_get_custom_clusters_from_server(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    conditions: dict[str, bool] = {"published": True, "minimal": True, "custom": True}
    clusters = await misp_api.get_custom_clusters(conditions, server)

    assert isinstance(clusters[0], GetGalaxyClusterResponse)


@pytest.mark.asyncio
async def test_get_galaxy_cluster_from_server(init_api_config):
    mmisp_api: MispAPI = MispAPI()
    server: Server = await mmisp_api.get_server(1)
    cluster = await mmisp_api.get_galaxy_cluster(50, server)
    assert cluster.uuid == "a47b3aa0-604c-4c27-938b-c9aed2724309"


@pytest.mark.asyncio
async def test_get_minimal_events_from_server(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    events = await misp_api.get_minimal_events(True, server)
    assert len(events) > 1300


@pytest.mark.asyncio
async def test_get_event(init_api_config):
    misp_api: MispAPI = MispAPI()

    event: AddEditGetEventDetails = await misp_api.get_event(100)
    assert isinstance(type(event), AddEditGetEventDetails)


@pytest.mark.asyncio
async def test_get_event_for_server(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)

    event = await misp_api.get_event(2, server)
    assert event.uuid == UUID("54ae77a8-f9e7-4bc3-abbc-672c11f2e00f")


@pytest.mark.asyncio
async def test_get_sightings_from_event(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)

    sightings = await misp_api.get_sightings_from_event(20, server)
    assert sightings[0].id == 10


@pytest.mark.asyncio
async def test_get_proposals(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)
    proposals = await misp_api.get_proposals(server)
    assert proposals[0].id == 2


@pytest.mark.asyncio
async def test_get_sharing_groups(init_api_config):
    misp_api: MispAPI = MispAPI()
    server: Server = await misp_api.get_server(1)

    sharing_groups = await misp_api.get_sharing_groups(server)
    assert sharing_groups[0].SharingGroup.name == "biggest test"


@pytest.mark.asyncio
async def test_get_event_attributes(init_api_config):
    misp_api: MispAPI = MispAPI()
    attributes = await misp_api.get_event_attributes(2)
    assert isinstance(attributes[0], AttributeWithTagRelationship)


@pytest.mark.asyncio
async def test_get_user(init_api_config):
    misp_api: MispAPI = MispAPI()
    user = await misp_api.get_user(1)
    assert user.email == "admin@admin.test"


@pytest.mark.asyncio
async def test_get_object(init_api_config):
    misp_api: MispAPI = MispAPI()
    misp_object: ObjectWithAttributesResponse = await misp_api.get_object(2)
    assert misp_object.uuid == UUID("875aa3e7-569c-49b0-9e5b-bf2418a1bce8")


@pytest.mark.asyncio
async def test_get_sharing_group(init_api_config):
    misp_api: MispAPI = MispAPI()
    sharing_group = await misp_api.get_sharing_group(1)
    assert sharing_group.SharingGroup.name == "TestSharingGroup"


@pytest.mark.asyncio
async def test_create_attribute(init_api_config):
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
async def test_create_tag(init_api_config):
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
async def test_attach_attribute_tag(init_api_config, db, attribute, tag):
    misp_api: MispAPI = MispAPI()
    await misp_api.attach_attribute_tag(attribute_id=attribute.id, tag_id=tag.id, local=True)
    query = (
        select(EventTag).where(and_(AttributeTag.attribute_id == attribute.id, AttributeTag.tag_id == tag.id)).exists()
    )
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_attach_event_tag(init_api_config, db, event, tag):
    misp_api: MispAPI = MispAPI()
    await misp_api.attach_event_tag(event_id=event.id, tag_id=tag.id, local=True)
    query = select(EventTag).where(and_(EventTag.event_id == event.id, EventTag.tag_id == tag.id)).exists()
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_modify_event_tag_relationship(init_api_config, db, event_with_normal_tag):
    misp_api: MispAPI = MispAPI()
    event_tag_id: int = await misp_sql.get_event_tag_id(event_with_normal_tag.id, event_with_normal_tag.eventtags[0].id)

    relationship_type: str = "Test Relationship"

    await misp_api.modify_event_tag_relationship(event_tag_id=event_tag_id, relationship_type=relationship_type)
    query = select(EventTag.relationship_type).where(EventTag.id == event_tag_id)
    assert (await db.execute(query)).scalar() == relationship_type


@pytest.mark.asyncio
async def test_modify_attribute_tag_relationship(init_api_config, db, attribute_with_normal_tag):
    misp_api: MispAPI = MispAPI()
    attribute_tag_id: int = await misp_sql.get_attribute_tag_id(
        attribute_with_normal_tag.id, attribute_with_normal_tag.attributetags[0].id
    )

    relationship_type: str = "Test Relationship"

    await misp_api.modify_attribute_tag_relationship(
        attribute_tag_id=attribute_tag_id, relationship_type=relationship_type
    )
    query = select(AttributeTag.relationship_type).where(AttributeTag.id == attribute_tag_id)
    assert (await db.execute(query)).scalar() == relationship_type
