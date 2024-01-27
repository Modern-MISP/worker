from pydantic import Field

from mmisp.worker.jobs.correlation.job_data import InternPluginResult
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.jobs.correlation.plugins.database_plugin_interface import DatabasePluginInterface
from mmisp.worker.plugins.plugin import Plugin


class CorrelationPlugin(Plugin):
    PLUGIN_INFO: CorrelationPluginInfo = Field(..., allow_mutation=False)

    def run(self) -> InternPluginResult:
        """
        Runs the plugin. To be implemented by the plugin.
        :return: the result of the plugin
        :rtype: InternPluginResult
        :raises: PluginExecutionException: If the plugin is executed but an error occurs.
        """
        pass

    def __init__(self, value: str, database: DatabasePluginInterface):
        __value: str = value
        __database: DatabasePluginInterface = database
