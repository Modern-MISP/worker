from enum import Enum

from pydantic import BaseModel

from src.plugins.plugin import Plugin
from src.worker.enrichment_job.enrich_attribute_job import EnrichAttributeResult
from src.misp_dataclasses.misp_attribute import MispEventAttribute


class EnrichmentPluginType(str, Enum):
    """
    Enum describing all possible enrichment plugin types.
    """
    EXPANSION = "expansion"
    hover = "hover"


class PluginIO(BaseModel):
    """
    Encapsulates information about the accepted and returned attribute types for a plugin.
    """

    INPUT: list[str]  # Attribute types accepted by the plugin.
    OUTPUT: list[str]  # Attribute types that can be created/returned by the plugin.

    class Config:
        allow_mutation: False


class EnrichmentPlugin(Plugin):
    """
    Protocol class describing an enrichment plugin.

    Provides functionality for enriching a given MISP Event-Attribute.
    Creates and returns new attributes and tags.
    """

    ENRICHMENT_TYPE: EnrichmentPluginType
    MISP_ATTRIBUTES: PluginIO

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