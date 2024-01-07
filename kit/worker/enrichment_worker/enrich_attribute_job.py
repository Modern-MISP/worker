from pydantic import BaseModel

from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship, EventTagRelationship
from kit.worker.worker import Worker
from kit.misp_database.misp_api import MispAPI
from kit.worker.enrichment_worker.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginType
from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory


class EnrichAttributeData(BaseModel):
    """
    Encapsulates the necessary data to create an enrich-attribute job.
    """
    attribute_id: int
    enrichmentPlugins: list[str]


class EnrichAttributeResult(BaseModel):
    """
    Encapsulates the result of an enrich-attribute job.

    Contains newly created attributes and tags.
    """
    attributes: list[MispEventAttribute]
    event_tags: list[(MispTag, EventTagRelationship)]


class EnrichAttributeJob(Worker):
    """
    Provides an implementation for the enrich-attribute job.

    Takes a Misp event-attribute as input and runs specified plugins to enrich the attribute.
    """

    def run(self, data: EnrichAttributeData) -> EnrichAttributeResult:
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

    @staticmethod
    def process_attribute(misp_attribute: MispEventAttribute, enrichment_plugins: list[str]) -> EnrichAttributeResult:
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
