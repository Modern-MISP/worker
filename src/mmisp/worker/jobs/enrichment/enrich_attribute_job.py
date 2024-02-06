from http.client import HTTPException

from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData, EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin, PluginIO
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute


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
    except (APIException, HTTPException) as api_exception:
        raise JobException(f"Could not fetch attribute with id {data.attribute_id} from MISP API: {api_exception}.")

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
    for plugin_name in enrichment_plugins:
        if enrichment_plugin_factory.is_plugin_registered(plugin_name):

            # Skip Plugins that are not compatible with the attribute.
            plugin_io: PluginIO = enrichment_plugin_factory.get_plugin_io(plugin_name)
            if misp_attribute.type not in plugin_io.INPUT:
                # TODO: Log plugin skipped
                continue

            # Instantiate Plugin
            plugin: EnrichmentPlugin
            try:
                plugin: EnrichmentPlugin = enrichment_plugin_factory.create(plugin_name, misp_attribute)
            except NotAValidPlugin as exception:
                # TODO: Log NotAValidPlugin exception
                continue

            # Execute Plugin and save result
            plugin_result: EnrichAttributeResult = EnrichAttributeResult()
            try:
                plugin_result = plugin.run()
            except Exception as exception:
                # TODO: Log PluginExecutionException
                # raise PluginExecutionException(f"Plugin could not be executed successfully: {exception}")
                continue

            result.append(plugin_result)

        else:
            # TODO: Log PluginNotFound exception
            pass

    return result
