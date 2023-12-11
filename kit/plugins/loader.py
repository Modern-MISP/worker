import importlib


class PluginInterface:

    @staticmethod
    def register() -> None:
        """Register the necessary items in the plugin factory."""


def import_module(name: str) -> PluginInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


def load_plugins(plugins: list[str]) -> None:
    """Loads the plugins defined in the plugins list."""
    for plugin_file in plugins:
        plugin = import_module(plugin_file)
        plugin.register()
