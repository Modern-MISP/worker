from mmisp.worker.controller.celery_app.celery_app import celery_app
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult, EnrichAttributeResult
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_tag import EventTagRelationship, MispTag, AttributeTagRelationship


@celery_app.task
def enrich_event_job(data: EnrichEventData) -> EnrichEventResult:
    """
    Encapsulates a Job enriching a given MISP Event.

    Job fetches MISP Attributes from a given Event and executes the specified enrichment plugins
    for each of these attributes.
    Newly created Attributes and Tags are attached to the Event in the MISP-Database.

    :param data: The event id and enrichment plugins.
    :return: The number of newly created attributes.
    :rtype: EnrichEventResult
    """

    api: MispAPI = enrichment_worker.misp_api
    sql: MispSQL = enrichment_worker.misp_sql

    # Fetch Attributes by event id
    attributes: list[MispEventAttribute] = []
    try:
        attributes = api.get_event_attributes(data.event_id)
    except Exception as exception:
        # TODO after MispAPI is implemented: Implement
        pass

    created_attributes: int = 0
    for attribute in attributes:
        # Run plugins
        result: EnrichAttributeResult = enrich_attribute(attribute, data.enrichment_plugins)

        # Write created attributes to database
        for new_attribute in result.attributes:
            try:
                api.create_attribute(new_attribute)
                created_attributes += 1
            except Exception as exception:
                # TODO after MispAPI is implemented: Implement
                pass

            for new_tag in new_attribute.tags:
                tag: MispTag = new_tag[0]
                relationship: AttributeTagRelationship = new_tag[1]
                if not tag.id:
                    tag_id = api.create_tag(tag)
                    relationship.tag_id = tag_id
                api.attach_attribute_tag(relationship)
                relationship.id = sql.get_attribute_tag_id(new_attribute.id, relationship.tag_id)
                api.modify_attribute_tag_relationship(relationship)

        # Write created event tags to database
        for new_tag in result.event_tags:
            tag: MispTag = new_tag[0]
            relationship: EventTagRelationship = new_tag[1]

            if not tag.id:
                tag_id = api.create_tag(tag)
                relationship.tag_id = tag_id

            api.attach_event_tag(relationship)
            relationship.id = sql.get_event_tag_id(relationship.event_id, relationship.tag_id)
            api.modify_event_tag_relationship(relationship)

    return EnrichEventResult(created_attributes=created_attributes)
