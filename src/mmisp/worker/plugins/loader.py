import importlib
from types import ModuleType
from typing import Protocol, cast

from mmisp.worker.exceptions.plugin_exceptions import PluginRegistrationError
from mmisp.worker.plugins.factory import PluginFactory


class PluginInterface(Protocol):
    """
    Protocol class (interface) providing the necessary functions each plugin must implement to be able to become loaded.
    """

    @staticmethod
    def register(factory: PluginFactory) -> None:
        """
        Registers the plugin in the given factory.

        :param factory: The factory in which the plugin is registered.
        :type factory: PluginFactory
        """


class PluginLoader:
    """
    Implements the loading and registration process of plugins.
    """

    @staticmethod
    def __import_module(name: str) -> PluginInterface:
        imported_module: ModuleType = importlib.import_module(name)
        return cast(PluginInterface, imported_module)

    @classmethod
    def load_plugins(cls, plugins: list[str], factory: PluginFactory) -> None:
        """
        Loads the specified plugins and registers them in the given factory.

        :param plugins: The list of plugin modules to load.
        :type plugins: list[str]
        :param factory: The factory in which the plugins are to be registered.
        :type factory: PluginFactory
        """

        for plugin_file in plugins:
            plugin: PluginInterface
            try:
                plugin = cls.__import_module(plugin_file)
            except ModuleNotFoundError:
                # TODO: Log ModuleNotFoundError
                continue

            try:
                plugin.register(factory)
            except PluginRegistrationError:
                # TODO: Log PluginRegistrationError
                continue
