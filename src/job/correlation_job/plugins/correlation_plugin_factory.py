from src.job.correlation_job.plugins.database_plugin_interface import DatabasePluginInterface
from src.misp_database.misp_sql import MispSQL
from src.plugins.factory import PluginFactory
from src.job.correlation_job.plugins.correlation_plugin import CorrelationPlugin
from src.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginType, CorrelationPluginInfo


class CorrelationPluginFactory(PluginFactory[CorrelationPlugin]):

    def create(self, plugin_name: str, misp_value: str, database_interface: DatabasePluginInterface) \
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

    def get_plugin_info(self, plugin_name: str) -> CorrelationPluginInfo:
        """
        Returns the type of given correlation plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The type of the correlation plugin.
        :rtype: CorrelationPluginType
        """
        pass
