from time import sleep

import pytest
from sqlalchemy import and_, exists, select
from sqlalchemy.sql import text

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.sharing_groups import ViewUpdateSharingGroupLegacyResponse
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.event import EventTag
from mmisp.tests.generators.attribute_generator import generate_valid_random_create_attribute_data
from mmisp.worker.misp_database import misp_sql


@pytest.mark.asyncio
async def test_get_event(init_api_config, misp_api, event):
    api_event: AddEditGetEventDetails = await misp_api.get_event(event.id)
    assert isinstance(api_event, AddEditGetEventDetails)
    assert api_event.uuid == event.uuid


@pytest.mark.asyncio
async def test_get_sharing_groups(init_api_config, sharing_group, misp_api, db):
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
    add_attribute_body.distribution = 1
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
    attribute_tag_id: int = await misp_sql.get_attribute_tag_id(db, attribute_id, tag_id)
    assert attribute_tag_id > 0

    query = select(
        exists().where(and_(AttributeTag.attribute_id == attribute_id, AttributeTag.tag_id == tag_id))
    ).select_from(AttributeTag)
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_attach_event_tag(init_api_config, misp_api, db, event, tag):
    event_id: int = event.id
    tag_id: int = tag.id
    await misp_api.attach_event_tag(event_id=event_id, tag_id=tag_id, local=tag.local_only)
    db.expire_all()

    query = select(exists().where(and_(EventTag.event_id == event_id, EventTag.tag_id == tag_id))).select_from(EventTag)
    assert (await db.execute(query)).scalar()


@pytest.mark.asyncio
async def test_modify_event_tag_relationship(init_api_config, misp_api, db, event_with_normal_tag_local):
    assert len(event_with_normal_tag_local.eventtags) == 1
    event_tag = event_with_normal_tag_local.eventtags[0]
    event_tag_id: int = event_tag.id

    relationship_type: str = "Test Relationship"

    await misp_api.modify_event_tag_relationship(event_tag_id=event_tag_id, relationship_type=relationship_type)
    print(await misp_api.get_event(event_with_normal_tag_local.id))
    sleep(5)

    statement = text("SELECT * FROM event_tags")
    for row in await db.execute(statement):
        print(row)

    db.expire_all()
    await db.refresh(event_tag)

    assert event_tag.relationship_type == relationship_type
    query = select(EventTag).where(EventTag.id == event_tag_id)
    result = await db.execute(query)
    et = result.scalar()
    assert et.id == event_tag_id
    assert et.relationship_type == relationship_type


@pytest.mark.asyncio
async def test_modify_attribute_tag_relationship(init_api_config, misp_api, db, attribute_with_normal_tag_local):
    attribute = attribute_with_normal_tag_local[0]
    #    at = attribute_with_normal_tag[1]

    assert len(attribute.attributetags) == 1
    attribute_tag_id: int = attribute.attributetags[0].id

    relationship_type: str = "Test Relationship"

    assert await misp_api.modify_attribute_tag_relationship(
        attribute_tag_id=attribute_tag_id, relationship_type=relationship_type
    )
    db.expire_all()
    query = select(AttributeTag).where(AttributeTag.id == attribute_tag_id)
    attribute_tag = (await db.execute(query)).scalar()
    print("bonobo: ", vars(attribute_tag))
    assert attribute_tag is not None
    assert attribute_tag.relationship_type == relationship_type
