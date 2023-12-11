from enum import Enum
from pydantic import BaseModel


class PluginType(str, Enum):
    correlation = "correlation"
    enrichment = "enrichment"


class Plugin(BaseModel):
    name: str
    pluginType: PluginType
    description: str
    author: str
    version: float

    def process_attribute(self) -> object:
        """TODO"""