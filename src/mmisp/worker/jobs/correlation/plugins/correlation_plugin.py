from typing import Self

from pydantic import Field

from mmisp.worker.jobs.correlation.job_data import InternPluginResult
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.plugins.plugin import Plugin


class CorrelationPlugin(Plugin):
    """
    Class to be implemented by correlation plugins. It provides the basic functionality to run a correlation plugin.
    """

    PLUGIN_INFO: CorrelationPluginInfo = Field(..., allow_mutation=False)

    def run(self: Self) -> InternPluginResult | None:
        """
        Runs the plugin. To be implemented by the plugin.
        :return: the result of the plugin
        :rtype: InternPluginResult
        :raises: PluginExecutionException: If the plugin is executed but an error occurs.
        """
        pass

    def __init__(self: Self, value: str, misp_sql: MispSQL, misp_api: MispAPI, threshold: int) -> None:
        self.value: str = value
        self.misp_sql: MispSQL = misp_sql
        self.misp_api: MispAPI = misp_api
        self.threshold: int = threshold
