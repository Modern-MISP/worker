import importlib
import pkgutil
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
        module: ModuleType
        module = importlib.import_module(name)

        return cast(PluginInterface, module)

    @classmethod
    def load_plugins(cls, plugins: list[str], factory: PluginFactory) -> None:
        """
        Loads the specified plugins and registers them in the given factory.

        :param plugins: The list of plugin modules to load.
        :type plugins: list[str]
        :param factory: The factory in which the plugins are to be registered.
        :type factory: PluginFactory
        """

        for plugin in plugins:
            plugin_module: PluginInterface
            try:
                plugin_module = cls.__import_module(plugin)
            except ModuleNotFoundError:
                # TODO: Log ModuleNotFoundError
                continue

            try:
                plugin_module.register(factory)
            except PluginRegistrationError:
                # TODO: Log PluginRegistrationError
                continue

    @classmethod
    def load_plugins_from_package(cls, package: str, factory: PluginFactory):
        """
        Loads alle plugins that are in the specified package.

        :param package: The package to load the plugins from.
        :type package: str
        :param factory: The factory in which the plugins are to be registered.
        :type factory: PluginFactory
        """

        if not package:
            raise ValueError("Package name is required. May not be empty.")

        modules: list[str] = []
        for module in pkgutil.iter_modules(package.replace('.', '/')):
            modules.append(f"{package}.{module.name}")

        cls.load_plugins(modules, factory)
