from abc import ABC
from typing import TypeVar, Generic

from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound, NotAValidPlugin, PluginRegistrationError
from mmisp.worker.plugins.plugin import Plugin, PluginInfo

T = TypeVar("T", bound=Plugin)
U = TypeVar("U", bound=PluginInfo)


class PluginFactory(Generic[T, U], ABC):
    """
    Provides a Factory for registering and managing plugins.

    Instantiation of plugins is not part of this class.
    """

    def __init__(self):
        """
        Constructs a new plugin factory without any plugins registered.
        """

        self._plugins: dict[str, type[T]] = {}

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
            raise NotAValidPlugin(message="Attribute 'PLUGIN_INFO' is missing.")

        if plugin_info.NAME not in self._plugins:
            self._plugins[plugin_info.NAME] = plugin
        elif plugin != self._plugins[plugin_info.NAME]:
            raise PluginRegistrationError(f"Registration not possible. "
                                          f"The are at least two plugins with the same name '{plugin_info.name}'.")
        else:
            # If plugin is already registered, do nothing.
            pass

    def unregister(self, plugin_name: str):
        """
        Unregisters a plugin.

        The plugin can be registered again later.

        :param plugin_name: The name of the plugin to remove from the factory.
        :type plugin_name: str
        :raises PluginNotFound: If there is no plugin with the specified name.
        """

        if not self.is_plugin_registered(plugin_name):
            raise PluginNotFound(message=f"Unknown plugin '{plugin_name}'. Cannot be removed.")

        self._plugins.pop(plugin_name)

    def get_plugin_info(self, plugin_name: str) -> U:
        """
        Returns information about a registered plugin.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The information about the plugin.
        :rtype: U
        :raises PluginNotFound: If there is no plugin with the specified name.
        """

        if not self.is_plugin_registered(plugin_name):
            raise PluginNotFound(message=f"The specified plugin '{plugin_name}' is not known.")

        return self._plugins[plugin_name].PLUGIN_INFO

    def get_plugins(self) -> list[U]:
        """
        Returns a list of registered Plugins.

        :return: The list of plugins.
        :rtype: list[PluginInfo]
        """

        info: list[U] = []
        for plugin in self._plugins:
            info.append(self._plugins[plugin].PLUGIN_INFO)

        return info

    def is_plugin_registered(self, plugin_name: str) -> bool:
        """
        Checks if the given plugin is registered in the factory.

        :param plugin_name: The name of the plugin to check.
        :type plugin_name: str
        :return: True if the plugin is registered
        """

        if plugin_name:
            return plugin_name in self._plugins
        else:
            raise ValueError("Plugin name may not be emtpy.")
