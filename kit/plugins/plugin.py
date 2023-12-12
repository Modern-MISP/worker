from enum import Enum
from typing import List

from pydantic import BaseModel


class PluginType(str, Enum):
    correlation = "correlation"
    enrichment = "enrichment"


class PluginIO(BaseModel):
    input: List[str]  # Attributstypen die vom Plugin akzeptiert werden.
    output: List[str]  # Attributstypen die vom Plugin erstellt/zurückgegeben werden können.


class Plugin(BaseModel):
    name: str
    pluginType: PluginType
    description: str
    author: str
    version: float

    def process_attribute(self) -> object:
        """TODO"""