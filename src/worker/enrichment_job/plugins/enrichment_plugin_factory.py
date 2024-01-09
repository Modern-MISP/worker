from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.plugins.factory import PluginFactory
from src.worker.enrichment_job.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginType, PluginIO


class EnrichmentPluginFactory(PluginFactory[EnrichmentPlugin]):
    """
    Encapsulates a factory specifically for Enrichment Plugins.
    """

    def create(self, plugin_name: str, misp_attribute: MispEventAttribute) -> EnrichmentPlugin:
        """
        Creates an instance of a given plugin initialized with the specified event attribute.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :param misp_attribute: The MISP-Attribute to enrich.
        :type misp_attribute: MispEventAttribute
        :return: The instantiated enrichment plugin.
        :rtype: EnrichmentPlugin
        """

        pass
        # try:
        #    creator_func = self.plugin_creation_funcs[plugin_name]
        # except KeyError:
        #    raise ValueError(f"TODO") from None
        # return creator_func(misp_attribute, misp_attribute_tags)

    def get_enrichment_plugin_type(self, plugin_name: str) -> EnrichmentPluginType:
        """
        Returns the type of given enrichment plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The type of the enrichment plugin.
        :rtype: EnrichmentPluginType
        """
        pass

    def get_plugin_io(self, plugin_name: str) -> PluginIO:
        """
        Returns information about the accepted and returned attribute types of a given enrichment plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The information
        :rtype: PluginIO
        """
        pass
