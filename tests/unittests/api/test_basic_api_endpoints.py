from uuid import UUID

import pytest
from sqlalchemy import and_, exists, select

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.sharing_groups import ViewUpdateSharingGroupLegacyResponse
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.event import EventTag
from mmisp.tests.generators.attribute_generator import generate_valid_random_create_attribute_data
from mmisp.worker.misp_database import misp_sql


@pytest.mark.asyncio
async def test_get_server(init_api_config, misp_api, server):
    get_server_result: Server = await misp_api.get_server(server.id)
    assert server.name == get_server_result.name
    assert server.url == get_server_result.url


@pytest.mark.asyncio
async def test_get_custom_clusters_from_server(init_api_config, misp_api):
    server: Server = await misp_api.get_server(1)
    conditions: dict[str, bool] = {"published": True, "minimal": True, "custom": True}
    clusters = await misp_api.get_custom_clusters(conditions, server)

    assert isinstance(clusters[0], GetGalaxyClusterResponse)


@pytest.mark.asyncio
async def test_get_galaxy_cluster_from_server(init_api_config, misp_api):
    server: Server = await misp_api.get_server(1)
    cluster = await misp_api.get_galaxy_cluster(50, server)
    assert cluster.uuid == "a47b3aa0-604c-4c27-938b-c9aed2724309"


@pytest.mark.asyncio
async def test_get_minimal_events_from_server(init_api_config, misp_api):
    server: Server = await misp_api.get_server(1)
    events = await misp_api.get_minimal_events(True, server)
    assert len(events) > 1300


@pytest.mark.asyncio
async def test_get_event(init_api_config, misp_api, event):
    api_event: AddEditGetEventDetails = await misp_api.get_event(event.id)
    assert isinstance(api_event, AddEditGetEventDetails)
    assert api_event.uuid == event.uuid


@pytest.mark.asyncio
async def test_get_event_for_server(init_api_config, misp_api):
    server: Server = await misp_api.get_server(1)

    event = await misp_api.get_event(2, server)
    assert event.uuid == UUID("54ae77a8-f9e7-4bc3-abbc-672c11f2e00f")


@pytest.mark.asyncio
async def test_get_sightings_from_event(init_api_config, misp_api, sighting):
    sightings = await misp_api.get_sightings_from_event(sighting.event_id)
    assert sightings[0].id == sighting.id


@pytest.mark.asyncio
async def test_get_proposals(init_api_config, misp_api, shadow_attribute):
    proposals = await misp_api.get_proposals()
    assert shadow_attribute in proposals


@pytest.mark.asyncio
async def test_get_sharing_groups(init_api_config, sharing_group, misp_api):
    sharing_groups = await misp_api.get_sharing_groups()
    assert len(sharing_groups) > 0
    assert sharing_group.name in [group.SharingGroup.name for group in sharing_groups]


@pytest.mark.asyncio
async def test_get_event_attributes(init_api_config, misp_api, event_with_attributes):
    attributes = await misp_api.get_event_attributes(event_with_attributes.id)
    for attribute in attributes:
        assert attribute.uuid in [attr.uuid for attr in event_with_attributes.attributes]


@pytest.mark.asyncio
async def test_get_user(init_api_config, misp_api, site_admin_user):
    user = await misp_api.get_user(site_admin_user.id)
    assert user.email == site_admin_user.email


@pytest.mark.asyncio
async def test_get_object(init_api_config, misp_api, object1):
    misp_object: ObjectWithAttributesResponse = await misp_api.get_object(object1.id)
    assert misp_object.uuid == object1.uuid


@pytest.mark.asyncio
async def test_get_sharing_group(init_api_config, misp_api, sharing_group):
    api_sharing_group: ViewUpdateSharingGroupLegacyResponse = await misp_api.get_sharing_group(sharing_group.id)
    assert api_sharing_group.SharingGroup.name == sharing_group.name


@pytest.mark.asyncio
async def test_create_attribute(init_api_config, misp_api, event, sharing_group):
    add_attribute_body: AddAttributeBody = generate_valid_random_create_attribute_data()
    add_attribute_body.event_id = event.id
    add_attribute_body.sharing_group_id = sharing_group.id
    assert (await misp_api.create_attribute(add_attribute_body)) > 0


@pytest.mark.asyncio
async def test_create_tag(init_api_config, misp_api, organisation, site_admin_user):
    tag: TagCreateBody = TagCreateBody(
        name="Test tag",
        colour="#ffffff",
        exportable=True,
        org_id=organisation.id,
        user_id=site_admin_user.id,
        hide_tag=False,
        numerical_value=12345,
        local_only=True,
    )
    assert (await misp_api.create_tag(tag)) >= 0


@pytest.mark.asyncio
async def test_attach_attribute_tag(init_api_config, misp_api, db, attribute, tag):
    attribute_id = attribute.id
    tag_id = tag.id
    await misp_api.attach_attribute_tag(attribute_id=attribute_id, tag_id=tag_id, local=tag.local_only)
    db.expire_all()

    query = select(
        exists().where(and_(AttributeTag.attribute_id == attribute_id, AttributeTag.tag_id == tag_id))
    ).select_from(AttributeTag)
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_attach_event_tag(init_api_config, misp_api, db, event, tag):
    await misp_api.attach_event_tag(event_id=event.id, tag_id=tag.id, local=True)
    db.expire_all()

    query = select(exists().where(and_(EventTag.event_id == event.id, EventTag.tag_id == tag.id))).select_from(EventTag)
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_modify_event_tag_relationship(init_api_config, misp_api, db, event_with_normal_tag):
    assert len(event_with_normal_tag.eventtags) == 1
    event_tag_id: int = await misp_sql.get_event_tag_id(
        db, event_with_normal_tag.id, event_with_normal_tag.eventtags[0].id
    )

    assert event_tag_id and event_tag_id > 0

    relationship_type: str = "Test Relationship"

    await misp_api.modify_event_tag_relationship(event_tag_id=event_tag_id, relationship_type=relationship_type)
    query = select(EventTag.relationship_type).where(EventTag.id == event_tag_id)
    assert (await db.execute(query)).scalar() == relationship_type


@pytest.mark.asyncio
async def test_modify_attribute_tag_relationship(init_api_config, misp_api, db, attribute_with_normal_tag):
    attribute_tag_id: int = await misp_sql.get_attribute_tag_id(
        db, attribute_with_normal_tag.id, attribute_with_normal_tag.attributetags[0].id
    )

    assert attribute_tag_id and attribute_tag_id > 0

    relationship_type: str = "Test Relationship"

    await misp_api.modify_attribute_tag_relationship(
        attribute_tag_id=attribute_tag_id, relationship_type=relationship_type
    )
    query = select(AttributeTag.relationship_type).where(AttributeTag.id == attribute_tag_id)
    assert (await db.execute(query)).scalar() == relationship_type
