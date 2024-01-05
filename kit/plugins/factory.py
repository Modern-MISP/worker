from abc import ABC
from typing import Callable, TypeVar, Generic

from kit.plugins.plugin import Plugin

T = TypeVar("T", bound=Plugin)


class PluginFactory(Generic[T], ABC):

    def __init__(self):
        self.plugin_creation_funcs: dict[str, Callable[..., T]] = {}

    def register(self, plugin_name: str, creator_fn: Callable[..., T]) -> None:
        """Register a new plugin."""
        self.plugin_creation_funcs[plugin_name] = creator_fn

    def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin."""
        self.plugin_creation_funcs.pop(plugin_name, None)