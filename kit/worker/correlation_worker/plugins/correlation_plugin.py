from enum import Enum

from kit.api.job_router.job_router import CorrelationPluginData, CorrelateValueResponse
from kit.plugins.plugin import PluginMeta, Plugin


class CorrelationPluginType(str, Enum):
    allCorrelations = "all"
    selectedCorrelations = "selected"


class CorrelationPlugin(Plugin):
    correlationType: CorrelationPluginType

    def run(self) -> CorrelateValueResponse:
        pass
