from abc import ABC
from typing import Generic, Self, TypeVar, cast

from mmisp.plugins.plugin_info import PluginInfo
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin, PluginNotFound, PluginRegistrationError
from mmisp.worker.plugins.plugin import Plugin

_T = TypeVar("_T", bound=Plugin)
_U = TypeVar("_U", bound=PluginInfo)


class PluginFactory(Generic[_T, _U], ABC):
    """
    Provides a Factory for registering and managing plugins.

    Instantiation of plugins is not part of this class.
    """

    def __init__(self: Self) -> None:
        """
        Constructs a new plugin factory without any plugins registered.
        """

        self._plugins: dict[str, type[_T]] = {}

    def register(self: Self, plugin: type[_T]) -> None:
        """
        Registers a new plugin.

        :param plugin: The class of the plugin to register.
        :type plugin: type[T]
        :raises NotAValidPlugin: If the plugin is missing the 'PLUGIN_INFO' attribute.
        :raises PluginRegistrationError: If there is already a plugin registered with the same name.
        """

        plugin_info: PluginInfo
        try:
            plugin_info = cast(_U, plugin.PLUGIN_INFO)
        except AttributeError:
            raise NotAValidPlugin(message="Attribute 'PLUGIN_INFO' is missing.")

        if plugin_info.NAME not in self._plugins:
            self._plugins[plugin_info.NAME] = plugin
        elif plugin != self._plugins[plugin_info.NAME]:
            raise PluginRegistrationError(
                f"Registration not possible. The are at least two plugins with the same name '{plugin_info.NAME}'."
            )
        else:
            # If plugin is already registered, do nothing.
            pass

    def unregister(self: Self, plugin_name: str) -> None:
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

    def get_plugin_info(self: Self, plugin_name: str) -> _U:
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

        return cast(_U, self._plugins[plugin_name].PLUGIN_INFO)

    def get_plugins(self: Self) -> list[_U]:
        """
        Returns a list of registered Plugins.

        :return: The list of plugins.
        :rtype: list[PluginInfo]
        """

        info: list[_U] = []
        for plugin in self._plugins:
            info.append(cast(_U, self._plugins[plugin].PLUGIN_INFO))

        return info

    def is_plugin_registered(self: Self, plugin_name: str) -> bool:
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
