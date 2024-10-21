import asyncio
from http.client import HTTPException

from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.api_schemas.attributes import SearchAttributesAttributesDetails
from mmisp.db.database import sessionmanager
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute, NewTag
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import (
    EnrichEventData,
    EnrichEventResult,
)
from mmisp.worker.jobs.enrichment.utility import parse_attributes_with_tag_relationships
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import get_attribute_tag_id, get_event_tag_id

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
    return asyncio.run(_enrich_event_job(user_data, data))


async def _enrich_event_job(user_data: UserData, data: EnrichEventData) -> EnrichEventResult:
    async with sessionmanager.session() as session:
        api: MispAPI = enrichment_worker.misp_api

        # Fetch Attributes by event id
        attributes_response: list[SearchAttributesAttributesDetails] = []
        try:
            attributes_response = await api.get_event_attributes(data.event_id)
        except (APIException, HTTPException) as api_exception:
            raise JobException(
                f"Could not fetch attributes for event with id {data.event_id} from MISP API: {api_exception}."
            )

        attributes: list[AttributeWithTagRelationship] = await parse_attributes_with_tag_relationships(
            session, attributes_response
        )

        created_attributes: int = 0
        for attribute in attributes:
            # Run plugins
            result: EnrichAttributeResult = enrich_attribute(attribute, data.enrichment_plugins)

            # Write created attributes to database
            for new_attribute in result.attributes:
                try:
                    asyncio.run(_create_attribute(new_attribute))
                    created_attributes += 1
                except HTTPException as http_exception:
                    _logger.exception(f"Could not create attribute with MISP-API. {http_exception}")
                    continue
                except APIException as api_exception:
                    raise JobException(f"Could not create attribute {new_attribute} with MISP-API: {api_exception}.")

            # Write created event tags to database
            for new_tag in result.event_tags:
                try:
                    asyncio.run(_write_event_tag(data.event_id, new_tag))
                except HTTPException as http_exception:
                    _logger.exception(f"Could not create event tag with MISP-API. {http_exception}")
                    continue
                except APIException as api_exception:
                    raise JobException(f"Could not create event tag {new_tag} with MISP-API: {api_exception}.")

        return EnrichEventResult(created_attributes=created_attributes)


async def _create_attribute(session: AsyncSession, attribute: NewAttribute) -> None:
    api: MispAPI = enrichment_worker.misp_api

    attribute_id: int = await api.create_attribute(attribute.attribute)

    for new_tag in attribute.tags:
        tag_id: int | None = new_tag.tag_id
        if not tag_id:
            if new_tag.tag:
                tag_id = await api.create_tag(new_tag.tag)
            else:
                raise ValueError("At least one of the values tag_id or tag is required for a NewAttributeTag.")

        await api.attach_attribute_tag(attribute_id, tag_id, new_tag.local)
        attribute_tag_id: int = await get_attribute_tag_id(session, attribute_id, tag_id)
        await api.modify_attribute_tag_relationship(attribute_tag_id, new_tag.relationship_type)


async def _write_event_tag(session: AsyncSession, event_id: int, event_tag: NewTag) -> None:
    api: MispAPI = enrichment_worker.misp_api

    tag_id: int | None = event_tag.tag_id

    if not tag_id:
        if event_tag.tag:
            tag_id = await api.create_tag(event_tag.tag)
        else:
            raise ValueError("At least one of the values tag_id or tag is required for a NewEventTag.")

    await api.attach_event_tag(event_id, tag_id, event_tag.local)
    event_tag_id: int = await get_event_tag_id(session, event_id, tag_id)
    await api.modify_event_tag_relationship(event_tag_id, event_tag.relationship_type)
