"""
This is a plugin to test the correlation plugin integration.
The plugin correlates all attributes with the same value.
"""

import sys

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import Attribute
from mmisp.plugins.factory import register

# from mmisp.db.models.attribute import Attribute
# from mmisp.plugins.exceptions import PluginExecutionException
from mmisp.plugins.types import CorrelationPluginType, PluginType

# from mmisp.worker.jobs.correlation.job_data import InternPluginResult
# from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginType

NAME: str = "CorrelationTestPlugin"
PLUGIN_TYPE: PluginType = PluginType.CORRELATION
DESCRIPTION: str = "This is a plugin to test the correlation plugin integration."
AUTHOR: str = "Tobias Gasteiger"
VERSION: str = "1.0"
CORRELATION_TYPE: CorrelationPluginType = CorrelationPluginType.ALL_CORRELATIONS


async def run(db: AsyncSession, attribute: Attribute, correlation_threshold: int) -> None:
    """
    Runs the plugin.
    :return: the result of the plugin
    :rtype: InternPluginResult
    """
    #        if self.value == "exception":
    #            raise PluginExecutionException("This is a test exception.")
    #        if self.value == "just_exception":
    #            raise RuntimeError("This is a test exception.")
    #        if self.value == "no_result":
    #            return None
    #        if self.value == "one":
    #            return InternPluginResult(
    #                success=True, found_correlations=True, is_over_correlating_value=False, correlations=[Attribute()]
    #            )
    raise NotImplementedError


#        attributes: list[Attribute] = await misp_sql.get_attributes_with_same_value(session, self.value)
#        over_correlating: bool = len(attributes) > self.threshold
#
#        return InternPluginResult(
#            success=True,
#            found_correlations=len(attributes) > 1,
#            is_over_correlating_value=over_correlating,
#            correlations=attributes,
#        )


register(sys.modules[__name__])
