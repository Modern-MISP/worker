from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData, EnrichAttributeResult
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute

"""
Provides an implementation for the enrich-attribute jobs.

Takes a Misp event-attribute as input and runs specified plugins to enrich the attribute.
"""


@celery_app.task
def enrich_attribute_job(data: EnrichAttributeData) -> EnrichAttributeResult:
    """
    Runs the enrichment process.

    Executes each of the specified Plugins to enrich the given attribute.

    :param data: The data needed for the enrichment process.
    :return: The created Attributes and Tags.
    :rtype: EnrichAttributeResult
    """
    pass
    # 1. Fetch Attribute by id
    # 2. Initialize Plugins
    # 3. Run Plugins
    # 4. Return created attributes and tags


def enrich_attribute(misp_attribute: MispEventAttribute, enrichment_plugins: list[str]) -> EnrichAttributeResult:
    """
    Enriches the given event attribute with the specified plugins and returns the created attributes and tags.
    :param misp_attribute: The attribute to enrich.
    :type misp_attribute: MispEventAttribute
    :param enrichment_plugins: The plugins to use for enriching the attribute.
    :type enrichment_plugins: list[str]
    :return: The created Attributes and Tags.
    :rtype: EnrichAttributeData
    """
    pass
