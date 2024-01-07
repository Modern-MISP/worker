from enum import Enum

from kit.api.worker_router.worker_router import PluginIO
from kit.plugins.plugin import Plugin
from kit.worker.enrichment_job.enrich_attribute_job import EnrichAttributeResult
from kit.misp_dataclasses.misp_attribute import MispEventAttribute


class EnrichmentPluginType(str, Enum):
    """
    Enum describing all possible enrichment plugin types.
    """
    EXPANSION = "expansion"
    hover = "hover"


class EnrichmentPlugin(Plugin):
    """
    Protocol class describing an enrichment plugin.

    Provides functionality for enriching a given MISP Event-Attribute.
    Creates and returns new attributes and tags.
    """

    __ENRICHMENT_TYPE: EnrichmentPluginType
    __MISP_ATTRIBUTES: PluginIO

    def __init__(self, misp_attribute: MispEventAttribute):
        """
        Creates a new plugin initialized with an event attribute.
        
        :param misp_attribute: The MISP Event-Attribute to enrich.
        :type misp_attribute: MispEventAttribute
        """
        ...

    def run(self) -> EnrichAttributeResult:
        """
        Entry point for the plugin. Starts enrichment process and returns created attributes and tags.
        :return: The created (enriched) attributes and tags.
        :rtype: EnrichAttributeResult
        """
        ...
