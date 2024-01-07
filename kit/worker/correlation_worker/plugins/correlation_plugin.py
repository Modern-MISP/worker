from enum import Enum

from kit.api.job_router.job_router import CorrelationPluginData, CorrelateValueResponse
from kit.plugins.plugin import PluginMeta


class CorrelationPluginType(str, Enum):
    allCorrelations = "all"
    selectedCorrelations = "selected"


class CorrelationPlugin(PluginMeta):
    correlationType: CorrelationPluginType

    def process(self) -> CorrelateValueResponse:
        pass
