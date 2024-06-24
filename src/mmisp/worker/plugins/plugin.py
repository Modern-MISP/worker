from enum import Enum
from typing import Any, Protocol, Self

from mmisp.plugins.plugin_info import PluginInfo


class PluginType(str, Enum):
    """
    Enum encapsulating possible plugin types.
    """


class Plugin(Protocol):
    """
    Interface providing all attributes and methods a plugin must implement.
    """

    PLUGIN_INFO: PluginInfo
    """Information about the plugin."""

    def run(self: Self) -> Any:
        """
        Entry point of the plugin. Runs the plugin and returns any existing result.

        :return: The result the plugin returns
        :rtype Any
        """
        ...
