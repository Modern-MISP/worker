from mmisp.worker.jobs.correlation.job_data import InternPluginResult
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import CorrelationPluginFactory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo, CorrelationPluginType
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.plugins.plugin import PluginInfo, PluginType


class CorrelationTestPlugin(CorrelationPlugin):
    """
    This is a plugin to test the correlation plugin integration.
    The plugin correlates all attributes with the same value.
    """
    PLUGIN_INFO: CorrelationPluginInfo = PluginInfo(NAME="Correlation Test Plugin", PLUGIN_TYPE=PluginType.CORRELATION,
                                                    DESCRIPTION="This is a plugin to test the correlation plugin " +
                                                                "integration.",
                                                    AUTHOR="Tobias Gasteiger", VERSION=1.0,
                                                    CORRELATION_TYPE={CorrelationPluginType.ALL_CORRELATIONS},)

    def run(self) -> InternPluginResult:
        """
        Runs the plugin.
        :return: the result of the plugin
        :rtype: InternPluginResult
        """
        attributes: list[MispEventAttribute] = self.database.get_attributes_with_same_value(self.value)
        over_correlating: bool = len(attributes) > self.database.threshold

        return InternPluginResult(success=True, found_correlations=len(attributes) > 1,
                                  is_over_correlating_value=over_correlating,
                                  correlations=attributes)


def register(factory: CorrelationPluginFactory):
    factory.register(CorrelationTestPlugin)
