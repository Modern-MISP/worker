from enum import Enum
from typing import Protocol, Any

from pydantic import BaseModel, ConfigDict, constr


class PluginType(str, Enum):
    """
    Enum encapsulating possible plugin types.
    """

    CORRELATION = "correlation"
    """Type for plugins specifically made for correlation jobs."""
    ENRICHMENT = "enrichment"
    """Type for plugins specifically made for enrichment jobs."""


class PluginInfo(BaseModel):
    """
    Encapsulates information about a plugin.
    """

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    NAME: constr(min_length=1)
    """Name of the plugin"""
    PLUGIN_TYPE: PluginType
    """Type of the plugin"""
    DESCRIPTION: str = None
    """Description of the plugin"""
    AUTHOR: str = None
    """Author who wrote the plugin"""
    VERSION: str = None
    """Version of the plugin"""


class Plugin(Protocol):
    """
    Interface providing all attributes and methods a plugin must implement.
    """

    PLUGIN_INFO: PluginInfo
    """Information about the plugin."""

    def run(self) -> Any:
        """
        Entry point of the plugin. Runs the plugin and returns any existing result.

        :return: The result the plugin returns
        :rtype Any
        """
        ...
