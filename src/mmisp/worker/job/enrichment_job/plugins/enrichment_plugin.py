from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from mmisp.worker.plugins.plugin import Plugin, PluginInfo
from mmisp.worker.job.enrichment_job.job_data import EnrichAttributeResult
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute


class EnrichmentPluginType(str, Enum):
    """
    Enum describing all possible enrichment plugin types.
    """
    EXPANSION = "expansion"
    HOVER = "hover"


class PluginIO(BaseModel):
    """
    Encapsulates information about the accepted and returned attribute types for a plugin.
    """

    model_config = ConfigDict(frozen=True)

    INPUT: list[str]  # Attribute types accepted by the plugin.
    OUTPUT: list[str]  # Attribute types that can be created/returned by the plugin.


class EnrichmentPluginInfo(PluginInfo):
    ENRICHMENT_TYPE: set[EnrichmentPluginType]
    MISP_ATTRIBUTES: PluginIO


class EnrichmentPlugin(Plugin):
    """
    Protocol class describing an enrichment plugin.

    Provides functionality for enriching a given MISP Event-Attribute.
    Creates and returns new attributes and tags.
    """

    PLUGIN_INFO: EnrichmentPluginInfo = Field(..., allow_mutation=False)

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
