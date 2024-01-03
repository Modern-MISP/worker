import importlib
from typing import Protocol, cast

from kit.plugins.factory import PluginFactory


class PluginInterface(Protocol):

    @staticmethod
    def register(factory: PluginFactory) -> None:
        """Register the necessary items in the plugin factory."""


def import_module(name: str) -> PluginInterface:
    """Imports a module given a name."""
    return cast(PluginInterface, importlib.import_module(name))


def load_plugins(plugins: list[str], factory: PluginFactory) -> None:
    """Loads the plugins defined in the plugins list."""
    for plugin_file in plugins:
        plugin = import_module(plugin_file)
        plugin.register(factory)
