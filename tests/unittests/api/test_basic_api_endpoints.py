from time import time_ns
from uuid import UUID

import pytest
from mmisp.util.uuid import uuid
from sqlalchemy import and_, select, exists

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
async def test_get_event(init_api_config, event):
    misp_api: MispAPI = MispAPI()

    api_event: AddEditGetEventDetails = await misp_api.get_event(event.id)
    assert isinstance(type(api_event), AddEditGetEventDetails)
    assert api_event.uuid == event.uuid


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
async def test_get_event_attributes(init_api_config, event_with_attributes):
    misp_api: MispAPI = MispAPI()
    attributes = await misp_api.get_event_attributes(event_with_attributes.id)
    for attribute in attributes:
        assert attribute.uuid in [attr.uuid for attr in event_with_attributes.attributes]


@pytest.mark.asyncio
async def test_get_user(init_api_config, site_admin_user):
    misp_api: MispAPI = MispAPI()
    user = await misp_api.get_user(site_admin_user.id)
    assert user.email == site_admin_user.email


@pytest.mark.asyncio
async def test_get_object(init_api_config, object):
    misp_api: MispAPI = MispAPI()
    misp_object: ObjectWithAttributesResponse = await misp_api.get_object(object.id)
    assert misp_object.uuid == object.uuid


@pytest.mark.asyncio
async def test_get_sharing_group(init_api_config, sharing_group):
    misp_api: MispAPI = MispAPI()
    api_sharing_group = await misp_api.get_sharing_group(1)
    assert api_sharing_group.SharingGroup.name == sharing_group.name


@pytest.mark.asyncio
async def test_create_attribute(init_api_config, event, sharing_group, object):
    misp_api: MispAPI = MispAPI()
    add_attribute_body: AddAttributeBody = AddAttributeBody(
        object_relation="act-as",
        category="Other",
        type="text",
        to_ids=False,
        uuid=uuid(),
        timestamp=time_ns(),
        distribution=0,
        sharing_group_id=0,
        comment="No comment",
        deleted=False,
        disable_correlation=False,
        first_seen=time_ns(),
        last_seen=time_ns(),
        value="testing",
    )
    add_attribute_body.event_id = event.id
    add_attribute_body.sharing_group_id = sharing_group.id
    add_attribute_body.object_id = object.id
    assert (await misp_api.create_attribute(add_attribute_body)) > 0


@pytest.mark.asyncio
async def test_create_tag(init_api_config, organisation, site_admin_user):
    misp_api: MispAPI = MispAPI()
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
async def test_attach_attribute_tag(init_api_config, db, attribute, tag):
    misp_api: MispAPI = MispAPI()
    await misp_api.attach_attribute_tag(attribute_id=attribute.id, tag_id=tag.id, local=True)
    query = select(exists().where(and_(
        EventTag.attribute_id == attribute.id,
        EventTag.tag_id == tag.id
    ))).select_from(EventTag)
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_attach_event_tag(init_api_config, db, event, tag):
    misp_api: MispAPI = MispAPI()
    await misp_api.attach_event_tag(event_id=event.id, tag_id=tag.id, local=True)
    query = select(exists().where(and_(
        EventTag.event_id == event.id,
        EventTag.tag_id == tag.id
    ))).select_from(EventTag)
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
