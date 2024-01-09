from enum import Enum
from typing import Protocol, Any

from pydantic import BaseModel, Field


class PluginType(str, Enum):
    """
    Enum encapsulating the possible plugin types.
    """
    CORRELATION = "correlation"
    ENRICHMENT = "enrichment"


class PluginMeta(BaseModel):
    """
    Encapsulates meta information about a plugin.
    """
    NAME: str
    PLUGIN_TYPE: PluginType
    DESCRIPTION: str
    AUTHOR: str
    VERSION: float

    class Config:
        allow_mutation: False


class Plugin(Protocol):
    """
    Class representing the structure of a plugin.
    """

    PLUGIN_META: PluginMeta = Field(..., allow_mutation=False)

    def run(self) -> Any:
        """
        Entry point of a plugin. Runs a plugin and returns any existing result.

        :return: The result the plugin returns
        :rtype Any
        """
        ...