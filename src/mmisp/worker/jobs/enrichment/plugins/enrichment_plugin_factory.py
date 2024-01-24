from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.plugins.factory import PluginFactory
from mmisp.worker.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPlugin, PluginIO, EnrichmentPluginInfo, \
    EnrichmentPluginInfo


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

    def get_plugin_info(self, plugin_name: str) -> EnrichmentPluginInfo:
        """
        Returns information about the given enrichment plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The plugin information.
        :rtype: EnrichmentPluginInfo
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
