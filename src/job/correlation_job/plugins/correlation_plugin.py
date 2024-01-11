from enum import Enum

from pydantic import Field, BaseModel

from src.job.correlation_job.job_data import CorrelateValueResponse
from src.misp_database.misp_sql import MispSQL
from src.plugins.plugin import Plugin, PluginMeta


class CorrelationPluginType(str, Enum):
    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"


class CorrelationPlugin(Plugin):
    CORRELATION_TYPE: CorrelationPluginType = Field(..., allow_mutation=False)

    def run(self) -> CorrelateValueResponse:
        pass

    def __init__(self, value: str, misp_sql: MispSQL):
        __value: str = value
        __misp_sql: MispSQL = misp_sql
        pass


class CorrelationPluginInfo(BaseModel):
    plugin: PluginMeta
    correlationType: CorrelationPluginType
