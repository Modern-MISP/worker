from enum import Enum

from pydantic import Field, BaseModel

from src.job.correlation_job.response_data import CorrelateValueResponse
from src.plugins.plugin import Plugin, PluginMeta


class CorrelationPluginType(str, Enum):
    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"


class CorrelationPlugin(Plugin):
    CORRELATION_TYPE: CorrelationPluginType = Field(..., allow_mutation=False)

    def run(self) -> CorrelateValueResponse:
        pass

    def __init__(self, value: str):
        __value: str = value
        pass


class CorrelationPluginInfo(BaseModel):
    plugin: PluginMeta
    correlationType: CorrelationPluginType
