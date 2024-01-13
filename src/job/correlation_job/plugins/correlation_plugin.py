from pydantic import Field

from src.job.correlation_job.job_data import CorrelateValueResponse
from src.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from src.job.correlation_job.plugins.database_plugin_interface import DatabasePluginInterface
from src.misp_dataclasses.misp_correlation import MispCorrelation
from src.plugins.plugin import Plugin


class CorrelationPlugin(Plugin):
    PLUGIN_INFO: CorrelationPluginInfo = Field(..., allow_mutation=False)

    def run(self) -> tuple[CorrelateValueResponse, list[MispCorrelation]]:
        pass

    def __init__(self, value: str, database: DatabasePluginInterface):
        __value: str = value
        __database: DatabasePluginInterface = database
        pass
