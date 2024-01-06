from typing import List

from pydantic import BaseModel

from kit.misp_dataclasses.misp_attribute import EventAttribute
from kit.misp_dataclasses.misp_tag import Tag
from kit.worker.worker import Worker
from kit.misp_database.misp_api import MispAPI
from kit.worker.enrichment_worker.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginType
from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory


class EnrichedAttribute(BaseModel):
    """
    Stores a newly created attribute of an attribute enrichment job.
    """
    eventAttribute: EventAttribute
    tags: List[Tag]
    #tags: List[int]
    #newTags: List[Tag]


class EnrichAttributeResult(BaseModel):
    attributes: List[EnrichedAttribute]
    eventTags: List[int]
    newEventTags: List[Tag]


class EnrichAttributeJob(Worker):

    def run(self, attribute_id: int, enrichment_plugins: List[str]) -> List[EnrichedAttribute]:
        """
        Runs the enrichment process.

        Executes each of the specified Plugins to enrich the attribute.

        :param attribute_id: The id of the MISP-Attribute to process.
        :type attribute_id: int
        :param enrichment_plugins: The list of plugins to use for enrichment of the Attribute.
        :type enrichment_plugins: List[str]
        :return: The created Attributes and Tags.
        :rtype: EnrichedAttribute
        """
        pass
        # 1. Fetch Attribute by id
        # 2. Initialize Plugins
        # 3. Run Plugins
        # 4. Return created attributes and tags

    @staticmethod
    def process_attribute(event_attribute: EventAttribute, tags: List[Tag], enrichment_plugins: List[str])\
            -> List[EnrichedAttribute]:
        pass
