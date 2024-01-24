from pydantic import Field

from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.jobs.correlation.plugins.database_plugin_interface import DatabasePluginInterface
from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation
from mmisp.worker.plugins.plugin import Plugin


class CorrelationPlugin(Plugin):
    PLUGIN_INFO: CorrelationPluginInfo = Field(..., allow_mutation=False)

    def run(self) -> tuple[CorrelateValueResponse, list[MispCorrelation]]:
        pass

    def __init__(self, value: str, database: DatabasePluginInterface):
        __value: str = value
        __database: DatabasePluginInterface = database
        pass
