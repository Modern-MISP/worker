from typing import Self

from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin, PluginNotFound
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.plugins.factory import PluginFactory


class CorrelationPluginFactory(PluginFactory[CorrelationPlugin, CorrelationPluginInfo]):
    """
    The factory to register and create correlation plugins.
    """

    def create(self: Self, plugin_name: str, misp_value: str, misp_api: MispAPI, threshold: int) -> CorrelationPlugin:
        """
        Create an instance of a plugin.

        :param threshold: the current correlation threshold
        :type threshold: int
        :param misp_api: the misp api for the plugin to use
        :type misp_api: MispAPI
        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :param misp_value: The value to correlate.
        :type misp_value: str
        :return: The instantiated correlation plugin, initialized with the value.
        """
        if not self.is_plugin_registered(plugin_name):
            raise PluginNotFound(message=f"Unknown plugin '{plugin_name}'. Cannot be instantiated.")

        plugin_instance: CorrelationPlugin
        try:
            plugin_instance = self._plugins[plugin_name](misp_value, misp_api, threshold)
        except TypeError as type_error:
            raise NotAValidPlugin(message=f"Plugin '{plugin_name}' has incorrect constructor: {type_error}")

        return plugin_instance


correlation_plugin_factory = CorrelationPluginFactory()
"""The factory to create correlation plugins for the whole application."""
