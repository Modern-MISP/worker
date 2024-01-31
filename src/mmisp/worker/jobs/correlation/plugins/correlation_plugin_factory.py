from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound, NotAValidPlugin
from mmisp.worker.jobs.correlation.plugins.database_plugin_interface import DatabasePluginInterface
from mmisp.worker.plugins.factory import PluginFactory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo


class CorrelationPluginFactory(PluginFactory[CorrelationPlugin, CorrelationPluginInfo]):

    def create(self, plugin_name: str, misp_value: str, database_interface: DatabasePluginInterface) \
            -> CorrelationPlugin:
        """
        Create an instance of a plugin.

        :param database_interface: interface to communicate with the database
        :type database_interface: DatabasePluginInterface
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :param misp_value: The value to correlate.
        :type misp_value: str
        :return: The instantiated correlation plugin, initialized with the value.
        """
        if not self._is_plugin_registered(plugin_name):
            raise PluginNotFound(f"Unknown plugin '{plugin_name}'. Cannot be instantiated.")

        plugin_instance: CorrelationPlugin
        try:
            plugin_instance = self.plugins[plugin_name](misp_value, database_interface)
        except TypeError as type_error:
            raise NotAValidPlugin(f"Plugin '{plugin_name}' has incorrect constructor: {type_error}")

        return plugin_instance

    def get_all_plugin_info(self) -> list[CorrelationPluginInfo]:
        """
        Get a list of plugin info from all the correlation plugins
        registered in the correlation plugin factory.
        :return: list of correlation plugin info
        :rtype: list[CorrelationPluginInfo]
        """
        plugins: list[CorrelationPlugin] = self.get_plugins()
        plugin_infos: list[CorrelationPluginInfo] = list()
        for plugin in plugins:
            plugin_infos.append(self.get_plugin_info(plugin))
        return plugin_infos


correlation_plugin_factory = CorrelationPluginFactory()
