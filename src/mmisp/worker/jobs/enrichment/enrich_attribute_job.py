import asyncio

from celery.utils.log import get_task_logger
from requests import HTTPError

from mmisp.api_schemas.attributes import GetAttributeAttributes
from mmisp.db.database import sessionmanager
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.enrichment.enrichment_plugin import PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.jobs.enrichment.utility import parse_attribute_with_tag_relationship
from mmisp.worker.misp_database.misp_api import MispAPI

db_logger = get_jobs_logger(__name__)
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
    return asyncio.run(_enrich_attribute_job(user_data, data))


@add_ajob_db_log
async def _enrich_attribute_job(user_data: UserData, data: EnrichAttributeData) -> EnrichAttributeResult:
    assert sessionmanager is not None
    async with sessionmanager.session() as session:
        api: MispAPI = MispAPI(session)

        # Fetch Attribute by id
        attribute_response: GetAttributeAttributes
        try:
            attribute_response = await api.get_attribute(data.attribute_id)
        except (APIException, HTTPError) as api_exception:
            raise JobException(f"Could not fetch attribute with id {data.attribute_id} from MISP API: {api_exception}.")

        attribute: AttributeWithTagRelationship = await parse_attribute_with_tag_relationship(
            session, attribute_response
        )

        return enrich_attribute(attribute, data.enrichment_plugins)


def enrich_attribute(
    misp_attribute: AttributeWithTagRelationship, enrichment_plugins: list[str]
) -> EnrichAttributeResult:
    """
    Enriches the given event attribute with the specified plugins and returns the created attributes and tags.

    :param misp_attribute: The attribute to enrich.
    :type misp_attribute: AttributeWithTagRelationship
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
                _logger.error(
                    f"Plugin {plugin_name} is not compatible with attribute type {misp_attribute.type}. "
                    f"Plugin execution will be skipped."
                )
                continue

            # Instantiate Plugin
            plugin: EnrichmentPlugin
            try:
                plugin = enrichment_plugin_factory.create(plugin_name, misp_attribute)
            except NotAValidPlugin as exception:
                _logger.exception(exception)
                continue

            # Execute Plugin and save result
            plugin_result: EnrichAttributeResult
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
