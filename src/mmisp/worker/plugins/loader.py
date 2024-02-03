import importlib.util
import os.path
import sys
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Protocol, cast

from mmisp.worker.exceptions.plugin_exceptions import PluginRegistrationError, PluginImportError
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

    PLUGIN_MODULE_NAME_PREFIX: str = "mmisp_plugins"

    @classmethod
    def __import_module(cls, path: str) -> PluginInterface:
        plugin_dir_name: str = os.path.basename(os.path.split(path)[0])
        module_name: str = os.path.splitext(os.path.basename(path))[0]
        extended_module_name: str = f"{cls.PLUGIN_MODULE_NAME_PREFIX}.{plugin_dir_name}.{module_name}"

        module: ModuleType
        if extended_module_name in sys.modules.keys():
            module = sys.modules[extended_module_name]
        else:
            module_spec: ModuleSpec
            if os.path.isfile(path):
                module_spec = importlib.util.spec_from_file_location(extended_module_name, path)
            else:
                module_init_path: str = os.path.join(path, "__init__.py")
                module_spec = importlib.util.spec_from_file_location(
                    extended_module_name, module_init_path, submodule_search_locations=[])

            module = importlib.util.module_from_spec(module_spec)
            sys.modules[extended_module_name] = module
            try:
                module_spec.loader.exec_module(module)
            except FileNotFoundError as file_not_found_error:
                raise file_not_found_error
            except Exception as import_error:
                raise PluginImportError(message=f"An error occurred while importing the plugin '{path}'. "
                                                f"Error: {import_error}")

        return cast(PluginInterface, module)

    @classmethod
    def load_plugins(cls, plugins: list[str], factory: PluginFactory) -> None:
        """
        Loads the specified plugins and registers them in the given factory.

        :param plugins: A list of paths to plugin modules to load.
        :type plugins: list[str]
        :param factory: The factory in which the plugins are to be registered.
        :type factory: PluginFactory
        """

        for plugin in plugins:
            plugin_module: PluginInterface
            try:
                plugin_module = cls.__import_module(plugin)
            except FileNotFoundError as file_not_found_error:
                # TODO: Log FileNotFoundError
                # print(file_not_found_error)
                continue
            except PluginImportError as import_error:
                # TODO: Log import_error
                # print(import_error)
                continue

            try:
                plugin_module.register(factory)
            except PluginRegistrationError:
                # TODO: Log PluginRegistrationError
                continue

    @classmethod
    def load_plugins_from_directory(cls, directory: str, factory: PluginFactory):
        """
        Loads all plugins that are in the specified directory.

        :param directory: The path to a directory containing plugins to load.
        :type directory: str
        :param factory: The factory in which the plugins are to be registered.
        :type factory: PluginFactory
        """

        if not directory:
            raise ValueError("Path to a directory is required. May not be empty.")
        if not os.path.isdir(directory):
            raise ValueError(f"The directory '{directory}' doesn't exist.")

        path_content: list[str] = os.listdir(directory)
        plugin_modules: list[str] = []
        for element in path_content:
            element_path: str = os.path.join(directory, element)
            if os.path.isdir(element_path):
                if os.path.isfile(os.path.join(element_path, "__init__.py")):
                    plugin_modules.append(element_path)
            else:
                file_extension: str = os.path.splitext(element)[1]
                if file_extension == ".py":
                    plugin_modules.append(element_path)

        cls.load_plugins(plugin_modules, factory)
