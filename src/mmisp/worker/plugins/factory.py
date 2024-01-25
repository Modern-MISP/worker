from abc import ABC
from typing import TypeVar, Generic

from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound, NotAValidPlugin, PluginRegistrationError
from mmisp.worker.plugins.plugin import Plugin, PluginInfo

T = TypeVar("T", bound=Plugin)


class PluginFactory(Generic[T], ABC):
    """
    Provides a Factory for registering and managing plugins.

    Instantiation of plugins is not part of this class.
    """

    def __init__(self):
        """
        Constructs a new plugin factory without any plugins registered.
        """

        self.plugins: dict[str, type[T]] = {}

    def register(self, plugin: type[T]):
        """
        Registers a new plugin.

        :param plugin: The class of the plugin to register.
        :type plugin: type[T]
        :raises NotAValidPlugin: If the plugin is missing the 'PLUGIN_INFO' attribute.
        :raises PluginRegistrationError: If there is already a plugin registered with the same name.
        """

        plugin_info: PluginInfo
        try:
            plugin_info = plugin.PLUGIN_INFO
        except AttributeError:
            raise NotAValidPlugin("Attribute 'PLUGIN_INFO' is missing.")

        if plugin_info.name not in self.plugins:
            self.plugins[plugin_info.name] = plugin
        else:
            raise PluginRegistrationError(f"Registration not possible. "
                                          f"The are at least two plugins with the same name '{plugin_info.name}'.")

    def unregister(self, plugin_name: str):
        """
        Unregisters a plugin.

        The plugin can be registered again later.

        :param plugin_name: The name of the plugin to remove from the factory.
        :type plugin_name: str
        :raises PluginNotFound: If there is no plugin with the specified name.
        """

        if plugin_name:
            if plugin_name in self.plugins:
                self.plugins.pop(plugin_name)
            else:
                raise PluginNotFound(f"Unknown plugin '{plugin_name}'. Cannot be removed.")
        else:
            raise ValueError("Plugin name may not be emtpy.")

    def get_plugin_info(self, plugin_name: str) -> PluginInfo:
        """
        Returns information about a registered plugin.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The information about the plugin.
        :rtype: PluginInfo
        :raises PluginNotFound: If there is no plugin with the specified name.
        """

        if plugin_name:
            if plugin_name in self.plugins:
                return self.plugins[plugin_name].PLUGIN_INFO
            else:
                raise PluginNotFound(f"The specified plugin '{plugin_name}' is not known.")
        else:
            raise ValueError("Plugin name may not be emtpy.")

    def get_plugins(self) -> list[PluginInfo]:
        """
        Returns a list of registered Plugins.

        :return: The list of plugins.
        :rtype: list[PluginInfo]
        """

        info: list[PluginInfo] = []
        for plugin in self.plugins:
            info.append(self.plugins[plugin].PLUGIN_INFO)

        return info
