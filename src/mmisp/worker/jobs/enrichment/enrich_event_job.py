import logging
from http.client import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from streaq import WrappedContext

from mmisp.db.database import sessionmanager
from mmisp.db.models.attribute import Attribute
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute, NewTag
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute
from mmisp.worker.jobs.enrichment.job_data import (
    EnrichEventData,
    EnrichEventResult,
)
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import get_attribute_tag_id, get_event_tag_id

from .queue import queue

db_logger = get_jobs_logger(__name__)

_logger = logging.getLogger("mmisp")


@queue.task()
@add_ajob_db_log
async def enrich_event_job(ctx: WrappedContext[None], user_data: UserData, data: EnrichEventData) -> EnrichEventResult:
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
    assert sessionmanager is not None
    async with sessionmanager.session() as db:
        api: MispAPI = MispAPI(db)
        query = select(Attribute).filter(Attribute.event_id == data.event_id)
        res = await db.execute(query)
        attributes = res.scalars().all()

        print(f"enrich_event_job parsed_attributes: {len(attributes)}")

        created_attributes: int = 0
        for attribute in attributes:
            # Run plugins
            result: EnrichAttributeResult = await enrich_attribute(db, attribute, data.enrichment_plugins)
            print(f"enrich_event_job enrich_attribute_result: {result} for attribute: {attribute}")

            # Write created attributes to database
            for new_attribute in result.attributes:
                try:
                    await _create_attribute(db, api, new_attribute)
                    created_attributes += 1
                except HTTPException as http_exception:
                    _logger.exception(f"Could not create attribute with MISP-API. {http_exception}")
                    continue
                except APIException as api_exception:
                    raise JobException(f"Could not create attribute {new_attribute} with MISP-API: {api_exception}.")

            # Write created event tags to database
            for new_tag in result.event_tags:
                try:
                    await _write_event_tag(db, api, data.event_id, new_tag)
                except HTTPException as http_exception:
                    _logger.exception(f"Could not create event tag with MISP-API. {http_exception}")
                    continue
                except APIException as api_exception:
                    raise JobException(f"Could not create event tag {new_tag} with MISP-API: {api_exception}.")

        return EnrichEventResult(created_attributes=created_attributes)


async def _create_attribute(session: AsyncSession, api: MispAPI, attribute: NewAttribute) -> None:
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


async def _write_event_tag(session: AsyncSession, api: MispAPI, event_id: int, event_tag: NewTag) -> None:
    tag_id: int | None = event_tag.tag_id

    if not tag_id:
        if event_tag.tag:
            tag_id = await api.create_tag(event_tag.tag)
        else:
            raise ValueError("At least one of the values tag_id or tag is required for a NewEventTag.")

    await api.attach_event_tag(event_id, tag_id, event_tag.local)
    event_tag_id: int = await get_event_tag_id(session, event_id, tag_id)
    await api.modify_event_tag_relationship(event_tag_id, event_tag.relationship_type)
