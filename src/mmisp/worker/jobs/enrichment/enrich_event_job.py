from http.client import HTTPException

from celery.utils.log import get_task_logger

from mmisp.api_schemas.attributes import SearchAttributesAttributesDetails, GetAttributeTag
from mmisp.api_schemas.tags import TagViewResponse, TagCreateBody
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult, EnrichAttributeResult
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship
from mmisp.worker.misp_dataclasses.event_tag_relationship import EventTagRelationship
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute, NewAttribute

_logger = get_task_logger(__name__)


@celery_app.task
def enrich_event_job(user_data: UserData, data: EnrichEventData) -> EnrichEventResult:
    """
    Encapsulates a Job enriching a given MISP Event.

    Job fetches MISP Attributes from a given Event and executes the specified enrichment plugins
    for each of these attributes.
    Newly created Attributes and Tags are attached to the Event in the MISP-Database.

    :param user_data: The user who created the job. (not used)
    :type user_data: UserData
    :param data: The event id and enrichment plugins.
    :return: The number of newly created attributes.
    :rtype: EnrichEventResult
    """

    api: MispAPI = enrichment_worker.misp_api

    # Fetch Attributes by event id
    raw_attributes: list[SearchAttributesAttributesDetails] = []
    try:
        raw_attributes = api.get_event_attributes(data.event_id)
    except (APIException, HTTPException) as api_exception:
        raise JobException(f"Could not fetch attributes for event with id {data.event_id} "
                           f"from MISP API: {api_exception}.")

    attributes: list[MispFullAttribute] = _parse_misp_attributes(raw_attributes)

    created_attributes: int = 0
    for attribute in attributes:
        # Run plugins
        result: EnrichAttributeResult = enrich_attribute(attribute, data.enrichment_plugins)

        # Write created attributes to database
        for new_attribute in result.attributes:
            try:
                _create_attribute(new_attribute.attribute)
                created_attributes += 1
            except HTTPException as http_exception:
                _logger.exception(f"Could not create attribute with MISP-API. {http_exception}")
                continue
            except APIException as api_exception:
                raise JobException(f"Could not create attribute {new_attribute} with MISP-API: {api_exception}.")

        # Write created event tags to database
        for new_tag in result.event_tags:
            try:
                _write_event_tag(new_tag)
            except HTTPException as http_exception:
                _logger.exception(f"Could not create event tag with MISP-API. {http_exception}")
                continue
            except APIException as api_exception:
                raise JobException(f"Could not create event tag {new_tag} with MISP-API: {api_exception}.")

    return EnrichEventResult(created_attributes=created_attributes)


def _create_attribute(attribute: NewAttribute):
    api: MispAPI = enrichment_worker.misp_api
    sql: MispSQL = enrichment_worker.misp_sql

    attribute.id = api.create_attribute(attribute.attribute)

    for new_tag in attribute.tags:
        tag: TagCreateBody = new_tag.tag
        relationship: AttributeTagRelationship = new_tag.relationship
        relationship.attribute_id = attribute.id

        if not tag.id:
            tag.id = api.create_tag(tag)
            relationship.tag_id = tag.id

        api.attach_attribute_tag(relationship)
        relationship.id = sql.get_attribute_tag_id(attribute.id, relationship.tag_id)
        api.modify_attribute_tag_relationship(relationship)


def _write_event_tag(event_tag: tuple[TagViewResponse, EventTagRelationship]):
    api: MispAPI = enrichment_worker.misp_api
    sql: MispSQL = enrichment_worker.misp_sql

    tag: TagViewResponse = event_tag[0]
    relationship: EventTagRelationship = event_tag[1]

    if not tag.id:
        tag_id = api.create_tag(tag)
        relationship.tag_id = tag_id

    api.attach_event_tag(relationship)
    relationship.id = sql.get_event_tag_id(relationship.event_id, relationship.tag_id)
    api.modify_event_tag_relationship(relationship)


def _parse_misp_attributes(attributes: list[SearchAttributesAttributesDetails]) -> list[MispFullAttribute]:
    sql: MispSQL = enrichment_worker.misp_sql
    parsed_attributes: list[MispFullAttribute] = []
    for attribute in attributes:
        attribute_tags: list[tuple[GetAttributeTag, AttributeTagRelationship]] = []
        for tag in attribute.Tag:
            attribute_tag_id: int = sql.get_attribute_tag_id(attribute.id, tag.id)
            tag_relationship: str = sql.get_attribute_tag_relationship(attribute_tag_id)
            attribute_tags.append(
                (tag,
                 AttributeTagRelationship(id=attribute_tag_id,
                                          attribute_id=attribute.id,
                                          tag_id=tag.id,
                                          local=tag.local,
                                          relationship_type=tag_relationship
                                          )))

        parsed_attributes.append(MispFullAttribute(
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
            attribute_tags=attribute_tags
        ))
    return parsed_attributes
