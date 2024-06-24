from typing import Self

from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.plugins.plugin import Plugin


class EnrichmentPlugin(Plugin):
    """
    Interface for an enrichment plugin.

    Provides functionality for enriching a given MISP Event-Attribute.
    Creates and returns new attributes and tags.
    """

    PLUGIN_INFO: EnrichmentPluginInfo
    """Information about the plugin."""

    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        """
        Creates a new enrichment plugin initialized with an event attribute.

        :param misp_attribute: The MISP Event-Attribute to enrich.
        :type misp_attribute: AttributeWithTagRelationship
        """
        ...

    def run(self: Self) -> EnrichAttributeResult:
        """
        Entry point for the plugin. Starts enrichment process and returns created attributes and tags.
        :return: The created (enriched) attributes and tags.
        :rtype: EnrichAttributeResult
        """
        ...
