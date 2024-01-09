import importlib
from typing import Protocol, cast

from src.plugins.factory import PluginFactory


class PluginInterface(Protocol):
    """
    Protocol class (interface) providing the necessary functions each plugin must implement to be able to become loaded.
    """

    @staticmethod
    def register(factory: PluginFactory) -> None:
        """
        Register the necessary items in the plugin factory.
        """


class PluginLoader:

    @staticmethod
    def __import_module(name: str) -> PluginInterface:
        """
        Imports a module given a name.

        :param name: The name of the module.
        :type: str
        """

        return cast(PluginInterface, importlib.import_module(name))

    @staticmethod
    def load_plugins(plugins: list[str], factory: PluginFactory) -> None:
        """
        Loads the specified plugins and registers them in the given factory.

        :param plugins: The list of plugins to load.
        :type plugins: list[str]
        :param factory: The factory in which the plugins are to be registered.
        :type factory: PluginFactory
        """
        for plugin_file in plugins:
            plugin = PluginLoader.__import_module(plugin_file)
            plugin.register(factory)
