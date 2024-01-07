from kit.plugins.factory import PluginFactory
from kit.worker.correlation_job.plugins.correlation_plugin import CorrelationPlugin, CorrelationPluginType


class CorrelationPluginFactory(PluginFactory[CorrelationPlugin]):

    def create(self, plugin_name: str, misp_value: str) \
            -> CorrelationPlugin:
        """
        Create an instance of a plugin.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :param misp_value: The value to correlate.
        :type misp_value: str
        :return: The instantiated correlation plugin, initialized with the value.
        """

        pass
        # try:
        #    creator_func = self.plugin_creation_funcs[plugin_name]
        # except KeyError:
        #    raise ValueError(f"TODO") from None
        # return creator_func(misp_attribute, misp_attribute_tags)

    def get_correlation_plugin_type(self, plugin_name: str) -> CorrelationPluginType:
        """
        Returns the type of given correlation plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The type of the correlation plugin.
        :rtype: CorrelationPluginType
        """
        pass