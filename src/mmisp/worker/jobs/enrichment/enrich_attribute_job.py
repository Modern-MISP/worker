import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from streaq import WrappedContext

from mmisp.db.database import sessionmanager
from mmisp.db.models.attribute import Attribute
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.plugins import factory
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.protocols import EnrichmentPlugin
from mmisp.plugins.types import PluginType
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData

from .queue import queue

db_logger = get_jobs_logger(__name__)


_logger = logging.getLogger("mmisp")


@queue.task()
@add_ajob_db_log
async def enrich_attribute_job(
    ctx: WrappedContext[None], user_data: UserData, data: EnrichAttributeData
) -> EnrichAttributeResult:
    """
    Provides an implementation of the enrich-attribute job.

    Takes a Misp event-attribute as input and runs specified plugins to enrich the attribute.

    Args:
      user_data: The user who created the job. (not used)
      data: The data needed for the enrichment process.
    Returns:
        The created Attributes and Tags.
    """
    assert sessionmanager is not None
    async with sessionmanager.session() as db:
        query = select(Attribute).filter(Attribute.id == data.attribute_id)
        attribute = (await db.execute(query)).scalars().one_or_none()

        if attribute is None:
            return EnrichAttributeResult()

        return await enrich_attribute(db, attribute, data.enrichment_plugins)


async def enrich_attribute(
    db: AsyncSession, misp_attribute: Attribute, enrichment_plugins: list[str]
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
        if not factory.is_plugin_registered(PluginType.ENRICHMENT, plugin_name):
            _logger.warning(f"Plugin '{plugin_name}' is not registered. Cannot be used for enrichment.")
            continue

        plugin: EnrichmentPlugin = factory.get_plugin(PluginType.ENRICHMENT, plugin_name)

        # Skip Plugins that are not compatible with the attribute.
        if misp_attribute.type not in plugin.ATTRIBUTE_TYPES_INPUT:
            _logger.info(
                f"Plugin {plugin_name} is not compatible with attribute type {misp_attribute.type}. "
                f"Plugin execution will be skipped."
            )
            continue

        # Execute Plugin and save result
        plugin_result: EnrichAttributeResult
        try:
            plugin_result = await plugin.run(db, misp_attribute)
        except Exception as exception:
            _logger.exception(f"Execution of plugin '{plugin_name}' failed. {exception}")
            continue

        if plugin_result:
            result.append(plugin_result)

    return result
