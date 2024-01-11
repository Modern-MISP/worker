from enum import Enum

from pydantic import Field, BaseModel

from src.job.correlation_job.job_data import CorrelateValueResponse
from src.job.correlation_job.plugins.database_plugin_interface import DatabasePluginInterface
from src.misp_database.misp_sql import MispSQL
from src.misp_dataclasses.misp_correlation import MispCorrelation
from src.plugins.plugin import Plugin, PluginInfo


class CorrelationPluginType(str, Enum):
    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"


class CorrelationPlugin(Plugin):
    CORRELATION_TYPE: CorrelationPluginType = Field(..., allow_mutation=False)

    def run(self) -> tuple[CorrelateValueResponse, list[MispCorrelation]]:
        pass

    def __init__(self, value: str, database: DatabasePluginInterface):
        __value: str = value
        __database: DatabasePluginInterface = database
        pass


class CorrelationPluginInfo(BaseModel):
    plugin: PluginInfo
    correlationType: CorrelationPluginType
