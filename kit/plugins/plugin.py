from enum import Enum
from typing import Protocol, Any

from pydantic import BaseModel


class PluginType(str, Enum):
    """
    Enum encapsulating the possible plugin types.
    """
    correlation = "correlation"
    enrichment = "enrichment"


class PluginIO(BaseModel):
    """
    Encapsulates information about the accepted and returned attribute types for a plugin.
    """

    input: list[str]  # Attribute types accepted by the plugin.
    output: list[str]  # Attribute types that can be created/returned by the plugin.


class PluginMeta(BaseModel):
    """
    Encapsulates meta information about a plugin.
    """
    name: str
    pluginType: PluginType
    description: str
    author: str
    version: float


class Plugin(Protocol):
    """
    Class representing the structure of a plugin.
    """

    __plugin_meta: dict

    def run(self) -> Any:
        """
        Entry point of a plugin. Runs a plugin and returns any existing result.

        :return: The result the plugin returns
        :rtype Any
        """
        ...
