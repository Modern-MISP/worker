from enum import Enum
from typing import List, Protocol, Any

from pydantic import BaseModel


class PluginType(str, Enum):
    correlation = "correlation"
    enrichment = "enrichment"


class PluginIO(BaseModel):
    input: List[str]  # Attribute types accepted by the plugin.
    output: List[str]  # Attribute types that can be created/returned by the plugin.


class PluginMeta(BaseModel):
    name: str
    pluginType: PluginType
    description: str
    author: str
    version: float


class Plugin(Protocol):
    def process(self) -> Any:
        ...
