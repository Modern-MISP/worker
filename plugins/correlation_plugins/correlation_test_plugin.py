from typing import Self

from mmisp.db.models.attribute import Attribute
from mmisp.worker.exceptions.plugin_exceptions import PluginExecutionException
from mmisp.worker.jobs.correlation.job_data import InternPluginResult
from mmisp.worker.jobs.correlation.plugins.correlation_plugin import CorrelationPlugin
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import CorrelationPluginFactory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo, CorrelationPluginType
from mmisp.worker.plugins.plugin import PluginType


class CorrelationTestPlugin(CorrelationPlugin):
    """
    This is a plugin to test the correlation plugin integration.
    The plugin correlates all attributes with the same value.
    """

    PLUGIN_INFO: CorrelationPluginInfo = CorrelationPluginInfo(
        NAME="CorrelationTestPlugin",
        PLUGIN_TYPE=PluginType.CORRELATION,
        DESCRIPTION="This is a plugin to test the correlation " "plugin integration.",
        AUTHOR="Tobias Gasteiger",
        VERSION="1.0",
        CORRELATION_TYPE=CorrelationPluginType.ALL_CORRELATIONS,
    )

    def __init__(self: Self, value: str, misp_sql, misp_api, threshold: int):
        if value == "instructor_fail":
            raise TypeError("Test.")
        super().__init__(value, misp_sql, misp_api, threshold)

    def run(self: Self) -> InternPluginResult | None:
        """
        Runs the plugin.
        :return: the result of the plugin
        :rtype: InternPluginResult
        """
        if self.value == "exception":
            raise PluginExecutionException("This is a test exception.")
        if self.value == "just_exception":
            raise RuntimeError("This is a test exception.")
        if self.value == "no_result":
            return None
        if self.value == "one":
            return InternPluginResult(
                success=True, found_correlations=True, is_over_correlating_value=False, correlations=[Attribute()]
            )

        attributes: list[Attribute] = self.misp_sql.get_attributes_with_same_value(self.value)
        over_correlating: bool = len(attributes) > self.threshold

        return InternPluginResult(
            success=True,
            found_correlations=len(attributes) > 1,
            is_over_correlating_value=over_correlating,
            correlations=attributes,
        )


def register(factory: CorrelationPluginFactory):
    factory.register(CorrelationTestPlugin)
