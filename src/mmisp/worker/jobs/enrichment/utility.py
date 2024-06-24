from mmisp.api_schemas.attributes import GetAttributeAttributes, GetAttributeTag, SearchAttributesAttributesDetails
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute


def parse_misp_full_attribute(attribute: GetAttributeAttributes) -> MispFullAttribute:
    sql: MispSQL = enrichment_worker.misp_sql
    attribute_tags: list[tuple[GetAttributeTag, AttributeTagRelationship]] = []
    for tag in attribute.Tag:
        attribute_tags.append((tag, _get_attribute_tag_relationship(attribute.id, tag)))

    return MispFullAttribute(
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
        Tag=attribute.Tag,
        attribute_tags=attribute_tags,
    )


def parse_misp_full_attributes(attributes: list[SearchAttributesAttributesDetails]) -> list[MispFullAttribute]:
    parsed_attributes: list[MispFullAttribute] = []
    for attribute in attributes:
        attribute_tags: list[tuple[GetAttributeTag, AttributeTagRelationship]] = []
        for tag in attribute.Tag:
            attribute_tags.append((tag, _get_attribute_tag_relationship(attribute.id, tag)))

        parsed_attributes.append(
            MispFullAttribute(
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
                Tag=attribute.Tag,
                attribute_tags=attribute_tags,
            )
        )
    return parsed_attributes


def _get_attribute_tag_relationship(attribute_id: int, tag: GetAttributeTag) -> AttributeTagRelationship:
    sql: MispSQL = enrichment_worker.misp_sql

    attribute_tag_id: int = sql.get_attribute_tag_id(attribute_id, tag.id)
    tag_relationship: str = sql.get_attribute_tag_relationship(attribute_tag_id)
    return AttributeTagRelationship(
        id=attribute_tag_id,
        attribute_id=attribute_id,
        tag_id=tag.id,
        local=tag.local,
        relationship_type=tag_relationship,
    )
