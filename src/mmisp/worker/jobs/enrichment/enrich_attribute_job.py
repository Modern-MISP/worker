from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData, EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute


@celery_app.task
def enrich_attribute_job(data: EnrichAttributeData) -> EnrichAttributeResult:
    """
    Provides an implementation of the enrich-attribute job.

    Takes a Misp event-attribute as input and runs specified plugins to enrich the attribute.

    :param data: The data needed for the enrichment process.
    :type data: EnrichAttributeData
    :return: The created Attributes and Tags.
    :rtype: EnrichAttributeResult
    """

    api: MispAPI = enrichment_worker.misp_api

    # Fetch Attribute by id
    attribute: MispEventAttribute
    try:
        attribute = api.get_event_attribute(data.attribute_id)
    except Exception as exception:
        # TODO after MispAPI is implemented: Try ... except
        pass

    return enrich_attribute(attribute, data.enrichment_plugins)


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

    result: EnrichAttributeResult = EnrichAttributeResult()
    for plugin in enrichment_plugins:
        if enrichment_plugin_factory.is_plugin_registered(plugin):
            # Instantiate Plugin
            try:
                plugin: EnrichmentPlugin = enrichment_plugin_factory.create(plugin, misp_attribute)
            except NotAValidPlugin as exception:
                # TODO: Log NotAValidPlugin exception
                pass

            # Execute Plugin and save result
            try:
                plugin_result: EnrichAttributeResult = plugin.run()
                result.append(plugin_result)
            except Exception as exception:
                # TODO: Log PluginExecutionException
                # raise PluginExecutionException(f"Plugin could not be executed successfully: {exception}")
                pass

        else:
            # TODO: Log PluginNotFound exception
            pass

    return result
