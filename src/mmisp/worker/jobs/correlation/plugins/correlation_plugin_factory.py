from mmisp.worker.jobs.correlation.plugins.database_plugin_interface import DatabasePluginInterface
from mmisp.worker.plugins.factory import PluginFactory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginType, CorrelationPluginInfo


class CorrelationPluginFactory(PluginFactory[CorrelationPlugin]):

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

        pass
        # try:
        #    creator_func = self.plugin_creation_funcs[plugin_name]
        # except KeyError:
        #    raise ValueError(f"TODO") from None
        # return creator_func(misp_attribute, misp_attribute_tags)

    def get_plugin_info(self, plugin_name: str) -> CorrelationPluginInfo:
        """
        Returns the info of given correlation plugin.
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The info of the correlation plugin.
        :rtype: CorrelationPluginType
        """
        pass

    def get_all_plugin_info(self) -> list[CorrelationPluginInfo]:
        """
        Get a list of plugin info from all the correlation plugins
        registered in the correlation plugin factory.
        :return: list of correlation plugin info
        :rtype: list[CorrelationPluginInfo]
        """
        plugins: list[str] = self.get_plugins()
        plugin_infos: list[CorrelationPluginInfo] = list()
        for plugin in plugins:
            plugin_infos.append(self.get_plugin_info(plugin))
        return plugin_infos

    def load_plugins(self, path: str) -> bool:
        """
        Loads all correlation plugins from the given path.
        :param path: path to the folder where correlation plugins are located
        :type path: str
        :return: if it was successful to load the plugins
        :rtype: bool
        """
        pass


correlation_plugin_factory = CorrelationPluginFactory()
