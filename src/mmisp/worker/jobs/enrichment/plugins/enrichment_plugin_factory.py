from typing import Self

from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin, PluginNotFound
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin
from mmisp.worker.plugins.factory import PluginFactory


class EnrichmentPluginFactory(PluginFactory[EnrichmentPlugin, EnrichmentPluginInfo]):
    """
    Encapsulates a factory specifically for Enrichment Plugins.
    """

    def create(self: Self, plugin_name: str, misp_attribute: AttributeWithTagRelationship) -> EnrichmentPlugin:
        """
        Creates an instance of a given plugin initialized with the specified event attribute.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :param misp_attribute: The MISP-Attribute to enrich.
        :type misp_attribute: AttributeWithTagRelationship
        :return: The instantiated enrichment plugin.
        :rtype: EnrichmentPlugin
        :raises PluginNotFound: If there is no plugin with the specified name.
        :raises NotAValidPlugin: If the constructor of the plugin does not match the interface.
        """

        if not self.is_plugin_registered(plugin_name):
            raise PluginNotFound(message=f"Unknown plugin '{plugin_name}'. Cannot be instantiated.")

        plugin_instance: EnrichmentPlugin
        try:
            plugin_instance = self._plugins[plugin_name](misp_attribute)
        except TypeError as type_error:
            raise NotAValidPlugin(message=f"Plugin '{plugin_name}' has incorrect constructor: {type_error}")

        return plugin_instance

    def get_plugin_io(self: Self, plugin_name: str) -> PluginIO:
        """
        Returns information about the accepted and returned attribute types of a given enrichment plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The accepted and returned types of attributes.
        :rtype: PluginIO
        """

        if not self.is_plugin_registered(plugin_name):
            raise PluginNotFound(message=f"Unknown plugin '{plugin_name}'.")

        return self.get_plugin_info(plugin_name).MISP_ATTRIBUTES


enrichment_plugin_factory = EnrichmentPluginFactory()
