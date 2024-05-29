from http.client import HTTPException

from celery.utils.log import get_task_logger

from mmisp.api_schemas.tags.get_tag_response import TagViewResponse
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult, EnrichAttributeResult
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.event_tag_relationship import EventTagRelationship
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship

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
    attributes: list[MispEventAttribute] = []
    try:
        attributes = api.get_event_attributes(data.event_id)
    except (APIException, HTTPException) as api_exception:
        raise JobException(f"Could not fetch attributes for event with id {data.event_id} "
                           f"from MISP API: {api_exception}.")

    created_attributes: int = 0
    for attribute in attributes:
        # Run plugins
        result: EnrichAttributeResult = enrich_attribute(attribute, data.enrichment_plugins)

        # Write created attributes to database
        for new_attribute in result.attributes:
            try:
                _create_attribute(new_attribute)
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


def _create_attribute(attribute: MispEventAttribute):
    api: MispAPI = enrichment_worker.misp_api
    sql: MispSQL = enrichment_worker.misp_sql

    attribute.id = api.create_attribute(attribute)

    for new_tag in attribute.tags:
        tag: TagViewResponse = new_tag[0]
        relationship: AttributeTagRelationship = new_tag[1]
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
