from http.client import HTTPException

from celery.utils.log import get_task_logger

from mmisp.api_schemas.attributes import GetAttributeAttributes
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData, EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin, PluginIO
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.jobs.enrichment.utility import parse_misp_full_attribute
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute

_logger = get_task_logger(__name__)


@celery_app.task
def enrich_attribute_job(user_data: UserData, data: EnrichAttributeData) -> EnrichAttributeResult:
    """
    Provides an implementation of the enrich-attribute job.

    Takes a Misp event-attribute as input and runs specified plugins to enrich the attribute.

    :param user_data: The user who created the job. (not used)
    :type user_data: UserData
    :param data: The data needed for the enrichment process.
    :type data: EnrichAttributeData
    :return: The created Attributes and Tags.
    :rtype: EnrichAttributeResult
    """

    api: MispAPI = enrichment_worker.misp_api

    # Fetch Attribute by id
    raw_attribute: GetAttributeAttributes
    try:
        raw_attribute = api.get_attribute(data.attribute_id)
    except (APIException, HTTPException) as api_exception:
        raise JobException(f"Could not fetch attribute with id {data.attribute_id} from MISP API: {api_exception}.")

    attribute: MispFullAttribute = parse_misp_full_attribute(raw_attribute)

    return enrich_attribute(attribute, data.enrichment_plugins)


def enrich_attribute(misp_attribute: MispFullAttribute, enrichment_plugins: list[str]) -> EnrichAttributeResult:
    """
    Enriches the given event attribute with the specified plugins and returns the created attributes and tags.

    :param misp_attribute: The attribute to enrich.
    :type misp_attribute: MispFullAttribute
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
                _logger.error(f"Plugin {plugin_name} is not compatible with attribute type {misp_attribute.type}. "
                              f"Plugin execution will be skipped.")
                continue

            # Instantiate Plugin
            plugin: EnrichmentPlugin
            try:
                plugin: EnrichmentPlugin = enrichment_plugin_factory.create(plugin_name, misp_attribute)
            except NotAValidPlugin as exception:
                _logger.exception(f"Instance of plugin '{plugin_name}' could not be created. {exception}")
                continue

            # Execute Plugin and save result
            plugin_result: EnrichAttributeResult = EnrichAttributeResult()
            try:
                plugin_result = plugin.run()
            except Exception as exception:
                _logger.exception(f"Execution of plugin '{plugin_name}' failed. {exception}")
                continue

            if plugin_result:
                result.append(plugin_result)

        else:
            _logger.error(f"Plugin '{plugin_name}' is not registered. Cannot be used for enrichment.")

    return result
