from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.enrichment.enrich_attribute_job import enrich_attribute
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult, EnrichAttributeResult
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute


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

        # Write created event tags to database
        for new_tag in result.event_tags:
            if not new_tag[0].id:
                tag_id = api.create_tag(new_tag[0])
                new_tag[1].tag_id = tag_id
            api.attach_event_tag(new_tag[1])

    return EnrichEventResult(created_attributes=created_attributes)
