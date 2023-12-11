from typing import Any, Callable, List

from kit.plugins.plugin import Plugin

plugin_creation_funcs: dict[str, Callable[..., Plugin]] = {}


def register(plugin_name: str, creator_fn: Callable[..., Plugin]) -> None:
    """Register a new plugin."""
    plugin_creation_funcs[plugin_name] = creator_fn


def unregister(plugin_name: str) -> None:
    """Unregister a plugin."""
    plugin_creation_funcs.pop(plugin_name, None)


def create(plugin_name: str, arguments: List[object]) -> Plugin:
    """Create an instance of a plugin."""
    """TODO: arguments"""

    try:
        creator_func = plugin_creation_funcs[plugin_name]
    except KeyError:
        raise ValueError(f"TODO") from None
    return creator_func(arguments)
