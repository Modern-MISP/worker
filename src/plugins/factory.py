from abc import ABC
from typing import Callable, TypeVar, Generic

from src.plugins.plugin import Plugin, PluginInfo

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
        self.plugin_creation_funcs: dict[str, Callable[..., T]] = {}

    def register(self, plugin_name: str, creator_fn: Callable[..., T]):
        """
        Registers a new plugin.

        :param plugin_name: The name under which the plugin should be registered.
        :type plugin_name: str
        :param creator_fn: The creator function of the plugin.
        :type creator_fn: Callable[..., T]
        """
        self.plugin_creation_funcs[plugin_name] = creator_fn

    def unregister(self, plugin_name: str):
        """
        Unregisters a plugin.

        :param plugin_name: The name of the plugin to unregister.
        :type plugin_name: str
        """
        self.plugin_creation_funcs.pop(plugin_name, None)

    def get_plugin_info(self, plugin_name: str) -> PluginInfo:
        """
        Returns information about a given plugin.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :return: The information about the plugin.
        :rtype: PluginInfo
        """
        pass

    def get_plugins(self) -> list[str]:
        """
        Returns a list of registered Plugins.

        :return: A list of plugin names.
        :rtype: list[str]
        """
        pass
