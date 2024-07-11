from mmisp.api_schemas.attributes import GetAttributeAttributes, GetAttributeTag, SearchAttributesAttributesDetails
from mmisp.db.models.attribute import AttributeTag
from mmisp.plugins.models.attribute import AttributeTagWithRelationshipType, AttributeWithTagRelationship
from mmisp.worker.misp_database.misp_sql import get_attribute_tag, get_attribute_tag_id


async def parse_attribute_with_tag_relationship(attribute: GetAttributeAttributes) -> AttributeWithTagRelationship:
    tags: list[AttributeTagWithRelationshipType] = []
    for tag in attribute.Tag or []:
        tags.append(await _parse_attribute_tag_with_relationship(attribute.id, tag))

    return AttributeWithTagRelationship(
        id=attribute.id,
        event_id=attribute.event_id,
        object_id=attribute.object_id,
        object_relation=attribute.object_relation,
        category=attribute.category,
        type=attribute.type,
        value=attribute.value,
        to_ids=attribute.to_ids,
        uuid=attribute.uuid,
        timestamp=attribute.timestamp,
        distribution=attribute.distribution,
        sharing_group_id=attribute.sharing_group_id,
        comment=attribute.comment,
        deleted=attribute.deleted,
        disable_correlation=attribute.disable_correlation,
        first_seen=attribute.first_seen,
        last_seen=attribute.last_seen,
        event_uuid=attribute.event_uuid,
        data=attribute.data,
        Tag=tags,
    )


async def parse_attributes_with_tag_relationships(
    attributes: list[SearchAttributesAttributesDetails],
) -> (list)[AttributeWithTagRelationship]:
    parsed_attributes: list[AttributeWithTagRelationship] = []
    for attribute in attributes:
        tags: list[AttributeTagWithRelationshipType] = []
        for tag in attribute.Tag:
            tags.append(await _parse_attribute_tag_with_relationship(attribute.id, tag))

        parsed_attributes.append(
            AttributeWithTagRelationship(
                id=attribute.id,
                event_id=attribute.event_id,
                object_id=attribute.object_id,
                object_relation=attribute.object_relation,
                category=attribute.category,
                type=attribute.type,
                value=attribute.value,
                to_ids=attribute.to_ids,
                uuid=attribute.uuid,
                timestamp=attribute.timestamp,
                distribution=attribute.distribution,
                sharing_group_id=attribute.sharing_group_id,
                comment=attribute.comment,
                deleted=attribute.deleted,
                disable_correlation=attribute.disable_correlation,
                first_seen=attribute.first_seen,
                last_seen=attribute.last_seen,
                event_uuid=attribute.event_uuid,
                data=attribute.data,
                Tag=tags,
            )
        )
    return parsed_attributes


async def _parse_attribute_tag_with_relationship(
    attribute_id: int, tag: GetAttributeTag
) -> AttributeTagWithRelationshipType:
    attribute_tag_id: int = await get_attribute_tag_id(attribute_id, tag.id)
    attribute_tag: AttributeTag = await get_attribute_tag(attribute_tag_id)
    return AttributeTagWithRelationshipType(
        **tag.dict(), relationship_local=attribute_tag.local, relationship_type=attribute_tag.relationship_type
    )
