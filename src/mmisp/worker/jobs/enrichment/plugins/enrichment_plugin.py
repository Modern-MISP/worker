from enum import Enum

from pydantic import BaseModel, ConfigDict, conlist, confrozenset

from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute
from mmisp.worker.plugins.plugin import Plugin, PluginInfo


class EnrichmentPluginType(str, Enum):
    """
    Enum describing all possible enrichment plugin types.
    """

    EXPANSION = "expansion"
    """Enrichment Plugins of this type generate new attributes that can be attached to a MISP-Event 
    to add additional information permanently."""
    HOVER = "hover"
    """Enrichment Plugins of this type generate information that is usually only displayed once 
    and should not be stored permanently in the database."""


class PluginIO(BaseModel):
    """
    Encapsulates information about the accepted and returned attribute types of a plugin.
    """

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True, str_min_length=1)

    INPUT: conlist(str, min_length=1)
    """Attribute types accepted by the Enrichment Plugin."""
    OUTPUT: conlist(str, min_length=1)
    """Attribute types returned by the Enrichment Plugin."""


class EnrichmentPluginInfo(PluginInfo):
    ENRICHMENT_TYPE: confrozenset(EnrichmentPluginType, min_length=1)
    """The type of the enrichment plugin."""
    MISP_ATTRIBUTES: PluginIO
    """The accepted and returned types of attributes of the enrichment plugin."""


class EnrichmentPlugin(Plugin):
    """
    Interface for an enrichment plugin.

    Provides functionality for enriching a given MISP Event-Attribute.
    Creates and returns new attributes and tags.
    """

    PLUGIN_INFO: EnrichmentPluginInfo
    """Information about the plugin."""

    def __init__(self, misp_attribute: MispFullAttribute):
        """
        Creates a new enrichment plugin initialized with an event attribute.
        
        :param misp_attribute: The MISP Event-Attribute to enrich.
        :type misp_attribute: MispFullAttribute
        """
        ...

    def run(self) -> EnrichAttributeResult:
        """
        Entry point for the plugin. Starts enrichment process and returns created attributes and tags.
        :return: The created (enriched) attributes and tags.
        :rtype: EnrichAttributeResult
        """
        ...
